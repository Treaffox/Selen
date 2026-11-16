#!/usr/bin/env python3
"""Erzeugt die Selen-Website (Legacy-Design-Look) nach site/dist.

  site.py

Voraussetzung: tools/build.py ist gelaufen (dist/). Das Legacy-Design-System
wird aus site/vendor/ übernommen (Kopie von trfx-legacy.min.css, legacy.js, Marke).
"""
import html
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fontTools.ttLib import TTFont
from selen import config as C

ROOT = C.ROOT
SITE = ROOT / "site"
OUT = SITE / "dist"
VENDOR = SITE / "vendor"
V = C.VERSION

ICONS = ["home", "type", "download", "info", "check", "code", "sliders", "doc", "globe", "palette", "book", "keyboard",
         "gear", "layout", "table", "star", "box", "terminal", "tag"]


def sprite():
    """Nur die benutzten Symbole aus der Icon-Bibliothek des Design Systems."""
    src = (VENDOR / "trfx-legacy-icons.svg").read_text()
    defs = re.search(r"<defs>.*?</defs>", src, re.S)
    syms = []
    for n in ICONS:
        m = re.search(rf'<symbol id="i-{n}".*?</symbol>', src, re.S)
        if not m:
            raise SystemExit(f"Symbol {n} fehlt")
        syms.append(m.group(0))
    # Verläufe stehen in <defs> oder als eigene Elemente: ganzen Kopf bis zum ersten Symbol übernehmen
    head = src[:src.index("<symbol")]
    return head + "".join(syms) + "</svg>"


def icon(n, extra=""):
    return f'<svg class="lg-icon{extra}" aria-hidden="true"><use href="#i-{n}"/></svg>'


def charset(font):
    cm = font.getBestCmap()
    return cm


RANGES = [
    ("Ziffern", [(0x30, 0x39)]),
    ("Großbuchstaben", [(0x41, 0x5A), (0xC0, 0xD6), (0xD8, 0xDE)]),
    ("Kleinbuchstaben", [(0x61, 0x7A), (0xDF, 0xF6), (0xF8, 0xFF)]),
    ("Satz- und Sonderzeichen", [(0x21, 0x2F), (0x3A, 0x40), (0x5B, 0x60), (0x7B, 0x7E), (0xA1, 0xBF), (0x2010, 0x2027), (0x20AC, 0x20AC), (0x2190, 0x2193), (0x2212, 0x2212), (0x2260, 0x2264)]),
    ("Latein erweitert", [(0x100, 0x17F)]),
    ("Griechisch", [(0x391, 0x3A9), (0x3B1, 0x3C9)]),
    ("Kyrillisch", [(0x410, 0x44F), (0x401, 0x401), (0x451, 0x451)]),
]


def glyph_blocks(cm):
    out = []
    for title, rs in RANGES:
        chars = [chr(u) for a, b in rs for u in range(a, b + 1) if u in cm and chr(u).strip()]
        cells = "".join(f'<span class="glyph" role="listitem" title="U+{ord(c):04X}">{html.escape(c)}</span>' for c in chars)
        out.append(f'<h3>{title} <span class="count">({len(chars)})</span></h3>\n<div class="glyphs" role="list" aria-label="{title}">{cells}</div>')
    return "\n".join(out)


def feature_table():
    rows = [
        ("tnum / pnum", "Ziffern tabellarisch (Standard) / proportional"),
        ("lnum / onum", "Versalziffern / Mediävalziffern"),
        ("case", "Satzzeichen und Klammern für Versalien"),
        ("frac, numr, dnom", "Brüche, Zähler, Nenner"),
        ("sups, subs, sinf, ordn", "hoch- und tiefgestellt, Ordinalzeichen"),
        ("smcp, c2sc", "Kapitälchen"),
        ("zero", "Null mit Schrägstrich"),
        ("salt", "Versal-I mit Serifen (Verdana-Art), unterscheidet I, l und 1 eindeutig"),
        ("ss03, ss04, ss06, ss07", "Stilvarianten aus der Vorlage (florin, hakenlose Formen u. a.)"),
        ("kern, mark, mkmk", "Unterschneidung, Akzente und gestapelte Akzente"),
    ]
    return "".join(f"<tr><th scope=\"row\"><code>{a}</code></th><td>{b}</td></tr>" for a, b in rows)


