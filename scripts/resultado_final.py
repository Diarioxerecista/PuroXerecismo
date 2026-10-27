"""Imagen de resultado final para redes (843x1264) a partir del modelo de scripts/plantilla-resultado/.

Uso (desde la raíz del repo):
  python3 scripts/resultado_final.py "Xerez CD" "Marbella F.C." 1 0 fotos/publicadas/foto-partido.jpg salida.jpg [--vert 0.4]

Los nombres de equipo son los de PARTIDOS/ESCUDOS en index.html. La foto es la del partido
(se recorta para llenar la franja superior; --vert mueve el encuadre: 0 arriba, 1 abajo).
Requiere Pillow.
"""
import json, os, re, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, 'plantilla-resultado', 'modelo.jpg')
FUENTES = ['/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
AZUL_ARRIBA, AZUL_ABAJO = (8, 42, 92), (3, 26, 70)


def fuente(tam):
    for f in FUENTES:
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def escudos_y_nombres():
    html = open('index.html', encoding='utf-8').read()
    bloque = re.search(r'const ESCUDOS = \{(.*?)\};', html, re.S).group(1)
    esc = {re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), k): v for k, v in re.findall(r"'((?:[^'\\]|\\.)*)'\s*:\s*'([^']+)'", bloque)}
    nombres = {e['escudo']: e['nombre'] for e in json.load(open('clasificacion.json', encoding='utf-8'))['equipos']}
    return esc, nombres


def nombre_visible(equipo, esc, nombres):
    ruta = esc.get(equipo, '')
    for k, v in nombres.items():
        if os.path.basename(k) == os.path.basename(ruta):
            return v.upper()
    return re.sub(r'^(C\.D\.|U\.D\.|C\.A\.|C\.P\.|C\.|RC)\s+', '', equipo).replace(' F.C.', '').upper()


def mascara_rect(w, h, caja, fundidos):
    """Máscara blanca en `caja` con fundidos (izq, arriba, der, abajo) en píxeles."""
    m = Image.new('L', (w, h), 0)
    x0, y0, x1, y1 = caja
    fi, fa, fd, fb = fundidos
    d = ImageDraw.Draw(m)
    for y in range(y0, y1):
        va = min(1, (y - y0) / fa) if fa else 1
        vb = min(1, (y1 - y) / fb) if fb else 1
        d.line([(x0, y), (x1, y)], fill=int(255 * va * vb))
    hor = Image.new('L', (w, h), 0)
    dh = ImageDraw.Draw(hor)
    for x in range(x0, x1):
        vi = min(1, (x - x0) / fi) if fi else 1
        vd = min(1, (x1 - x) / fd) if fd else 1
        dh.line([(x, 0), (x, h)], fill=int(255 * vi * vd))
    return ImageChops.multiply(m, hor)


def degradado(w, h, c0, c1):
    g = Image.new('RGB', (w, h))
    d = ImageDraw.Draw(g)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(c0, c1)))
    return g


def texto(lienzo, xy, s, f, max_ancho=None):
    d = ImageDraw.Draw(lienzo)
    while max_ancho and d.textlength(s, font=f) > max_ancho and f.size > 20:
        f = fuente(f.size - 2)
    sombra = Image.new('RGBA', lienzo.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, 160), anchor='mm')
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(lienzo).text(xy, s, font=f, fill=(255, 255, 255, 255), anchor='mm')


def pegar_escudo(lienzo, ruta, centro, caja):
    e = Image.open(ruta).convert('RGBA')
    e = ImageOps.contain(e, caja, Image.LANCZOS)
    sombra = Image.new('RGBA', lienzo.size, (0, 0, 0, 0))
    a = e.split()[3].point(lambda v: v * 0.55)
    sombra.paste((0, 0, 0, 255), (centro[0] - e.width // 2 + 4, centro[1] - e.height // 2 + 6), a)
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(6)))
    lienzo.alpha_composite(e, (centro[0] - e.width // 2, centro[1] - e.height // 2))


def main(local, visitante, gl, gv, foto, salida, vert=0.4):
    esc, nombres = escudos_y_nombres()
    for eq in (local, visitante):
        assert eq in esc, f'Sin escudo en ESCUDOS de index.html: {eq}'
    base = Image.open(MODELO).convert('RGB')
    W, H = base.size
    lienzo = base.copy()

    # 1. Borrar la zona central del modelo (foto, escudos, nombres, marcador) con azul liso
    centro = (0, 95, W, 955)
    azul = degradado(W, H, AZUL_ARRIBA, AZUL_ABAJO)
    lienzo.paste(azul, (0, 0), mascara_rect(W, H, centro, (60, 40, 60, 40)))
    lienzo.paste(azul, (0, 0), mascara_rect(W, H, (40, 440, W - 20, 950), (40, 60, 40, 20)))

    # 2. Foto del partido en la franja superior, fundida con el azul
    fx0, fy0, fx1, fy1 = 0, 105, W, 720
    f = Image.open(foto).convert('RGB')
    f = ImageOps.fit(f, (fx1 - fx0, fy1 - fy0), Image.LANCZOS, centering=(0.5, vert))
    capa = Image.new('RGB', (W, H)); capa.paste(f, (fx0, fy0))
    lienzo.paste(capa, (0, 0), mascara_rect(W, H, (fx0, fy0, fx1, fy1), (70, 70, 70, 230)))

    # 3. Recuperar del modelo los elementos blancos de arriba (logos RFEF y "Juntos somos más")
    lum = base.convert('L')
    for caja in ((225, 30, 600, 125), (680, 25, 820, 200)):
        m = Image.new('L', (W, H), 0)
        m.paste(lum.crop(caja).point(lambda v: 255 if v > 185 else (0 if v < 140 else (v - 140) * 255 // 45)), caja[:2])
        lienzo.paste(base, (0, 0), m)

    # 4. Escudo del Xerez en marca de agua (arriba a la izquierda), como en el modelo
    lienzo = lienzo.convert('RGBA')
    marca = Image.open(esc['Xerez CD']).convert('RGBA')
    marca = ImageOps.contain(marca, (185, 300), Image.LANCZOS)
    gris = ImageOps.grayscale(marca).point(lambda v: 150 + v // 3)
    marca = Image.merge('RGBA', (gris.point(lambda v: v * 0.75), gris.point(lambda v: v * 0.85), gris,
                                 marca.split()[3].point(lambda v: v * 0.28)))
    lienzo.alpha_composite(marca, (12, 0))

    # 5. Escudos, nombres y marcador
    pegar_escudo(lienzo, esc[local], (228, 690), (200, 190))
    pegar_escudo(lienzo, esc[visitante], (617, 690), (200, 190))
    texto(lienzo, (228, 818), nombre_visible(local, esc, nombres), fuente(44), 330)
    texto(lienzo, (617, 818), nombre_visible(visitante, esc, nombres), fuente(44), 330)
    gran = fuente(92)
    texto(lienzo, (228, 904), str(gl), gran)
    texto(lienzo, (425, 904), 'FINAL', gran)
    texto(lienzo, (617, 904), str(gv), gran)

    lienzo.convert('RGB').save(salida, quality=92)
    print('ok', salida)


if __name__ == '__main__':
    a = sys.argv[1:]
    vert = 0.4
    if '--vert' in a:
        i = a.index('--vert'); vert = float(a[i + 1]); del a[i:i + 2]
    main(a[0], a[1], a[2], a[3], a[4], a[5], vert)
