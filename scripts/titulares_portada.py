# Escribe en index.html los últimos titulares como HTML normal, para que Google
# los lea sin esperar a que la portada cargue las noticias. La portada los
# sustituye en cuanto carga. Ejecutar al publicar o retirar un artículo:
#   python3 -I scripts/titulares_portada.py          (reescribe el bloque)
#   python3 -I scripts/titulares_portada.py --check  (solo comprueba, sale con 1 si está desfasado)
import html, json, os, re, sys
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
INI, FIN = '<!-- TITULARES-INICIO', '<!-- TITULARES-FIN -->'
N = 17  # los mismos que enseña la portada

def bloque():
    es = json.load(open('noticias-es.json', encoding='utf-8'))
    sl = json.load(open('mapa-slugs.json', encoding='utf-8'))
    ids = [k for k, a in es.items() if a['categoria'] not in ('historias', 'opinion')]
    ids.sort(key=lambda k: (es[k]['fecha'], int(re.sub(r'\D', '', k))), reverse=True)
    txt = lambda s: html.escape(re.sub(r'<[^>]+>', '', s), quote=False)
    out = []
    for k in ids[:N]:
        a = es[k]
        out.append(f'      <article class="card"><span class="eyebrow">{txt(a["eyebrow"])}</span>'
                   f'<h4><a class="tit-link" href="/noticias/{html.escape(sl[k])}/">{txt(a["title"])}</a></h4>'
                   f'<p>{txt(a["lead"])}</p></article>')
    return '\n'.join(out)

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(re.escape(INI) + r'[^\n]*-->\n(.*?)[ \t]*' + re.escape(FIN), h, re.S)
if not m: sys.exit('No encuentro el bloque de titulares en index.html')
nuevo = bloque() + '\n'
if '--check' in sys.argv:
    sys.exit(0 if m.group(1) == nuevo else 1)
if m.group(1) != nuevo:
    open('index.html', 'w', encoding='utf-8', newline='').write(h[:m.start(1)] + nuevo + h[m.end(1):])
print(f'titulares de portada: {nuevo.count("<article")}')
