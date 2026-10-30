# Reglas del proyecto — Diario Xerecista (www.diarioxerecista.es)

Web de aficionados del Xerez CD, bilingüe ES/EN, temporada 2026/27 (Segunda RFEF, Grupo IV).

## Dónde trabajar
- **En Claude Code / GitHub:** el repositorio ES la web. Edita los archivos en la raíz y haz commit + push. No uses las carpetas espejo.
- Las antiguas carpetas espejo (`subir-ahora/`, `web-completa/`, `para-subir/`) ya no se usan: la única copia de la web es la raíz del repositorio.
- Ignorar: `entrega-art66/`, `entrega-art67/`, `screenshots/`, `uploads/`, `preview-*.html`, `cromo-preview.html`.

## Entregas: carpetas SIEMPRE completas
Al subir, si se cambia el contenido de una carpeta se borra todo lo demás que había en ella. Por tanto, cualquier entrega que toque una carpeta (fotos/, noticias/, en/, fotos/escudos/, etc.) debe incluir esa carpeta ENTERA con todo su contenido actual, nunca solo los archivos nuevos. Ante la duda, entregar la web completa sincronizada. (En GitHub no aplica: el push ya sube solo lo cambiado sin borrar nada.)

## Publicación bilingüe obligatoria
TODO artículo que se publique (noticia, crónica, opinión, historia) se publica SIEMPRE en español y en inglés en la misma tanda, sin preguntar. Eso implica:
- entrada en `noticias-es.json` y `noticias-en.json` con el mismo id (artNN, siguiente número libre)
- slug en `mapa-slugs.json` y `mapa-slugs-en.json`
- foto en `fotos-articulos.json`
- carpeta HTML en `noticias/...` y en `en/noticias/...`
- bloque `<url>` en `sitemap.xml` para ambas URLs, con hreflang es/en/x-default cruzado
- enlaces cruzados ES↔EN en la cabecera (🇬🇧 English / 🇪🇸 Español) y al pie de cada artículo

El texto español se respeta literal (solo se corrigen erratas evidentes y mayúsculas de nombres propios, avisando). El inglés es traducción fiel, sin reescribir ni resumir.

## Estilo de redacción
- Cuando el usuario envíe notas o datos sueltos, redactar la pieza como un periodista deportivo profesional de un diario local: pirámide invertida, lo más importante en el titular y la entradilla, frases claras, sin adornos ni opiniones (salvo en Opinión).
- Usar solo los datos que dé el usuario y los del repositorio (calendario, clasificación, plantilla). No inventar declaraciones, cifras ni fuentes.
- Lo que sea suposición, escribirlo como tal ("podría", "según apuntan").
- Avisar al usuario de cualquier dato que no cuadre con el repositorio antes de publicar.
- Enseñar al usuario solo el texto en español antes de publicarlo. Cuando lo apruebe, publicar a la vez la versión española y la inglesa.
- Si el usuario envía el texto ya redactado, se respeta literal (como dice la sección de publicación bilingüe).

## Rotación de noticias (categoría "noticia" únicamente)
Mantener siempre un máximo de 17 artículos con `categoria: "noticia"` (o array que incluya "noticia" pero no "cronica") en noticias-es.json. Al publicar uno nuevo que supere ese total, borrar el más antiguo (por `fecha`; empate → id menor) de esa categoría en:
- noticias-es.json y noticias-en.json
- mapa-slugs.json y mapa-slugs-en.json
- fotos-articulos.json
- sitemap.xml (bloque `<url>` es y en)
- su carpeta HTML en noticias/... y en/noticias/... (comprobar SIEMPRE que existe también la EN y borrarla)
- su foto en `fotos/publicadas/`, para ahorrar espacio en la web, SOLO si ya no la usa ningún otro archivo (otro artículo en fotos-articulos.json, cualquier HTML, index.html, plantilla.json…). Buscar el nombre del archivo en todo el proyecto antes de borrarla. Si se usa en otro sitio, se conserva.
- No borrar fotos de `fotos/publicadas/` que no sean de un artículo borrado: las no usadas son el banco para "una foto cualquiera / de partidos anteriores". Tampoco tocar `fotos/cromos/`, `fotos/escudos/`, `fotos/plantilla/` ni `fotos/publicidad/` por esta regla.
- Al entregar fuera de GitHub, incluir la carpeta `fotos/publicadas/` entera si se ha borrado alguna foto.

