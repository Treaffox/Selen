# Änderungsprotokoll – Selen

Alle nennenswerten Änderungen an der Schrift stehen hier. Versionen folgen
[Semantic Versioning](https://semver.org/lang/de/): MAJOR für Änderungen, die
Satz oder Zeilenhöhe bestehender Texte sichtbar verschieben, MINOR für neue
Zeichen und Funktionen, PATCH für Korrekturen.

## [0.1.1] – 2026-11-16

### Korrigiert
- **Punkte schmaler als der Stamm:** Die quadratischen Punkte (i, j, Satzzeichen, Trema) hatten die Fläche des alten runden Punkts. In schweren Gewichten ist der Stamm aber breiter als diese Fläche, so dass der i-Punkt schmaler war als der Balken darunter (Black, auch Bold und ExtraBold). Jetzt ist jeder einzelne Punkt mindestens so breit wie der Stamm seines Gewichts (Waagrechte Paare wie Trema und Auslassungspunkte mindestens 0,8 Stamm, sonst verschmelzen sie). Vergrößert wird nach oben, der Abstand zum Stamm bleibt. Betrifft alle Zeichen mit Punkten: i, j, ï und alle Akzente mit Punkt, ! ? : ; . … und die Punkte in ɨ, ǰ und Verwandten, aufrecht und kursiv.

## [0.1.0] – 2026-11-16

Erste Version. Humanistische Interface-Sans für das TRFX Legacy Design System,
gedacht als eigener Ersatz für Tahoma (und für „TRFX Sans“ mit DejaVu Sans Condensed).

### Neu
- Gewichte 200 bis 900 (ExtraLight, Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black), aufrecht und kursiv, als Variable Font und als 16 statische Schnitte (OTF, gehintete TTF, WOFF2).
- 2.967 Zeichen: Latein mit Erweiterungen und Vietnamesisch, Griechisch (polytonisch), Kyrillisch.
- Tabellarische Ziffern als Standard (wie Tahoma und Verdana), proportionale Ziffern mit `pnum`.
- Quadratische Punkte auf i, j, Umlauten und Satzzeichen (Tahoma, Verdana, Brom).
- Teilweise gestraffte Rundungen (Brom), moderat, damit Schultern gleichmäßig bleiben.
- Zeilenhöhe 1,25 eingebaut (hhea = typo, USE_TYPO_METRICS), wie Tahoma und Verdana.
- Gehintet mit ttfautohint für 8 bis 48 ppem, ausgelegt auf 11 bis 14 px.

### Herkunft und Abgrenzung
- Konturbasis ist **Noto Sans** (OFL), geschnitten auf 91,5 % Breite und 3,5 % größer skaliert. Die Proportionen orientieren sich an Tahoma und Verdana, das Gerüst an DejaVu Sans und PT Sans, die Rundungen teilweise an Brom.
- DejaVu Sans und PT Sans sind **nicht** als Outline-Quelle verwendet: Die DejaVu-Master (ExtraLight, Book, Bold) sind untereinander nicht interpolierbar, PT Sans hat nur Regular und Bold. Für 200 bis 900 in beiden Stilen brauchte es eine Basis mit durchgehend kompatiblen Mastern.
- Tahoma, Verdana und Brom-Konturen sind nicht enthalten.
