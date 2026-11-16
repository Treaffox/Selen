#!/bin/sh
# Holt die Vorlage von Selen (Noto Sans, Latein/Griechisch/Kyrillisch) in genau dem Stand,
# auf dem die Schrift aufbaut, und wandelt sie mit glyphs2ufo (aus glyphsLib) in UFOs um.
#   sh tools/fetch_upstream.sh
set -eu
cd "$(dirname "$0")/.."
GLYPHS2UFO="${GLYPHS2UFO:-.venv/bin/glyphs2ufo}"
REPO=https://github.com/notofonts/latin-greek-cyrillic.git
COMMIT=ffaec0a756877220dbf718ce08b8479a0be82479
if [ -d upstream/noto/.git ] && [ "$(git -C upstream/noto rev-parse HEAD)" = "$COMMIT" ]; then
  echo "upstream/noto: schon auf $COMMIT"
else
  rm -rf upstream/noto; mkdir -p upstream/noto
  git -C upstream/noto init -q
  git -C upstream/noto remote add origin "$REPO"
  git -C upstream/noto fetch -q --depth 1 origin "$COMMIT"
  git -C upstream/noto checkout -q FETCH_HEAD
fi
rm -rf work/noto-ufo; mkdir -p work/noto-ufo/NotoSans work/noto-ufo/NotoSans-Italic
"$GLYPHS2UFO" -m work/noto-ufo/NotoSans upstream/noto/sources/NotoSans.glyphspackage
"$GLYPHS2UFO" -m work/noto-ufo/NotoSans-Italic upstream/noto/sources/NotoSans-Italic.glyphspackage
echo "Vorlage bereit."
