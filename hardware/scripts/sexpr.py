"""Minimal helpers for KiCad S-expression files (symbol libraries)."""
import re


def block_end(text, start):
    """Index just past the closing parenthesis of the block that starts at text[start] == '('."""
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
    raise ValueError("block not closed")


def find_symbol(lib_text, name):
    """Return the text of the top-level symbol `name` from a .kicad_sym."""
    m = re.search(r'\(symbol "' + re.escape(name) + r'"', lib_text)
    if not m:
        raise KeyError(name)
    return lib_text[m.start():block_end(lib_text, m.start())]


def symbol_pins(sym_text):
    """Pins of a symbol (unit 0/1, body style 1): list of dicts."""
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
