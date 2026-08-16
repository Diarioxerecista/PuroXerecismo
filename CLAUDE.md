# Reglas del proyecto

## Rotación de noticias (categoría "noticia" únicamente)
Mantener siempre un máximo de 17 artículos con `categoria: "noticia"` (o array que incluya "noticia" pero no "cronica") en noticias-es.json. Al publicar uno nuevo que supere ese total, borrar el más antiguo de esa categoría en:
- noticias-es.json y noticias-en.json
- mapa-slugs.json y mapa-slugs-en.json
- fotos-articulos.json
- sitemap.xml (bloque `<url>` es y en)
- su carpeta HTML en noticias/articulos/... y en/noticias/articulos/... (si existe)

Las Crónicas (categoria incluye "cronica") y las Historias Xerecistas (categoria "historias") NO cuentan para este límite y no se borran por esta regla — se conservan siempre.

La portada necesita al menos 17 artículos no-"historias" (1 destacado + 4 en barra lateral + 12 en "Lo último") para no quedar en blanco; con 17 noticias + crónicas aparte, siempre hay margen de sobra.
