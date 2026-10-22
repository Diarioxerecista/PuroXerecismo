# Comprobaciones de "Antes de entregar" (CLAUDE.md). Uso: python3 scripts/comprobar.py
import json, os, re, sys, glob, ast
from urllib.parse import unquote
from collections import Counter
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
B = 'https://www.diarioxerecista.es/'; err = []
def load(p):
    try: return json.load(open(p, encoding='utf-8'))
    except Exception as e: err.append(f'JSON inválido {p}: {e}')
for p in glob.glob('*.json'): load(p)
es, en, sl, sle, fa = (load(p) for p in ['noticias-es.json', 'noticias-en.json', 'mapa-slugs.json', 'mapa-slugs-en.json', 'fotos-articulos.json'])
sm = open('sitemap.xml', encoding='utf-8').read(); locs = re.findall(r'<loc>(.*?)</loc>', sm)
cats = lambda a: a['categoria'] if isinstance(a['categoria'], list) else [a['categoria']]
for k in set(es) | set(en) | set(sl) | set(sle) | set(fa):
    for name, d in [('ES', es), ('EN', en), ('slug ES', sl), ('slug EN', sle), ('foto', fa)]:
        if k not in d: err.append(f'{k}: falta {name}')
    if k in fa and not os.path.isfile(fa[k]['foto']): err.append(f'{k}: foto no existe {fa[k]["foto"]}')
    for d, base in [(sl, 'noticias'), (sle, 'en/noticias')]:
        if k in d:
            if not os.path.isfile(f'{base}/{d[k]}/index.html'): err.append(f'{k}: falta HTML {base}/{d[k]}')
            if B + base + '/' + d[k] + '/' not in locs: err.append(f'{k}: no está en sitemap {base}')
            if re.search(r'/(\d{4}-\d\d)/\1/', d[k]): err.append(f'{k}: mes duplicado')
dirs = {os.path.relpath(os.path.dirname(f), 'noticias') for f in glob.glob('noticias/*/*/*/index.html')}
dirsen = {os.path.relpath(os.path.dirname(f), 'en/noticias') for f in glob.glob('en/noticias/*/*/*/index.html')}
err += [f'carpeta ES huérfana {d}' for d in dirs - set(sl.values())] + [f'carpeta EN huérfana {d}' for d in dirsen - set(sle.values())]
valid = {B + 'noticias/' + s + '/' for s in sl.values()} | {B + 'en/noticias/' + s + '/' for s in sle.values()}
err += [f'sitemap huérfano {l}' for l in locs if '/noticias/' in l and l not in valid] + [f'sitemap duplicado {l}' for l, c in Counter(locs).items() if c > 1]
for b in re.findall(r'<url>.*?</url>', sm, re.S):
    if '/noticias/' in b and 'hreflang="en"' not in b: err.append('sitemap sin hreflang en: ' + re.search(r'<loc>(.*?)</loc>', b).group(1))
n = [k for k, a in es.items() if 'noticia' in cats(a) and 'cronica' not in cats(a)]
if len(n) != 17: err.append(f'recuento de noticias = {len(n)} (debe ser 17)')
for f in glob.glob('noticias/*/*/*/index.html') + glob.glob('en/noticias/*/*/*/index.html'):
    h = open(f, encoding='utf-8').read(); d = os.path.dirname(f)
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    if not m or m.group(1) != B + d + '/': err.append(f'canonical mal en {f}')
    for u in re.findall(r'(?:href|src)="([^"]+)"', h):
        if u.startswith(('http', 'mailto:', '#', 'data:', 'javascript:', 'tel:')): continue
        t = os.path.normpath(os.path.join(d, unquote(u.split('#')[0].split('?')[0])))
        if u.endswith('/'): t = os.path.join(t, 'index.html')
        if not os.path.exists(t): err.append(f'ruta rota en {f}: {u}')
    for img in re.findall(r'(?:og:image|twitter:image)" content="https://www\.diarioxerecista\.es/([^"]+)"', h):
        if not os.path.isfile(img): err.append(f'imagen para redes no existe en {f}: {img}')
idx = open('index.html', encoding='utf-8').read()
esc = {ast.literal_eval(k): ast.literal_eval(v) for k, v in re.findall(r"^\s*('(?:[^'\\]|\\.)*')\s*:\s*('(?:[^'\\]|\\.)*')", re.search(r'const ESCUDOS\s*=\s*\{(.*?)\};', idx, re.S).group(1), re.M)}
err += [f'escudo no existe {k}' for k, v in esc.items() if not os.path.isfile(v)]
err += [f'clasificación sin escudo {e["nombre"]}' for e in load('clasificacion.json')['equipos'] if not os.path.isfile(e['escudo'])]
p = re.search(r'const PARTIDOS\s*=\s*\[(.*?)\];', idx, re.S).group(1)
rows = re.findall(r"\{fecha:'([^']+)',jornada:'([^']+)',\s*local:\s*('(?:[^'\\]|\\.)*'),\s*visitante:\s*('(?:[^'\\]|\\.)*')(.*?)\}", p)
oficiales = {ast.literal_eval(x) for r in rows if "amistoso" not in r[4] for x in (r[2], r[3])}
err += [f'rival oficial sin escudo {t}' for t in oficiales - set(esc)]
import xml.dom.minidom
try: xml.dom.minidom.parseString(sm.encode())
except Exception as e: err.append(f'sitemap XML inválido: {e}')
print(f'noticias={len(n)} | artículos={len(es)} | URLs sitemap={len(locs)}')
print('OK: sin fallos' if not err else 'FALLOS:\n  ' + '\n  '.join(err))
sys.exit(1 if err else 0)
