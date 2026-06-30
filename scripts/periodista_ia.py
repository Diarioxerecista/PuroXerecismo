"""
Periodista IA — Diario Xerecista (v2)
========================================

Qué hace este script:
  1. Busca archivos .yml nuevos en datos/pendientes/
  2. Redacta una noticia ORIGINAL en español con Gemini, usando un prompt
     especializado según el tipo (fichaje, resultado, declaraciones…)
  3. Traduce la noticia al inglés con buen estilo periodístico
  4. Genera el HTML de la noticia (ES + EN) con metaetiquetas SEO/OG/Twitter
  5. Actualiza noticias-es.json, noticias-en.json, mapa-slugs.json y
     fotos-articulos.json automáticamente
  6. Si hay una foto en fotos/pendientes/, la asigna a la noticia
  7. Mueve el .yml procesado a datos/publicadas/

Quién lo ejecuta: GitHub Actions, automáticamente, cada vez que subes
un archivo nuevo a datos/pendientes/ (ver .github/workflows/publicar.yml).

Requiere la variable de entorno GEMINI_API_KEY (configurada como "secret"
en GitHub, nunca escrita en el código).
"""

import os
import re
import sys
import json
import glob
import time
import shutil
import datetime
import unicodedata
import yaml
from google import genai

MODEL          = "gemini-2.5-flash"
BASE_URL       = "https://www.diarioxerecista.es"
TWITTER_HANDLE = "@Puroxerecismo"
SITE_NAME      = "Diario Xerecista"
MAX_REINTENTOS = 3
SLUG_MAX_LEN   = 75

RUTA_PENDIENTES      = "datos/pendientes"
RUTA_PUBLICADAS      = "datos/publicadas"
RUTA_NOTICIAS_ES     = "noticias-es.json"
RUTA_NOTICIAS_EN     = "noticias-en.json"
RUTA_MAPA_SLUGS      = "mapa-slugs.json"
RUTA_FOTOS_ARTICULOS = "fotos-articulos.json"
RUTA_FOTOS_PENDIENTES = "fotos/pendientes"
RUTA_FOTOS_USADAS    = "fotos/usadas"
RUTA_FOTOS_PUBLICADAS = "fotos/publicadas"
EXTENSIONES_FOTO     = (".jpg", ".jpeg", ".png", ".webp")


# ─── Utilidades ────────────────────────────────────────────────────────────────

