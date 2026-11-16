"""Grundoperationen auf UFO-Mastern: laden, interpolieren, skalieren."""
import math
import ufoLib2

NUMERIC_INFO = ("xHeight", "capHeight", "ascender", "descender")


def load_master(path):
    """Öffnet ein UFO und behält nur die Standardebene (plus '{…}'-Zwischenebenen)."""
    font = ufoLib2.Font.open(path)
    font.unlazify() if hasattr(font, "unlazify") else None
    for layer in list(font.layers):
        if layer is font.layers.defaultLayer or layer.name.startswith("{"):
            continue
        del font.layers[layer.name]
    return font


def compatible(ga, gb):
    if len(ga.contours) != len(gb.contours) or len(ga.components) != len(gb.components):
        return False
    for ca, cb in zip(ga.contours, gb.contours):
        if len(ca.points) != len(cb.points):
            return False
        for pa, pb in zip(ca.points, cb.points):
            if pa.type != pb.type:
                return False
    for ca, cb in zip(ga.components, gb.components):
        if ca.baseGlyph != cb.baseGlyph:
            return False
    return True


def _l(a, b, t):
    return a + (b - a) * t


def lerp_glyph_into(target, ga, gb, t, rnd=round):
    """Schreibt die Interpolation ga→gb (Faktor t) in target (Struktur wie ga)."""
    for ct, ca, cb in zip(target.contours, ga.contours, gb.contours):
        for pt, pa, pb in zip(ct.points, ca.points, cb.points):
            pt.x = rnd(_l(pa.x, pb.x, t))
            pt.y = rnd(_l(pa.y, pb.y, t))
    for kt, ka, kb in zip(target.components, ga.components, gb.components):
        ta, tb = tuple(ka.transformation), tuple(kb.transformation)
        vals = [_l(x, y, t) for x, y in zip(ta, tb)]
        vals[4], vals[5] = rnd(vals[4]), rnd(vals[5])
        kt.transformation = type(ka.transformation)(*vals)
    bn = {a.name: a for a in gb.anchors}
    for at, aa in zip(target.anchors, ga.anchors):
        ab = bn.get(aa.name)
        if ab is not None:
            at.x = rnd(_l(aa.x, ab.x, t))
            at.y = rnd(_l(aa.y, ab.y, t))
    target.width = rnd(_l(ga.width, gb.width, t))


def lerp_font(fa, fb, t, glyph_override=None):
    """Neuer Master = fa + t·(fb − fa). fa wird dabei verändert und zurückgegeben.

    glyph_override: {name: (ga, gb, t)} für Glyphen mit abweichender Stützstelle.
    """
    glyph_override = glyph_override or {}
    bad = []
    for g in fa:
        name = g.name
        if name in glyph_override:
            ga, gb, tt = glyph_override[name]
        elif name in fb:
            ga, gb, tt = g, fb[name], t
        else:
            bad.append(name)
            continue
        if not compatible(ga, gb):
            bad.append(name)
            continue
        if ga is g:
            snapshot = g.copy()
            lerp_glyph_into(g, snapshot, gb, tt)
        else:
            if not compatible(g, ga):
                bad.append(name)
                continue
            lerp_glyph_into(g, ga, gb, tt)
    # Kerning
    pairs = set(fa.kerning) | set(fb.kerning)
    kern = {}
    for p in pairs:
        v = round(_l(fa.kerning.get(p, 0), fb.kerning.get(p, 0), t))
        if v:
            kern[p] = v
    fa.kerning.clear()
    fa.kerning.update(kern)
    for attr in NUMERIC_INFO:
        a, b = getattr(fa.info, attr, None), getattr(fb.info, attr, None)
        if a is not None and b is not None:
            setattr(fa.info, attr, round(_l(a, b, t)))
    return fa, bad


def xscale_font(font, s, italic_angle=0.0):
    """Skaliert alle Glyphen horizontal um s. Bei Kursiven wird um die geneigte
    Achse skaliert, der Neigungswinkel bleibt also erhalten."""
    if abs(s - 1.0) < 1e-9:
        return
    tan = math.tan(math.radians(-italic_angle)) if italic_angle else 0.0

    def fx(x, y):
        return round((x - y * tan) * s + y * tan)

    for g in font:
        for c in g.contours:
            for p in c.points:
                p.x = fx(p.x, p.y)
        for a in g.anchors:
            a.x = fx(a.x, a.y)
        for k in g.components:
            t = list(k.transformation)
            t[4] = fx(t[4], t[5])
            k.transformation = type(k.transformation)(*t)
        g.width = round(g.width * s)
    for p in list(font.kerning):
        font.kerning[p] = round(font.kerning[p] * s)


def track_font(font, delta):
    """Erhöht die Laufweite: delta/2 links und rechts an jedem Glyph mit Breite > 0."""
    if not delta:
        return
    half = delta / 2.0
    comp_based = {}
    for g in font:
        if g.width <= 0:
            continue
        g.width = round(g.width + delta)
        for c in g.contours:
            for p in c.points:
                p.x = round(p.x + half)
        for a in g.anchors:
            a.x = round(a.x + half)
    # Komponenten: Basis hat sich bereits um half verschoben. Marken (Breite 0) nicht.
    for g in font:
        shift_self = half if g.width > 0 else 0.0
        for k in g.components:
            base = font[k.baseGlyph] if k.baseGlyph in font else None
            base_shift = half if (base is not None and base.width > 0) else 0.0
            dx = shift_self - base_shift
            if dx:
                t = list(k.transformation)
                t[4] = round(t[4] + dx)
                k.transformation = type(k.transformation)(*t)


def scale_font(font, s):
    """Skaliert alles gleichmaessig (Konturen, Anker, Komponenten, Breiten, Kerning, Metriken)."""
    if abs(s - 1.0) < 1e-9:
        return
    for g in font:
        for c in g.contours:
            for p in c.points:
                p.x, p.y = round(p.x * s), round(p.y * s)
        for a in g.anchors:
            a.x, a.y = round(a.x * s), round(a.y * s)
        for k in g.components:
            t = list(k.transformation)
            t[4], t[5] = round(t[4] * s), round(t[5] * s)
            k.transformation = type(k.transformation)(*t)
        g.width = round(g.width * s)
    for p in list(font.kerning):
        font.kerning[p] = round(font.kerning[p] * s)
    i = font.info
    for k in ("xHeight", "capHeight", "ascender", "descender", "openTypeHheaAscender", "openTypeHheaDescender",
              "openTypeHheaLineGap", "openTypeOS2TypoAscender", "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap",
              "openTypeOS2WinAscent", "openTypeOS2WinDescent"):
        v = getattr(i, k, None)
        if v is not None:
            setattr(i, k, round(v * s))
