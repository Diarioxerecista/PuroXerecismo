"""Kit para X al acabar un partido: imagen de resultado + texto del tuit en tuit/ (página invisible).

Uso (desde la raíz del repo, lo lanzan los workflows):
  python3 scripts/kit_redes.py --live     # si live.json está en FINAL y aún no hay kit de ese partido, lo crea
  python3 scripts/kit_redes.py --foto     # rehace la imagen con la última foto subida a fotos/partido/
  python3 scripts/kit_redes.py --prueba   # kit del último partido con resultado en PARTIDOS (goleadores de su crónica)

Escribe tuit/resultado.jpg y tuit/datos.json. Requiere Pillow (y pillow-heif para fotos HEIC del iPhone).
"""
import hashlib, json, os, re, sys, unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resultado_final as rf

DIR = 'tuit'
DATOS = os.path.join(DIR, 'datos.json')
IMAGEN = os.path.join(DIR, 'resultado.jpg')
SUBIDAS = os.path.join('fotos', 'partido')
AHORA = lambda: datetime.now(ZoneInfo('Europe/Madrid'))


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def partidos():
    html = open('index.html', encoding='utf-8').read()
    bloque = re.search(r'const PARTIDOS = \[(.*?)\n\s*\];', html, re.S).group(1)
    out = []
    for linea in re.findall(r'\{fecha:[^\n]*\}', bloque):
        d = dict(re.findall(r"(\w+):'((?:[^'\\]|\\.)*)'", linea))
        m = re.search(r"resultado:'([^']*)'", linea)
        d['resultado'] = m.group(1) if m else None
        out.append(d)
    return out


def buscar_partido(local, visitante):
    """El partido de PARTIDOS con esos equipos más cercano a hoy (para jornada, tipo y sede)."""
    hoy = AHORA().date().isoformat()
    cand = [p for p in partidos() if p.get('local') == local and p.get('visitante') == visitante]
    cand.sort(key=lambda p: abs((datetime.fromisoformat(p['fecha']) - datetime.fromisoformat(hoy)).days))
    return cand[0] if cand else {}


def leer(p, defecto=None):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return defecto


def foto_archivo(clave, gana_xerez):
    """Foto de liga de archivo (nunca de la Copa ante el Cádiz), fija para cada partido."""
    fotos = sorted(f for f in os.listdir('fotos/publicadas')
                   if f.lower().endswith(('.jpg', '.jpeg')) and 'cadiz' not in f.lower()
                   and 'xerez' in f.lower() and re.search(r'-j\d+-', f.lower()))
    alegres = [f for f in fotos if re.search(r'celebra|gol|saludo', f.lower())]
    lista = (alegres if gana_xerez and alegres else [f for f in fotos if f not in alegres] or fotos)
    i = int(hashlib.md5(clave.encode()).hexdigest(), 16) % len(lista)
    return os.path.join('fotos/publicadas', lista[i])


def texto_tuit(d):
    esc, nombres = rf.escudos_y_nombres()
    vis = lambda e: rf.nombre_visible(e, esc, nombres).title().replace('Cd', 'CD').replace(' De ', ' de ')
    loc, vis_ = vis(d['local']), vis(d['visitante'])
    lineas = [f"✅ FINAL | {loc} {d['gl']}-{d['gv']} {vis_}", '']
    goles = sorted(d.get('goles') or [], key=lambda g: int(re.sub(r'\D', '', str(g.get('minuto', ''))) or 0))
    por_jugador = {}  # un doblete o un hat-trick en una sola línea: "Julito 52', 77', 78'"
    for g in goles:
        extra = {'pen': ' (p)', 'pp': ' (pp)'}.get(g.get('tipo') or '', '')
        equipo = d['local'] if g.get('equipo') == 'local' else d['visitante']
        por_jugador.setdefault((g.get('jugador', ''), equipo), []).append(f"{g.get('minuto', '')}'{extra}")
    for (jugador, equipo), mins in por_jugador.items():
        quien = '' if equipo == 'Xerez CD' else f" ({vis(equipo)})"
        lineas.append(f"⚽ {jugador} {', '.join(mins)}{quien}")
    if goles:
        lineas.append('')
    xerez_local = d['local'] == 'Xerez CD'
    gx, gr = (d['gl'], d['gv']) if xerez_local else (d['gv'], d['gl'])
    lineas.append('Victoria del Xerez CD 💙' if gx > gr else ('Reparto de puntos' if gx == gr else 'Derrota del Xerez CD'))
    lineas += ['', '📲 diarioxerecista.es', '',
               '#XerezCD #CopaDelRey' if d.get('copa') else '#XerezCD #SegundaRFEF']
    return '\n'.join(lineas)


