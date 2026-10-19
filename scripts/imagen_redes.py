# Imagen para redes (1200x630) con el titular encima de la foto del artículo.
# Solo la usan X, WhatsApp y Facebook al compartir el enlace (og:image / twitter:image);
# en la web el artículo mantiene su foto.
#
# Uso (en el Mac mini, con Pillow instalado):
#   python3 scripts/imagen_redes.py <foto> <etiqueta> <titular> fotos/logo-diario-xerecista.png <salida.jpg> [posición vertical 0-1]
# Ejemplo:
#   python3 scripts/imagen_redes.py fotos/publicadas/x.jpg "Opinión" "¿Y si pedimos ayuda?" fotos/logo-diario-xerecista.png fotos/redes/art93-es.jpg 0.2
# La posición vertical (por defecto 0.35) elige qué parte de la foto se ve: 0 = arriba, 1 = abajo.
# Tipografías de macOS: Georgia Bold (titular) y DIN Alternate Bold (etiqueta y dominio).
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1200, 630
AZUL = (13, 44, 84); ORO = (201, 162, 75); BLANCO = (255, 255, 255)
F_TIT = '/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
F_DIN = '/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf'

def escudo_blanco(im):
    """Escudo en blanco: lo azul pasa a blanco opaco y lo blanco a transparente."""
    im = im.convert('RGBA')
    r, g, b, a = im.split()
    lum = Image.merge('RGB', (r, g, b)).convert('L')
    alfa = Image.eval(lum, lambda v: int(255 * (1 - v / 255) ** 0.7))
    alfa = ImageChops.multiply(alfa, a)
    blanco = Image.new('RGBA', im.size, (255, 255, 255, 0))
    blanco.putalpha(alfa)
    return blanco

def cubrir(im, w, h, vert=0.35):
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * vert)
    return im.crop((x, y, x + w, y + h))

def partir(draw, texto, fuente, ancho):
    lineas, actual = [], ''
    for p in texto.split():
        prueba = (actual + ' ' + p).strip()
        if draw.textlength(prueba, font=fuente) <= ancho: actual = prueba
        else: lineas.append(actual); actual = p
    lineas.append(actual); return lineas

def generar(foto, etiqueta, titulo, logo, salida, vert=0.35):
    base = cubrir(Image.open(foto).convert('RGB'), W, H, vert)
    # degradado azul desde la mitad hacia abajo para que el texto se lea siempre
    grad = Image.new('L', (1, H))
    for y in range(H):
        t = max(0, (y - H * 0.25) / (H * 0.75)); grad.putpixel((0, y), int(235 * min(1, t ** 1.1)))
    # y otro degradado lateral: más oscuro a la izquierda, donde va el texto
    lat = Image.new('L', (W, 1))
    for x in range(W):
        lat.putpixel((x, 0), int(150 * max(0, 1 - x / (W * 0.75))))
    from PIL import ImageChops
    mascara = ImageChops.lighter(grad.resize((W, H)), lat.resize((W, H)))
    capa = Image.new('RGB', (W, H), AZUL)
    base = Image.composite(capa, base, mascara)
    d = ImageDraw.Draw(base)
    margen = 64
    # titular: el mayor tamaño que quepa en 3 líneas como máximo
    for tam in range(96, 40, -4):
        ft = ImageFont.truetype(F_TIT, tam)
        lineas = partir(d, titulo, ft, W - 2 * margen - 40)
        if len(lineas) <= 3: break
    alto_linea = int(tam * 1.12)
    y_tit = H - 92 - alto_linea * len(lineas)
    # etiqueta dorada encima del titular
    fe = ImageFont.truetype(F_DIN, 26)
    et = etiqueta.upper()
    ancho_et = d.textlength(et, font=fe)
    y_et = y_tit - 54
    d.rectangle([margen, y_et, margen + ancho_et + 28, y_et + 38], fill=ORO)
    d.text((margen + 14, y_et + 6), et, font=fe, fill=AZUL)
    for i, l in enumerate(lineas):
        d.text((margen, y_tit + i * alto_linea), l, font=ft, fill=BLANCO)
    # pie: línea dorada, dominio y escudo
    d.rectangle([margen, H - 58, margen + 70, H - 54], fill=ORO)
    fd = ImageFont.truetype(F_DIN, 24)
    d.text((margen + 86, H - 70), 'DIARIOXERECISTA.ES', font=fd, fill=(255, 255, 255))
    lg = escudo_blanco(Image.open(logo)); lg.thumbnail((78, 104))
    base.paste(lg, (W - margen - lg.width, H - 28 - lg.height), lg)
    base.save(salida, 'JPEG', quality=85, optimize=True, progressive=True)

if __name__ == '__main__':
    generar(*sys.argv[1:6], vert=float(sys.argv[6]) if len(sys.argv) > 6 else 0.35)