def slugify(texto: str, max_len: int = SLUG_MAX_LEN) -> str:
    """Convierte un título en un slug URL-seguro, sin dependencias externas."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "-", texto)
    texto = texto.strip("-")
    if len(texto) > max_len:
        cortado = texto[:max_len]
        if "-" in cortado:
            texto = cortado.rsplit("-", 1)[0]
        else:
            texto = cortado
    return texto


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: no se ha encontrado GEMINI_API_KEY en el entorno.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def cargar_json(ruta: str) -> dict:
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_json(ruta: str, datos: dict):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def siguiente_id_articulo(noticias_es: dict) -> str:
    numeros = [int(k[3:]) for k in noticias_es.keys() if re.match(r"^art\d+$", k)]
    return f"art{max(numeros) + 1 if numeros else 1}"


# ─── Foto ──────────────────────────────────────────────────────────────────────

def siguiente_foto_disponible() -> str | None:
    """
    Devuelve la ruta de la siguiente foto disponible (la más antigua primero),
    la copia a fotos/publicadas/ y la mueve a fotos/usadas/.
    """
    os.makedirs(RUTA_FOTOS_PENDIENTES, exist_ok=True)
    candidatas = [
        f for f in os.listdir(RUTA_FOTOS_PENDIENTES)
        if f.lower().endswith(EXTENSIONES_FOTO)
    ]
    if not candidatas:
        return None

    candidatas.sort(key=lambda f: (f, os.path.getmtime(os.path.join(RUTA_FOTOS_PENDIENTES, f))))
    elegida = candidatas[0]

    os.makedirs(RUTA_FOTOS_PUBLICADAS, exist_ok=True)
    ruta_origen    = os.path.join(RUTA_FOTOS_PENDIENTES, elegida)
    ruta_publicada = os.path.join(RUTA_FOTOS_PUBLICADAS, elegida)
    shutil.copy2(ruta_origen, ruta_publicada)

    os.makedirs(RUTA_FOTOS_USADAS, exist_ok=True)
    shutil.move(ruta_origen, os.path.join(RUTA_FOTOS_USADAS, elegida))
    return ruta_publicada


# ─── Gemini ────────────────────────────────────────────────────────────────────

def llamar_gemini(client, prompt: str) -> dict:
    """Llama a Gemini con reintentos automáticos si falla o devuelve JSON inválido."""
    ultimo_error = None
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            resp = client.models.generate_content(model=MODEL, contents=prompt)
            raw  = resp.text.strip()
            raw  = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
            return json.loads(raw)
        except Exception as e:
            ultimo_error = e
            if intento < MAX_REINTENTOS:
                espera = 2 ** intento
                print(f"  ⚠ Intento {intento} fallido ({e}). Reintentando en {espera}s…")
                time.sleep(espera)
    print(f"ERROR: Gemini falló {MAX_REINTENTOS} veces. Último error: {ultimo_error}")
    sys.exit(1)


# ─── Prompts especializados ────────────────────────────────────────────────────

INSTRUCCIONES_POR_TIPO = {
    "fichaje": (
        "Noticia de FICHAJE. Destaca el nombre del jugador, su procedencia, posición y "
        "estadísticas si las hay. Explica qué puede aportar al equipo. "
        "El eyebrow debe ser 'Mercado de fichajes'."
    ),
    "resultado": (
        "Noticia de RESULTADO. Empieza la entradilla con el marcador final. "
        "Menciona los goleadores, los minutos clave y el impacto en la clasificación. "
        "El eyebrow debe ser 'Resultado'."
    ),
    "declaraciones": (
        "Noticia de DECLARACIONES. La cita textual es el centro de la noticia. "
        "Contextualiza quién habla, en qué momento y por qué son relevantes sus palabras. "
        "El eyebrow puede ser 'Entrevista' o 'Declaraciones'."
    ),
    "pretemporada": (
        "Noticia de PRETEMPORADA. Describe las actividades del equipo, el estado de forma "
        "y los objetivos para la temporada que viene. El eyebrow debe ser 'Pretemporada'."
    ),
    "club": (
        "Noticia institucional del CLUB. Puede ser sobre infraestructuras, directiva, "
        "eventos o comunicados oficiales. El eyebrow puede ser 'Club' o 'Institucional'."
    ),
}


def instrucciones_tipo(tipo: str) -> str:
    return INSTRUCCIONES_POR_TIPO.get(
        tipo.lower().strip(),
        "Noticia general del Xerez CD. El eyebrow debe reflejar el tema de forma breve.",
    )


def redactar_noticia_es(client, datos_brutos: dict) -> dict:
    tipo = datos_brutos.get("tipo", "club")
    cita = datos_brutos.get("cita_textual", "").strip()
    cita_block = ""
    if cita:
        cita_block = (
            f'\nCita textual disponible (cítala UNA vez, entre comillas, '
            f'atribuyendo a la fuente "{datos_brutos.get("fuente", "fuente propia")}"): '
            f'"{cita}"'
        )

    prompt = f"""Eres redactor del Diario Xerecista, un periódico digital de aficionados
del Xerez Club Deportivo (Segunda Federación, Grupo IV). Escribe una noticia ORIGINAL en
ESPAÑOL a partir únicamente de estos datos:

Tipo de noticia: {tipo}
{instrucciones_tipo(tipo)}

Datos en bruto (pueden estar mal escritos o desordenados — ignora los fallos de forma,
usa solo el contenido):
{datos_brutos['datos']}
{cita_block}

ESTILO del Diario Xerecista: cercano, de aficionado informado, con orgullo azulino pero
sin sensacionalismo. Frases claras y cortas. Un párrafo de entradilla fuerte (lead) y
2-3 párrafos de desarrollo, añadiendo contexto razonable sin inventar datos nuevos.

Si usas la cita textual, atribúyela siempre a la fuente indicada.

