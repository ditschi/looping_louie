#!/usr/bin/env bash
# Richtet alle Werkzeuge für die Entwicklung ein (Ubuntu/Debian).
# Kann gefahrlos mehrfach ausgeführt werden: installiert nur, was fehlt.
set -euo pipefail
cd "$(dirname "$0")"

APT_PACKAGES=(kicad kicad-packages3d just zip python3 python3-matplotlib default-jre curl)

echo "== System-Pakete (apt)"
missing=()
for pkg in "${APT_PACKAGES[@]}"; do
    dpkg -s "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
done
if ((${#missing[@]})); then
    echo "Fehlt: ${missing[*]}"
    sudo apt update
    sudo apt install "${missing[@]}"
else
    echo "Alle vorhanden."
fi

echo "== Python-Werkzeuge (uv)"
if ! command -v uv >/dev/null; then
    echo "uv fehlt. Installation siehe https://docs.astral.sh/uv/getting-started/installation/"
    echo "Danach dieses Skript erneut starten."
    exit 1
fi
if command -v easyeda2kicad >/dev/null; then
    echo "easyeda2kicad vorhanden."
else
    uv tool install easyeda2kicad
fi

echo "== Autorouter Freerouting (tools/freerouting.jar)"
if [[ -f tools/freerouting.jar ]]; then
    echo "vorhanden."
else
    url=$(curl -fsSL https://api.github.com/repos/freerouting/freerouting/releases/latest \
        | python3 -c 'import json,sys; print(next(a["browser_download_url"] for a in json.load(sys.stdin)["assets"] if a["name"].endswith(".jar")))')
    echo "Lade $url"
    mkdir -p tools
    curl -fL -o tools/freerouting.jar "$url"
fi

if [[ ! -f "$HOME/.config/kicad/9.0/sym-lib-table" ]]; then
    echo
    echo "Hinweis: KiCad einmal starten und Schaltplan- sowie Platineneditor öffnen,"
    echo "damit die globalen Bibliothekstabellen angelegt werden."
fi

echo "== Prüfung"
just check