Las Crónicas (categoria incluye "cronica") y las Historias Xerecistas (categoria "historias") NO cuentan para este límite y no se borran — se conservan siempre.

La portada necesita al menos 17 artículos no-"historias" (1 destacado + 4 en barra lateral + 12 en "Lo último").

## Formato de un artículo

### JSON (`noticias-es.json` / `noticias-en.json`, objeto con claves artNN)
```json
"art85": {
  "fecha": "2026-10-12",
  "categoria": "noticia",
  "eyebrow": "Xerez CD · Enfermería",
  "title": "Titular",
  "lead": "Entradilla",
  "body": ["Párrafo…", "<strong>Ladillo</strong>", "Párrafo…"]
}
```
- Ladillos: elemento del array con `<strong>…</strong>` (en el HTML se pintan como `<h2>`).
- Categorías: `"noticia"`, `["cronica","noticia"]`, `"historias"`, `"opinion"` (solo sección Opinión, no sale en portada), `["opinion","noticia"]` (opinión que sí sale en portada y cuenta para las 17).
- Eyebrows usados: "Segunda RFEF · Jornada N" / "Segunda RFEF · Matchday N"; "Opinión · Análisis" / "Opinion · Analysis"; "Xerez CD · Enfermería" / "Xerez CD · Injuries".
- Crónicas: rellenar SIEMPRE `goleadoresHome` y `goleadoresAway` con el formato "Nombre 24'" (varios separados por `<br>`), con el nombre tal como figura en plantilla.json (campo `nombre`). Sin goles: `""`. Si el texto no da el minuto, preguntar.

### Slugs (`mapa-slugs*.json`)
- Noticias/opinión: `articulos/AAAA-MM/slug-del-titular`; crónicas: `cronicas/AAAA-MM/slug`.
- Slug = titular en minúsculas, sin tildes ni signos, palabras con guiones. EN a partir del titular inglés.
- Si se cambia el titular después, NO se cambia el slug (no romper enlaces) salvo que se pida.
- ¡Ojo! Nunca duplicar el mes en la ruta (`/2026-10/2026-10/`).

### Foto (`fotos-articulos.json`)
```json
"art85": { "foto": "fotos/publicadas/Noticia_zelu.jpg", "creditoFoto": "Foto: Diario Xerecista" }
```
- Fotos en `fotos/publicadas/`. Si piden "una foto cualquiera / de partidos anteriores", elegir una que no use ningún otro artículo y que encaje con el tema.
- Peso: antes de publicar una foto nueva, dejarla en JPEG de calidad 82, progresivo, con 1400 px de ancho como máximo (las de 1000 px pasan de ~800 KB a ~200 KB sin diferencia visible).
- Crédito siempre "Foto: Diario Xerecista" (EN: "Photo: Diario Xerecista").
- Encuadre: las tarjetas, el destacado y las miniaturas recortan la foto por arriba (`top center`). Si lo importante queda cortado (p. ej. una foto vertical), añadir `"objectPosition": "center 50%"` (u otro valor CSS) en su entrada de fotos-articulos.json.

### HTML
- Copiar la estructura del artículo publicado más reciente y cambiar: title, description, canonical, hreflang, og:*, twitter:*, JSON-LD (headline, description, image, datePublished, dateModified, inLanguage, @id), eyebrow, h1, foto + alt, lead, cuerpo, byline, enlace de compartir en X (texto: titular + salto + URL + salto + `#XerezCD`, sin `&via=`; el hashtag detrás hace que X muestre el enlace), enlaces ES↔EN.
- Rutas relativas: ES `noticias/articulos/AAAA-MM/slug/` → `../../../../`; EN `en/noticias/articulos/AAAA-MM/slug/` → `../../../../../`.
- Canonical = URL absoluta propia: `https://www.diarioxerecista.es/noticias/<slug>/` y `https://www.diarioxerecista.es/en/noticias/<slug>/`.
- hreflang: es, en y x-default (= ES) en ambas páginas.
- Byline: "Redacción — 12 de octubre de 2026" / "Newsroom — 12 October 2026"; en opinión "Opinión — …" / "Opinion — …".
- Firma externa (p. ej. "Carlos López, periodista"): ponerla en el byline del HTML y en el campo `"autor"` del JSON de cada idioma ("Carlos López, journalist" en EN); sin `autor`, la portada pone "Redacción".

