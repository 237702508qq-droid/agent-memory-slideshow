#!/usr/bin/env python3
"""Upload deck files to GitHub repo via gh api contents endpoint (PUT per file)."""
import base64
import json
import os
import subprocess
import sys

REPO = "237702508qq-droid/agent-memory-slideshow"
ROOT = "/home/song/agent-memory-deck/slideshow"
INCLUDE = ["index.html", "README.md"]
DIRS = ["composition", "vendor", "assets", "scripts", "qa"]


def gh(args, stdin=None):
    r = subprocess.run(["gh"] + args, capture_output=True, text=True, input=stdin)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {r.stderr[:500]}")
    return r.stdout


def existing_sha(path):
    try:
        out = gh(["api", f"repos/{REPO}/contents/{path}"])
        return json.loads(out).get("sha")
    except RuntimeError:
        return None  # empty repo / not found -> PUT creates
    except Exception:
        return None


def put(path, local):
    size = os.path.getsize(local)
    with open(local, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    args = ["api", "--method", "PUT", f"repos/{REPO}/contents/{path}", "--input", "-"]
    try:
        sha = existing_sha(path)
        body = json.dumps({"message": f"deploy: {path}", "content": b64})
        if sha:
            body = json.dumps({"message": f"update: {path}", "content": b64, "sha": sha})
        gh(args, stdin=body)
        print(f"  ok  {path} ({size}B)")
        return True
    except RuntimeError as e:
        msg = str(e)
        if '"sha" wasn' in msg or "422" in msg:
            try:
                sha = existing_sha(path)
                body = json.dumps({"message": f"update: {path}", "content": b64, "sha": sha})
                gh(args, stdin=body)
                print(f"  ok  {path} ({size}B, retried)")
                return True
            except RuntimeError as e2:
                print(f"  FAIL {path}: {str(e2)[:200]}")
                return False
        print(f"  FAIL {path}: {msg[:200]}")
        return False


def main():
    files = [(f, os.path.join(ROOT, f)) for f in INCLUDE]
    for d in DIRS:
        dp = os.path.join(ROOT, d)
        for fn in sorted(os.listdir(dp)):
            fp = os.path.join(dp, fn)
            if os.path.isfile(fp):
                files.append((f"{d}/{fn}", fp))
    failed = [rel for rel, fp in files if not put(rel, fp)]
    print(f"\nuploaded {len(files) - len(failed)}/{len(files)} files")
    if failed:
        print("FAILED:", failed)
        sys.exit(1)


if __name__ == "__main__":
    main()
