"""Drift check: the generators still reproduce the committed symbol library and schematics.

Runs each generator, compares its output with the file as it was before (UUIDs ignored: the charger schematic
was committed with random ones) and always restores the original file. Exit code 1 on drift, i.e. a hand
edit that the next `just schematic` would lose, or a generator change that was not regenerated.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "hardware" / "scripts"
GENERATED = {
    "gen_symbols.py": "hardware/lib/louie.kicad_sym",
    "gen_main_schematic.py": "hardware/main-board/louie-main.kicad_sch",
    "gen_charger_schematic.py": "hardware/charger-board/louie-charger.kicad_sch",
}
UUID = re.compile(r'(\(uuid "|\(path "/)[0-9a-f-]{36}')


def normalized(text: str) -> str:
    return UUID.sub(r"\1-", text)


def drifted(generator: str, output: str) -> bool:
    target = ROOT / output
    before = target.read_bytes()
    try:
        subprocess.run([sys.executable, str(SCRIPTS / generator)], cwd=ROOT, check=True, capture_output=True)
        return normalized(target.read_text()) != normalized(before.decode())
    finally:
        target.write_bytes(before)


def main() -> int:
    failed = [f"{output} (from {gen})" for gen, output in GENERATED.items() if drifted(gen, output)]
    for item in failed:
        print(f"drift: {item} differs from the generator output", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