Responde SOLO con JSON válido, sin texto adicional, sin marcadores de código:
{{
  "eyebrow": "categoría corta, ej. Mercado de fichajes",
  "title": "titular periodístico, máximo 90 caracteres",
  "lead": "párrafo de entradilla",
  "body": ["párrafo 1", "párrafo 2", "párrafo 3 opcional"]
}}
"""
    return llamar_gemini(client, prompt)


def traducir_noticia_en(client, noticia_es: dict) -> dict:
    prompt = f"""Traduce esta noticia de fútbol al inglés con estilo periodístico
natural (como lo escribiría un periodista deportivo inglés), no como traducción
literal palabra por palabra. Mantén el mismo significado y los mismos datos exactos.

Eyebrow: {noticia_es['eyebrow']}
Title: {noticia_es['title']}
Lead: {noticia_es['lead']}
Body: {json.dumps(noticia_es['body'], ensure_ascii=False)}

Responde SOLO con JSON válido, sin texto adicional, sin marcadores de código,
con las claves "eyebrow", "title", "lead", "body" (body es una lista de strings).
"""
    return llamar_gemini(client, prompt)


# ─── Generación de HTML ────────────────────────────────────────────────────────

def _og_imagen(ruta_foto: str | None) -> str:
    if not ruta_foto:
        return ""
    url_foto = f"{BASE_URL}/{ruta_foto.replace(os.sep, '/')}"
    return (
        f'\n<meta property="og:image" content="{url_foto}">'
        f'\n<meta property="og:image:width" content="1200">'
        f'\n<meta property="og:image:height" content="630">'
        f'\n<meta name="twitter:image" content="{url_foto}">'
    )


def generar_html_es(art_id: str, slug: str, noticia: dict, ruta_foto: str | None) -> None:
    titulo       = noticia["title"]
    descripcion  = noticia["lead"][:160]
    url_canonica = f"{BASE_URL}/noticias/{slug}/"
    og_img       = _og_imagen(ruta_foto)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} — {SITE_NAME}</title>

<meta name="description" content="{descripcion}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{url_canonica}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="{url_canonica}">
<meta property="og:locale" content="es_ES">{og_img}

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titulo}">
<meta name="twitter:description" content="{descripcion}">
<meta name="twitter:site" content="{TWITTER_HANDLE}">

<!--
  A PROPÓSITO no hay <meta http-equiv="refresh"> aquí: ese sistema lo
  sigue también el robot de X, y acababa leyendo las metaetiquetas
  genéricas de portada en vez de las de esta noticia. La redirección
  de abajo es SOLO JavaScript: los robots de redes sociales no lo
  ejecutan, así que se quedan leyendo las metaetiquetas de arriba. Un
  humano real sí lo ejecuta y pasa automáticamente a la web normal.
-->
<script>window.location.replace("{BASE_URL}/?n={art_id}");</script>
</head>
<body>
  <p>Cargando «{titulo}»…</p>
</body>
</html>
"""
    directorio = os.path.join("noticias", slug)
    os.makedirs(directorio, exist_ok=True)
    with open(os.path.join(directorio, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def generar_html_en(art_id: str, slug: str, noticia: dict, ruta_foto: str | None) -> None:
    titulo       = noticia["title"]
    descripcion  = noticia["lead"][:160]
    url_canonica = f"{BASE_URL}/noticias-en/{slug}/"
    og_img       = _og_imagen(ruta_foto)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo} — {SITE_NAME}</title>

<meta name="description" content="{descripcion}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<link rel="canonical" href="{url_canonica}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{descripcion}">
<meta property="og:url" content="{url_canonica}">
<meta property="og:locale" content="en_GB">{og_img}

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{titulo}">
<meta name="twitter:description" content="{descripcion}">
<meta name="twitter:site" content="{TWITTER_HANDLE}">

<!--
  A PROPÓSITO no hay <meta http-equiv="refresh"> aquí: ese sistema lo
  sigue también el robot de X, y acababa leyendo las metaetiquetas
  genéricas de portada en vez de las de esta noticia. La redirección
  de abajo es SOLO JavaScript: los robots de redes sociales no lo
  ejecutan, así que se quedan leyendo las metaetiquetas de arriba. Un
  humano real sí lo ejecuta y pasa automáticamente a la web normal.
-->
<script>window.location.replace("{BASE_URL}/?n={art_id}&lang=en");</script>
</head>
<body>
  <p>Loading "{titulo}"…</p>
</body>
</html>
"""
    directorio = os.path.join("noticias-en", slug)
    os.makedirs(directorio, exist_ok=True)
    with open(os.path.join(directorio, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    client   = get_client()
    archivos = sorted(glob.glob(os.path.join(RUTA_PENDIENTES, "*.yml")))

    if not archivos:
        print("No hay noticias pendientes. Nada que hacer.")
        return

    noticias_es     = cargar_json(RUTA_NOTICIAS_ES)
    noticias_en     = cargar_json(RUTA_NOTICIAS_EN)
    mapa_slugs      = cargar_json(RUTA_MAPA_SLUGS)
    fotos_articulos = cargar_json(RUTA_FOTOS_ARTICULOS)

    for ruta in archivos:
        print(f"\nProcesando: {ruta}")
        with open(ruta, "r", encoding="utf-8") as f:
            datos_brutos = yaml.safe_load(f)

        # 1. Redactar y traducir
        noticia_es = redactar_noticia_es(client, datos_brutos)
        noticia_en = traducir_noticia_en(client, noticia_es)

        # 2. IDs y slugs
        art_id  = siguiente_id_articulo(noticias_es)
        slug_es = slugify(noticia_es["title"])
        slug_en = slugify(noticia_en["title"])
        hoy     = datetime.date.today().isoformat()

        # 3. Foto
        ruta_foto    = siguiente_foto_disponible()
        credito_foto = datos_brutos.get("credito_foto", "Foto: PuroXerecismo").strip()

        # 4. Entradas en los JSON de noticias
        entrada_es = {
            "fecha":     hoy,
            "categoria": "noticia",
            "eyebrow":   noticia_es["eyebrow"],
            "title":     noticia_es["title"],
            "lead":      noticia_es["lead"],
            "body":      noticia_es["body"],
        }
        entrada_en = {
            "fecha":     hoy,
            "categoria": "noticia",
            "eyebrow":   noticia_en["eyebrow"],
            "title":     noticia_en["title"],
            "lead":      noticia_en["lead"],
            "body":      noticia_en["body"],
        }
        if ruta_foto:
            entrada_es["foto"] = ruta_foto
            entrada_en["foto"] = ruta_foto

        noticias_es[art_id] = entrada_es
        noticias_en[art_id] = entrada_en

        # 5. mapa-slugs y fotos-articulos
        mapa_slugs[art_id] = slug_es
        if ruta_foto:
            fotos_articulos[art_id] = {
                "foto":        ruta_foto,
                "creditoFoto": credito_foto,
            }

        # 6. Generar HTML con metaetiquetas SEO/OG
        generar_html_es(art_id, slug_es, noticia_es, ruta_foto)
        generar_html_en(art_id, slug_en, noticia_en, ruta_foto)

        # 7. Mover el .yml a publicadas/
        nombre  = os.path.basename(ruta)
        destino = os.path.join(RUTA_PUBLICADAS, f"{hoy}-{nombre}")
        shutil.move(ruta, destino)

        print(f"  ✓ {art_id}: {noticia_es['title']}")
        print(f"    ES → /noticias/{slug_es}/")
        print(f"    EN → /noticias-en/{slug_en}/")
        if ruta_foto:
            print(f"    📷 {ruta_foto} ({credito_foto})")

    # 8. Guardar todos los JSONs
    guardar_json(RUTA_NOTICIAS_ES,     noticias_es)
    guardar_json(RUTA_NOTICIAS_EN,     noticias_en)
    guardar_json(RUTA_MAPA_SLUGS,      mapa_slugs)
    guardar_json(RUTA_FOTOS_ARTICULOS, fotos_articulos)

    print("\nListo. Todos los archivos actualizados.")


if __name__ == "__main__":
    main()
