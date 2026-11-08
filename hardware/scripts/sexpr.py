"""Minimale Hilfen für KiCads S-Expression-Dateien (Symbolbibliotheken)."""
import re


def block_end(text, start):
    """Index hinter der schließenden Klammer des Blocks, der bei text[start] == '(' beginnt."""
    depth, i, in_str = 0, start, False
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("Block nicht geschlossen")


def find_symbol(lib_text, name):
    """Gibt den Text des Top-Level-Symbols `name` aus einer .kicad_sym zurück."""
    m = re.search(r'\(symbol "' + re.escape(name) + r'"', lib_text)
    if not m:
        raise KeyError(name)
    return lib_text[m.start():block_end(lib_text, m.start())]


def symbol_pins(sym_text):
    """Pins eines Symbols (Einheit 0/1, Darstellung 1): Liste von dicts."""
    pins = []
    for m in re.finditer(r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)', sym_text):
        block = sym_text[m.start():block_end(sym_text, m.start())]
        number = re.search(r'\(number "([^"]*)"', block).group(1)
        name = re.search(r'\(name "([^"]*)"', block).group(1)
        pins.append(dict(
            type=m.group(1), x=float(m.group(2)), y=float(m.group(3)), rot=float(m.group(4)),
            number=number, name=name, hidden="(hide yes)" in block,
        ))
    return pins
