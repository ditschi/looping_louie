#!/usr/bin/env python3
"""Keep-best gate for routing (docs/development.md, section "Routing: keep the best result").

Each board has a checked-in result file hardware/<board>/routing.json with the fingerprint of the design, the
metrics of the official routing and information on router and tools. A new routing run replaces the official
.kicad_pcb only if it is better for the same design (or the design has changed).

Fingerprint: SHA-256 over the normalized content of the *unrouted* board (output of `just pcb`: placement,
pre-routes, zone outlines, keepout areas, rules, nets) plus the rules from the project file
(board.design_settings, net_settings) and the .kicad_dru. Normalized means: without UUIDs (also in paths),
without generator/version tags, without plot settings, without zone fills; elements sorted (KiCad sorts by UUID
when saving, so the order is random).

Because the routers (route_fix.py, stitch.py) lock their tracks and vias just like the pre-routes, a routed
board does not tell what is a pre-route. Therefore routing.json also holds the normalized content hash of the
official routed board (board_hash). If a run starts from exactly this board (repeated `just route` without
`just pcb`), the stored fingerprint applies; otherwise the start is treated as an unrouted board and its content
hash is the fingerprint.

Decision (route_score.py, hardware/routing-score.toml, docs/routing-score.md): hard constraints (DRC errors,
unconnected items, copper in the antenna keepout, under-width current paths) → Deb's rule → weighted score S with
threshold (ΔS ≤ −min_improvement) and veto. routing.json stores metrics, score, hash of the configuration and
metrics version; if hash or version no longer match, the official board is measured again.

Usage:
  route_gate.py fingerprint <board.kicad_pcb>            print the content hash
  route_gate.py measure <board.kicad_pcb> [project.kicad_pro] [--board B]   print metrics (JSON)
  route_gate.py init <board> [--preroute FILE]           create routing.json from the official board
  route_gate.py check <board> <candidate> [--start FILE] [--force] [--apply]
                                                         send a candidate through the gate; without --apply
                                                         only a dry run (nothing is changed). Start of the
                                                         simulated run: the official board by default
  route_gate.py score [board] [candidate …]              score table of the official board and the candidates
                                                         (e.g. build/<board>/keep/*.kicad_pcb), report per
                                                         candidate, Pareto view; changes nothing
  route_gate.py explain [board] <candidate>              decision with contributions, tipping factors, robustness
For measure/init/check/score/explain it must run with the system Python that contains pcbnew.
"""
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import route_score  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
BOARDS = {"main-board": "louie-main", "charger-board": "louie-charger"}
UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
TOKEN_RE = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
# nodes that are not part of the design (generated, random or output settings)
DROP = {"uuid", "tstamp", "filled_polygon", "fill_segments", "generator", "generator_version", "version",
        "pcbplotparams"}
TRACK_KINDS = {"segment", "arc", "via"}
# lists whose children KiCad writes sorted by UUID: sort the children for the hash
SORTED = {"kicad_pcb", "footprint", "group"}


def pcb_path(board):
    return ROOT / "hardware" / board / f"{BOARDS[board]}.kicad_pcb"


def record_path(board):
    return ROOT / "hardware" / board / "routing.json"


# --- Fingerprint ----------------------------------------------------------------------------------------------------

def parse(text):
    stack, cur = [], []
    for tok in TOKEN_RE.findall(text):
        if tok == "(":
            stack.append(cur)
            cur = []
        elif tok == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(tok)
    return cur[0]


def canon(node, drop_tracks=False, top=True):
    """Normalized text form of a node (see module docstring)."""
    if not isinstance(node, list):
        return UUID_RE.sub("~", node)
    head = node[0] if node and isinstance(node[0], str) else ""
    atoms, lists = [], []
    for child in node:
        if isinstance(child, list):
            h = child[0] if child and isinstance(child[0], str) else ""
            if h in DROP or (top and drop_tracks and h in TRACK_KINDS):
                continue
            lists.append(canon(child, drop_tracks, top=False))
        else:
            atoms.append(canon(child))
    if head == "fill":  # zone: "(fill yes …)" only means "is filled"
        atoms = [a for a in atoms if a not in ("yes", "no")]
    if head in SORTED:
        lists.sort()
    return "(" + " ".join(atoms + lists) + ")"


