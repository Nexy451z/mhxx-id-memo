#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: 再現性 (reviewer).

tools/build.py を実行し、生成物が再現するか (冪等か) を検証する。
事前にハッシュを控え、実行後に比較する。
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

PY = r"C:\Users\haruk\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"

WATCH = [
    "data/index.json",
    "web/data.js",
    "web/mhxx-id-memo.html",
]


def sha(p):
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def snapshot(repo):
    snap = {}
    for rel in WATCH:
        snap[rel] = sha(os.path.join(repo, rel))
    # TSV 全部
    for area in ("equip", "world"):
        d = os.path.join(repo, "data", area)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".tsv"):
                rel = "data/%s/%s" % (area, fn)
                snap[rel] = sha(os.path.join(repo, rel))
    return snap


def run_build(repo):
    bp = os.path.join(repo, "tools", "build.py")
    if not os.path.exists(bp):
        return None, "tools/build.py が存在しない"
    r = subprocess.run([PY, bp], cwd=repo, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--twice", action="store_true", help="2 回実行して冪等性も見る")
    a = ap.parse_args()
    repo = a.repo

    before = snapshot(repo)
    print("=" * 78)
    print("再現性検証: python tools/build.py")
    print("=" * 78)
    print("実行前の生成物: %d 個" % sum(1 for v in before.values() if v))

    rc, out = run_build(repo)
    if rc is None:
        print("[Critical] %s" % out)
        return 1
    print("exit=%s" % rc)
    tail = [l for l in out.splitlines() if l.strip()][-25:]
    for l in tail:
        print("  | %s" % l)

    after = snapshot(repo)
    changed, created, removed = [], [], []
    for k, v in after.items():
        if before.get(k) is None and v is not None:
            created.append(k)
        elif before.get(k) != v:
            changed.append(k)
    for k, v in before.items():
        if v is not None and after.get(k) is None:
            removed.append(k)

    print("-" * 78)
    print("新規生成: %d %s" % (len(created), created[:10]))
    print("内容変化: %d %s" % (len(changed), changed[:10]))
    print("消失:     %d %s" % (len(removed), removed[:10]))

    bad = 0
    if rc != 0:
        print("[Critical] build.py が非 0 終了")
        bad += 1
    if changed:
        print("[Major] build.py 実行で生成物が変化 (= リポジトリ内の生成物が build.py の出力と不一致)")
        bad += 1
    if removed:
        print("[Major] build.py 実行で生成物が消えた")
        bad += 1

    # index.json の内容検証
    ip = os.path.join(repo, "data", "index.json")
    if os.path.exists(ip):
        try:
            idx = json.loads(open(ip, encoding="utf-8").read())
            n = len(idx.get("tables", [])) if isinstance(idx, dict) else len(idx)
            print("index.json: tables=%d" % n)
        except Exception as e:
            print("[Critical] index.json が JSON として不正: %s" % e)
            bad += 1
    else:
        print("[Critical] data/index.json が生成されていない")
        bad += 1

    if a.twice:
        mid = snapshot(repo)
        rc2, out2 = run_build(repo)
        after2 = snapshot(repo)
        diff = [k for k in after2 if mid.get(k) != after2.get(k)]
        print("-" * 78)
        print("2 回目実行: exit=%s, 変化=%d %s" % (rc2, len(diff), diff[:8]))
        if diff:
            print("[Major] build.py が冪等でない (2 回目で出力が変化)")
            bad += 1

    print("-" * 78)
    print("再現性: %s" % ("OK" if bad == 0 else "NG (%d)" % bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
