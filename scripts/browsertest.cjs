/* Browser runtime test — agent-memory slideshow (7 main + 1 branch scene). */
const puppeteer = require("puppeteer-core");
const CHROME = "/tmp/pw-slideshow/chromium-1243/chrome-linux64/chrome";
const BASE = process.env.DECK_URL || "http://127.0.0.1:8792/index.html";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function main() {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    defaultViewport: { width: 1600, height: 900 },
  });
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.log("PAGE-ERROR:", String(e).slice(0, 200)));
  const results = [];
  const ok = (name, cond, extra = "") => results.push([cond ? "PASS" : "FAIL", name, extra]);

  await page.goto(BASE, { waitUntil: "networkidle2", timeout: 60000 });
  await sleep(2500);

  const frame = () => page.frames().find((f) => f.url().includes("composition/index.html"));

  async function activeSlide() {
    return page.evaluate(() => {
      const el = document.querySelector("hyperframes-slideshow");
      const f = el.querySelector("hyperframes-player").iframeElement;
      if (!f || !f.contentDocument) return null;
      const a = f.contentDocument.querySelector(".scene-frame.is-active");
      return a ? a.id : null;
    });
  }
  async function counter() {
    return page.evaluate(() => {
      const el = document.querySelector("hyperframes-slideshow");
      const m = (el.querySelector("[data-hf-chrome]") || { textContent: "" }).textContent.match(/(\d+)\s*\/\s*(\d+)/);
      return m ? { cur: +m[1], total: +m[2] } : null;
    });
  }
  async function fragOpacities(ids) {
    const f = frame();
    return f.evaluate((ids) => ids.map((id) => {
      const el = document.getElementById(id);
      return el ? getComputedStyle(el).opacity : null;
    }), ids);
  }
  async function pressKey(k) { await page.keyboard.press(k); await sleep(650); }
  async function nextUntil(target, max = 40) {
    for (let i = 0; i < max; i++) {
      if ((await activeSlide()) === target) return true;
      await pressKey("ArrowRight");
    }
    return (await activeSlide()) === target;
  }
  async function pill(sel) {
    return page.evaluate((sel) => {
      const el = document.querySelector("hyperframes-slideshow");
      const p = el.querySelector(sel);
      if (!p) return null;
      const r = p.getBoundingClientRect();
      return { x: r.x + r.width / 2, y: r.y + r.height / 2, text: p.textContent.trim().slice(0, 40) };
    }, sel);
  }

  // 1. manifest & timelines
  const manifest = await page.evaluate(() => {
    const p = document.querySelector("hyperframes-player");
    try { return (p.scenes || []).map((s) => s.id || s.compositionId); } catch (e) { return []; }
  });
  ok("8 scenes resolved in player manifest", manifest.length === 8,
    `got ${manifest.length}: ${manifest.join(",")}`);
  const f0 = frame();
  const tlKeys = await f0.evaluate(() => Object.keys(window.__timelines || {}));
  ok("timelines registered (root + 8 scenes)", tlKeys.length === 9, `got ${tlKeys.length}`);

  // 2. slide 1
  ok("slide 1 is p1-cover", (await activeSlide()) === "p1-cover", await activeSlide());
  let c = await counter();
  ok("counter 1/7", c && c.cur === 1 && c.total === 7, JSON.stringify(c));

  // 3. P2 fragments
  await pressKey("ArrowRight");
  ok("slide 2 is p2-problems", (await activeSlide()) === "p2-problems", await activeSlide());
  let op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  ok("p2 entry: only fragment 1 visible", op[0] === "1" && op[1] === "0", JSON.stringify(op));
  await pressKey("ArrowRight");
  op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  ok("p2: fragment 2 revealed", op[1] === "1" && op[2] === "0", JSON.stringify(op));
  await pressKey("ArrowRight");
  await pressKey("ArrowRight");
  op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
  ok("p2: all 4 fragments revealed", op.every((o) => o === "1"), JSON.stringify(op));

  // 4. hotspot -> case-detail branch
  const pill1 = await pill('.hf-hotspot-pill[data-hotspot-target="case-detail"]');
  ok("case-detail pill rendered on p2", !!pill1, JSON.stringify(pill1));
  if (pill1) {
    await page.mouse.click(pill1.x, pill1.y);
    await sleep(1000);
    ok("branch entered: b-cases active", (await activeSlide()) === "b-cases", await activeSlide());
    c = await counter();
    ok("branch counter scoped (1/1)", c && c.cur === 1 && c.total === 1, JSON.stringify(c));
    await pressKey("ArrowLeft");
    ok("prev pops back to p2-problems", (await activeSlide()) === "p2-problems", await activeSlide());
    op = await fragOpacities(["p2-c1", "p2-c2", "p2-c3", "p2-c4"]);
    ok("back returns to held fragment (last: all 4 revealed)", op.every((o) => o === "1"), JSON.stringify(op));
  }

  // 5. in-composition clickable card? (P2 has no clickable card; test on P5->none. skip)
  // walk P3..P7
  ok("nextUntil p3-roots", await nextUntil("p3-roots"), await activeSlide());
  op = await fragOpacities(["p3-r1", "p3-r2", "p3-r3"]);
  ok("p3 entry: first fragment only", op[0] === "1" && op[1] === "0", JSON.stringify(op));
  ok("nextUntil p4-solution", await nextUntil("p4-solution"), await activeSlide());
  ok("nextUntil p5-how", await nextUntil("p5-how"), await activeSlide());
  ok("nextUntil p6-custom", await nextUntil("p6-custom"), await activeSlide());
  ok("nextUntil p7-value", await nextUntil("p7-value"), await activeSlide());
  c = await counter();
  ok("counter 7/7", c && c.cur === 7 && c.total === 7, JSON.stringify(c));
  const t = await f0.evaluate(() => (window.__timelines && window.__timelines.root) ? window.__timelines.root.time() : -1);
  ok("playhead in p7 range [60,70)", t >= 60 && t < 70, `t=${Number(t).toFixed(2)}`);

  // 6. back to slide 1
  for (let i = 0; i < 45; i++) {
    if ((await activeSlide()) === "p1-cover") break;
    await pressKey("ArrowLeft");
  }
  ok("ArrowLeft returns to slide 1", (await activeSlide()) === "p1-cover", await activeSlide());

  await browser.close();
  let fails = 0;
  for (const [st, name, extra] of results) {
    if (st === "FAIL") fails++;
    console.log(`${st}  ${name}${extra ? "   | " + extra : ""}`);
  }
  console.log(fails === 0 ? "\nALL BROWSER TESTS PASSED" : `\n${fails} TEST(S) FAILED`);
  process.exit(fails === 0 ? 0 : 1);
}

main().catch((e) => { console.error(e); process.exit(1); });
