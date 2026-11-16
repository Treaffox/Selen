#!/usr/bin/env python3
"""Probeabzug: Gewichtsleiter aufrecht/kursiv (statische TTF) und Kleinschrift gegen DejaVu Sans Condensed.
  ladder.py out.png [text]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent
out = sys.argv[1]
T = sys.argv[2] if len(sys.argv) > 2 else "Hamburgefonstiv Il1 0O 2026 äöü ßg"
W = ["ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]
img = Image.new("RGB", (1500, 1700), "white"); d = ImageDraw.Draw(img); y = 8
for w in W:
    for it in ("", "Italic"):
        name = {"Regular": "Italic"}.get(w, w + "Italic") if it else w
        f = ImageFont.truetype(str(ROOT / f"dist/ttf/Selen-{name}.ttf"), 34)
        d.text((10, y), T, font=f, fill="black"); y += 46
y += 10
refs = [("Selen", lambda s, b: ROOT / f"dist/ttf/Selen-{'Bold' if b else 'Regular'}.ttf"),
        ("DejaVuCond", lambda s, b: f"/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed{'-Bold' if b else ''}.ttf"),
        ("DejaVu", lambda s, b: f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if b else ''}.ttf")]
txt = "Datei Bearbeiten Ansicht Einstellungen Hilfe – 12 Treffer, 3 neu (Größe 1,5 MB)"
for label, fn in refs:
    for size in (11, 12, 13, 14):
        for b in (0, 1):
            f = ImageFont.truetype(str(fn(size, b)), size)
            d.text((10, y), f"{label} {size}", fill="#a00", font=ImageFont.load_default())
            d.text((110, y - 2), txt, font=f, fill="black"); y += size + 8
    y += 10
img.crop((0, 0, 1500, y)).save(out); print(out, y)
