#!/usr/bin/env python3
"""Static self-check: island schema / fragment times / island sync / node --check / assets."""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(ROOT, "..", "composition", "index.html")
WRAP = os.path.join(ROOT, "..", "index.html")

ISLAND_RE = re.compile(r'<script type="application/hyperframes-slideshow\+json">(.*?)</script>', re.S)
SCENE_RE = re.compile(r'data-composition-id="([^"]+)"\s+data-start="(\d+)"\s+data-duration="(\d+)"')

errors = []

comp_html = open(COMP, encoding="utf-8").read()
wrap_html = open(WRAP, encoding="utf-8").read()

comp_islands = ISLAND_RE.findall(comp_html)
wrap_islands = ISLAND_RE.findall(wrap_html)
if len(comp_islands) != 1:
    errors.append(f"composition island count = {len(comp_islands)}, expected 1")
if len(wrap_islands) != 1:
    errors.append(f"wrapper island count = {len(wrap_islands)}, expected 1")

comp_island = json.loads(comp_islands[0])
wrap_island = json.loads(wrap_islands[0])
if comp_island != wrap_island:
    errors.append("wrapper island OUT OF SYNC with composition island")

scenes = {}
for cid, start, dur in SCENE_RE.findall(comp_html):
    if cid == "root":
        continue
    scenes[cid] = (int(start), int(dur))

main_slides = comp_island.get("slides", [])
seqs = comp_island.get("slideSequences", [])
seq_ids = {s["id"] for s in seqs}
branch_ids = {sl["sceneId"] for sq in seqs for sl in sq["slides"]}

for sl in main_slides + [sl for sq in seqs for sl in sq["slides"]]:
    if sl["sceneId"] not in scenes:
        errors.append(f"sceneId '{sl['sceneId']}' unresolved")

for sl in main_slides:
    sid = sl["sceneId"]
    if sid in scenes:
        s, d = scenes[sid]
        for t in sl.get("fragments", []):
            if t < s or t > s + d:
                errors.append(f"fragment {t} of {sid} outside [{s},{s+d}]")
for sq in seqs:
    for sl in sq["slides"]:
        sid = sl["sceneId"]
        if sid in scenes:
            s, d = scenes[sid]
            for t in sl.get("fragments", []):
                if t < s or t > s + d:
                    errors.append(f"branch fragment {t} of {sid} outside [{s},{s+d}]")

for sl in main_slides:
    for h in sl.get("hotspots", []):
        if h["target"] not in seq_ids:
            errors.append(f"hotspot '{h['id']}' targets unknown sequence '{h['target']}'")
        for k, v in h.get("region", {}).items():
            if not (0 <= v <= 100):
                errors.append(f"hotspot '{h['id']}' region {k}={v} outside 0-100")

main_ids = {sl["sceneId"] for sl in main_slides}
if main_ids & branch_ids:
    errors.append(f"branch scenes in main line: {main_ids & branch_ids}")

ordered = sorted((scenes[sid][0], scenes[sid][0] + scenes[sid][1], sid) for sid in main_ids if sid in scenes)
prev_end, prev_sid = -1, None
for s, e, sid in ordered:
    if s < prev_end:
        errors.append(f"main-line overlap: {sid} overlaps {prev_sid}")
    prev_end, prev_sid = e, sid

max_end = max(s + d for s, d in scenes.values())
m = re.search(r'data-composition-id="root"[^>]*data-duration="(\d+)"', comp_html)
root_dur = int(m.group(1)) if m else -1
if root_dur < max_end:
    errors.append(f"root duration {root_dur} < last scene end {max_end}")

# node --check inline scripts
SCRIPT_RE = re.compile(r"<script(?![^>]*\bsrc=)(?![^>]*type=\"application/hyperframes-slideshow\+json\")([^>]*)>(.*?)</script>", re.S)
tmp = tempfile.mkdtemp()
n = 0
for path in (COMP, WRAP):
    html = open(path, encoding="utf-8").read()
    for attrs, body in SCRIPT_RE.findall(html):
        if not body.strip():
            continue
        n += 1
        f = os.path.join(tmp, f"inline_{n}.js")
        open(f, "w", encoding="utf-8").write(body)
        r = subprocess.run(["node", "--check", f], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(f"node --check failed: inline script #{n}:\n{r.stderr.strip()}")

# .frag elements must have reveals
frag_els = set(re.findall(r'class="[^"]*\bfrag\b[^"]*"[^>]*id="([^"]+)"', comp_html))
fr_table = re.findall(r'\{ t: ([\d.]+), el: "([^"]+)" \}', comp_html)
table_ids = {eid for _, eid in fr_table}
island_times = sorted(float(t) for sl in main_slides for t in sl.get("fragments", []))
table_times = sorted(float(t) for t, _ in fr_table)
if island_times != table_times:
    errors.append(f"FRAGMENTS table {table_times} != island {island_times}")
missing = frag_els - table_ids
if missing:
    errors.append(f".frag without reveal: {sorted(missing)}")

for img in set(re.findall(r'src="\.\./assets/([^"]+)"', comp_html)):
    if not os.path.isfile(os.path.join(ROOT, "..", "assets", img)):
        errors.append(f"missing asset: {img}")

for e in errors:
    print("ERROR:", e)
if errors:
    sys.exit(1)
print(f"ALL CHECKS PASSED ({len(main_slides)} main slides, {len(seqs)} sequence(s), "
      f"{sum(len(s.get('fragments', [])) for s in main_slides)} fragments, {n} inline scripts node-checked)")
