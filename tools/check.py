#!/usr/bin/env python3
"""Prüft die gebauten Fonts in dist/ und gibt eine kompakte Übersicht aus."""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

DIST = Path(__file__).resolve().parents[1] / "dist"
problems = []


def name(f, i):
    r = f["name"].getName(i, 3, 1, 0x409)
    return r.toUnicode() if r else None


def check(p):
    f = TTFont(p)
    os2, head = f["OS/2"], f["head"]
    italic = "Italic" in p.name
    row = {
        "file": p.name, "fam": name(f, 1), "sub": name(f, 2), "typo": f"{name(f, 16) or ''}/{name(f, 17) or ''}",
        "ps": name(f, 6), "ver": name(f, 5), "wght": os2.usWeightClass, "rev": round(head.fontRevision, 3),
        "glyphs": len(f.getGlyphOrder()), "cps": len(f.getBestCmap()),
    }
    if os2.achVendID != "TRFX":
        problems.append(f"{p.name}: VendorID {os2.achVendID}")
    if os2.fsType != 0:
        problems.append(f"{p.name}: fsType {os2.fsType}")
    if bool(os2.fsSelection & 1) != italic or bool(head.macStyle & 2) != italic:
        problems.append(f"{p.name}: Italic-Bits falsch")
    if italic and f["post"].italicAngle == 0:
        problems.append(f"{p.name}: italicAngle 0")
    if f["post"].isFixedPitch or os2.panose.bProportion == 9:
        problems.append(f"{p.name}: als Monospace markiert")
    cm = f.getBestCmap()
    dw = {f["hmtx"][cm[ord(c)]][0] for c in "0123456789"}
    if len(dw) != 1:
        problems.append(f"{p.name}: Ziffern nicht tabellarisch: {sorted(dw)}")
    if not 8 <= os2.xAvgCharWidth / 1000 * 10 <= 8 * 1000 and os2.xAvgCharWidth <= 0:
        problems.append(f"{p.name}: xAvgCharWidth")
    fam = name(f, 16) or name(f, 1)
    if not (fam or "").startswith("Selen"):
        problems.append(f"{p.name}: Familienname {fam!r}")
    for i in (1, 3, 4, 5, 6, 16):
        v = name(f, i) or ""
        for bad in ("Noto", "Google", "Droid", "Brom", "Krypton", "DejaVu", "Bitstream"):
            if bad in v:
                problems.append(f"{p.name}: name {i} enthält {bad!r}: {v[:60]}")
    if f["hhea"].ascent != 1000 or f["hhea"].descent != -250 or f["hhea"].lineGap != 0:
        problems.append(f"{p.name}: hhea {f['hhea'].ascent}/{f['hhea'].descent}")
    if (os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap) != (f["hhea"].ascent, f["hhea"].descent, 0):
        problems.append(f"{p.name}: typo ≠ hhea")
    if not os2.fsSelection & (1 << 7):
        problems.append(f"{p.name}: USE_TYPO_METRICS fehlt")
    if os2.usWinAscent < head.yMax or os2.usWinDescent < -head.yMin:
        problems.append(f"{p.name}: win {os2.usWinAscent}/{os2.usWinDescent} < bbox {head.yMax}/{head.yMin}")
    if "STAT" not in f:
        problems.append(f"{p.name}: keine STAT-Tabelle")
    gdef_marks = {g for g, c in f["GDEF"].table.GlyphClassDef.classDefs.items() if c == 3}
    cmap = f.getBestCmap()
    import unicodedata
    for u, g in cmap.items():
        if unicodedata.category(chr(u)) == "Mn":
            if g not in gdef_marks:
                problems.append(f"{p.name}: {g} (U+{u:04X}) nicht als Akzent klassifiziert")
            if f["hmtx"][g][0] != 0:
                problems.append(f"{p.name}: Akzent {g} hat Breite {f['hmtx'][g][0]}")
    if "fvar" in f:
        row["axes"] = [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in f["fvar"].axes]
        row["inst"] = len(f["fvar"].instances)
        row["stat"] = [a.AxisTag for a in f["STAT"].table.DesignAxisRecord.Axis]
    feats = sorted({r.FeatureTag for r in f["GSUB"].table.FeatureList.FeatureRecord}) if "GSUB" in f else []
    row["gsub"] = " ".join(feats)
    gpos = sorted({r.FeatureTag for r in f["GPOS"].table.FeatureList.FeatureRecord}) if "GPOS" in f else []
    if "kern" not in gpos:
        problems.append(f"{p.name}: keine kern-Positionierung")
    if "mark" not in gpos:
        problems.append(f"{p.name}: keine mark-Positionierung")
    return row


def main():
    files = sorted(DIST.rglob("*.ttf")) + sorted(DIST.rglob("*.otf"))
    rows = [check(p) for p in files]
    for r in rows:
        if r["file"].endswith("].ttf") or r["file"] in ("Selen-Regular.otf", "Selen-BoldItalic.ttf", "Selen-Regular.ttf"):
            print(r)
    print(f"\n{len(files)} Dateien geprüft.")
    print("Probleme:" if problems else "Keine Probleme gefunden.")
    for p in problems:
        print(" -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
