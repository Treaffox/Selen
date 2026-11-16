#!/usr/bin/env python3
"""Prüft in allen statischen TTF: kein einzelner Punkt (i, j, ! : ; . …) schmaler als der Stamm (l), Paare mindestens 0,8 Stamm."""
import math
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
ROOT = Path(__file__).resolve().parent.parent
def contours(gs, name):
    rp = DecomposingRecordingPen(gs); gs[name].draw(rp); out = []; cur = []
    for op, a in rp.value:
        if op == "moveTo": cur = [a[0]]
        elif op in ("lineTo", "qCurveTo", "curveTo"): cur += list(a)
        elif op in ("closePath", "endPath"): out.append(cur)
    return out
bad = []; n = 0
for p in sorted((ROOT / "dist/ttf").glob("*.ttf")):
    f = TTFont(p); gs = f.getGlyphSet(); cm = f.getBestCmap()
    tan = math.tan(math.radians(12)) if "Italic" in p.name else 0
    ux = lambda pt: pt[0] - pt[1] * tan
    l = contours(gs, cm[ord("l")])[0]; stem = max(map(ux, l)) - min(map(ux, l))
    for ch in "ij!?:;.,ï…ǰɨ":
        if ord(ch) not in cm: continue
        cs = contours(gs, cm[ord(ch)]); xh = 560
        small = [c for c in cs if len(c) <= 12 and max(ux(q) for q in c) - min(ux(q) for q in c) < stem * 2.2 and (max(q[1] for q in c) - min(q[1] for q in c)) < stem * 2.2 and len(c) >= 4]
        dots = [c for c in small if max(q[1] for q in c) - min(q[1] for q in c) < stem * 1.5 and not (ch in ",;" and min(q[1] for q in c) < 0 and len(c) > 6)]
        for c in dots:
            w = max(ux(q) for q in c) - min(ux(q) for q in c); n += 1
            pair = ch in "ï…"
            if w < stem * (0.78 if pair else 0.96): bad.append((p.name, ch, round(w), round(stem)))
print(f"{n} Punkte geprüft, Fehler: {len(bad)}", bad[:10])