def generar(d, foto, origen):
    os.makedirs(DIR, exist_ok=True)
    rf.main(d['local'], d['visitante'], d['gl'], d['gv'], foto, IMAGEN, d.get('vert', 0.4), d.get('copa'))
    d.update(foto=foto, origenFoto=origen, texto=texto_tuit(d), generado=AHORA().strftime('%d/%m/%Y %H:%M'),
             v=AHORA().strftime('%Y%m%d%H%M%S'))
    json.dump(d, open(DATOS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('kit creado:', d['clave'], '| foto:', foto)


def datos_partido(local, visitante, gl, gv, goles, fecha):
    p = buscar_partido(local, visitante)
    gl, gv = int(gl), int(gv)
    gana = (gl > gv) if local == 'Xerez CD' else (gv > gl)
    return {'clave': f"{fecha} {local} - {visitante}", 'fecha': fecha, 'jornada': p.get('jornada', ''),
            'local': local, 'visitante': visitante, 'gl': gl, 'gv': gv, 'goles': goles,
            'copa': p.get('tipo') == 'copa', 'ganaXerez': gana}


def desde_live():
    live = leer('live.json', {}) or {}
    if not (live.get('activo') and live.get('estado') == 'FINAL'):
        print('live.json no está en FINAL: nada que hacer'); return
    m = re.match(r'\s*(\d+)\s*-\s*(\d+)', str(live.get('resultado', '')))
    if not m:
        print('resultado ilegible en live.json'); return
    d = datos_partido(live['local'], live['visitante'], m.group(1), m.group(2), live.get('goles') or [],
                      AHORA().date().isoformat())
    previo = leer(DATOS, {}) or {}
    if previo.get('clave') == d['clave'] and previo.get('origenFoto') == 'tuya':
        print('ya hay kit con foto propia de este partido: no se toca'); return
    if previo.get('clave') == d['clave'] and previo.get('gl') == d['gl'] and previo.get('gv') == d['gv'] \
            and previo.get('goles') == d['goles']:
        print('kit ya creado y sin cambios'); return
    generar(d, foto_archivo(d['clave'], d['ganaXerez']), 'archivo')


def goles_de_cronica(local, visitante, resultado):
    es = leer('noticias-es.json', {})
    for a in sorted(es.values(), key=lambda a: a.get('fecha', ''), reverse=True):
        if a.get('scoreHome') == local and a.get('scoreAway') == visitante and a.get('score') == resultado:
            goles = []
            for lado, campo in (('local', 'goleadoresHome'), ('visitante', 'goleadoresAway')):
                for t in filter(None, re.split(r'<br\s*/?>', a.get(campo) or '')):
                    mm = re.match(r"\s*(.*?)\s+(\d+)'?\s*(\(p\)|\(pp\))?\s*$", t)
                    if mm:
                        goles.append({'equipo': lado, 'jugador': mm.group(1), 'minuto': mm.group(2),
                                      'tipo': {'(p)': 'pen', '(pp)': 'pp'}.get(mm.group(3) or '', '')})
            return goles
    return []


def prueba():
    jugados = [p for p in partidos() if p.get('resultado') and p.get('tipo') != 'amistoso']
    p = max(jugados, key=lambda p: p['fecha'])
    gl, gv = p['resultado'].split('-')
    d = datos_partido(p['local'], p['visitante'], gl, gv, goles_de_cronica(p['local'], p['visitante'], p['resultado']),
                      p['fecha'])
    generar(d, foto_archivo(d['clave'], d['ganaXerez']), 'archivo')


def desde_foto():
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except Exception:
        pass
    from PIL import Image, ImageOps
    if not os.path.isdir(SUBIDAS):
        print('no hay carpeta de subidas'); return
    subidas = [os.path.join(SUBIDAS, f) for f in os.listdir(SUBIDAS)
               if not f.startswith('.') and f.lower() != 'leeme.md']
    if not subidas:
        print('no hay fotos subidas'); return
    d = leer(DATOS)
    if not d:
        prueba(); d = leer(DATOS)
    nueva = max(subidas, key=os.path.getmtime)
    img = ImageOps.exif_transpose(Image.open(nueva)).convert('RGB')
    if img.width > 1400:
        img = img.resize((1400, round(img.height * 1400 / img.width)), Image.LANCZOS)
    base = f"{norm(d['local'])}-{norm(d['visitante'])}-{norm(d.get('jornada') or d['fecha'])}-grada"
    n = 1
    while os.path.exists(f'fotos/publicadas/{base}-{n}.jpg'):
        n += 1
    destino = f'fotos/publicadas/{base}-{n}.jpg'
    img.save(destino, 'JPEG', quality=82, progressive=True, optimize=True)
    for f in subidas:
        os.remove(f)
    # Las fotos verticales del móvil: encuadre algo más arriba para no cortar las cabezas
    d['vert'] = 0.3 if img.height > img.width else 0.4
    generar(d, destino, 'tuya')


if __name__ == '__main__':
    modo = (sys.argv[1:] or ['--live'])[0]
    {'--live': desde_live, '--foto': desde_foto, '--prueba': prueba}[modo]()
