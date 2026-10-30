#!/usr/bin/env python3
"""Despierta el robot del directo (directo.yml) desde el Mac mini.

GitHub no garantiza su programación cada 5 minutos (el 29/10/2026 no lanzó
el robot hasta el descanso). Este script lo ejecuta launchd cada 15 minutos:
si hoy hay partido en la lista PARTIDOS de directo.yml y estamos entre 80 min
antes del saque y 100 min después, y no hay ningún robot en marcha o en cola,
lanza directo.yml con workflow_dispatch.

El token se lee del Llavero con `git credential fill` (nunca se guarda ni se imprime).
Uso: despertar_directo.py [--prueba]   (--prueba: dice qué haría, sin lanzar nada)
"""
import json, re, subprocess, sys, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

REPO = "Diarioxerecista/PuroXerecismo"
WORKFLOW = "directo.yml"
ANTES, DESPUES = 80, 100   # ventana en minutos alrededor del saque
API = f"https://api.github.com/repos/{REPO}/actions/workflows/{WORKFLOW}"
PRUEBA = "--prueba" in sys.argv


def log(*a):
    print(datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d %H:%M"), *a, flush=True)


def token():
    r = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True, timeout=30,
                       env={"GIT_TERMINAL_PROMPT": "0", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
    for linea in r.stdout.splitlines():
        if linea.startswith("password="):
            return linea[len("password="):]
    raise SystemExit("No hay token de github.com en el Llavero")


def peticion(url, metodo="GET", datos=None, tok=None):
    req = urllib.request.Request(url, method=metodo, data=json.dumps(datos).encode() if datos else None)
    req.add_header("Accept", "application/vnd.github+json")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        cuerpo = r.read()
        return json.loads(cuerpo) if cuerpo else None


def main():
    # Lista de partidos tal como está en GitHub (no depende de la copia local)
    yml = urllib.request.urlopen(f"https://raw.githubusercontent.com/{REPO}/main/.github/workflows/{WORKFLOW}", timeout=30).read().decode()
    partidos = re.findall(r'\{"fecha":"(\d{4}-\d\d-\d\d)","hora":"(\d\d:\d\d)","local":"([^"]*)","visitante":"([^"]*)"', yml)

    ahora = datetime.now(ZoneInfo("Europe/Madrid"))
    hoy = ahora.strftime("%Y-%m-%d")
    partido = next((p for p in partidos if p[0] == hoy), None)
    if not partido:
        return
    h, m = map(int, partido[1].split(":"))
    saque = ahora.replace(hour=h, minute=m, second=0, microsecond=0)
    if not (saque - timedelta(minutes=ANTES) <= ahora <= saque + timedelta(minutes=DESPUES)):
        return

    tok = token()
    activos = [r for estado in ("in_progress", "queued")
               for r in peticion(f"{API}/runs?status={estado}&per_page=5", tok=tok)["workflow_runs"]]
    nombre = f"{partido[2]} - {partido[3]} ({partido[1]})"
    if activos:
        log(nombre, "| robot ya en marcha, nada que hacer")
        return
    if PRUEBA:
        log(nombre, "| PRUEBA: lanzaría el robot ahora")
        return
    peticion(f"{API}/dispatches", "POST", {"ref": "main"}, tok)
    log(nombre, "| robot lanzado")


if __name__ == "__main__":
    main()
