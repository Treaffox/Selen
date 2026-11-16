#!/usr/bin/env python3
"""Erzeugt die Selen-Master (UFO + Designspace) aus den Noto-Sans-Zwischenmastern.

  prepare.py [--style Roman|Italic]

Ergebnis: sources/<Stil>/Selen-<Master>.ufo und Selen[-Italic].designspace
"""
import argparse, shutil, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from fontTools.designspaceLib import (AxisDescriptor, AxisLabelDescriptor, DesignSpaceDocument, DiscreteAxisDescriptor,
    InstanceDescriptor, RangeAxisSubsetDescriptor, SourceDescriptor, VariableFontDescriptor)
from selen import config as C
from selen.ufo_ops import load_master, track_font, scale_font
from fontTools.pens.pointPen import ReverseContourPointPen
from fontTools.pens.transformPen import TransformPointPen
from selen.dots import find_dots, square_dots
from selen.squircle import squircle_glyph

INFO_CLEAR = ["openTypeNamePreferredFamilyName", "openTypeNamePreferredSubfamilyName", "openTypeNameCompatibleFullName",
    "openTypeNameWWSFamilyName", "openTypeNameWWSSubfamilyName", "postscriptFontName", "postscriptFullName",
    "styleMapFamilyName", "styleMapStyleName", "openTypeNameUniqueID", "openTypeNameSampleText", "trademark",
    "woffMetadataUniqueID", "woffMetadataVendor", "woffMetadataCredits", "woffMetadataDescription",
    "woffMetadataLicense", "woffMetadataCopyright", "woffMetadataTrademark", "woffMetadataLicensee",
    "macintoshFONDName", "postscriptUniqueID", "openTypeHeadCreated"]
STYLE_NAME = {"ExtraLight": "ExtraLight", "Regular": "Regular", "Bold": "Bold", "Black": "Black"}

def set_info(font, master, wght, italic):
    i = font.info
    for k in INFO_CLEAR:
        setattr(i, k, None)
    suffix = " Italic" if italic else ""
    style = STYLE_NAME[master] + suffix if not (master == "Regular" and italic) else "Italic"
    if master == "Regular" and not italic: style = "Regular"
    i.familyName = C.FAMILY
    i.styleName = style
    i.openTypeOS2WeightClass = wght
    i.openTypeNameDesigner = C.DESIGNER
    i.openTypeNameDesignerURL = C.URL
    i.openTypeNameManufacturer = C.DESIGNER
    i.openTypeNameManufacturerURL = C.URL
    i.openTypeNameLicense = C.LICENSE_DESC
    i.openTypeNameLicenseURL = C.LICENSE_URL
    i.openTypeNameDescription = C.DESCRIPTION
    i.copyright = C.COPYRIGHT
    i.openTypeOS2VendorID = C.VENDOR_ID
    i.versionMajor, i.versionMinor = C.VERSION_MAJOR, C.VERSION_MINOR
    i.italicAngle = C.ITALIC_ANGLE if italic else 0
    i.openTypeHeadCreated = None
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = C.ASC, -C.DESC, 0
    i.openTypeOS2TypoAscender, i.openTypeOS2TypoDescender, i.openTypeOS2TypoLineGap = C.ASC, -C.DESC, 0
    i.ascender, i.descender = C.ASC, -C.DESC
    t = i.openTypeOS2Selection or []
    i.openTypeOS2Selection = sorted(set(t) | {7})
    f_ = font
    if f_.features.text:
        import re
        f_.features.text = re.sub(r"feature kern \{.*?\} kern;\n?", "", f_.features.text, flags=re.S)

def bad_components(font):
    """(Glyph, Komponentenindex) mit verschachtelter oder transformierter Komponente."""
    out = {}
    for g in font:
        for i, c in enumerate(g.components):
            tr = tuple(c.transformation)
            nested = c.baseGlyph in font and bool(font[c.baseGlyph].components)
            if nested or tr[:4] != (1, 0, 0, 1):
                out.setdefault(g.name, []).append(i)
    return out


def flatten(font, sel):
    n = 0
    for name, idxs in sel.items():
        g = font[name]
        for i in sorted(idxs, reverse=True):
            if i < len(g.components):
                c = g.components[i]
                tr = tuple(c.transformation)
                pen = g.getPointPen()
                if tr[0] * tr[3] - tr[1] * tr[2] < 0:
                    pen = ReverseContourPointPen(pen)
                font[c.baseGlyph].drawPoints(TransformPointPen(pen, tr))
                g.removeComponent(c); n += 1
    return n


def fix_marks(f):
    """U+031A hat in der Vorlage Breite (Noto), U+034F/U+FE00 fehlen als Marke in GDEF."""
    by_u = {u: g.name for g in f for u in g.unicodes}
    n31a, n34f, nfe00 = by_u[0x031A], by_u[0x034F], by_u[0xFE00]
    g = f[n31a]
    if g.width:
        dx = -round(g.width / 2)
        for c in g.contours:
            for p in c.points: p.x += dx
        for a in g.anchors: a.x += dx
        g.width = 0
    if 0x2E3C in by_u.keys() and f[by_u[0x2E3C]].width == 0:
        f[by_u[0x2E3C]].width = f["period"].width
    cats = f.lib.setdefault("public.openTypeCategories", {})
    import unicodedata
    for g in f:
        if any(unicodedata.category(chr(u)) in ("Mn", "Me") for u in g.unicodes) or (not g.unicodes and any(a.name and a.name.startswith("_") for a in g.anchors)):
            cats[g.name] = "mark"
        elif g.contours or g.components:
            cats[g.name] = "ligature" if "_" in g.name.split(".")[0] else "base"
    for n in (n31a, n34f, nfe00):
        cats[n] = "mark"