def weight_rows():
    names = [(200, "ExtraLight"), (300, "Light"), (400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"),
             (800, "ExtraBold"), (900, "Black")]
    sample = "Datei Bearbeiten Ansicht – Hamburgefonstiv 0123456789"
    out = []
    for w, n in names:
        out.append(f'<tr><th scope="row">{w}<br><span class="sub">{n}</span></th>'
                   f'<td class="w{w}">{sample}</td><td class="w{w} it">{sample}</td></tr>')
    return "".join(out)


PAGE = """<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Selen – Schrift für das TRFX Legacy Design</title>
  <meta name="description" content="Selen ist eine humanistische Sans in der Tradition von Tahoma und Verdana: Gewichte 200 bis 900, aufrecht und kursiv, Latein, Griechisch und Kyrillisch. Frei unter der SIL Open Font License.">
  <meta name="theme-color" content="#2f6397">
  <link rel="icon" type="image/svg+xml" href="assets/brand/trfx-legacy-icon.svg">
  <link rel="preload" href="assets/fonts/Selen-VF.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/trfx-legacy.min.css?v=@V@">
  <link rel="stylesheet" href="assets/selen.css?v=@V@">
</head>
<body>
@SPRITE@
<a class="lg-skip" href="#inhalt">Zum Inhalt springen</a>

<header class="lg-header">
  <div class="lg-header__inner">
    <a class="lg-brand" href="./">
      <img src="assets/brand/trfx-legacy-logo.svg" width="157" height="34" alt="TRFX.DE">
    </a>
    <nav class="lg-nav" aria-label="Hauptnavigation">
      <ul>
        <li><a href="#start" aria-current="page">@I_home@Start</a></li>
        <li><a href="#schnitte">@I_type@Schnitte</a></li>
        <li><a href="#tester">@I_sliders@Tester</a></li>
        <li><a href="#zeichen">@I_keyboard@Zeichen</a></li>
        <li><a href="#features">@I_gear@Features</a></li>
        <li><a href="#download">@I_download@Download</a></li>
      </ul>
    </nav>
  </div>
  <div class="lg-header__rule"></div>
</header>

<div class="lg-address" role="region" aria-label="Adresse">
  <div class="lg-address__inner">
    <span class="lg-address__label" id="adr-label">Adresse</span>
    <nav aria-labelledby="adr-label" class="lg-address__nav">
      <ol class="lg-address__path">
        <li>@I_globe@<a href="./">selen.trfx.de</a></li>
      </ol>
    </nav>
  </div>
</div>

<div class="lg-layout">
  <aside class="lg-layout__side" aria-label="Seitenleiste">
    <div class="lg-pane">
      <details class="lg-pane__group" open>
        <summary>Auf dieser Seite</summary>
        <div class="lg-pane__body"><ul>
          <li><a href="#start">Selen</a></li>
          <li><a href="#schnitte">Schnitte</a></li>
          <li><a href="#tester">Tester</a></li>
          <li><a href="#aktion">In Aktion</a></li>
          <li><a href="#zeichen">Zeichen</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#download">Download</a></li>
          <li><a href="#herkunft">Herkunft und Lizenz</a></li>
          <li><a href="#changelog">Änderungen</a></li>
        </ul></div>
      </details>
      <details class="lg-pane__group lg-pane__group--meta" open>
        <summary>Details</summary>
        <div class="lg-pane__body">
          <p><strong>Selen @V@</strong></p>
          <p>Lizenz: SIL Open Font License 1.1</p>
          <p><a href="#changelog">Änderungsprotokoll</a></p>
        </div>
      </details>
    </div>
  </aside>

  <main class="lg-main" id="inhalt" tabindex="-1">

<section class="hero lg-window" id="start" aria-labelledby="hero-titel">
  <div class="lg-window__title">@I_type@<span class="lg-window__text" id="hero-titel">Selen – Schrift für das TRFX Legacy Design</span></div>
  <div class="lg-window__body lg-window__body--page">
    <div>
      <h1>Selen</h1>
      <p class="hero__claim"><strong>Klar lesbar bei 11 bis 14 Pixeln.</strong></p>
      <p class="lg-lead">Eine humanistische Sans in der Tradition von Tahoma und Verdana, gebaut für Oberflächen im TRFX Legacy Design. Große x-Höhe, offene Bögen, quadratische Punkte und tabellarische Ziffern. Gewichte von 200 bis 900, aufrecht und kursiv.</p>
      <div class="lg-actions lg-actions--start">
        <a class="lg-btn is-default" href="#download">Herunterladen</a>
        <a class="lg-btn" href="#tester">Ausprobieren</a>
      </div>
      <ul class="facts">
        <li><strong>@NW@</strong>Gewichte</li>
        <li><strong>@NCP@</strong>Zeichen</li>
        <li><strong>3</strong>Schriftsysteme</li>
        <li><strong>OFL</strong>frei nutzbar</li>
      </ul>
    </div>
    <div class="hero__sample" aria-hidden="true"><span class="big">Aa</span><span class="small">Hamburgefonstiv<br>0123456789</span></div>
  </div>
</section>

<section id="schnitte" aria-labelledby="h-schnitte">
  <h2 id="h-schnitte">Schnitte</h2>
  <p>Acht Gewichte, jeweils aufrecht und kursiv. Als Variable Font stufenlos von 200 bis 900, dazu 16 statische Schnitte für Desktop und Windows.</p>
  <div class="lg-scroll" tabindex="0">
    <table class="lg-table lg-table--zebra">
      <caption>Alle Gewichte</caption>
      <thead><tr><th scope="col">Gewicht</th><th scope="col">Aufrecht</th><th scope="col">Kursiv</th></tr></thead>
      <tbody>@WROWS@</tbody>
    </table>
  </div>
</section>

<section id="tester" aria-labelledby="h-tester">
  <h2 id="h-tester">Tester</h2>
  <div class="lg-window lg-window--quiet" aria-labelledby="tt">
    <div class="lg-window__title"><span class="lg-window__text" id="tt">Text eingeben und einstellen</span></div>
    <div class="lg-window__body">
      <div class="tester-controls">
        <div class="lg-field"><label for="t-text">Text</label>
          <textarea class="lg-textarea" id="t-text" rows="3">Der schnelle braune Fuchs springt über den faulen Hund. 0123456789 – Il1 O0</textarea>
        </div>
        <div class="lg-field"><label for="t-size">Größe: <output id="t-size-o">24</output> px</label>
          <input type="range" id="t-size" min="9" max="96" value="24">
        </div>
        <div class="lg-field"><label for="t-wght">Gewicht: <output id="t-wght-o">400</output></label>
          <input type="range" id="t-wght" min="200" max="900" step="1" value="400">
        </div>
        <div class="lg-check"><input type="checkbox" id="t-italic"><label for="t-italic">Kursiv</label></div>
        <div class="lg-check"><input type="checkbox" id="t-pnum"><label for="t-pnum">proportionale Ziffern (<code>pnum</code>)</label></div>
      </div>
      <p class="tester-out" id="t-out" aria-live="off">Der schnelle braune Fuchs springt über den faulen Hund. 0123456789 – Il1 O0</p>
    </div>
  </div>
</section>

<section id="aktion" aria-labelledby="h-aktion">
  <h2 id="h-aktion">In Aktion</h2>
  <p>Selen in 12 bis 14 Pixeln, wie in einer Anwendung im Legacy Design.</p>
  <div class="lg-window" aria-labelledby="ta">
    <div class="lg-window__title">@I_table@<span class="lg-window__text" id="ta">Benutzer verwalten</span></div>
    <div class="lg-window__body">
      <div class="lg-toolbar" role="toolbar" aria-label="Aktionen">
        <button type="button" class="lg-btn lg-btn--sm">@I_doc@Neu</button>
        <button type="button" class="lg-btn lg-btn--sm">@I_check@Speichern</button>
        <button type="button" class="lg-btn lg-btn--sm">@I_gear@Einstellungen</button>
      </div>
      <div class="lg-scroll" tabindex="0">
        <table class="lg-table lg-table--zebra">
          <caption>12 Treffer, 3 neu</caption>
          <thead><tr><th scope="col">Name</th><th scope="col">Rolle</th><th scope="col">Zuletzt</th><th scope="col">Größe</th></tr></thead>
          <tbody>
            <tr><td>Anna Müller</td><td>Administrator</td><td>16.11.2026</td><td>1,5 MB</td></tr>
            <tr><td>Boris Ščerbak</td><td>Redakteur</td><td>15.11.2026</td><td>0,8 MB</td></tr>
            <tr><td>Γιώργος Παπαδόπουλος</td><td>Gast</td><td>12.11.2026</td><td>12,4 KB</td></tr>
            <tr><td>Étienne Nguyễn</td><td>Redakteur</td><td>09.11.2026</td><td>3,0 MB</td></tr>
          </tbody>
        </table>
      </div>
      <form class="lg-form" data-lg-noop>
        <div class="lg-field"><label for="f-q">Suchen</label><input class="lg-input" id="f-q" type="text" value="Müller"></div>
        <div class="lg-check"><input type="checkbox" id="f-a" checked><label for="f-a">Nur aktive Benutzer</label></div>
        <div class="lg-actions"><button class="lg-btn is-default" type="button">Suchen</button><button class="lg-btn" type="button">Abbrechen</button></div>
      </form>
    </div>
  </div>
</section>

<section id="zeichen" aria-labelledby="h-zeichen">
  <h2 id="h-zeichen">Zeichen</h2>
  <p>@NCP@ Zeichen in @NG@ Glyphen: Latein mit allen europäischen Erweiterungen und Vietnamesisch, Griechisch einschließlich polytonischer Zeichen, Kyrillisch einschließlich der nichtslawischen Sprachen. Eine Auswahl:</p>
  @GLYPHS@
</section>

<section id="features" aria-labelledby="h-features">
  <h2 id="h-features">Features</h2>
  <div class="lg-scroll" tabindex="0">
    <table class="lg-table lg-table--zebra">
      <caption>OpenType-Features</caption>
      <thead><tr><th scope="col">Feature</th><th scope="col">Wirkung</th></tr></thead>
      <tbody>@FEATURES@</tbody>
    </table>
  </div>
  <p>Aktivieren im Web mit <code>font-feature-settings: "pnum"</code> oder <code>font-variant-numeric: proportional-nums</code>.</p>
</section>

<section id="download" aria-labelledby="h-download">
  <h2 id="h-download">Download</h2>
  <div class="lg-notice lg-notice--info" role="note"><p><strong>Selen @V@</strong>: Variable Fonts, 16 statische Schnitte (OTF und gehintete TTF), WOFF2, Lizenz und Anleitung in einem Paket.</p></div>
  <p><a class="lg-btn is-default" href="@ZIP@" download>@I_download@Selen-@V@.zip (@ZIPSIZE@)</a></p>
  <h3>Im Web einbinden</h3>
<pre class="lg-source" tabindex="0"><code>@font-face {
  font-family: "Selen";
  src: url("Selen[wght].woff2") format("woff2");
  font-weight: 200 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Selen";
  src: url("Selen-Italic[wght].woff2") format("woff2");
  font-weight: 200 900;
  font-style: italic;
  font-display: swap;
}
body { font-family: "Selen", Tahoma, Verdana, sans-serif; }</code></pre>
  <h3>Im Legacy Design System</h3>
<pre class="lg-source" tabindex="0"><code>:root {
  --lg-font-text: "Selen", Tahoma, Verdana, sans-serif;
  --lg-font-head: var(--lg-font-text);
}</code></pre>
</section>

<section id="herkunft" aria-labelledby="h-herkunft">
  <h2 id="h-herkunft">Herkunft und Lizenz</h2>
  <p>Selen baut auf <strong>Noto Sans</strong> auf (SIL Open Font License, The Noto Project Authors). Die Proportionen orientieren sich an Tahoma und Verdana, das Gerüst an DejaVu Sans und PT Sans, die Rundungen teilweise an Brom. Konturen von Tahoma, Verdana, DejaVu, PT Sans oder Brom sind nicht enthalten.</p>
  <p>Selen steht unter der <a href="assets/LICENSE.txt">SIL Open Font License 1.1</a>. „Selen“ ist Reserved Font Name: Abgeleitete Schriften müssen anders heißen. Selen ist mit Claude Code entstanden (<em>this font is vibe coded using Claude Code</em>).</p>
</section>

<section id="changelog" aria-labelledby="h-changelog">
  <h2 id="h-changelog">Änderungen</h2>
  <h3>0.1.0 – 16.11.2026</h3>
  <ul>
    <li>Erste Version: Gewichte 200 bis 900, aufrecht und kursiv, Variable Font und 16 statische Schnitte.</li>
    <li>Latein, Griechisch, Kyrillisch (@NCP@ Zeichen), tabellarische Ziffern als Standard.</li>
    <li>Quadratische Punkte, teilweise gestraffte Rundungen, gehintet für 8 bis 48 ppem.</li>
  </ul>
</section>

  </main>
</div>

<footer class="lg-footer">
  <div class="lg-footer__inner">
    <ul class="lg-footer__links">
      <li><a href="#download">Download</a></li>
      <li><a href="assets/LICENSE.txt">Lizenz</a></li>
      <li><a href="#changelog">Änderungen</a></li>
    </ul>
    <p class="lg-footer__copy">© 2026 TRFX · Selen @V@ · SIL Open Font License 1.1</p>
  </div>
</footer>
<script src="assets/legacy.js?v=@V@"></script>
<script src="assets/selen.js?v=@V@"></script>
</body>
</html>
"""


def build():
    dist = ROOT / "dist"
    if not (dist / "variable").exists():
        raise SystemExit("dist/ fehlt, erst tools/build.py ausführen")
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets/fonts").mkdir(parents=True)
    (OUT / "assets/brand").mkdir(parents=True)
    (OUT / "downloads").mkdir()
    vf = TTFont(dist / "variable/Selen[wght].ttf")
    cm = vf.getBestCmap()
    ncp, ng = len(cm), len(vf.getGlyphOrder())

    # Schriften der Seite
    shutil.copy(VENDOR / "Krypton-VF.woff2", OUT / "assets/fonts/Krypton-VF.woff2")  # Monospace des Design Systems (OFL)
    shutil.copy(dist / "webfonts/Selen[wght].woff2", OUT / "assets/fonts/Selen-VF.woff2")
    shutil.copy(dist / "webfonts/Selen-Italic[wght].woff2", OUT / "assets/fonts/Selen-Italic-VF.woff2")
    # Design System
    shutil.copy(VENDOR / "trfx-legacy.min.css", OUT / "assets/trfx-legacy.min.css")
    shutil.copy(VENDOR / "legacy.js", OUT / "assets/legacy.js")
    for n in ("trfx-legacy-logo.svg", "trfx-legacy-icon.svg"):
        shutil.copy(VENDOR / n, OUT / "assets/brand" / n)
    shutil.copy(SITE / "src/selen.css", OUT / "assets/selen.css")
    shutil.copy(SITE / "src/selen.js", OUT / "assets/selen.js")
    shutil.copy(ROOT / "LICENSE", OUT / "assets/LICENSE.txt")

    # Download-Paket
    zpath = OUT / "downloads" / f"Selen-{V}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for sub in ("variable", "otf", "ttf", "webfonts"):
            for p in sorted((dist / sub).iterdir()):
                z.write(p, f"Selen-{V}/{sub}/{p.name}")
        for n in ("LICENSE", "README.md", "CHANGELOG.md", "VERSION"):
            z.write(ROOT / n, f"Selen-{V}/{n}")
    size = zpath.stat().st_size / 1e6

    page = PAGE
    rep = {"@V@": V, "@NW@": "8 × 2", "@NCP@": f"{ncp:,}".replace(",", "."), "@NG@": f"{ng:,}".replace(",", "."),
           "@ZIP@": f"downloads/Selen-{V}.zip", "@ZIPSIZE@": f"{size:.1f} MB".replace(".", ","),
           "@WROWS@": weight_rows(), "@FEATURES@": feature_table(), "@GLYPHS@": glyph_blocks(cm), "@SPRITE@": sprite_block()}
    for k, v in rep.items():
        page = page.replace(k, v)
    page = re.sub(r"@I_([a-z-]+)@", lambda m: icon(m.group(1)), page)
    left = re.findall(r"@[A-Za-z_]+@", page)
    assert not left, left
    (OUT / "index.html").write_text(page)
    (OUT / "404.html").write_text(PAGE404.replace("@V@", V))
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n")
    (OUT / "version.json").write_text(json.dumps({"name": "Selen", "version": V, "download": f"/downloads/Selen-{V}.zip",
                                                   "characters": ncp, "glyphs": ng}, indent=1))
    print(f"Seite: {OUT} ({ncp} Zeichen, ZIP {size:.1f} MB)")


def sprite_block():
    return f'<div hidden>{sprite()}</div>' if False else sprite().replace("<svg ", '<svg class="lg-sprite" aria-hidden="true" focusable="false" ', 1)


PAGE404 = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seite nicht gefunden – Selen</title><link rel="stylesheet" href="/assets/trfx-legacy.min.css?v=@V@"><link rel="stylesheet" href="/assets/selen.css?v=@V@"></head>
<body><main class="lg-main" id="inhalt" tabindex="-1"><section class="lg-window"><div class="lg-window__title"><span class="lg-window__text">Selen</span></div>
<div class="lg-window__body"><h1>Seite nicht gefunden</h1><p>Diese Adresse gibt es nicht.</p><p><a class="lg-btn is-default" href="/">Zur Startseite</a></p></div></section></main></body></html>
"""

if __name__ == "__main__":
    build()
