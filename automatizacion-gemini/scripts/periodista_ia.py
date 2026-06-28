"""
Periodista IA — Diario Xerecista (versión Gemini, arquitectura JSON)
=======================================================================

Qué hace este script:
  1. Busca archivos .yml nuevos en datos/pendientes/
  2. Para cada uno, le pide a Gemini que redacte una noticia ORIGINAL en
     español a partir de los hechos que tú escribiste (no copia ningún
     artículo ajeno, porque solo recibe los datos sueltos que tú le diste).
  3. Le pide a Gemini que traduzca esa misma noticia al inglés, con buen
     estilo periodístico (no traducción literal palabra por palabra).
  4. Añade la noticia nueva a noticias-es.json y noticias-en.json.
  5. Si hay una foto disponible en fotos/pendientes/, la asigna a la
     noticia (la copia a fotos/publicadas/ y la marca como usada).
  6. Mueve el archivo .yml procesado a datos/publicadas/ para no repetir
     la noticia en la siguiente ejecución.

Quién lo ejecuta: GitHub Actions, automáticamente, cada vez que subes
un archivo nuevo a datos/pendientes/ (ver .github/workflows/publicar.yml).

Requiere la variable de entorno GEMINI_API_KEY (se configura como
"secret" en GitHub, nunca se escribe en el código — ver README.md).
"""

import os
import re
import sys
import json
import glob
import shutil
import datetime
import yaml
from google import genai

MODEL = "gemini-2.5-flash"
RUTA_PENDIENTES = "datos/pendientes"
RUTA_PUBLICADAS = "datos/publicadas"
RUTA_NOTICIAS_ES = "noticias-es.json"
RUTA_NOTICIAS_EN = "noticias-en.json"
RUTA_FOTOS_PENDIENTES = "fotos/pendientes"
RUTA_FOTOS_USADAS = "fotos/usadas"
RUTA_FOTOS_PUBLICADAS = "fotos/publicadas"
EXTENSIONES_FOTO = (".jpg", ".jpeg", ".png", ".webp")


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: no se ha encontrado GEMINI_API_KEY en el entorno.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def siguiente_foto_disponible() -> str | None:
    """
    Devuelve la ruta (para usar en el JSON/HTML) de la siguiente foto
    disponible, EN ORDEN (la más antigua subida primero), o None si no
    hay ninguna foto pendiente. Nombra tus fotos como 01-foto.jpg,
    02-foto.jpg... para controlar el orden de uso.
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
    ruta_origen = os.path.join(RUTA_FOTOS_PENDIENTES, elegida)
    ruta_publicada = os.path.join(RUTA_FOTOS_PUBLICADAS, elegida)
    shutil.copy2(ruta_origen, ruta_publicada)

    os.makedirs(RUTA_FOTOS_USADAS, exist_ok=True)
    shutil.move(ruta_origen, os.path.join(RUTA_FOTOS_USADAS, elegida))

    return ruta_publicada


def llamar_gemini(client, prompt: str) -> dict:
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    raw = resp.text.strip()
    raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
    return json.loads(raw)


def redactar_noticia_es(client, datos_brutos: dict) -> dict:
    """
    El modelo solo ve los hechos sueltos que escribiste a mano en el .yml,
    nunca un artículo ajeno completo. Esto evita el problema de copyright:
    no hay nada que parafrasear porque no se le da ningún artículo de origen.
    """
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

Tipo de noticia: {datos_brutos['tipo']}

Datos en bruto (pueden estar mal escritos o desordenados, ignora los fallos de forma,
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
    """
    Traduce la noticia ya redactada al inglés, con buen estilo periodístico
    (reescritura natural, no traducción literal palabra por palabra).
    """
    prompt = f"""Traduce esta noticia de fútbol al inglés, con estilo periodístico
natural (como lo escribiría un periodista deportivo inglés), no como una traducción
literal palabra por palabra. Mantén el mismo significado y los mismos datos exactos.

Eyebrow: {noticia_es['eyebrow']}
Title: {noticia_es['title']}
Lead: {noticia_es['lead']}
Body: {json.dumps(noticia_es['body'], ensure_ascii=False)}

Responde SOLO con JSON válido, sin texto adicional, sin marcadores de código,
con las claves "eyebrow", "title", "lead", "body" (body es una lista de strings).
"""
    return llamar_gemini(client, prompt)


def siguiente_id_articulo(noticias_es: dict) -> str:
    numeros = [int(k[3:]) for k in noticias_es.keys() if k.startswith("art")]
    siguiente = max(numeros) + 1 if numeros else 1
    return f"art{siguiente}"


def cargar_json(ruta: str) -> dict:
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_json(ruta: str, datos: dict):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    client = get_client()
    archivos = sorted(glob.glob(os.path.join(RUTA_PENDIENTES, "*.yml")))

    if not archivos:
        print("No hay noticias pendientes. Nada que hacer.")
        return

    noticias_es = cargar_json(RUTA_NOTICIAS_ES)
    noticias_en = cargar_json(RUTA_NOTICIAS_EN)

    for ruta in archivos:
        print(f"Procesando: {ruta}")
        with open(ruta, "r", encoding="utf-8") as f:
            datos_brutos = yaml.safe_load(f)

        noticia_es = redactar_noticia_es(client, datos_brutos)
        noticia_en = traducir_noticia_en(client, noticia_es)

        art_id = siguiente_id_articulo(noticias_es)
        ruta_foto = siguiente_foto_disponible()
        hoy = datetime.date.today().isoformat()

        entrada_es = {
            "fecha": hoy,
            "categoria": "noticia",
            "eyebrow": noticia_es["eyebrow"],
            "title": noticia_es["title"],
            "lead": noticia_es["lead"],
            "body": noticia_es["body"],
        }
        entrada_en = {
            "fecha": hoy,
            "categoria": "noticia",
            "eyebrow": noticia_en["eyebrow"],
            "title": noticia_en["title"],
            "lead": noticia_en["lead"],
            "body": noticia_en["body"],
        }
        if ruta_foto:
            entrada_es["foto"] = ruta_foto
            entrada_en["foto"] = ruta_foto

        noticias_es[art_id] = entrada_es
        noticias_en[art_id] = entrada_en

        # Mover el .yml procesado a publicadas/ con fecha, para no repetirlo
        nombre = os.path.basename(ruta)
        destino = os.path.join(RUTA_PUBLICADAS, f"{hoy}-{nombre}")
        shutil.move(ruta, destino)

        if ruta_foto:
            print(f"  -> Publicado como {art_id}: {noticia_es['title']} (foto: {ruta_foto})")
        else:
            print(f"  -> Publicado como {art_id}: {noticia_es['title']} (sin foto disponible)")

    guardar_json(RUTA_NOTICIAS_ES, noticias_es)
    guardar_json(RUTA_NOTICIAS_EN, noticias_en)
    print("Listo. Cambios aplicados a noticias-es.json y noticias-en.json")


if __name__ == "__main__":
    main()
