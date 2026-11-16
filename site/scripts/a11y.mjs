// Selen – Barrierefreiheit mit axe-core (WCAG 2.1 AA), hell und dunkel.
//   PORT=8080 node site/scripts/a11y.mjs
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
// Playwright aus node_modules neben dem Projekt (npm install) oder aus PLAYWRIGHT_DIR.
const require = createRequire(process.env.PLAYWRIGHT_DIR ? process.env.PLAYWRIGHT_DIR.replace(/\/?$/, "/") : import.meta.url);
const { chromium } = require("playwright");
const AXE = readFileSync(process.env.AXE || require.resolve("axe-core/axe.min.js"), "utf8");
const BASE = process.env.BASE || `http://localhost:${process.env.PORT || 8080}`;
const b = await chromium.launch();
let bad = 0;
for (const scheme of ["light"]) {
  for (const w of [390, 1280]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, colorScheme: scheme, bypassCSP: true,
      extraHTTPHeaders: process.env.BASE ? {} : { "X-Forwarded-Proto": "https" } });
    const p = await ctx.newPage();
    await p.goto(BASE + "/", { waitUntil: "networkidle" });
    await p.evaluate(() => document.fonts.ready);
    await p.addScriptTag({ content: AXE });
    const r = await p.evaluate(async () => {
      const res = await axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"] } });
      return res.violations.map((v) => ({ id: v.id, impact: v.impact, n: v.nodes.length, help: v.help, t: v.nodes.slice(0, 3).map((n) => n.target.join(" ") + " :: " + (n.failureSummary || "").split("\n").slice(1, 2).join("")) }));
    });
    console.log(`== ${scheme} ${w}px: ${r.length} Verstöße`);
    for (const v of r) { bad++; console.log(`  [${v.impact}] ${v.id} (${v.n}) ${v.help}`); v.t.forEach((t) => console.log("     ", t.slice(0, 220))); }
    await ctx.close();
  }
}
await b.close();
process.exit(bad ? 1 : 0);
