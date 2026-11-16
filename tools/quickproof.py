#!/usr/bin/env python3
"""Schneller Probeabzug: kompiliert Master-UFOs (ohne Hinting) und setzt Text neben Vergleichsschriften.
  quickproof.py out.png [Master ...]  (Standard: Regular)"""
import sys, io
from pathlib import Path
import ufoLib2, ufo2ft
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent
out = sys.argv[1]; masters = sys.argv[2:] or ["Regular"]
TXT = ["Hamburgefonstiv 0123456789 Il1| O0 rnm", "Der schnelle braune Fuchs springt über den faulen Hund. ÄÖÜ ß €",
       "ΑΒΓΔ αβγδ  Съешь ещё этих мягких булок  gjpqy@&%"]
fonts = []
for m in masters:
    f = ufoLib2.Font.open(ROOT / f"sources/Roman/Selen-{m}.ufo")
    tt = ufo2ft.compileTTF(f, removeOverlaps=True, overlapsBackend="pathops")
    b = io.BytesIO(); tt.save(b); b.seek(0)
    fonts.append((f"Selen {m}", b.read()))
refs = [("DejaVu Sans Condensed", "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
        ("DejaVu Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
rows = []
for label, data in fonts: rows.append((label, io.BytesIO(data)))
for label, p in refs: rows.append((label, p))
W = 1500; sizes = [13, 28, 56]
H = len(rows) * (sum(int(s * 1.5) for s in sizes[:1]) + 90 + 150) + 40
img = Image.new("RGB", (W, 3000), "white"); d = ImageDraw.Draw(img); y = 10
for label, src in rows:
    d.text((10, y), label, fill="#a00", font=ImageFont.load_default()); y += 16
    for s, t in zip([13, 28, 40], TXT):
        if isinstance(src, io.BytesIO): src.seek(0)
        ft = ImageFont.truetype(src, s)
        d.text((10, y), t, fill="black", font=ft); y += int(s * 1.45)
    y += 14
img.crop((0, 0, W, y)).save(out); print(out, y)
