"""Genera la galería «La foto del partido» (ES y EN) a partir de foto-partido.json.

Uso (desde la raíz del repo):  python3 -I scripts/foto_partido.py
- foto-partido.json: {"fotos": [ {jornada, fecha, partido, foto, objectPosition?, titulo, pie, titulo_en, pie_en, cronica?} ]}
  La más reciente primero (la portada muestra la primera).
- Escribe la-foto-del-partido/index.html y en/la-foto-del-partido/index.html y añade ambas URLs a sitemap.xml si faltan.
"""
import html, json, os, urllib.parse

BASE = 'https://www.diarioxerecista.es'
URL_ES = BASE + '/la-foto-del-partido/'
URL_EN = BASE + '/en/la-foto-del-partido/'
fotos = json.load(open('foto-partido.json', encoding='utf-8'))['fotos']
slugs_es = json.load(open('mapa-slugs.json', encoding='utf-8'))
slugs_en = json.load(open('mapa-slugs-en.json', encoding='utf-8'))
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
e = lambda s: html.escape(str(s or ''), quote=True)

CSS = """
.fp-wrap{max-width:1000px;margin:0 auto;padding:40px 16px 64px}
.fp-wrap h1{font-family:'Fraunces',serif;font-weight:900;font-size:40px;line-height:1.1;color:var(--azul-profundo);margin:6px 0 8px}
.fp-sub{font-size:14px;color:var(--tinta-suave);margin-bottom:28px}
.fp-dest{background:var(--azul-profundo);border-top:5px solid var(--oro);border-radius:3px;overflow:hidden;margin-bottom:36px}
.fp-dest img{display:block;width:100%;height:auto;cursor:zoom-in}
.fp-dest .fp-txt{padding:18px 20px 20px;color:#fff}
.fp-et{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--oro);margin-bottom:8px}
.fp-dest h2{font-family:'Fraunces',serif;font-style:italic;font-weight:900;font-size:28px;line-height:1.2;margin:0 0 10px;color:#fff}
.fp-dest p{font-size:15px;line-height:1.7;color:rgba(255,255,255,.9);margin:0}
.fp-dest small,.fp-card small{display:block;font-size:11px;margin-top:10px;opacity:.6}
.fp-dest .fp-x-btn{display:inline-block;margin:12px 0 0 10px;vertical-align:top}
.fp-dest a.fp-cr{display:inline-block;margin-top:12px;font-size:12px;font-weight:700;color:var(--azul-profundo);background:var(--oro);padding:7px 12px;text-decoration:none;border-radius:2px}
.fp-h3{font-family:'Fraunces',serif;font-weight:900;font-size:24px;color:var(--azul-profundo);margin:0 0 14px}
.fp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
.fp-card{background:#fff;border:1px solid var(--linea);border-radius:3px;overflow:hidden}
.fp-card img{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;cursor:zoom-in}
.fp-card .fp-txt{padding:12px 14px 14px}
.fp-card .fp-et{color:#b3262e}
.fp-card h2{font-family:'Fraunces',serif;font-weight:900;font-size:18px;line-height:1.25;color:var(--azul-profundo);margin:0 0 6px}
.fp-card p{font-size:13px;line-height:1.6;color:var(--tinta-suave);margin:0}
.fp-card a.fp-cr{display:inline-block;margin-top:8px;font-size:12px;font-weight:700;text-decoration:none}
.fp-lb{display:none;position:fixed;inset:0;background:rgba(5,15,30,.94);z-index:50;align-items:center;justify-content:center;padding:16px}
.fp-lb:target{display:flex}
.fp-lb img{max-width:100%;max-height:100%;object-fit:contain}
.fp-lb .fp-x{position:absolute;inset:0}
@media(max-width:560px){.fp-wrap h1{font-size:30px}.fp-dest h2{font-size:22px}}
"""


def fecha(f, en):
    a, m, d = (int(x) for x in f.split('-'))
    return f'{d} {MONTHS[m-1]} {a}' if en else f'{d} de {MESES[m-1]} de {a}'


