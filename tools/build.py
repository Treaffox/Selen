#!/usr/bin/env python3
"""Kompletter Build von Selen.

  build.py [--skip-prepare] [--skip-static]

Ablauf: prepare (Quellen) → fontmake (variabel + statisch TTF/OTF) →
ttfautohint (statische TTF) → Nachbearbeitung (fsType, gasp) → WOFF2 →
Lizenz/Changelog nach dist/.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fontTools.ttLib import TTFont, newTable
from selen import config as C

VENV_BIN = C.ROOT / ".venv" / "bin"
DESIGNSPACES = [C.SOURCES / "Roman" / f"{C.FILE_STEM}.designspace",
                C.SOURCES / "Italic" / f"{C.FILE_STEM}-Italic.designspace"]


def run(cmd):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("\n".join((r.stdout + r.stderr).splitlines()[-30:]))
        raise SystemExit(f"fehlgeschlagen: {' '.join(map(str, cmd))}")
    print(f"  ok ({time.time() - t:.0f}s) {' '.join(str(c) for c in cmd[1:4])} …")


def fontmake(ds, fmt, out, interpolate=False):
    cmd = [str(VENV_BIN / "fontmake"), "-m", str(ds), "-o", *fmt, "--output-dir", str(out)]
    if interpolate:
        cmd += ["-i", "--overlaps-backend", "pathops"]
    run(cmd)


def family_win():
    """win-Metriken aus der Ausdehnung aller Master beider Stile (prepare-log.json)."""
    try:
        log = json.loads((C.SOURCES / "prepare-log.json").read_text())
        boxes = [v for k, v in log.items() if k.endswith(".bbox")]
        return max(b[0] for b in boxes), -min(b[1] for b in boxes)
    except (OSError, ValueError):
        return C.WIN


def static_stat(f):
    """STAT für einen statischen Schnitt: sein Gewicht und Stil als Achsenwerte."""
    from fontTools.otlLib.builder import buildStatTable
    os2 = f["OS/2"]
    w = os2.usWeightClass
    name = {u: n for u, n, _ in C.WEIGHTS}[w]
    italic = bool(os2.fsSelection & 1)
    wv = {"value": w, "name": name}
    if w == 400:
        wv.update(flags=0x2, linkedValue=700)
    iv = {"value": 1, "name": "Italic"} if italic else {"value": 0, "name": "Roman", "flags": 0x2, "linkedValue": 1}
    buildStatTable(f, [{"tag": "wght", "name": "Weight", "values": [wv]},
                       {"tag": "ital", "name": "Italic", "values": [iv]}], elidedFallbackName=2)


def smart_dropout(f):
    """Ungehintete TTF (Variable Fonts): prep mit Smart-Dropout-Control, sonst
    können dünne Striche bei kleinen Größen abreißen."""
    from fontTools.ttLib.tables import ttProgram
    prep = newTable("prep")
    prog = ttProgram.Program()
    prog.fromAssembly(["PUSHW[ ]", "511", "SCANCTRL[ ]", "PUSHB[ ]", "4", "SCANTYPE[ ]"])
    prep.program = prog
    f["prep"] = prep
    f["maxp"].maxStackElements = max(getattr(f["maxp"], "maxStackElements", 0), 2)


def postprocess(path, win):
    f = TTFont(path)
    f["OS/2"].fsType = 0  # installierbar, frei einbettbar (OFL)
    f["OS/2"].usWinAscent, f["OS/2"].usWinDescent = win
    hinted = "fpgm" in f
    if "glyf" in f and not hinted:
        smart_dropout(f)
    if "glyf" in f and "gasp" not in f:
        gasp = newTable("gasp")
        gasp.gaspRange = {0xFFFF: 0x000F}
        f["gasp"] = gasp
    if hinted:
        f["head"].flags |= 1 << 3  # ganzzahlige ppem bei Hinting
    if "fvar" not in f and "STAT" not in f:
        static_stat(f)
    f["name"].removeNames(platformID=1)  # nur Windows-Namen (Mac-Einträge sind veraltet)
    f.save(path)


def autohint(path):
    """Hintet einen statischen TTF (Windows, kleine Größen). Variable Fonts bleiben ungehintet."""
    import ttfautohint
    tmp = path.with_suffix(".hinted.ttf")
    ttfautohint.ttfautohint(in_file=str(path), out_file=str(tmp), hinting_range_min=8, hinting_range_max=48,
                            increase_x_height=14, windows_compatibility=True, hint_composites=True,
                            no_info=True, default_script="latn", fallback_script="none")
    tmp.replace(path)


# Block- und Powerline-Zeichen müssen exakt die Zelle füllen. ttfautohint
# rastet ihre Kanten an x-Höhe/Oberlänge ein und verschiebt sie; ohne Anweisungen
# werden sie als reine Umrisse gerastert und schließen lückenlos an.
UNHINTED_RANGES = ((0x2580, 0x259F), (0xE0A0, 0xE0D4))  # Blockelemente, Powerline


def unhint_blocks(path):
    from fontTools.ttLib.tables import ttProgram
    f = TTFont(path)
    glyf = f["glyf"]
    names = {n for u, n in f.getBestCmap().items() if any(a <= u <= b for a, b in UNHINTED_RANGES)}
    for n in names:
        g = glyf[n]
        if g.numberOfContours != 0 or g.isComposite():
            g.program = ttProgram.Program()
            g.program.fromBytecode(b"")
    f.save(path)


def woff2(path, out_dir):
    f = TTFont(path)
    f.flavor = "woff2"
    dst = out_dir / (path.stem + ".woff2")
    f.save(dst)
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-prepare", action="store_true")
    ap.add_argument("--skip-static", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    if not a.skip_prepare:
        print("Quellen vorbereiten …")
        run([str(VENV_BIN / "python"), str(C.ROOT / "tools" / "prepare.py")])

    var_dir, ttf_dir, otf_dir, web_dir = (C.DIST / d for d in ("variable", "ttf", "otf", "webfonts"))
    dirs = [var_dir, web_dir] + ([] if a.skip_static else [ttf_dir, otf_dir])
    for d in dirs:
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)

    print("Variable Fonts …")
    for ds in DESIGNSPACES:
        fontmake(ds, ["variable"], var_dir)
    if not a.skip_static:
        print("Statische Schnitte …")
        for ds in DESIGNSPACES:
            fontmake(ds, ["ttf"], ttf_dir, interpolate=True)
            fontmake(ds, ["otf"], otf_dir, interpolate=True)
        print("Hinting (ttfautohint) …")
        for p in sorted(ttf_dir.glob("*.ttf")):
            autohint(p)

    print("Nachbearbeitung und WOFF2 …")
    fonts = sorted(var_dir.glob("*.ttf")) + sorted(ttf_dir.glob("*.ttf")) + sorted(otf_dir.glob("*.otf"))
    win = family_win()
    print(f"  win-Metriken {win[0]}/{win[1]}")
    for p in fonts:
        postprocess(p, win)
    for p in sorted(var_dir.glob("*.ttf")) + sorted(ttf_dir.glob("*.ttf")):
        woff2(p, web_dir)

    for name in ("LICENSE", "CHANGELOG.md", "README.md", "VERSION"):
        src = C.ROOT / name
        if src.exists():
            shutil.copy(src, C.DIST / name)
    n = sum(1 for _ in C.DIST.rglob("*.*"))
    print(f"Fertig: Version {C.VERSION}, {n} Dateien in {C.DIST} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