### Imagen para redes (`fotos/redes/`)
- Cada artículo nuevo lleva una imagen para compartir de 1200×630 con el titular encima: `fotos/redes/artNN-es.jpg` y `fotos/redes/artNN-en.jpg`, generadas con `scripts/imagen_redes.py` a partir de la foto del artículo. Etiqueta según el tipo: "Noticia"/"News", "Crónica"/"Match report", "Opinión"/"Opinion", "Historias"/"Stories".
- En el HTML de cada idioma, `og:image` y `twitter:image` apuntan a su imagen de redes, con `og:image:width` 1200 y `og:image:height` 630. En la web (portada, tarjetas, artículo) se sigue viendo la foto normal; el JSON-LD también usa la foto normal.
- X y WhatsApp guardan la vista previa de un enlace la primera vez que lo ven: la imagen tiene que estar ANTES de que se comparta. Si se cambia después, al tuitear pegar el enlace con `?v=2` (o otro número) y avisar al usuario de que los tuits ya publicados no cambian.
- Requiere Pillow (en el Mac mini se instala en un entorno temporal: `python3 -m venv … && pip install pillow`).

### Sitemap (un bloque por idioma, al final antes de `</urlset>`)
```xml
<url>
    <loc>URL</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
    <lastmod>AAAA-MM-DD</lastmod>
    <xhtml:link rel="alternate" hreflang="es" href="URL-ES"/>
    <xhtml:link rel="alternate" hreflang="en" href="URL-EN"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="URL-ES"/>
  </url>
```

### Imagen de resultado final (redes)
- Al acabar un partido, si el usuario lo pide: `python3 scripts/resultado_final.py "<local>" "<visitante>" <gl> <gv> <foto> <salida.jpg> [--vert 0.4]` (nombres como en `ESCUDOS` de index.html; foto del partido o de archivo). Usa el modelo del usuario `scripts/plantilla-resultado/modelo.jpg` (843×1264, con logos RFEF, anunciantes Lugo y El Jardín de Papel). Se entrega al usuario; no se sube a la web. En partidos de Copa (`tipo:'copa'` en PARTIDOS) pone "COPA DEL REY" en lugar del logo de Segunda Federación.
- Publicación automática en X: DESACTIVADA desde el 30/10/2026 (X pide créditos de pago; el usuario decidió quitarla). El paso de `directo.yml` que ejecuta `scripts/publicar_x.py` tiene `if: false`; para reactivarlo, volver a `if: always()`. Sigue disponible la publicación manual con el workflow `resultado-x.yml` (Actions → Run workflow), que también necesita créditos. Cualquier publicación en X la hace el usuario.

## Clasificación (`clasificacion.json`)
- `{ actualizado, jornada, fuente, equipos: [{ nombre, escudo, pj, pts, gf, gc }] }`. 18 equipos.
- Con los resultados de una jornada: sumar pj, gf, gc y pts (3/1/0) a los 18, ordenar por pts → diferencia de goles → goles a favor, y subir `jornada` y `actualizado`. Comprobar antes que `jornada` es la anterior (no sumar dos veces).
- Jornada a medias: se pueden sumar solo los partidos ya jugados, subiendo `jornada` y añadiendo `"pendientes": ["Local - Visitante", …]` con los que faltan; la web muestra "Clasificación provisional de la jornada N (faltan X partidos)". Al completar la jornada, sumar SOLO los de `pendientes` y borrar el campo.
- Nombres exactos del JSON: Betis B, Recreativo de Huelva, Ciudad de Lucena, Badajoz, Tenerife B, Estepona, Don Benito, Linares Deportivo, Mijas Las Lagunas, Sevilla Atlético, Salerm Puente Genil, Atlético Sanluqueño, Xerez CD, Atlético Central, Marbella, Las Palmas Atlético, Tamaraceite, Antoniano. Mapear los que dé el usuario ("Betis Deportivo"→Betis B, "Recreativo"→Recreativo de Huelva, "CD Badajoz"→Badajoz, "Puente Genil"→Salerm Puente Genil, "UD Las Palmas Atlético"→Las Palmas Atlético, "Atlético Antoniano"→Antoniano, "CP Mijas Las Lagunas"→Mijas Las Lagunas, "CD Estepona"→Estepona).
- Escudos en `fotos/escudos/`. Zonas por posición (las pinta index.html): 1.º ascenso, 2.º–5.º play off, 13.º play out, 14.º–18.º descenso.
- El workflow `.github/workflows/clasificacion.yml` (GitHub Actions, activo, domingos y lunes) reescribe este JSON desde TheSportsDB, así que la edición manual puede quedar pisada; si los datos de la API son peores que los manuales, avisar al usuario.
- Tras actualizar, comprobar que las distancias que citen los artículos coinciden con la tabla y avisar si no.