def page(en):
    up = '../../' if en else '../'
    url, otro = (URL_EN, up + 'la-foto-del-partido/') if en else (URL_ES, up + 'en/la-foto-del-partido/')
    T = (lambda a, b: b if en else a)
    titulo = T('La foto del partido', 'Photo of the match')
    desc = T('La temporada 2026/27 del Xerez CD, jornada a jornada, en una foto: la imagen de cada partido elegida por el Diario Xerecista.',
             "Xerez CD's 2026/27 season, matchday by matchday, in one photo: the image of every game chosen by Diario Xerecista.")
    cards, lbs = [], []
    for i, f in enumerate(fotos):
        tit = f.get('titulo_en') if en and f.get('titulo_en') else f['titulo']
        pie = f.get('pie_en') if en and f.get('pie_en') else f.get('pie', '')
        lab = f"{T('Jornada', 'Matchday')} {f['jornada']} · {f['partido']}"
        cr = ''
        if f.get('cronica'):
            s = (slugs_en if en else slugs_es).get(f['cronica'])
            if s:
                cr = f'<a class="fp-cr" href="{up}{"en/" if en else ""}noticias/{s}/">{T("Leer la crónica →", "Read the match report →")}</a>'
        lid = f'f{i}'
        img = f'<a href="#{lid}"><img src="{up}{e(f["foto"])}" alt="{e(tit)}" loading="{"eager" if i == 0 else "lazy"}" style="object-position:{e(f.get("objectPosition", "center 30%"))}"></a>'
        txt = (f'<div class="fp-txt"><span class="fp-et">{e(lab)}</span><h2>{e(tit)}</h2><p>{e(pie)}</p>'
               f'<small>{T("Foto: Diario Xerecista", "Photo: Diario Xerecista")} · {fecha(f["fecha"], en)}</small>{cr}</div>')
        if i == 0:
            texto_x = f"📸 {titulo} · {T('Jornada', 'Matchday')} {f['jornada']}: {tit}\n\n{url}\n\n#XerezCD"
            share = 'https://x.com/intent/tweet?text=' + urllib.parse.quote(texto_x, safe='')
            txt = txt[:-6] + f'<a class="fp-x-btn share-x-btn" href="{share}" target="_blank" rel="noopener">{T("Compartir en 𝕏", "Share on 𝕏")}</a></div>'
        cards.append(f'<article class="{"fp-dest" if i == 0 else "fp-card"}">{img}{txt}</article>')
        lbs.append(f'<div class="fp-lb" id="{lid}"><a class="fp-x" href="#" aria-label="{T("Cerrar", "Close")}"></a><img src="{up}{e(f["foto"])}" alt="{e(tit)}"></div>')
    dest = cards[0] if cards else ''
    resto = ''
    if len(cards) > 1:
        resto = f'<h3 class="fp-h3">{T("Jornadas anteriores", "Previous matchdays")}</h3><div class="fp-grid">{"".join(cards[1:])}</div>'
    og = f'{BASE}/{fotos[0]["foto"]}' if fotos else f'{BASE}/fotos/logo-diario-xerecista.png'
    og_dim = ''
    if fotos:
        redes = f'fotos/redes/foto-partido-j{fotos[0]["jornada"]}-{"en" if en else "es"}.jpg'
        if os.path.exists(redes):
            og = f'{BASE}/{redes}'
            og_dim = '\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">'
    return f'''<!DOCTYPE html>
<html lang="{'en' if en else 'es'}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} | Diario Xerecista</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="es" href="{URL_ES}">
<link rel="alternate" hreflang="en" href="{URL_EN}">
<link rel="alternate" hreflang="x-default" href="{URL_ES}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Diario Xerecista">
<meta property="og:title" content="{titulo} · Xerez CD 2026/27">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">{og_dim}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{og}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,900;1,9..144,600;1,9..144,900&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}noticia.css?v=7">
<style>{CSS}</style>
<link rel="icon" href="{up}favicon.ico" sizes="48x48">
<link rel="icon" type="image/png" sizes="192x192" href="{up}icono-192.png">
<link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
</head>
<body>
  <header class="n-header">
    <a class="n-brand" href="{up}index.html">
      <img src="{up}fotos/escudos/escudo-xerez-cd-hd.png" alt="Escudo Xerez Club Deportivo">
      <span>Diario Xerecista</span>
    </a>
    <a class="n-home-link" href="{up}index.html">{T('Portada', 'Home')}</a>
    <a class="n-home-link" href="{otro}">{T('🇬🇧 English', '🇪🇸 Español')}</a>
  </header>
  <main class="fp-wrap">
    <span class="eyebrow">📸 Xerez CD · {T('Temporada 2026/27', '2026/27 season')}</span>
    <h1>{titulo}</h1>
    <p class="fp-sub">{T('La temporada, jornada a jornada, en una foto.', 'The season, matchday by matchday, in one photo.')}</p>
    {dest}
    {resto}
    <p style="margin-top:32px"><a class="back-link" href="{up}index.html">{T('← Volver a la portada', '← Back to home')}</a></p>
  </main>
  {''.join(lbs)}
  <footer class="n-foot">{T('© Diario Xerecista — Edición digital, temporada 2026/27', '© Diario Xerecista — Digital edition, 2026/27 season')}</footer>
</body>
</html>
'''


for en, d in ((False, 'la-foto-del-partido'), (True, 'en/la-foto-del-partido')):
    os.makedirs(d, exist_ok=True)
    open(d + '/index.html', 'w', encoding='utf-8').write(page(en))

sm = open('sitemap.xml', encoding='utf-8').read()
if URL_ES not in sm:
    last = fotos[0]['fecha'] if fotos else ''
    blk = ''
    for u in (URL_ES, URL_EN):
        blk += f'''<url>
    <loc>{u}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.6</priority>
    <lastmod>{last}</lastmod>
    <xhtml:link rel="alternate" hreflang="es" href="{URL_ES}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{URL_EN}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{URL_ES}"/>
  </url>
  '''
    open('sitemap.xml', 'w', encoding='utf-8').write(sm.replace('</urlset>', '  ' + blk.strip() + '\n</urlset>'))
else:
    import re
    last = fotos[0]['fecha'] if fotos else None
    if last:
        sm = re.sub(r'(<loc>' + re.escape(URL_ES) + r'</loc>.*?<lastmod>)[^<]*', r'\g<1>' + last, sm, flags=re.S)
        sm = re.sub(r'(<loc>' + re.escape(URL_EN) + r'</loc>.*?<lastmod>)[^<]*', r'\g<1>' + last, sm, flags=re.S)
        open('sitemap.xml', 'w', encoding='utf-8').write(sm)
print('galería:', len(fotos), 'fotos')
