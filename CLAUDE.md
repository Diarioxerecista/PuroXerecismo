# Reglas del proyecto — Diario Xerecista (www.diarioxerecista.es)

Web de aficionados del Xerez CD, bilingüe ES/EN, temporada 2026/27 (Segunda RFEF, Grupo IV).

## Dónde trabajar
- **En Claude Code / GitHub:** el repositorio ES la web. Edita los archivos en la raíz y haz commit + push. No uses las carpetas espejo.
- **En el entorno de diseño (claude.ai):** hay 4 copias que deben quedar idénticas: raíz, `subir-ahora/`, `web-completa/`, `para-subir/`. Cada cambio se aplica en las cuatro.
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
- Crédito siempre "Foto: Diario Xerecista" (EN: "Photo: Diario Xerecista").

### HTML
- Copiar la estructura del artículo publicado más reciente y cambiar: title, description, canonical, hreflang, og:*, twitter:*, JSON-LD (headline, description, image, datePublished, dateModified, inLanguage, @id), eyebrow, h1, foto + alt, lead, cuerpo, byline, enlace de compartir en X (`&via=Puroxerecismo`), enlaces ES↔EN.
- Rutas relativas: ES `noticias/articulos/AAAA-MM/slug/` → `../../../../`; EN `en/noticias/articulos/AAAA-MM/slug/` → `../../../../../`.
- Canonical = URL absoluta propia: `https://www.diarioxerecista.es/noticias/<slug>/` y `https://www.diarioxerecista.es/en/noticias/<slug>/`.
- hreflang: es, en y x-default (= ES) en ambas páginas.
- Byline: "Redacción — 12 de octubre de 2026" / "Newsroom — 12 October 2026"; en opinión "Opinión — …" / "Opinion — …".

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

## Clasificación (`clasificacion.json`)
- `{ actualizado, jornada, fuente, equipos: [{ nombre, escudo, pj, pts, gf, gc }] }`. 18 equipos.
- Con los resultados de una jornada: sumar pj, gf, gc y pts (3/1/0) a los 18, ordenar por pts → diferencia de goles → goles a favor, y subir `jornada` y `actualizado`. Comprobar antes que `jornada` es la anterior (no sumar dos veces).
- Nombres exactos del JSON: Betis B, Recreativo de Huelva, Ciudad de Lucena, Badajoz, Tenerife B, Estepona, Don Benito, Linares Deportivo, Mijas Las Lagunas, Sevilla Atlético, Salerm Puente Genil, Atlético Sanluqueño, Xerez CD, Atlético Central, Marbella, Las Palmas Atlético, Tamaraceite, Antoniano. Mapear los que dé el usuario ("Betis Deportivo"→Betis B, "Recreativo"→Recreativo de Huelva, "CD Badajoz"→Badajoz, "Puente Genil"→Salerm Puente Genil, "UD Las Palmas Atlético"→Las Palmas Atlético, "Atlético Antoniano"→Antoniano, "CP Mijas Las Lagunas"→Mijas Las Lagunas, "CD Estepona"→Estepona).
- Escudos en `fotos/escudos/`. Zonas por posición (las pinta index.html): 1.º ascenso, 2.º–5.º play off, 13.º play out, 14.º–18.º descenso.
- Existe el workflow `workflows/clasificacion.yml` (GitHub Actions, domingos y lunes) que reescribe este JSON desde TheSportsDB. Si está activo en el repo, la edición manual puede quedar pisada; si los datos de la API son peores que los manuales, avisar al usuario.
- Tras actualizar, comprobar que las distancias que citen los artículos coinciden con la tabla y avisar si no.

## Calendario y resultados (`PARTIDOS` dentro de `index.html`)
- Array `const PARTIDOS = [...]` en el script de index.html (no es un JSON aparte). Una línea por partido:
  `{fecha:'2026-10-18',jornada:'J7', local:'Xerez CD', visitante:'Ciudad de Lucena', hora:'17:00', resultado:null}`
- Al jugarse un partido: poner `resultado:'1-1'` (siempre goles local-visitante). Al confirmarse horario: añadir/cambiar `hora`.
- Amistosos: `tipo:'amistoso'`; Copa: `tipo:'copa'`, `jornada:'Copa del Rey'`; campo neutral o distinto: `sede:'…'`.
- Los nombres de rival deben coincidir con las claves de `ESCUDOS` en index.html para que salga el escudo; si llega un rival nuevo (p. ej. Copa), añadir su escudo en `fotos/escudos/` y su entrada en `ESCUDOS`.
- El widget "Próximo partido" de portada sale de este array; no requiere más cambios.
- Si cambia una hora, actualizarla también en `workflows/directo.yml` (lista PARTIDOS propia, con hora).

## Directo (`live.json`)
- Apagado: `{"activo": false}`.
- Encendido: `{"activo":true,"local":"Xerez CD","visitante":"Marbella","resultado":"1-0","minuto":65}`; opcionales `estado` ("DESCANSO", "FINAL") y `nota`. Sustituye al widget de próximo partido.
- Nombres como en `ESCUDOS`. Lo puede escribir el workflow `workflows/directo.yml` (cada 5 min en día de partido). Al acabar, volver a `{"activo": false}`.

## Plantilla y cromos (`plantilla.json` + `fotos/cromos/`)
- `plantilla.json` es un array; cada jugador: nombre, apellidos, nombreCompleto, dorsal, posicion (POR/DEF/CC/DEL…), posicionDetalle, fechaNacimiento (dd/mm/aaaa), edad, lugarNacimiento, nacionalidad, altura, pie, agente, fichado, contrato, valorMercado, historial [{temporada, deClub, aClub, valor}], cromo.
- `cromo` = ruta a `fotos/cromos/CromoNN-nombre.png` (numeración correlativa: Cromo01-ismael … Cromo17-peregrina; el siguiente es Cromo18). Imagen vertical proporción 280×396.
- La sección Plantilla pinta un cromo por jugador en el orden del array; al pulsar abre la ficha con los datos y el historial.
- Alta: añadir el objeto al array + el PNG en `fotos/cromos/` (entregar la carpeta `fotos/cromos/` entera). Baja: quitar el objeto y su PNG.
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

## Otros archivos
- `CNAME` (dominio de GitHub Pages) y `robots.txt`: no tocar.
- `noticia.css`: estilos comunes de todas las páginas de artículo.
- `workflows/`: automatismos de GitHub Actions (clasificación y directo). En el repo deben estar en `.github/workflows/` para ejecutarse; necesitan los secrets THESPORTSDB_KEY y API_FOOTBALL_KEY.

## Antes de entregar / hacer push — comprobar
- JSON válidos; cada artNN tiene ES, EN, slug ES/EN, foto existente, HTML ES/EN y entradas en el sitemap.
- No quedan slugs, fotos ni carpetas HTML huérfanas de artículos borrados.
- Recuento de noticias = 17.
- Ninguna ruta relativa rota (fotos, CSS, enlaces ES↔EN) y canonical sin mes duplicado.
- Escudo existente para cada equipo de `clasificacion.json` y cada rival de `PARTIDOS`.
- Avisar al usuario de incoherencias en el texto que envía (minutos, datos) sin corregirlas por iniciativa propia.
