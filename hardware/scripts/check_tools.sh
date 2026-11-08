#!/usr/bin/env bash
# Checks whether all tools for hardware development are installed.
set -u
KICAD_PYTHON="${KICAD_PYTHON:-/usr/bin/python3}"
fail=0

ok()   { printf '  \e[32m✔\e[0m %s\n' "$*"; }
bad()  { printf '  \e[31m✘\e[0m %s\n' "$*"; fail=1; }
warn() { printf '  \e[33m•\e[0m %s\n' "$*"; }

echo "Required:"
if command -v kicad-cli >/dev/null; then
    ver=$(kicad-cli version)
    if [[ ${ver%%.*} -ge 9 ]]; then ok "kicad-cli $ver"; else bad "kicad-cli $ver (at least 9 required)"; fi
else
    bad "kicad-cli missing  → sudo apt install kicad"
fi

if "$KICAD_PYTHON" -c "import pcbnew" 2>/dev/null; then
    ok "pcbnew $("$KICAD_PYTHON" -c 'import pcbnew; print(pcbnew.Version())') ($KICAD_PYTHON)"
else
    bad "Python module pcbnew missing in $KICAD_PYTHON  → comes with the KiCad package; set KICAD_PYTHON if needed"
fi

if command -v easyeda2kicad >/dev/null; then
    ok "easyeda2kicad"
else
    bad "easyeda2kicad missing  → uv tool install easyeda2kicad"
fi

echo "Optional:"
if [[ -d /usr/share/kicad/3dmodels ]]; then
    ok "KiCad 3D models"
else
    warn "KiCad 3D models missing (renders without component bodies)  → sudo apt install kicad-packages3d"
fi
if [[ -f "$HOME/.config/kicad/9.0/sym-lib-table" ]]; then
    ok "global symbol library table"
else
    warn "sym-lib-table missing  → open the KiCad schematic editor once"
fi
if command -v java >/dev/null; then ok "java (for Freerouting)"; else warn "java missing (only needed for Freerouting)"; fi
if [[ -f "$(dirname "$0")/../../tools/freerouting.jar" || -n "${FREEROUTING_JAR:-}" ]]; then ok "Freerouting"; else warn "Freerouting missing (for just route)  → ./setup.sh"; fi

exit $fail
