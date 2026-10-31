#!/usr/bin/env bash
# Prüft, ob alle Werkzeuge für die Hardware-Entwicklung installiert sind.
set -u
KICAD_PYTHON="${KICAD_PYTHON:-/usr/bin/python3}"
fail=0

ok()   { printf '  \e[32m✔\e[0m %s\n' "$*"; }
bad()  { printf '  \e[31m✘\e[0m %s\n' "$*"; fail=1; }
warn() { printf '  \e[33m•\e[0m %s\n' "$*"; }

echo "Pflicht:"
if command -v kicad-cli >/dev/null; then
    ver=$(kicad-cli version)
    if [[ ${ver%%.*} -ge 9 ]]; then ok "kicad-cli $ver"; else bad "kicad-cli $ver (mindestens 9 nötig)"; fi
else
    bad "kicad-cli fehlt  → sudo apt install kicad"
fi

if "$KICAD_PYTHON" -c "import pcbnew" 2>/dev/null; then
    ok "pcbnew $("$KICAD_PYTHON" -c 'import pcbnew; print(pcbnew.Version())') ($KICAD_PYTHON)"
else
    bad "Python-Modul pcbnew fehlt in $KICAD_PYTHON  → kommt mit dem KiCad-Paket; ggf. KICAD_PYTHON setzen"
fi

if command -v easyeda2kicad >/dev/null; then
    ok "easyeda2kicad"
else
    bad "easyeda2kicad fehlt  → uv tool install easyeda2kicad"
fi

echo "Optional:"
if [[ -d /usr/share/kicad/3dmodels ]]; then
    ok "KiCad-3D-Modelle"
else
    warn "KiCad-3D-Modelle fehlen (Renders ohne Bauteilkörper)  → sudo apt install kicad-packages3d"
fi
if [[ -f "$HOME/.config/kicad/9.0/sym-lib-table" ]]; then
    ok "globale Symbol-Bibliothekstabelle"
else
    warn "sym-lib-table fehlt  → KiCad-Schaltplaneditor einmal öffnen"
fi
if command -v java >/dev/null; then ok "java (für Freerouting)"; else warn "java fehlt (nur für Freerouting nötig)"; fi

exit $fail
