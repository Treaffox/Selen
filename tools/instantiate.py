#!/usr/bin/env python3
"""Schritt 1: Schneidet aus dem zweiachsigen Noto-Sans-Designspace (Gewicht x Breite)
eine einachsige Ebene bei fester Breite und schreibt Master-UFOs nach work/base/.

  instantiate.py [--width 91.5]  (Standard: BASE_WIDTH aus tools/selen/config.py)   (Designkoordinate der Breite, 100 = normal, 89 = 87,5 %)
"""
import argparse, shutil
from pathlib import Path
from fontTools.designspaceLib import DesignSpaceDocument, InstanceDescriptor
import sys
import ufoProcessor
sys.path.insert(0, str(Path(__file__).resolve().parent))
from selen import config as C

ROOT = Path(__file__).resolve().parent.parent
WEIGHTS = {"ExtraLight": 39, "Regular": 90, "Bold": 151, "Black": 190}  # Designwerte, 151 = Zwischenmaster

def run(style, width):
    src = ROOT / "work/noto-ufo" / ("NotoSans-Italic" if style == "Italic" else "NotoSans")
    ds_path = next(src.glob("*.designspace"))
    out = ROOT / "work/base" / style
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    doc = DesignSpaceDocument.fromfile(ds_path)
    doc.instances = []
    for name, w in WEIGHTS.items():
        inst = InstanceDescriptor()
        inst.filename = str((out / f"Base-{name}{'Italic' if style=='Italic' else ''}.ufo").resolve())
        inst.familyName = "Selen Base"; inst.styleName = name
        inst.location = {"Weight": w, "Width": width}
        doc.addInstance(inst)
    tmp = src / "_slice.designspace"
    doc.write(tmp)
    ufoProcessor.build(str(tmp), useVarlib=False, processRules=False, logger=None)
    tmp.unlink()
    print(style, "fertig:", sorted(p.name for p in out.glob("*.ufo")))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--width", type=float, default=C.BASE_WIDTH)
    a = ap.parse_args()
    for s in ("Roman", "Italic"): run(s, a.width)
