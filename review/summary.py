#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: テーブル棚卸し (README / docs との突合用)."""
import argparse
import json
import os
import sys

REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    a = ap.parse_args()

    total = 0
    rows_out = []
    for area in ("equip", "world"):
        mp = os.path.join(a.repo, "data", area, "_manifest.json")
        if not os.path.exists(mp):
            print("(no manifest) %s" % mp)
            continue
        man = json.loads(open(mp, encoding="utf-8").read())
        print("=" * 96)
        print("area=%s  tables=%d" % (area, len(man.get("tables", []))))
        print("%-20s %-14s %8s %-14s %-10s %s" % ("id", "file", "rows", "id_range", "conf", "columns"))
        print("-" * 96)
        for t in man.get("tables", []):
            cols = ",".join(c.get("name", "?") for c in (t.get("columns") or []))
            print("%-20s %-14s %8s %-14s %-10s %s"
                  % (t.get("id"), t.get("file"), t.get("row_count"),
                     t.get("id_range"), t.get("confidence"), cols))
            total += t.get("row_count") or 0
            rows_out.append(t)
        print()
    print("総行数: %d / テーブル数: %d" % (total, len(rows_out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
