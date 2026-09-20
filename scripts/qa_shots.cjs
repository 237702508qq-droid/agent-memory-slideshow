/* QA screenshots: every main slide + branch at full fragment reveal. */
const puppeteer = require("puppeteer-core");
const CHROME = "/tmp/pw-slideshow/chromium-1243/chrome-linux64/chrome";
const BASE = process.env.DECK_URL || "http://127.0.0.1:8792/index.html";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const FRAG_IDS = {
  "p2-problems": ["p2-c1", "p2-c2", "p2-c3", "p2-c4"],
  "p3-roots": ["p3-r1", "p3-r2", "p3-r3"],
  "p4-solution": ["p4-s1", "p4-s2", "p4-s3", "p4-bar"],
  "p5-how": ["p5-a1", "p5-a2", "p5-a3", "p5-bar"],
  "p6-custom": ["p6-g1", "p6-g2", "p6-g3"],
  "p7-value": ["p7-v1", "p7-v2", "p7-v3", "p7-v4", "p7-bar"],
};

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME, headless: "new",
    args: ["--no-sandbox", "--disable-dev-shm-usage"],
    defaultViewport: { width: 1920, height: 1080 },
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await page.goto(BASE, { waitUntil: "networkidle2", timeout: 60000 });
  await sleep(2500);

  const frame = () => page.frames().find((f) => f.url().includes("composition/index.html"));
  const active = () => page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const f = el.querySelector("hyperframes-player").iframeElement;
    const a = f.contentDocument && f.contentDocument.querySelector(".scene-frame.is-active");
    return a ? a.id : null;
  });
  async function nextUntil(target, max = 45) {
    for (let i = 0; i < max; i++) {
      if ((await active()) === target) return true;
      await page.keyboard.press("ArrowRight");
      await sleep(600);
    }
    return false;
  }
  async function revealAll(sceneId) {
    const ids = FRAG_IDS[sceneId] || [];
    for (let i = 0; i < ids.length + 2; i++) {
      const op = await frame().evaluate((ids) => ids.map((id) => {
        const el = document.getElementById(id);
        return el ? getComputedStyle(el).opacity : "1";
      }), ids);
      if (!op.includes("0")) break;
      if ((await active()) !== sceneId) break;
      await page.keyboard.press("ArrowRight");
      await sleep(600);
    }
  }
  const shot = (n) => page.screenshot({ path: `qa/${n}.png` });

  await sleep(1200);
  await shot("slide01-cover");
  for (const [i, sid] of ["p2-problems", "p3-roots", "p4-solution", "p5-how", "p6-custom", "p7-value"].entries()) {
    await nextUntil(sid);
    await revealAll(sid);
    await sleep(700);
    await shot(`slide0${i + 2}-${sid.replace("p", "").split("-")[0]}`);
  }
  // branch via pill on p2
  for (let i = 0; i < 45; i++) {
    if ((await active()) === "p1-cover") break;
    await page.keyboard.press("ArrowLeft");
    await sleep(450);
  }
  await nextUntil("p2-problems");
  await revealAll("p2-problems");
  const c = await page.evaluate(() => {
    const el = document.querySelector("hyperframes-slideshow");
    const p = el.querySelector('.hf-hotspot-pill[data-hotspot-target="case-detail"]');
    if (!p) return null;
    const r = p.getBoundingClientRect();
    return { x: r.x + r.width / 2, y: r.y + r.height / 2 };
  });
  if (c) {
    await page.mouse.click(c.x, c.y);
    await sleep(1200);
    await shot("branch-cases");
  }
  await browser.close();
  console.log("QA screenshots saved");
})().catch((e) => { console.error(e); process.exit(1); });