def project_rules(pcb, project=None):
    """Rules from .kicad_pro (board.design_settings, net_settings without colors) and .kicad_dru.
    project: path of the .kicad_pro (default: next to the board, same name)."""
    pro = Path(project) if project else Path(pcb).with_suffix(".kicad_pro")
    dru = pro.with_suffix(".kicad_dru")
    out = ""
    if pro.exists():
        data = json.loads(pro.read_text())
        net = {k: v for k, v in data.get("net_settings", {}).items() if k not in ("net_colors", "meta")}
        out += json.dumps({"design_settings": data.get("board", {}).get("design_settings"), "net_settings": net},
                          sort_keys=True)
    if dru.exists():
        out += "\n" + dru.read_text()
    return out


def content_hash(pcb, project=None, drop_tracks=False):
    """Normalized content hash of a board including project rules. drop_tracks=True: without tracks and vias
    (only for comparing placement, zones and rules between unrouted and routed board)."""
    text = canon(parse(Path(pcb).read_text()), drop_tracks)
    rules = project_rules(pcb, project)
    return hashlib.sha256((text + "\n" + rules).encode()).hexdigest()


def track_items(pcb):
    """Tracks and vias as normalized texts (comparison unrouted ⊆ routed)."""
    tree = parse(Path(pcb).read_text())
    return {canon(c, top=False) for c in tree if isinstance(c, list) and c and c[0] in TRACK_KINDS}


def run_fingerprint(start, record, project):
    """Fingerprint of the design a run starts from (see module docstring)."""
    h = content_hash(start, project)
    if record and h == record.get("board_hash"):
        return record["fingerprint"], "start = official routed board, fingerprint from routing.json"
    return h, "start = unrouted board"


# --- Metrics --------------------------------------------------------------------------------------------------------

def measure(pcb, project=None, board="main-board"):
    """Metrics of a board (route_score.measure_all) → dict(metrics=…, details=…). project: .kicad_pro whose rules
    (including .kicad_dru) should apply; if the board is not next to it, it is copied into a temporary directory
    for this (otherwise the DRC checks with default rules)."""
    m, d = route_score.measure_all(pcb, route_score.load_config(board), project)
    return {"metrics": m, "details": d}


def short(m, cfg=None, details=None):
    """Short line; with cfg additionally hard violation and score S."""
    text = (f"{m['unconnected']} open, DRC {m['drc_violations']}, islands {m['gnd_islands']}, "
            f"{m['via_count']} Vias, {m['track_length_mm']:.1f} mm")
    if cfg is not None and "drc_errors" in m:
        e = route_score.evaluate(cfg, m, details)
        text += f", hard {e['hard_total']}" + (f" ({', '.join(e['hard'])})" if e["hard"] else "") + f", S {e['S']:.2f}"
    return text


def slug(m, cfg=None, details=None):
    text = (f"drc{m['drc_violations']}-open{m['unconnected']}-isl{m['gnd_islands']}-via{m['via_count']}"
            f"-len{m['track_length_mm']:.0f}")
    if cfg is not None and "drc_errors" in m:
        e = route_score.evaluate(cfg, m, details)
        text += f"-hard{e['hard_total']}-S{e['S']:.1f}"
    return text


# --- Tools, result file ---------------------------------------------------------------------------------------------

def tool_versions(router):
    out = {}
    try:
        out["kicad"] = subprocess.run(["kicad-cli", "--version"], capture_output=True, text=True).stdout.strip()
    except OSError:
        pass
    jar = Path(os.environ.get("FREEROUTING_JAR", ROOT / "tools" / "freerouting.jar"))
    if router == "freerouting" and jar.exists():
        # the version is in the log (the JAR manifest says "unspecified"), plus build date/revision of the JAR
        logs = sorted((ROOT / "build").glob("*/route/**/freerouting.log"), key=lambda f: f.stat().st_mtime)
        m = re.search(r"Freerouting v(\S+)", logs[-1].read_text(errors="replace")) if logs else None
        version = m.group(1) if m else "?"
        try:
            manifest = zipfile.ZipFile(jar).read("META-INF/MANIFEST.MF").decode(errors="replace")
            date = re.search(r"Build-Date: *(\S+)", manifest)
            rev = re.search(r"Build-Revision: *(\S+)", manifest)
            version += f" (Build {date.group(1) if date else '?'} {rev.group(1)[:8] if rev else ''})".rstrip()
        except (OSError, KeyError, zipfile.BadZipFile):
            pass
        out["freerouting"] = version
    git = subprocess.run(["git", "-C", str(ROOT), "describe", "--always", "--dirty"], capture_output=True, text=True)
    if git.returncode == 0:
        out["repo"] = git.stdout.strip()
    return out


