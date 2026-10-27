"""Publica en X el resultado final de un partido del Xerez CD con la imagen de resultado_final.py.

Uso (desde la raíz del repo, con las claves en el entorno: X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET):
  python3 scripts/publicar_x.py                     # lee live.json; publica si está en "FINAL" y no se ha publicado ya
  python3 scripts/publicar_x.py "Xerez CD" "Marbella F.C." 1 0 [foto]   # publicación manual (prueba)

Lleva el registro de lo publicado en publicados-x.json para no repetir. Requiere Pillow, requests y requests-oauthlib.
"""
import json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from requests_oauthlib import OAuth1

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resultado_final

FOTO_POR_DEFECTO = 'fotos/publicadas/xerez-cd-accion-partido-2026-27.jpg'
REGISTRO = 'publicados-x.json'
IMAGEN = 'resultado-x.jpg'


def auth():
    claves = [os.environ.get(k, '').strip() for k in ('X_API_KEY', 'X_API_SECRET', 'X_ACCESS_TOKEN', 'X_ACCESS_SECRET')]
    if not all(claves):
        sys.exit('ERROR: faltan claves de X en los secrets del repositorio.')
    return OAuth1(*claves)


def subir_imagen(a, ruta):
    datos = open(ruta, 'rb').read()
    # API v2 de medios; si no está disponible para la cuenta, la v1.1 de siempre
    for url, campo in (('https://api.x.com/2/media/upload', 'media'),
                       ('https://upload.twitter.com/1.1/media/upload.json', 'media')):
        try:
            r = requests.post(url, auth=a, files={campo: ('resultado.jpg', datos, 'image/jpeg')},
                              data={'media_category': 'tweet_image'}, timeout=60)
            j = r.json() if r.content else {}
            mid = (j.get('data') or {}).get('id') or j.get('media_id_string')
            if r.ok and mid:
                return str(mid)
            print('Subida de imagen rechazada en', url, r.status_code, r.text[:300], flush=True)
        except Exception as e:
            print('Error subiendo imagen a', url, e, flush=True)
    return None


def tuitear(a, texto, media_id):
    cuerpo = {'text': texto}
    if media_id:
        cuerpo['media'] = {'media_ids': [media_id]}
    r = requests.post('https://api.x.com/2/tweets', auth=a, json=cuerpo, timeout=30)
    print('X respondió', r.status_code, r.text[:300], flush=True)
    return r.ok


def main():
    args = sys.argv[1:]
    hoy = datetime.now(ZoneInfo('Europe/Madrid')).strftime('%Y-%m-%d')
    if args:
        local, visitante, gl, gv = args[:4]
        foto = args[4] if len(args) > 4 else FOTO_POR_DEFECTO
        clave = None
    else:
        live = json.load(open('live.json', encoding='utf-8'))
        if not (live.get('activo') and live.get('estado') == 'FINAL'):
            print('No hay partido terminado en live.json.'); return
        local, visitante = live['local'], live['visitante']
        gl, gv = live['resultado'].split('-')
        foto = FOTO_POR_DEFECTO
        clave = f'{hoy} {local} - {visitante}'
        registro = json.load(open(REGISTRO, encoding='utf-8')) if os.path.exists(REGISTRO) else []
        if clave in registro or clave + ' (FALLO)' in registro:
            print('Ya publicado:', clave); return

    resultado_final.main(local, visitante, gl, gv, foto, IMAGEN)
    esc, nombres = resultado_final.escudos_y_nombres()
    nl = resultado_final.nombre_visible(local, esc, nombres).title().replace('Cd', 'CD')
    nv = resultado_final.nombre_visible(visitante, esc, nombres).title().replace('Cd', 'CD').replace('Cf', 'CF')
    texto = f'⚽ FINAL | {nl} {gl}-{gv} {nv}\n\nwww.diarioxerecista.es\n\n#XerezCD'

    a = auth()
    ok = tuitear(a, texto, subir_imagen(a, IMAGEN))
    if clave:
        # También se apunta el fallo: así no se reintenta cada 5 minutos
        registro.append(clave if ok else clave + ' (FALLO)')
        json.dump(registro, open(REGISTRO, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    if not ok:
        sys.exit('ERROR: X no aceptó la publicación.')
    print('Publicado en X:', texto.splitlines()[0])


if __name__ == '__main__':
    main()
