// Selen – Browsertest der Website (Chromium und Firefox).
//   PLAYWRIGHT_DIR=… PORT=8080 node site/scripts/test-site.mjs [Screenshot-Ordner]
//   BASE=https://selen.trfx.de node site/scripts/test-site.mjs
// Ohne BASE: http://localhost:$PORT mit Header X-Forwarded-Proto: https (Container lokal).
import { createRequire } from "node:module";
const require = createRequire(process.env.PLAYWRIGHT_DIR ? process.env.PLAYWRIGHT_DIR.replace(/\/?$/, "/") : import.meta.url);
const { chromium, firefox } = require("playwright");

const BASE = process.env.BASE || `http://localhost:${process.env.PORT || 8080}`;
const SHOTS = process.argv[2] || "";
const local = !process.env.BASE;
let fails = 0, passes = 0;
const ok = (c, m) => { if (c) passes++; else { fails++; console.log("FEHLER:", m); } };

async function run(type, name) {
  const browser = await type.launch();
  for (const [w, h, mobile] of [[1280, 900, false], [390, 844, true], [320, 640, true]]) {
    const ctx = await browser.newContext({
      viewport: { width: w, height: h }, hasTouch: mobile && name === "chromium", isMobile: mobile && name === "chromium",
      extraHTTPHeaders: local ? { "X-Forwarded-Proto": "https" } : {},
    });
    const page = await ctx.newPage();
    const msgs = [];
    page.on("console", (m) => { if (["error", "warning"].includes(m.type())) msgs.push(m.text()); });
    page.on("pageerror", (e) => msgs.push("pageerror: " + e.message));
    page.on("requestfailed", (r) => msgs.push("requestfailed: " + r.url()));
    const res = await page.goto(BASE + "/", { waitUntil: "networkidle" });
    const tag = `${name} ${w}px`;
    ok(res.status() === 200, `${tag}: Startseite ${res.status()}`);
    await page.evaluate(() => document.fonts.ready);
    ok(await page.evaluate(() => document.fonts.check('400 16px "Selen"')), `${tag}: Webfont nicht geladen`);
    const loaded = await page.evaluate(() => [...document.fonts].filter((f) => f.family.includes("Selen") && f.status === "loaded").length);
    ok(loaded >= 1, `${tag}: keine Selen-Fontdatei geladen (${loaded})`);
    ok((await page.evaluate(() => getComputedStyle(document.body).fontFamily)).replace(/"/g, "").startsWith('Selen'), `${tag}: body nicht in Selen`);
    ok(await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth) <= 0, `${tag}: horizontaler Überlauf`);
    ok((await page.title()).includes("Selen"), `${tag}: Titel`);
    // Gewichte: variable Achse wirkt (ExtraLight schmaler als Black)
    const wd = await page.evaluate(() => {
      const m = (wt) => { const s = document.createElement("span"); s.textContent = "Hamburgefonstiv"; s.style.fontSize = "60px";
        s.style.fontWeight = wt; document.body.appendChild(s); const x = s.getBoundingClientRect().width; s.remove(); return x; };
      return [m(200), m(400), m(900)];
    });
    ok(wd[0] < wd[1] && wd[1] < wd[2], `${tag}: Breiten nicht gewichtsabhängig ${wd}`);
    // Ziffern tabellarisch
    const tab = await page.evaluate(() => {
      const m = (t) => { const s = document.createElement("span"); s.textContent = t; s.style.fontSize = "60px";
        document.body.appendChild(s); const x = s.getBoundingClientRect().width; s.remove(); return x; };
      return [m("1111"), m("0000")];
    });
    ok(Math.abs(tab[0] - tab[1]) < 0.5, `${tag}: Ziffern nicht tabellarisch ${tab}`);
    // Tester
    await page.fill("#t-text", "Probe ÄÖÜ");
    await page.evaluate(() => { const r = document.getElementById("t-wght"); r.value = 900; r.dispatchEvent(new Event("input", { bubbles: true })); });
    const st = await page.evaluate(() => { const o = document.getElementById("t-out"); const c = getComputedStyle(o); return [o.textContent, c.fontWeight]; });
    ok(st[0] === "Probe ÄÖÜ" && st[1] === "900", `${tag}: Tester wirkt nicht ${st}`);
    await page.check("#t-italic");
    ok((await page.evaluate(() => getComputedStyle(document.getElementById("t-out")).fontStyle)) === "italic", `${tag}: Kursiv-Schalter`);
    // Glyphen, Download
    ok((await page.locator(".glyph").count()) > 300, `${tag}: zu wenige Glyphen gezeigt`);
    const href = await page.getAttribute("a[download]", "href");
    const zip = await page.request.get(new URL(href, BASE + "/").toString(), { headers: local ? { "X-Forwarded-Proto": "https" } : {} });
    ok(zip.status() === 200 && (await zip.body()).length > 1e6, `${tag}: ZIP ${zip.status()}`);
    // Keine internen Angaben
    const htmlText = await page.content();
    ok(!/\/opt\/|127\.0\.0\.1|treaffox@|@trfx\.de/.test(htmlText), `${tag}: interne Angaben im HTML`);
    ok(msgs.length === 0, `${tag}: Konsole: ${msgs.slice(0, 3).join(" | ")}`);
    if (SHOTS) await page.screenshot({ path: `${SHOTS}/${name}-${w}.png`, fullPage: true });
    await ctx.close();
  }
  await browser.close();
}

await run(chromium, "chromium");
await run(firefox, "firefox");
// Fehlerseite, version.json, Header
const r404 = await fetch(BASE + "/gibt-es-nicht", { headers: local ? { "X-Forwarded-Proto": "https" } : {} });
ok(r404.status === 404, `404: ${r404.status}`);
const hv = await fetch(BASE + "/version.json", { headers: local ? { "X-Forwarded-Proto": "https" } : {} });
ok((await hv.json()).version, "version.json");
const hh = await fetch(BASE + "/", { headers: local ? { "X-Forwarded-Proto": "https" } : {} });
ok((hh.headers.get("content-security-policy") || "").includes("default-src 'none'"), "CSP fehlt");
// Fester Link /latest/: gleiche Adresse, no-cache, CORS offen, richtige Typen, gleiche Version wie version.json
const H = local ? { "X-Forwarded-Proto": "https" } : {};
for (const [f, type] of [["selen.css", "text/css"], ["Selen-VF.woff2", "font/woff2"], ["Selen-Italic-VF.woff2", "font/woff2"], ["version.json", "application/json"], ["Selen-latest.zip", "application/zip"]]) {
  const r = await fetch(`${BASE}/latest/${f}`, { headers: H });
  ok(r.status === 200, `latest/${f}: ${r.status}`);
  ok((r.headers.get("content-type") || "").startsWith(type), `latest/${f}: Typ ${r.headers.get("content-type")}`);
  ok(r.headers.get("access-control-allow-origin") === "*", `latest/${f}: CORS fehlt`);
  ok((r.headers.get("cache-control") || "").includes("no-cache"), `latest/${f}: Cache-Control ${r.headers.get("cache-control")}`);
}
const lv = await (await fetch(`${BASE}/latest/version.json`, { headers: H })).json();
const sv = await (await fetch(`${BASE}/version.json`, { headers: H })).json();
ok(lv.version === sv.version, `latest/version.json ${lv.version} ≠ version.json ${sv.version}`);
const lcss = await (await fetch(`${BASE}/latest/selen.css`, { headers: H })).text();
ok(/font-weight: 200 900/.test(lcss) && lcss.includes("Selen-VF.woff2") && lcss.includes("Selen-Italic-VF.woff2"), "latest/selen.css ohne @font-face");
const lz = await fetch(`${BASE}/latest/Selen-latest.zip`, { headers: H });
ok((await lz.arrayBuffer()).byteLength > 1e6, "latest/Selen-latest.zip zu klein");
console.log(`${passes} von ${passes + fails} Prüfungen bestanden`);
process.exit(fails ? 1 : 0);