## Calendario y resultados (`PARTIDOS` dentro de `index.html`)
- Array `const PARTIDOS = [...]` en el script de index.html (no es un JSON aparte). Una línea por partido:
  `{fecha:'2026-10-18',jornada:'J7', local:'Xerez CD', visitante:'Ciudad de Lucena', hora:'17:00', resultado:null}`
- Al jugarse un partido: poner `resultado:'1-1'` (siempre goles local-visitante). Al confirmarse horario: añadir/cambiar `hora`.
- Amistosos: `tipo:'amistoso'`; Copa: `tipo:'copa'`, `jornada:'Copa del Rey'`; campo neutral o distinto: `sede:'…'`.
- Los nombres de rival deben coincidir con las claves de `ESCUDOS` en index.html para que salga el escudo; si llega un rival nuevo (p. ej. Copa), añadir su escudo en `fotos/escudos/` y su entrada en `ESCUDOS`.
- El widget "Próximo partido" de portada sale de este array; no requiere más cambios.
- Si cambia una hora, actualizarla también en `.github/workflows/directo.yml` (lista PARTIDOS propia, con hora).

## Directo (`live.json`)
- Apagado: `{"activo": false}`.
- Encendido: `{"activo":true,"local":"Xerez CD","visitante":"Marbella","resultado":"1-0","minuto":65}`; opcionales `estado` ("DESCANSO", "FINAL") y `nota`. Sustituye al widget de próximo partido.
- Nombres como en `ESCUDOS`. Lo escribe el workflow `.github/workflows/directo.yml`, solo y para todos los partidos de su lista `PARTIDOS` (no hay que hacer nada en cada partido).
- Cómo funciona: GitHub lo lanza cuando puede (programado cada 5 min, pero a veces con mucho retraso). Si arranca hasta 90 min antes del saque, espera sin gastar cuota; desde 10 min antes vigila el partido entero, consulta API-Football cada 150 s (unas 50-60 consultas por partido; el plan gratuito da 100/día) y sube cada cambio (minuto, goles, "DESCANSO"). Al terminar deja `"estado": "FINAL"` y la siguiente ejecución fuera de horario lo apaga. Un solo robot a la vez (`concurrency`).
- Despertador en el Mac mini: como GitHub a veces no lanza el robot a tiempo (29/10/2026 arrancó en el descanso), `scripts/despertar_directo.py` corre cada 15 min con launchd (`~/Library/LaunchAgents/es.diarioxerecista.despertar-directo.plist`, copia en `scripts/`). Si hoy hay partido en la lista de `directo.yml`, entre 80 min antes y 100 min después del saque, y no hay robot en marcha, lo lanza con workflow_dispatch usando el token del Llavero. Registro: `~/Library/Logs/diarioxerecista-despertar-directo.log`. Prueba sin lanzar: `python3 scripts/despertar_directo.py --prueba`.

## Plantilla y cromos (`plantilla.json` + `fotos/cromos/`)
- `plantilla.json` es un array; cada jugador: nombre, apellidos, nombreCompleto, dorsal, posicion (POR/DEF/CC/DEL…), posicionDetalle, fechaNacimiento (dd/mm/aaaa), edad, lugarNacimiento, nacionalidad, altura, pie, agente, fichado, contrato, valorMercado, historial [{temporada, deClub, aClub, valor}], cromo.
- `cromo` = ruta a `fotos/cromos/CromoNN-nombre.webp` (numeración correlativa: Cromo01-ismael … Cromo18-julito; el siguiente es Cromo19-nombre.webp). La web los muestra en proporción 280×396.
- Los cromos van en WebP, calidad 85, 600 px de ancho manteniendo la proporción (como máximo 600×900; sin deformar). Si el usuario pasa un PNG, convertirlo antes de subirlo y no subir el PNG.
- La sección Plantilla pinta un cromo por jugador en el orden del array; al pulsar abre la ficha con los datos y el historial.
- Alta: añadir el objeto al array + el WebP en `fotos/cromos/` (entregar la carpeta `fotos/cromos/` entera). Baja: quitar el objeto y su WebP.
- Foto de jugador para artículos: `fotos/publicadas/` (no usar el cromo como foto de noticia).