def load_record(board):
    p = record_path(board)
    return json.loads(p.read_text()) if p.exists() else None


def write_record(board, fingerprint, board_hash, meas, info):
    cfg = route_score.load_config(board)
    m, d = meas["metrics"], meas.get("details", {})
    e = route_score.evaluate(cfg, m, d)
    record = {"board": board, "fingerprint": fingerprint, "board_hash": board_hash, "metrics": m,
              "score": {"S": e["S"], "hard": e["hard"], "hard_total": e["hard_total"], "under_mm": e["under_mm"],
                        "parts": e["parts"]},
              "decision": "hard+weighted", "score_config_sha256": route_score.config_hash(),
              "metrics_version": route_score.METRICS_VERSION, "details": d,
              "router": info.get("router"), "variant": info.get("variant"),
              "runs": info.get("runs"), "note": info.get("note"),
              "timestamp": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
              "tools": tool_versions(info.get("router"))}
    record_path(board).write_text(json.dumps({k: v for k, v in record.items() if v is not None}, indent=2,
                                             ensure_ascii=False) + "\n")


def refresh_record(board, record, meas):
    """Re-enter the score of the official board (new configuration/metrics version), change nothing else."""
    info = {k: record.get(k) for k in ("router", "variant", "runs", "note")}
    write_record(board, record["fingerprint"], record["board_hash"], meas, info)
    saved = json.loads(record_path(board).read_text())
    saved["timestamp"], saved["tools"] = record.get("timestamp"), record.get("tools")
    saved["rescored"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    record_path(board).write_text(json.dumps(saved, indent=2, ensure_ascii=False) + "\n")


def record_current(record):
    """Do the stored metrics match the configuration and metrics version?"""
    return bool(record) and record.get("score_config_sha256") == route_score.config_hash() \
        and record.get("metrics_version") == route_score.METRICS_VERSION and "drc_errors" in record.get("metrics", {})


def stamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def keep_dir(board):
    d = ROOT / "build" / board / "keep"
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_copy(board, board_hash, project):
    """File with the content hash board_hash: build/<board>/keep/*.kicad_pcb or Git (HEAD)."""
    for f in sorted(keep_dir(board).glob("*.kicad_pcb"), key=lambda f: f.stat().st_mtime, reverse=True):
        if content_hash(f, project) == board_hash:
            return f
    rel = pcb_path(board).relative_to(ROOT)
    git = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"], capture_output=True)
    if git.returncode == 0:
        f = keep_dir(board) / f"git-head-{stamp()}.kicad_pcb"
        f.write_bytes(git.stdout)
        if content_hash(f, project) == board_hash:
            return f
        f.unlink()
    return None


# --- Gate -----------------------------------------------------------------------------------------------------------

def official_measurement(board, record, project, log=print):
    """Metrics of the official board: from routing.json if configuration hash and metrics version match; otherwise
    measured again (official file if it is still the result from routing.json, otherwise the copy from
    build/<board>/keep/ or Git). → (measurement or None, measured again?)"""
    if record_current(record):
        return {"metrics": record["metrics"], "details": record.get("details", {})}, False
    official = pcb_path(board)
    source = official if content_hash(official, project) == record["board_hash"] else \
        find_copy(board, record["board_hash"], project)
    if source is None:
        return None, False
    why = "metrics version changed" if record.get("metrics_version") not in (None, route_score.METRICS_VERSION) \
        else "score configuration changed" if record.get("score_config_sha256") else "no score in routing.json yet"
    log(f"Official board measured again ({why}): {source.relative_to(ROOT)}")
    return measure(source, project, board), True


def gate(board, candidate, fingerprint, metrics=None, info=None, force=False, log=print, dry_run=False):
    """Decide whether candidate becomes the official board. Return True if accepted.
    metrics: measurement of the candidate (dict(metrics, details), otherwise it is measured).
    dry_run=True: only decide and report, change no file."""
    info = dict(info or {})
    official = pcb_path(board)
    project = official.with_suffix(".kicad_pro")
    cfg = route_score.load_config(board)
    meas = metrics or measure(candidate, project, board)
    m = meas["metrics"]
    record = load_record(board)

    def accept(reason):
        if dry_run:
            log(f"Dry run: would accept ({reason}): {short(m, cfg, meas.get('details'))}")
            return True
        shutil.copy(candidate, official)
        shutil.copy(candidate, keep_dir(board) / f"accepted-{stamp()}-{slug(m, cfg, meas.get('details'))}.kicad_pcb")
        write_record(board, fingerprint, content_hash(official, project), meas, info)
        log(f"New run: {short(m, cfg, meas.get('details'))} → accepted ({reason}); "
            f"{official.relative_to(ROOT)} and {record_path(board).relative_to(ROOT)} updated")
        return True

    if force:
        info["note"] = "accepted with --force"
        return accept("--force")
    if record is None:
        return accept("no routing.json yet")
    if record["fingerprint"] != fingerprint:
        old = record["metrics"]
        info["note"] = f"design changed, baseline reset (before: {short(old)})"
        return accept(f"design changed, fingerprint {record['fingerprint'][:10]} → {fingerprint[:10]}, "
                      f"previous state {short(old)}")
    off, refreshed = official_measurement(board, record, project, log)
    if off is None:
        info["note"] = "previous result not found, new run accepted"
        log("  previous result (board_hash from routing.json) found neither in build/<board>/keep/ nor in Git "
            "– accepting the new run")
        return accept("replacement")
    ok, why, drivers = route_score.decide(cfg, meas, off)
    report = route_score.explain(cfg, "new", meas, "official", off)
    if not dry_run:
        out = ROOT / "build" / board / "route"
        out.mkdir(parents=True, exist_ok=True)
        (out / "score-report.txt").write_text("\n".join(report) + "\n")
    for line in report:
        log(line)
    eo, ec = route_score.evaluate(cfg, off["metrics"], off.get("details")), \
        route_score.evaluate(cfg, m, meas.get("details"))
    summary = (f"S {ec['S']:.2f} ({ec['S'] - eo['S']:+.2f}), hard {ec['hard_total']} (before {eo['hard_total']})")
    if ok:
        return accept(f"{why}; {summary}; main drivers {drivers}")
    if dry_run:
        log(f"Dry run: would reject ({why}): {summary}; main drivers {drivers}")
        return False
    if refreshed:
        refresh_record(board, record, off)
        log(f"  {record_path(board).relative_to(ROOT)}: score of the official board updated")
    rejected = ROOT / "build" / board / "route" / "rejected"
    rejected.mkdir(parents=True, exist_ok=True)
    target = rejected / f"{stamp()}-{slug(m, cfg, meas.get('details'))}.kicad_pcb"
    shutil.copy(candidate, target)
    log(f"New run: {summary} → rejected ({why}; main drivers {drivers}), "
        f"stored under {target.relative_to(ROOT)}")
    log(f"  new:    {short(m, cfg, meas.get('details'))}\n  before: {short(off['metrics'], cfg, off.get('details'))}")
    # the official file must be the previous result (just pcb overwrites it with the unrouted one)
    if content_hash(official, project) != record["board_hash"]:
        source = find_copy(board, record["board_hash"], project)
        if source:
            shutil.copy(source, official)
            log(f"  previous result restored from {source.relative_to(ROOT)}")
        else:
            info["note"] = "previous result not found, worse run accepted"
            log("  previous result (board_hash from routing.json) found neither in build/<board>/keep/ nor in Git "
                "– accepting the new run so that no unrouted board is left behind")
            return accept("replacement")
    return False


def preroute_board(board, out_dir):
    """Create the unrouted board like `just pcb`, but into out_dir (official files unchanged)."""
    if board != "main-board":
        sys.exit(f"{board}: please specify the unrouted board with --preroute")
    out = Path(out_dir) / pcb_path(board).name
    out.parent.mkdir(parents=True, exist_ok=True)
    for f in pcb_path(board).parent.iterdir():  # project file, rules, library tables as in the original
        if f.suffix in (".kicad_pro", ".kicad_dru") or f.name in ("fp-lib-table", "sym-lib-table"):
            shutil.copy(f, out.parent / f.name)
    python = os.environ.get("KICAD_PYTHON", sys.executable)
    subprocess.run([python, str(Path(__file__).parent / "gen_main_pcb.py")],
                   check=True, env=dict(os.environ, PCB_OUT=str(out)), capture_output=True)
    return out


def init(board, preroute=None, accept_mismatch=False):
    official = pcb_path(board)
    with tempfile.TemporaryDirectory() as tmp:
        pre = Path(preroute) if preroute else preroute_board(board, tmp)
        # project rules: for the generated state the .kicad_pro generated with it, otherwise the official one
        project = official.with_suffix(".kicad_pro") if preroute else pre.with_suffix(".kicad_pro")
        fp = content_hash(pre, project)
        # Does the official (routed) board match this unrouted one? Placement/zones/rules equal and all
        # pre-routes contained unchanged.
        same_design = (content_hash(pre, project, drop_tracks=True)
                       == content_hash(official, drop_tracks=True))
        missing = track_items(pre) - track_items(official)
    print(f"{board}: fingerprint {fp[:16]}…, placement/zones/rules equal: {same_design}, "
          f"missing pre-routes: {len(missing)}")
    if not (same_design and not missing) and not accept_mismatch:
        sys.exit("official board does not match the unrouted one – routing.json not written "
                 "(--accept-mismatch forces it)")
    meas = measure(official, board=board)
    old = load_record(board) or {}
    write_record(board, fp, content_hash(official), meas,
                 {"router": old.get("router") or ("own" if board == "main-board" else "freerouting"),
                  "variant": old.get("variant"), "note": "created from the official board (route_gate.py init)"})
    print(f"{record_path(board).relative_to(ROOT)}: {short(meas['metrics'], route_score.load_config(board), meas['details'])}")


def split_board(args):
    """[board] [rest …] → (board, rest); without a board name main-board applies."""
    if args and args[0] in BOARDS:
        return args[0], args[1:]
    return "main-board", list(args)


def score_cmd(args, explain_only=False):
    board, files = split_board(args)
    cfg = route_score.load_config(board)
    official = pcb_path(board)
    record = load_record(board)
    project = official.with_suffix(".kicad_pro")
    if record and content_hash(official, project) != record.get("board_hash"):
        print(f"Note: {official.relative_to(ROOT)} is not the board from routing.json (e.g. after just pcb)")
    boards = [(f"official ({official.name})", measure(official, project, board))]
    for f in files:
        boards.append((Path(f).name, measure(f, project, board)))
    if not explain_only:
        for line in route_score.table(cfg, boards):
            print(line)
        print()
    for name, b in boards[1:]:
        for line in route_score.explain(cfg, name, b, boards[0][0], boards[0][1]):
            print(line)
        print()
    if not explain_only:
        for line in route_score.pareto(cfg, boards):
            print(line)
        if len(boards) == 1:
            m, e = boards[0][1]["metrics"], route_score.evaluate(cfg, boards[0][1]["metrics"], boards[0][1]["details"])
            print("\nContributions (points):")
            for k, v in sorted(e["parts"].items(), key=lambda kv: -abs(kv[1])):
                print(f"  {k:24} {route_score.fmt(m.get(k)):>10} {v:>+8.2f}")
            for p in boards[0][1]["details"].get("paths", []):
                print(f"  path {p['name']}: " + (f"{p['drop_mv']} mV, min. {p['min_width_mm']} mm, {p['vias']} vias, "
                                                 f"too narrow {p['under_width_mm']} mm" if p.get("connected")
                                                 else "not connected"))


def main(argv):
    if len(argv) < 1:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "fingerprint":
        print(content_hash(args[0], *(args[1:2])))
    elif cmd == "measure":
        board = args[args.index("--board") + 1] if "--board" in args else "main-board"
        rest = [a for i, a in enumerate(args) if a != "--board" and (i == 0 or args[i - 1] != "--board")]
        meas = measure(rest[0], *(rest[1:2]), board=board)
        meas["evaluation"] = route_score.evaluate(route_score.load_config(board), meas["metrics"], meas["details"])
        print(json.dumps(meas, indent=2, ensure_ascii=False))
    elif cmd == "init":
        pre = args[args.index("--preroute") + 1] if "--preroute" in args else None
        init(args[0], pre, "--accept-mismatch" in args)
    elif cmd == "check":
        board, cand = args[0], Path(args[1])
        record = load_record(board)
        # start of the simulated run: the official board by default (repeated just route), otherwise --start
        start = Path(args[args.index("--start") + 1]) if "--start" in args else pcb_path(board)
        fp, why = run_fingerprint(start, record, pcb_path(board).with_suffix(".kicad_pro"))
        print(f"fingerprint {fp[:16]}… ({why})")
        gate(board, cand, fp, info={"router": "manual", "variant": f"route_gate.py check {cand.name}"},
             force="--force" in args, dry_run="--apply" not in args)
    elif cmd == "score":
        score_cmd(args)
    elif cmd == "explain":
        board, files = split_board(args)
        if len(files) != 1:
            sys.exit("explain [board] <candidate>")
        score_cmd([board] + files, explain_only=True)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
