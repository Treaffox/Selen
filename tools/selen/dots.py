"""Quadratische Punkte (Tahoma/Verdana/Brom): ersetzt kleine runde Punkt-Konturen
(i, j, Umlaute, Satzzeichen) durch Quadrate.

Jeder Punkt ist eine Kontur aus genau 4 Kurvenpunkten (rund). Ersatz: Kontur aus
4 Linienpunkten mit gleicher Laufrichtung, gleicher Mitte, gleicher Flaeche.
Die Auswahl wird einmal im Regular-Master getroffen (Glyphname, Konturindex) und
in allen Mastern gleich angewendet, damit die Interpolation bestehen bleibt.
"""
import math
from ufoLib2.objects import Point


def _is_dot(c, stem, max_rel, tan):
    pts = [p for p in c.points if p.type is not None]
    if len(pts) != 4 or any(p.type != "curve" for p in pts) or len(c.points) > 12:
        return None
    un = [(p.x - p.y * tan, p.y) for p in pts]
    xs, ys = [u[0] for u in un], [u[1] for u in un]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if w < 0.5 * stem or h < 0.5 * stem or max(w, h) > max_rel * stem:
        return None
    if not (0.75 <= w / h <= 1.35):
        return None
    return True


def find_dots(font, stem, max_rel=2.0, italic_angle=0.0):
    tan = math.tan(math.radians(-italic_angle)) if italic_angle else 0.0
    found = {}
    for g in font:
        for i, c in enumerate(g.contours):
            if _is_dot(c, stem, max_rel, tan):
                found.setdefault(g.name, []).append(i)
    return found


def square_dots(font, selection, italic_angle=0.0, fill=1.0):
    """fill = Quadratfläche relativ zur Kreisfläche (1.0 = gleiche Fläche)."""
    tan = math.tan(math.radians(-italic_angle)) if italic_angle else 0.0
    n = 0
    for name, idxs in selection.items():
        if name not in font:
            continue
        g = font[name]
        for i in idxs:
            c = g.contours[i]
            pts = [p for p in c.points if p.type is not None]
            if len(pts) != 4:
                continue
            un = [(p.x - p.y * tan, p.y) for p in pts]
            xs, ys = [u[0] for u in un], [u[1] for u in un]
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            side = math.sqrt(math.pi / 4 * w * h) * math.sqrt(fill) * 1.04
            hs = side / 2
            # Ecken: jeder Kurvenpunkt (Extrempunkt) -> die ihm naechste Ecke der Richtung
            corner = {"l": (-hs, 0), "r": (hs, 0), "t": (0, hs), "b": (0, -hs)}
            # Ordnet Extrempunkte nach Lage und setzt Ecken so, dass die Reihenfolge erhalten bleibt
            order = []
            for (ux, uy) in un:
                dx, dy = ux - cx, uy - cy
                order.append("r" if dx > abs(dy) else "l" if -dx > abs(dy) else "t" if dy > 0 else "b")
            # Extrempunkt (z. B. rechts) -> Ecke zwischen zwei Seiten: Laufrichtung gegen den Uhrzeigersinn
            nxt = {"r": (hs, hs), "t": (-hs, hs), "l": (-hs, -hs), "b": (hs, -hs)}
            if len(set(order)) != 4:
                continue
            # Bei Gegenuhrzeigersinn folgt auf r -> t -> l -> b; sonst Uhrzeigersinn: r -> b -> l -> t
            seq = order
            ccw = (seq[1], seq[2], seq[3]) == {"r": ("t", "l", "b"), "t": ("l", "b", "r"),
                                               "l": ("b", "r", "t"), "b": ("r", "t", "l")}[seq[0]]
            cw_next = {"r": (hs, -hs), "b": (-hs, -hs), "l": (-hs, hs), "t": (hs, hs)}
            newpts = []
            for o in order:
                ox, oy = (nxt if ccw else cw_next)[o]
                nx, ny = cx + ox, cy + oy
                newpts.append(Point(round(nx + ny * tan), round(ny), "line"))
            c.points = newpts
            n += 1
    return n
