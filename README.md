# Selen

> **THIS FONT IS VIBE CODED USING CLAUDE CODE**

Humanistische Interface-Sans in der Tradition von Tahoma und Verdana, gebaut
für das TRFX Legacy Design System. Große x-Höhe, offene Bögen, quadratische
Punkte, tabellarische Ziffern. Gewichte von 200 bis 900, aufrecht und kursiv,
Latein, Griechisch und Kyrillisch (2.967 Zeichen). Ausgelegt auf 11 bis 14 px.
Website und Testseite: https://selen.trfx.de

Version und Änderungen: `VERSION`, `CHANGELOG.md`. Lizenz: SIL Open Font
License 1.1 (`LICENSE`), Reserved Font Name „Selen“.

## Dateien

Im Download-Paket liegen die Ordner direkt im Hauptverzeichnis, im
Quell-Repository unter `fonts/`.

| Ordner | Inhalt |
|---|---|
| `variable/` | `Selen[wght].ttf`, `Selen-Italic[wght].ttf`: eine Datei je Stil, alle Gewichte 200–900 |
| `otf/` | 16 statische Schnitte (Desktop, Druck) |
| `ttf/` | 16 statische Schnitte, gehintet (Windows, kleine Größen) |
| `webfonts/` | WOFF2 der Variable Fonts und der statischen Schnitte |

## Im Web einbinden

```css
@font-face {
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
body { font-family: "Selen", Tahoma, Verdana, sans-serif; }
```

Im TRFX Legacy Design System genügt:

```css
:root { --lg-font-text: "Selen", Tahoma, Verdana, sans-serif; --lg-font-head: var(--lg-font-text); }
```

## OpenType-Features

Ziffern sind standardmäßig tabellarisch (`tnum`), proportional mit `pnum`.
Außerdem `lnum`, `onum`, `case`, `frac`, `numr`, `dnom`, `sups`, `subs`,
`sinf`, `ordn`, `smcp`, `c2sc`, `zero`, `salt` (Versal-I mit Serifen, trennt I/l/1), `ss03`, `ss04`, `ss06`, `ss07`, `kern`,
`mark`, `mkmk`.

## Selbst bauen

Die Quellen werden aus Noto Sans abgeleitet und mit fontmake gebaut.
Gebraucht werden Python 3.12 und Git.

```sh
sh tools/fetch_upstream.sh            # Noto Sans in dem Stand, auf dem Selen aufbaut → upstream/noto, work/noto-ufo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python tools/instantiate.py # schmaler Breitenschnitt, Master 200/400/700/900 → work/base
.venv/bin/python tools/build.py       # prepare + fontmake + Hinting + WOFF2 → dist/
.venv/bin/python tools/check.py       # Prüfungen
```

Die Gestaltungsparameter (Breite, Skalierung, Laufweite, Rundungen, Metriken)
stehen in `tools/selen/config.py`. Die Website entsteht mit `tools/site.py`.

## Herkunft und Dank

Selen baut auf **Noto Sans** von The Noto Project Authors auf (OFL 1.1).
Vorbilder für Proportionen und Details waren Tahoma und Verdana (Matthew Carter),
DejaVu Sans, PT Sans (ParaType) und Brom. Outlines aus diesen Schriften sind
nicht enthalten.