def build_designspace(style, paths):
    italic = style == "Italic"
    doc = DesignSpaceDocument()
    doc.formatVersion = "5.0"
    doc.elidedFallbackName = "Regular"
    wght = AxisDescriptor(tag="wght", name="Weight", minimum=200, default=400, maximum=900)
    wght.axisLabels = [AxisLabelDescriptor(name=n, userValue=u, elidable=(u == 400),
                                           linkedUserValue=700 if u == 400 else None) for u, n, _ in C.WEIGHTS]
    ital = DiscreteAxisDescriptor(tag="ital", name="Italic", values=[1 if italic else 0], default=1 if italic else 0)
    ital.axisLabels = [AxisLabelDescriptor(name="Italic", userValue=1)] if italic else \
        [AxisLabelDescriptor(name="Roman", userValue=0, elidable=True, linkedUserValue=1)]
    doc.axes = [wght, ital]
    for master, path in paths.items():
        s = SourceDescriptor(filename=path.name, familyName=C.FAMILY,
                             styleName=(master + (" Italic" if italic else "")).strip(),
                             designLocation={"Weight": C.MASTERS[master], "Italic": 1 if italic else 0})
        if master == "Regular":
            s.copyLib = s.copyInfo = s.copyGroups = s.copyFeatures = True
        doc.addSource(s)
    for u, n, _ in C.WEIGHTS:
        if italic:
            style_name = "Italic" if n == "Regular" else f"{n} Italic"
            ps = f"{C.FILE_STEM}-{'Italic' if n == 'Regular' else n + 'Italic'}"
        else:
            style_name, ps = n, f"{C.FILE_STEM}-{n}"
        if n in ("Regular", "Bold"):
            smf = C.FAMILY
            sms = (("bold " if n == "Bold" else "") + ("italic" if italic else "regular")).replace("bold regular", "bold")
        else:
            smf, sms = f"{C.FAMILY} {n}", ("italic" if italic else "regular")
        doc.addInstance(InstanceDescriptor(familyName=C.FAMILY, styleName=style_name, postScriptFontName=ps,
            styleMapFamilyName=smf, styleMapStyleName=sms, filename=f"instances/{ps}.ufo",
            designLocation={"Weight": u, "Italic": 1 if italic else 0}))
    vf = f"{C.FILE_STEM}{'-Italic' if italic else ''}[wght]"
    doc.addVariableFont(VariableFontDescriptor(name=vf, filename=vf, axisSubsets=[RangeAxisSubsetDescriptor(name="Weight")]))
    return doc


def build_style(style):
    italic = style == "Italic"
    out = C.SOURCES / style
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    rep = {}
    paths = {}
    ang = C.ITALIC_ANGLE if italic else 0
    reg = load_master(C.BASE / style / f"Base-Regular{'Italic' if italic else ''}.ufo")
    scale_font(reg, C.SCALE)
    lb = reg["l"].getBounds(reg)
    stem = round(lb.xMax - lb.xMin) if not italic else 95
    dot_sel = find_dots(reg, stem, italic_angle=ang) if C.SQUARE_DOTS else {}
    rep["dots"] = {k: v for k, v in dot_sel.items()}
    print(style, "Punkt-Glyphen:", len(dot_sel), "Stamm", stem)
    # verschachtelte/transformierte Komponenten (fontbakery): einmal im Regular bestimmen, in allen Mastern auflösen
    rounds = []
    for _ in range(4):
        csel = bad_components(reg)
        if not csel: break
        rounds.append(csel)
        flatten(reg, csel)
    rep["flatten_rounds"] = [sum(len(v) for v in r.values()) for r in rounds]
    for master, wght in C.MASTERS.items():
        src = C.BASE / style / f"Base-{master}{'Italic' if italic else ''}.ufo"
        f = load_master(src)
        scale_font(f, C.SCALE)
        if dot_sel:
            rep.setdefault("dots_squared", {})[master] = square_dots(f, dot_sel, ang)
        for csel in rounds:
            flatten(f, csel)
        track_font(f, C.TRACK[master])
        fix_marks(f)
        n = sum(squircle_glyph(g, C.SQ_CONVEX, C.SQ_CONCAVE, C.ITALIC_ANGLE if italic else 0) for g in f)
        set_info(f, master, wght, italic)
        name = f"{C.FILE_STEM}-{master}{'Italic' if italic else ''}.ufo"
        f.save(out / name, overwrite=True)
        ys = [b for g in f for b in [g.getBounds(f)] if b]
        rep[master] = {"squircled_segments": n}
        rep.setdefault("bbox", [0, 0])
        rep["bbox"] = [max(rep["bbox"][0], max(b.yMax for b in ys)), min(rep["bbox"][1], min(b.yMin for b in ys))]
        paths[master] = out / name
        print(style, master, "ok", n)
    build_designspace(style, paths).write(out / f"{C.FILE_STEM}{'-Italic' if italic else ''}.designspace")
    return rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--style", choices=["Roman", "Italic"])
    a = ap.parse_args()
    log = {}
    for s in ([a.style] if a.style else ["Roman", "Italic"]):
        r = build_style(s)
        log[s] = {k: v for k, v in r.items() if k != "dots"}
        log[s + ".bbox"] = r["bbox"]
    (C.ROOT / "sources/prepare-log.json").write_text(json.dumps(log, indent=1))
