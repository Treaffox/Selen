"""Superelliptische Rundungen ("eckig"): schiebt die Bézier-Anfasser jeder
Kurve in Richtung ihres Eckpunkts.

Die Operation verändert nur Off-Curve-Punkte entlang ihrer bestehenden
Tangenten. Punktzahl, Punktreihenfolge und Glätte bleiben erhalten, die Master
bleiben also interpolierbar.

Konvention der Quellen (kubisch, UFO): Außenkonturen laufen gegen den
Uhrzeigersinn, die Farbe liegt links der Laufrichtung. Eine Linkskurve ist damit
eine konvexe Außenform, eine Rechtskurve eine konkave Innenform (Punze).
Innenformen werden stärker eckig gezogen als Außenformen, damit der Strich in
der Diagonale nicht dicker wird und die Punzen offen bleiben.

Kursive werden vor der Operation entneigt und danach wieder geneigt, damit die
Ecken der Superellipse auf den aufrechten Achsen liegen.
"""
import math


def _angle_weight(deg, lo=35.0, full=62.0, hi_full=118.0, hi=150.0):
    """1.0 für Viertelbögen, weich auslaufend für flache Bögen und Spitzkehren."""
    if deg <= lo or deg >= hi:
        return 0.0
    if deg < full:
        x = (deg - lo) / (full - lo)
    elif deg > hi_full:
        x = (hi - deg) / (hi - hi_full)
    else:
        return 1.0
    return x * x * (3 - 2 * x)


def _axis_off(dx, dy):
    """Abweichung einer Richtung von der nächsten Achse in Grad (0 = waagrecht/senkrecht)."""
    a = abs(math.degrees(math.atan2(dy, dx))) % 90
    return min(a, 90 - a)


def squircle_segment(p0, p1, p2, p3, k_convex, k_concave, t_max=0.92, axis_tol=8.0, tan=0.0):
    """Gibt neue (p1, p2) zurück oder None, wenn das Segment unverändert bleibt.

    Nur Viertelbögen, deren beide Tangenten achsparallel sind (± axis_tol Grad),
    werden gestrafft. Übergänge in Stämme und schräge Strichenden bleiben, sonst
    entstehen Knicke. Bei Kursiven (Punkte entneigt übergeben, tan = Neigung)
    zählt eine Tangente als achsparallel, wenn sie es entneigt oder geneigt ist:
    Geists Kursive hat echte senkrechte Extrempunkte."""
    d0 = (p1[0] - p0[0], p1[1] - p0[1])
    d3 = (p2[0] - p3[0], p2[1] - p3[1])
    if math.hypot(*d0) < 1e-6 or math.hypot(*d3) < 1e-6:
        return None

    def off(d):
        o = _axis_off(*d)
        return min(o, _axis_off(d[0] + d[1] * tan, d[1])) if tan else o

    if off(d0) > axis_tol or off(d3) > axis_tol:
        return None
    den = d0[0] * d3[1] - d0[1] * d3[0]
    if abs(den) < 1e-9:
        return None
    ex, ey = p3[0] - p0[0], p3[1] - p0[1]
    a = (ex * d3[1] - ey * d3[0]) / den
    b = (ex * d0[1] - ey * d0[0]) / den
    if a < 1.0 or b < 1.0:
        return None
    e3 = (-d3[0], -d3[1])
    cross = d0[0] * e3[1] - d0[1] * e3[0]
    dot = d0[0] * e3[0] + d0[1] * e3[1]
    deg = abs(math.degrees(math.atan2(cross, dot)))
    w = _angle_weight(deg)
    if w <= 0:
        return None
    k = (k_convex if cross > 0 else k_concave) * w
    t0, t3 = 1.0 / a, 1.0 / b
    n0 = max(t0, min(t_max, t0 + k * (1 - t0)))
    n3 = max(t3, min(t_max, t3 + k * (1 - t3)))
    c = (p0[0] + a * d0[0], p0[1] + a * d0[1])
    q1 = (p0[0] + (c[0] - p0[0]) * n0, p0[1] + (c[1] - p0[1]) * n0)
    q2 = (p3[0] + (c[0] - p3[0]) * n3, p3[1] + (c[1] - p3[1]) * n3)
    return q1, q2


def squircle_glyph(glyph, k_convex, k_concave, italic_angle=0.0):
    """Wendet die Superellipse auf alle kubischen Segmente eines UFO-Glyphs an."""
    tan = math.tan(math.radians(-italic_angle)) if italic_angle else 0.0
    un = lambda p: (p.x - p.y * tan, p.y)
    changed = 0
    for contour in glyph.contours:
        pts = contour.points
        n = len(pts)
        if n < 4:
            continue
        for i, p in enumerate(pts):
            if p.type != "curve":
                continue
            a, b, c = pts[(i - 3) % n], pts[(i - 2) % n], pts[(i - 1) % n]
            if a.type is None or b.type is not None or c.type is not None:
                continue
            res = squircle_segment(un(a), un(b), un(c), un(p), k_convex, k_concave, tan=tan)
            if res is None:
                continue
            (x1, y1), (x2, y2) = res
            b.x, b.y = round(x1 + y1 * tan), round(y1)
            c.x, c.y = round(x2 + y2 * tan), round(y2)
            changed += 1
    return changed
