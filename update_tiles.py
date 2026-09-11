#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rafraîchit les briques de hauteur de mer de la page "Créneaux Mer Plate"
à partir de l'API gratuite Open-Meteo Marine Weather (aucune clé requise) —
plus besoin de Claude ni de navigateur pour scraper Météo Consult.

Usage : python3 update_tiles.py
(normalement lancé automatiquement par .github/workflows/refresh.yml)

Limite connue : l'API Marine d'Open-Meteo plafonne les prévisions à 8 jours
(aujourd'hui + 7), contre 13 jours obtenus manuellement via Météo Consult.
C'est le compromis nécessaire pour un rafraîchissement 100% automatique et
gratuit, sans dépendre d'un navigateur piloté par une IA.

Le tableau BROADCASTS (MXGP / F1 / MotoGP / VTT) n'est PAS mis à jour par ce
script : il nécessite un jugement humain (vérifier le bon week-end de course,
la bonne chaîne...). Modifiez-le à la main dans index.html si besoin.
"""
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Port de Palavas-les-Flots, zone côtière (mêmes coordonnées que la source
# Météo Consult marina-281 utilisée jusqu'ici).
LATITUDE = 43.5239
LONGITUDE = 3.9360
TZ_NAME = "Europe/Paris"
FORECAST_DAYS = 8  # maximum autorisé par l'API Marine d'Open-Meteo

HTML_FILE = "index.html"
TZ = ZoneInfo(TZ_NAME)

API_URL = (
    "https://marine-api.open-meteo.com/v1/marine"
    "?latitude={lat}&longitude={lon}&hourly=wave_height"
    "&timezone={tz}&forecast_days={days}"
).format(lat=LATITUDE, lon=LONGITUDE, tz=TZ_NAME.replace("/", "%2F"), days=FORECAST_DAYS)


def fetch_wave_heights():
    req = urllib.request.Request(API_URL, headers={"User-Agent": "creneaux-mer-plate/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.URLError as exc:
        raise RuntimeError("Impossible de contacter Open-Meteo : %s" % exc) from exc

    hourly = data.get("hourly")
    if not hourly or "time" not in hourly or "wave_height" not in hourly:
        raise RuntimeError("Réponse Open-Meteo inattendue (pas de champ hourly.wave_height) : %r" % (data,))

    times = hourly["time"]
    heights = hourly["wave_height"]
    if len(times) != len(heights):
        raise RuntimeError("Tableaux time/wave_height de longueurs différentes dans la réponse Open-Meteo")

    pairs = [(t, h) for t, h in zip(times, heights) if h is not None]
    if not pairs:
        raise RuntimeError("Aucune donnée de hauteur de mer exploitable reçue d'Open-Meteo")
    return pairs


def build_tiles_js(pairs):
    lines = []
    for t_str, h in pairs:
        start = datetime.fromisoformat(t_str).replace(tzinfo=TZ)
        end = start + timedelta(hours=1)
        lines.append(
            '    {{ s: "{s}", e: "{e}", h: {h} }},'.format(
                s=start.isoformat(timespec="seconds"),
                e=end.isoformat(timespec="seconds"),
                h=round(float(h), 1),
            )
        )
    if lines:
        lines[-1] = lines[-1].rstrip(",")
    return "\n".join(lines)


def update_html(tiles_body):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    now = datetime.now(TZ)
    next_check = now + timedelta(hours=2)

    html, n = re.subn(
        r"var TILES = \[.*?\];",
        "var TILES = [\n" + tiles_body.replace("\\", "\\\\") + "\n  ];",
        html, count=1, flags=re.S,
    )
    if n != 1:
        raise RuntimeError("Tableau `var TILES = [...]` introuvable dans %s" % HTML_FILE)

    html, n = re.subn(
        r'var LAST_UPDATE\s*= "[^"]*";',
        'var LAST_UPDATE = "%s";' % now.isoformat(timespec="seconds"),
        html, count=1,
    )
    if n != 1:
        raise RuntimeError("`var LAST_UPDATE = ...` introuvable dans %s" % HTML_FILE)

    html, n = re.subn(
        r'var NEXT_CHECK\s*= "[^"]*";',
        'var NEXT_CHECK  = "%s";' % next_check.isoformat(timespec="seconds"),
        html, count=1,
    )
    if n != 1:
        raise RuntimeError("`var NEXT_CHECK = ...` introuvable dans %s" % HTML_FILE)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    pairs = fetch_wave_heights()
    tiles_body = build_tiles_js(pairs)
    update_html(tiles_body)
    print("OK - %d briques écrites dans %s" % (len(pairs), HTML_FILE))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - on veut un message clair dans les logs GitHub Actions
        print("ERREUR : %s" % exc, file=sys.stderr)
        sys.exit(1)
