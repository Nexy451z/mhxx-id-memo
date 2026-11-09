#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: 全行チェック (reviewer).

サンプリングではなく全行を対象に、lead 指定の重点項目を検証する。
  1. stages 31 行: name_ja 空は 10/15 のみか、notes_ja に根拠があるか
  2. monsters 137 行: monster-index.csv / MONSTER_HUNT_NAMES と全一致するか
  3. quests 1508 行: quest_index が一意か、quest_id 重複の扱い
  4. row_id 主キー表: notes_ja に自然キーの説明があるか
"""
import csv
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources as S

REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"
bad = []


def read_csv(path):
    raw = open(path, "rb").read()
    body = raw[3:] if raw[:3] == b"\xef\xbb\xbf" else raw
    rdr = csv.reader(io.StringIO(body.decode("utf-8", errors="replace"), newline=""))
    rows = list(rdr)
    return (rows[0], rows[1:]) if rows else ([], [])


def load_manifest(area):
    p = os.path.join(REPO, "data", area, "_manifest.json")
    return {t["id"]: t for t in json.load(open(p, encoding="utf-8"))["tables"]}


def get_table(area, tid):
    man = load_manifest(area)
    t = man[tid]
    h, rows = read_csv(os.path.join(REPO, "data", area, t["file"]))
    return t, h, rows


def section(name):
    print("\n" + "=" * 78)
    print(name)
    print("=" * 78)


# ---------------------------------------------------------------- 1. stages
section("1. stages 全 31 行")
t, h, rows = get_table("world", "stages")
print("rows=%d  pk=%s" % (len(rows), t["primary_key"]))
i_id, i_ja, i_notes = h.index("stage_id"), h.index("name_ja"), h.index("notes_ja")
empty = [r[i_id] for r in rows if not r[i_ja].strip()]
print("name_ja が空の stage_id:", empty)
if empty != ["10", "15"]:
    bad.append("stages: name_ja 空が 10/15 以外: %s" % empty)
no_notes = [r[i_id] for r in rows if not r[i_notes].strip()]
print("notes_ja が空の stage_id:", no_notes)
if no_notes:
    bad.append("stages: notes_ja が空の行: %s" % no_notes)
# 根拠件数の書式 (n/m 件) を確認
import re
withcount = [r[i_id] for r in rows if re.search(r"\d+\s*/\s*\d+\s*件", r[i_notes])]
print("notes_ja に『n/m 件』形式の根拠がある行: %d / %d" % (len(withcount), len(rows)))
emap = S.questfields().get("ENUM_MAP_", [])
print("ENUM_MAP_ と表記一致: %d / %d" % (
    sum(1 for r in rows if int(r[i_id]) < len(emap) and r[i_ja] == emap[int(r[i_id])]), len(rows)))
print("サンプル notes_ja:")
for r in rows[:3]:
    print("  stage %s: %s" % (r[i_id], r[i_notes][:90]))

# ---------------------------------------------------------------- 2. monsters
section("2. monsters 全 137 行")
t, h, rows = get_table("world", "monsters")
print("rows=%d  pk=%s  id_range=%s" % (len(rows), t["primary_key"], t.get("id_range")))
mi = S.monster_index()
hunt = S.gamedata().get("MONSTER_HUNT_NAMES", [])
i_id, i_ja, i_en = h.index("monster_id"), h.index("name_ja"), h.index("name_en")
m_en, m_ja, m_missing = [], [], []
for r in rows:
    k = int(r[i_id])
    s = mi.get(k)
    if s is None:
        m_missing.append(k)
    elif r[i_en] and r[i_en] != s["monster"]:
        m_en.append((k, s["monster"], r[i_en]))
    exp = hunt[k - 1] if 1 <= k <= len(hunt) else None
    # SPEC §0.1「不明は空文字」: 出典が 不明 / Unknown[...] の行は空で正しい
    if exp is not None and r[i_ja] != exp:
        if exp in ("不明",) or exp.startswith("Unknown[") or exp == "":
            if r[i_ja] != "":
                m_ja.append((k, exp, r[i_ja]))
        else:
            m_ja.append((k, exp, r[i_ja]))
print("monster-index.csv に無い id:", m_missing)
print("name_en 不一致:", len(m_en), m_en[:5])
print("name_ja (MONSTER_HUNT_NAMES[id-1]) 不一致:", len(m_ja), m_ja[:5])
print("name_ja が空の id:", [r[i_id] for r in rows if not r[i_ja].strip()])
if m_missing or m_en or m_ja:
    bad.append("monsters: 不一致あり en=%d ja=%d missing=%d" % (len(m_en), len(m_ja), len(m_missing)))

# ---------------------------------------------------------------- 3. quests
section("3. quests 全 1508 行")
t, h, rows = get_table("world", "quests")
print("rows=%d  pk=%s" % (len(rows), t["primary_key"]))
i_idx, i_qid = h.index("quest_index"), h.index("quest_id")
idxs = [r[i_idx] for r in rows]
qids = [r[i_qid] for r in rows]
print("quest_index 一意: %s (dup=%d)" % (len(set(idxs)) == len(idxs), len(idxs) - len(set(idxs))))
from collections import Counter
c = Counter(qids)
dups = {k: v for k, v in c.items() if v > 1}
print("quest_id の重複: %s" % sorted(dups.items())[:10])
notes = t.get("notes_ja") or ""
print("manifest notes_ja に重複の説明あり: %s" % ("1049" in notes and "1050" in notes))
if len(set(idxs)) != len(idxs):
    bad.append("quests: quest_index が一意でない")
if not ("1049" in notes and "1050" in notes):
    bad.append("quests: quest_id 重複の説明が manifest notes_ja に無い")
# quest-index.csv と quest_index で突合 (quest_id は 1049/1050 が重複するため使わない)
qi = S.ref("quest-index.csv") or []
by_index = {x["index"]: x for x in qi}
mismatch, missing = [], []
for r in rows:
    s = by_index.get(r[i_idx])
    if s is None:
        missing.append(r[i_idx])
    elif s["quest_id"] != r[i_qid]:
        mismatch.append((r[i_idx], s["quest_id"], r[i_qid]))
print("quest-index.csv に index が無い行: %d %s" % (len(missing), missing[:5]))
print("quest_id 不一致: %d %s" % (len(mismatch), mismatch[:5]))
print("quest-index.csv 行数=%d / 本表=%d (差分は 1049/1050 の重複分)" % (len(qi), len(rows)))
if mismatch:
    bad.append("quests: quest_id が quest-index.csv と %d 行不一致" % len(mismatch))

# ---------------------------------------------------------------- 4. row_id
section("4. row_id 主キー表の自然キー説明")
allman = {}
for area in ("equip", "world"):
    for tid, t in load_manifest(area).items():
        allman[tid] = (area, t)
rowid_tables = [(tid, a, t) for tid, (a, t) in allman.items() if t.get("primary_key") == "row_id"]
print("row_id 主キー表: %d" % len(rowid_tables))
for tid, a, t in sorted(rowid_tables):
    notes = t.get("notes_ja") or ""
    # 複合キー/自然キーの説明は言い回しが一定でないので複数の語で判定する
    has = any(w in notes for w in ("自然キー", "複合キー", "重複なし", "元の主キー", "連番 row_id"))
    print("  %-18s notes_ja=%d 字  キー説明=%s" % (tid, len(notes), "あり" if has else "なし"))
    if not has:
        bad.append("row_id 表 %s に自然キーの説明が無い" % tid)
    if not notes.strip():
        bad.append("row_id 表 %s の notes_ja が空" % tid)

# ---------------------------------------------------------------- まとめ
section("まとめ")
if bad:
    for b in bad:
        print("[NG] %s" % b)
    print("\n不合格: %d" % len(bad))
else:
    print("すべて PASS")
sys.exit(1 if bad else 0)
