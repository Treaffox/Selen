// Probeabzug Akzente und Stapel im Browser (echte Shaping-Engine).
//   PLAYWRIGHT_DIR=… node tools/accents.mjs out.png
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
const require = createRequire(process.env.PLAYWRIGHT_DIR.replace(/\/?$/, "/"));
const { chromium } = require("playwright");
const D = resolve(new URL("..", import.meta.url).pathname, "dist/variable");
const T = ["Ấ Ầ Ẩ Ẫ Ậ Ắ Ặ Ế Ệ Ố Ộ Ớ Ợ Ứ Ự Ỹ Ỳ Ỷ Ǻ Ǘ Ǚ ǻ ǘ ǚ Ḉ Ṍ Ȫ", "ấầẩẫậắặếệốộớợứựỹỳỷ ǻǘǚ ḉṍ ǭ ǽ ǿ ŉ ŀ", "Ἄ Ἇ Ἣ Ὥ ᾼ ᾍ ᾯ ῷ ἄἇἣὥᾳᾴ ΐ ΰ ῒ", "ѐ ё й ѝ ў Ӓ ӧ ӣ Ӥ ӱ ӳ Ӂ ѣ ђ ћ ѿ", "ç ğ ş ţ ȩ ļ ņ ķ ṣ ẹ ḍ ṭ a̐ e̊ x̂ ĳ ÅÄÖÜ ÁÉÍÓÚ"];
let rows = "";
for (const [w, it] of [[200, 0], [400, 0], [900, 0], [200, 1], [400, 1], [900, 1]]) rows += T.map((t) => `<div style="font-weight:${w};font-style:${it ? "italic" : "normal"}">${t}</div>`).join("") + "<hr>";
const html = `<style>@font-face{font-family:S;src:url(file://${D}/Selen[wght].ttf);font-weight:200 900;font-style:normal}
@font-face{font-family:S;src:url(file://${D}/Selen-Italic[wght].ttf);font-weight:200 900;font-style:italic}
body{font:34px/1.5 S;margin:10px;width:1400px}hr{margin:4px 0}</style>${rows}`;
writeFileSync("/tmp/accents.html", html);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1420, height: 900 } });
await p.goto("file:///tmp/accents.html"); await p.evaluate(() => document.fonts.ready);
await p.screenshot({ path: process.argv[2], fullPage: true }); await b.close();
