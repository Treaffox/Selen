"""Zentrale Parameter von Selen. Designentscheidungen stehen hier, nicht im Code."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = (ROOT / "VERSION").read_text().strip()
_ma, _mi, _pa = (int(x) for x in VERSION.split("."))
VERSION_MAJOR, VERSION_MINOR = _ma, _mi * 100 + _pa

FAMILY = "Selen"
FILE_STEM = "Selen"
VENDOR_ID = "TRFX"
DESIGNER = "TRFX"
URL = "https://selen.trfx.de"
COPYRIGHT = (
    "Copyright 2026 TRFX (https://selen.trfx.de), with Reserved Font Name \"Selen\". "
    "Based on Noto Sans, Copyright 2022 The Noto Project Authors (https://github.com/notofonts/latin-greek-cyrillic)."
)
LICENSE_DESC = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
                "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"
DESCRIPTION = ("Selen - a humanist interface sans in the tradition of Tahoma and Verdana, "
               "for the TRFX Legacy Design System. Based on Noto Sans.")

BASE = ROOT / "work/base"
SOURCES = ROOT / "sources"
DIST = ROOT / "dist"

# Master: Name -> (wght-Wert der Achse, Laufweitenzuschlag in Einheiten (links+rechts))
MASTERS = {"ExtraLight": 200, "Regular": 400, "Bold": 700, "Black": 900}
TRACK = {"ExtraLight": 18, "Regular": 22, "Bold": 22, "Black": 20}
# Brom-Rundungen, teilweise: Anteil, um den die Anfasser zur Ecke wandern
SQ_CONVEX = 0.16
SQ_CONCAVE = 0.24
ITALIC_ANGLE = -12.0

SCALE = 1.035          # gleichmaessige Vergroesserung: x-Hoehe/Versalhoehe naeher an Tahoma/Verdana
BASE_WIDTH = 91.5      # Designkoordinate der Breite im Noto-Designspace (100 = normal, 89 = 87,5 %)
SQUARE_DOTS = True

WEIGHTS = [(200, "ExtraLight", "ExtraLight"), (300, "Light", "Light"), (400, "Regular", "Regular"), (500, "Medium", "Medium"),
           (600, "SemiBold", "SemiBold"), (700, "Bold", "Bold"), (800, "ExtraBold", "ExtraBold"), (900, "Black", "Black")]
WIN = (1250, 450)

# Zeilenmetrik wie Tahoma/Verdana (Zeilenhoehe 1,25); win-Metriken folgen der Ausdehnung
ASC, DESC = 1000, 250