## Fichajes (`fichajes.json`)
- `{ actualizado, jugadores: [{ nombre, posicion, dorsal?, procedencia?, estado }] }`, `estado`: "confirmado" o "rumor". Actualizar `actualizado` al tocarlo.

## Publicidad (`publicidad.json`)
- `{ colaboradores: [{ nombre, imagen, url, activo }] }`, imágenes en `fotos/publicidad/`.
- index.html tiene una lista de respaldo `COLABORADORES_RESPALDO`: si se añade o quita un colaborador, cambiarlo también ahí. Un patrocinador nunca debe desaparecer de la portada por error.

## Portada (`index.html`)
- Lee los JSON; no hace falta tocarla para publicar.
- Textos de interfaz ES/EN en el diccionario de traducciones del propio index.html: cambiar ambos idiomas.
- Secciones (`<section class="view" id="view-…">`): noticias, cronicas, calendario, clasificacion, historias, opinion, plantilla (cromos), contacto, articulo.
- Portada excluye `"historias"` y `"opinion"` puros; `["opinion","noticia"]` sí sale.
- Ya estamos en temporada: no usar la palabra "Pretemporada" en etiquetas de interfaz.
- Bloque bajo la noticia principal (columna del destacado, en este orden):
  1. Franja "Espacio publicitario · Pon tu publicidad aquí" con el botón a Contacto. Cuando haya un patrocinador para ese hueco, se sustituye por su banner.
  2. "Goleadores · Liga": todos los goleadores del Xerez CD en liga (hasta 6, en filas de 3), calculados automáticamente a partir de `goleadoresHome`/`goleadoresAway` de las crónicas con eyebrow "Jornada" (sin amistosos ni Copa). Foto = cromo de plantilla.json; sin cromo, la inicial. Empate: el que llegó antes a esa cifra y, si persiste, orden alfabético.

- Barra lateral, bajo el anuncio de Lugo: bloque "Xerez TV" con la lista de subidas del canal oficial de YouTube (@XerezCD_OFICIAL, lista `UU9VoHXdJS772qYHpRNvYGSQ`): muestra solo el último vídeo o directo, sin mantenimiento.

## Otros archivos
- `CNAME` (dominio de GitHub Pages) y `robots.txt`: no tocar.
- `noticia.css`: estilos comunes de todas las páginas de artículo.
- `.github/workflows/`: automatismos de GitHub Actions. Activos: `clasificacion.yml` y `directo.yml` (secrets THESPORTSDB_KEY y API_FOOTBALL_KEY). No existe ya la carpeta `workflows/` en la raíz.
- `publicar.yml` y `scripts/periodista_ia.py` están desactivados, usan la estructura antigua; no reactivar sin adaptarlos.
- Los cambios en `.github/workflows/` (p. ej. horas en `directo.yml`) se suben con commit + push como el resto: el token del Mac mini ("Mac mini - Diario Xerecista", en el Llavero como github.com) tiene los permisos `repo` y `workflow`. Si un push se rechaza por falta de `workflow` scope o por credenciales, el token ha caducado o perdido el permiso: crear otro en github.com/settings/tokens/new con `repo` y `workflow`, y sustituirlo en Acceso a Llaveros (entrada github.com). Nunca pegar el token en el chat.
- `directo.yml` calcula la ventana del partido con la hora de España (`ZoneInfo("Europe/Madrid")`); las horas de su lista PARTIDOS van en hora peninsular, como en index.html.

## Antes de entregar / hacer push — comprobar
- JSON válidos; cada artNN tiene ES, EN, slug ES/EN, foto existente, HTML ES/EN y entradas en el sitemap.
- No quedan slugs, fotos ni carpetas HTML huérfanas de artículos borrados.
- Recuento de noticias = 17.
- Ninguna ruta relativa rota (fotos, CSS, enlaces ES↔EN) y canonical sin mes duplicado.
- Escudo existente para cada equipo de `clasificacion.json` y cada rival de `PARTIDOS`.
- Avisar al usuario de incoherencias en el texto que envía (minutos, datos) sin corregirlas por iniciativa propia.
