#!/usr/bin/env bash
# Sets up all development tools (Ubuntu/Debian).
# Safe to run repeatedly: only installs what is missing.
set -euo pipefail
cd "$(dirname "$0")"

APT_PACKAGES=(kicad kicad-packages3d just zip python3 python3-matplotlib python3-numpy default-jre curl openscad inkscape)

echo "== System packages (apt)"
missing=()
for pkg in "${APT_PACKAGES[@]}"; do
    dpkg -s "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
done
if ((${#missing[@]})); then
    echo "Missing: ${missing[*]}"
    sudo apt update
    sudo apt install "${missing[@]}"
else
    echo "All present."
fi

echo "== Python tools (uv)"
if ! command -v uv >/dev/null; then
    echo "uv missing. Installation: https://docs.astral.sh/uv/getting-started/installation/"
    echo "Then run this script again."
    exit 1
fi
if command -v easyeda2kicad >/dev/null; then
    echo "easyeda2kicad present."
else
    uv tool install easyeda2kicad
fi

echo "== Autorouter Freerouting (tools/freerouting.jar)"
if [[ -f tools/freerouting.jar ]]; then
    echo "present."
else
    url=$(curl -fsSL https://api.github.com/repos/freerouting/freerouting/releases/latest \
        | python3 -c 'import json,sys; print(next(a["browser_download_url"] for a in json.load(sys.stdin)["assets"] if a["name"].endswith(".jar")))')
    echo "Downloading $url"
    mkdir -p tools
    curl -fL -o tools/freerouting.jar "$url"
fi

# Pre-router for route.py pre=krt (MIT license). Pinned version as tested in the spike on 2026-11-07; the Rust module
# grid_router comes precompiled from the release, shapely goes into its own venv (numpy/scipy from the system).
KRT_VERSION=v0.23.8
echo "== Pre-router KiCadRoutingTools $KRT_VERSION (tools/krt)"
if [[ -f tools/krt/rust_router/grid_router.so && "$(git -C tools/krt describe --tags 2>/dev/null)" == "$KRT_VERSION" ]]; then
    echo "present."
else
    rm -rf tools/krt
    git clone --depth 1 --branch "$KRT_VERSION" https://github.com/drandyhaas/KiCadRoutingTools tools/krt
    curl -fL -o tools/krt/rust_router/grid_router.so \
        "https://github.com/drandyhaas/KiCadRoutingTools/releases/download/$KRT_VERSION/grid_router-linux-x86_64.so"
fi
if [[ ! -x tools/krt-venv/bin/python ]]; then
    /usr/bin/python3 -m venv --system-site-packages tools/krt-venv
fi
tools/krt-venv/bin/python -c 'import shapely' 2>/dev/null || tools/krt-venv/bin/pip install "shapely>=2.0"

# Firmware (firmware/louie-fw): Rust nightly from rust-toolchain.toml, ldproxy, espflash. ESP-IDF itself is
# downloaded by esp-idf-sys on the first build into ~/.espressif (firmware/louie-fw/README.md).
echo "== Firmware toolchain (Rust, ldproxy, espflash)"
if ! command -v rustup >/dev/null && [[ -x "$HOME/.cargo/bin/rustup" ]]; then
    export PATH="$HOME/.cargo/bin:$PATH"
fi
if ! command -v rustup >/dev/null; then
    echo "rustup missing. Installation: https://rustup.rs – then run this script again."
else
    (cd firmware/louie-fw && rustup toolchain install)  # pinned nightly + rust-src from rust-toolchain.toml
    command -v ldproxy >/dev/null || cargo install --locked ldproxy
    if ! command -v espflash >/dev/null; then
        dpkg -s libudev-dev >/dev/null 2>&1 || sudo apt install libudev-dev
        cargo install --locked espflash
    fi
    dpkg -s python3-venv >/dev/null 2>&1 || echo "Missing for the ESP-IDF build: sudo apt install python3-venv"
    id -nG | grep -qw dialout || echo "Serial ports: sudo usermod -aG dialout $USER (then log in again)"
fi

if [[ ! -f "$HOME/.config/kicad/9.0/sym-lib-table" ]]; then
    echo
    echo "Note: start KiCad once and open the schematic and PCB editors"
    echo "so that the global library tables are created."
fi

echo "== Check"
just check
