// Selen – Screenshots aller Abschnitte (hell/dunkel, mehrere Breiten) zur Sichtprüfung.
//   PORT=8080 node site/scripts/shots.mjs OUTDIR
import { createRequire } from "node:module";
// Playwright aus node_modules neben dem Projekt (npm install) oder aus PLAYWRIGHT_DIR.
const require = createRequire(process.env.PLAYWRIGHT_DIR ? process.env.PLAYWRIGHT_DIR.replace(/\/?$/, "/") : import.meta.url);
const { chromium, firefox } = require("playwright");

const BASE = process.env.BASE || `http://localhost:${process.env.PORT || 8080}`;
const OUT = process.argv[2];
const local = !process.env.BASE;
const ids = ["start", "schnitte", "tester", "aktion", "zeichen", "features", "download"];
for (const [type, name] of [[chromium, "chromium"], [firefox, "firefox"]]) {
  const browser = await type.launch();
  for (const scheme of ["light", "dark"]) {
    for (const w of [320, 390, 1280]) {
      if (name === "firefox" && w === 390) continue;
      const ctx = await browser.newContext({ viewport: { width: w, height: w === 1280 ? 900 : 760 }, colorScheme: scheme,
        extraHTTPHeaders: local ? { "X-Forwarded-Proto": "https" } : {} });
      const p = await ctx.newPage();
      await p.goto(BASE + "/", { waitUntil: "networkidle" });
      await p.evaluate(() => document.fonts.ready);
      for (const id of ids) {
        if (id === "top") await p.evaluate(() => window.scrollTo(0, 0));
        else await p.evaluate((i) => document.getElementById(i).scrollIntoView(), id);
        await p.waitForTimeout(120);
        await p.screenshot({ path: `${OUT}/${name}-${scheme}-${w}-${id}.png` });
      }
      await ctx.close();
    }
  }
  await browser.close();
}
console.log("ok");
