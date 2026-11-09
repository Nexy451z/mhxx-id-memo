#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: 構造 / manifest 整合 / 捏造 / TSV (reviewer).

使い方:
    python review/verify.py [--repo DIR] [--json OUT.json]

終了コード: 0 = Critical/Major なし, 1 = Critical/Major あり
"""
import argparse
import csv
import glob
import io
import json
import os
import re
import sys

SRC_ROOT = r"C:\anyWorkspace\nx\mhxx"

SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
INT_RE = re.compile(r"^-?(0|[1-9][0-9]*)$")
# 注意: "-" はゲームデータに実在するプレースホルダ (NpcName_jpn.gmd / npc-index.csv) なので除外
BAD_EMPTY = {"NULL", "null", "None", "none", "N/A", "n/a", "nan", "NaN", "undefined", "?", "??", "TBD"}
CONFIDENCE = {"verified", "derived", "curated"}
TYPES = {"int", "str", "float", "bool"}

# 一次資料から確定できる ID 上限 (これを超える id_range は出典外 = 捏造疑い)
KNOWN_BOUNDS = {
    "items": (0, 2990),          # gamedata.rs LAST_ITEM_ID
    "weapon-types": (0, 14),     # HUNT_WEAPONS 15 種 (5 は欠番)
    "monsters": (1, 137),        # 狩猟記録の添字 1..137 / MONSTER_HUNT_NAMES 137 件
    "stages": (1, 104),          # questData .mib +0x14。1..27 + 夜版 101..104
    "skills": (0, 205),          # SKILL_NAMES 206 件
    "kinsects": (0, 31),         # KINSECT_NAMES 32 件
    "talismans": (0, 10),        # EQUIP_TALISMAN_NAMES 11 件
    "hunter-arts": (0, 200),
    "npcs": (1, 999),            # npc_id は連番でない (1..812 + 991..999 等)
    "awards": (0, 131),          # GC_Medal 0..131 が名前
}

findings = []


def add(sev, area, msg, evidence=""):
    findings.append({"severity": sev, "area": area, "message": msg, "evidence": evidence})


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def parse_csv_bytes(raw, path):
    """BOM/改行を検証しつつ (header, rows) を返す。"""
    if raw[:3] == b"\xef\xbb\xbf":
        body = raw[3:]
    else:
        add("Major", "format", "UTF-8 BOM なし", path)
        body = raw
    if b"\r" in body:
        n = body.count(b"\r\n")
        add("Major", "format", "CRLF 改行を検出 (LF 必須)", "%s: CRLF=%d" % (path, n))
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as e:
        add("Critical", "format", "UTF-8 として不正", "%s: %s" % (path, e))
        text = body.decode("utf-8", errors="replace")
    rdr = csv.reader(io.StringIO(text, newline=""))
    rows = [r for r in rdr]
    if not rows:
        add("Critical", "format", "空ファイル", path)
        return [], []
    header = [h.strip() for h in rows[0]]
    body = rows[1:]
    # build.py と同じく末尾の完全空行は落とす
    while body and not any((c or "").strip() for c in body[-1]):
        body.pop()
    return header, body


def check_table(repo, area, tdef, csv_path):
    """1 テーブルの構造検証。"""
    tid = tdef.get("id", "?")
    tag = "%s/%s" % (area, tid)
    if not os.path.exists(csv_path):
        add("Critical", "manifest", "manifest が指す CSV が存在しない", "%s -> %s" % (tag, tdef.get("file")))
        return None

    header, rows = parse_csv_bytes(read_bytes(csv_path), csv_path)

    # ヘッダ検証
    if not header:
        return None
    pk = tdef.get("primary_key")
    if pk is None:
        add("Major", "manifest", "primary_key 未定義", tag)
    elif header[0] != pk:
        add("Major", "structure", "1 列目が primary_key と不一致", "%s: header[0]=%r pk=%r" % (tag, header[0], pk))
    for c in header:
        if not SNAKE.match(c):
            add("Major", "structure", "列名が snake_case ASCII でない", "%s: %r" % (tag, c))
    if len(set(header)) != len(header):
        dup = [c for c in set(header) if header.count(c) > 1]
        add("Major", "structure", "列名重複", "%s: %s" % (tag, dup))

    # manifest columns 突合
    mcols = [c.get("name") for c in (tdef.get("columns") or [])]
    if mcols and mcols != header:
        add("Major", "manifest", "columns が CSV ヘッダと不一致",
            "%s: manifest=%s csv=%s" % (tag, mcols, header))
    for c in (tdef.get("columns") or []):
        if c.get("type") not in TYPES:
            add("Minor", "manifest", "columns[].type が不正", "%s: %s=%r" % (tag, c.get("name"), c.get("type")))

    # 行数
    rc = tdef.get("row_count")
    if rc != len(rows):
        add("Critical", "manifest", "row_count が実ファイルと不一致",
            "%s: manifest=%r actual=%d" % (tag, rc, len(rows)))

    # 主キー重複 / 空
    idx = {h: i for i, h in enumerate(header)}
    if pk in idx:
        pi = idx[pk]
        keys = [r[pi] if pi < len(r) else "" for r in rows]
        if any(k == "" for k in keys):
            add("Critical", "structure", "主キーに空値", "%s: %d 行" % (tag, sum(1 for k in keys if k == "")))
        cnt = {}
        for k in keys:
            cnt[k] = cnt.get(k, 0) + 1
        dups = {k: v for k, v in cnt.items() if v > 1}
        if dups:
            sample = list(dups.items())[:5]
            add("Critical", "structure", "主キー重複", "%s: %d 種 例=%s" % (tag, len(dups), sample))

        # 整数主キー: ゼロ埋め / 範囲
        ints = []
        bad = []
        for k in keys:
            if k == "":
                continue
            if INT_RE.match(k):
                ints.append(int(k))
            else:
                bad.append(k)
        if bad and (tdef.get("columns") or [{}])[0].get("type") == "int":
            add("Major", "structure", "int 主キーに非整数値", "%s: 例=%s" % (tag, bad[:5]))
        if ints:
            lo, hi = min(ints), max(ints)
            rng = tdef.get("id_range")
            if rng is None:
                add("Minor", "manifest", "id_range が null だが主キーは整数", "%s: 実測=[%d, %d]" % (tag, lo, hi))
            elif list(rng) != [lo, hi]:
                add("Critical", "manifest", "id_range が実データと不一致",
                    "%s: manifest=%s actual=[%d, %d]" % (tag, rng, lo, hi))
            b = KNOWN_BOUNDS.get(tid)
            if b and (lo < b[0] or hi > b[1]):
                add("Critical", "fabrication", "ID が一次資料の範囲外",
                    "%s: 実測=[%d, %d] 既知範囲=[%d, %d]" % (tag, lo, hi, b[0], b[1]))

    # 行の列数
    short = [i for i, r in enumerate(rows) if len(r) != len(header)]
    if short:
        add("Critical", "structure", "列数がヘッダと不一致の行",
            "%s: %d 行 例=行番号 %s" % (tag, len(short), [i + 2 for i in short[:5]]))

    # 型検証 / 捏造チェック
    for c in (tdef.get("columns") or []):
        name, typ = c.get("name"), c.get("type")
        if name not in idx:
            continue
        ci = idx[name]
        vals = [r[ci] if ci < len(r) else "" for r in rows]
        if typ == "int":
            bad = [v for v in vals if v != "" and not INT_RE.match(v)]
            if bad:
                add("Major", "structure", "int 列に非整数値", "%s.%s: 例=%s" % (tag, name, bad[:5]))
            padded = [v for v in vals if len(v) > 1 and v.startswith("0")]
            if padded:
                add("Minor", "structure", "int 列にゼロ埋め値", "%s.%s: 例=%s" % (tag, name, padded[:5]))
        elif typ == "bool":
            bad = [v for v in vals if v not in ("", "yes", "no")]
            if bad:
                add("Major", "structure", "bool 列が yes/no 以外", "%s.%s: 例=%s" % (tag, name, bad[:5]))
        elif typ == "float":
            bad = []
            for v in vals:
                if v == "":
                    continue
                try:
                    float(v)
                except ValueError:
                    bad.append(v)
            if bad:
                add("Major", "structure", "float 列に非数値", "%s.%s: 例=%s" % (tag, name, bad[:5]))
        bad_empty = sorted({v for v in vals if v in BAD_EMPTY})
        if bad_empty:
            add("Major", "fabrication", "空値に使ってはいけない文字列", "%s.%s: %s" % (tag, name, bad_empty))

    return {"header": header, "rows": rows, "path": csv_path, "def": tdef}


def check_manifest(repo, area):
    d = os.path.join(repo, "data", area)
    mp = os.path.join(d, "_manifest.json")
    if not os.path.exists(mp):
        add("Critical", "manifest", "_manifest.json が存在しない", d)
        return []
    try:
        man = json.loads(open(mp, encoding="utf-8").read())
    except Exception as e:
        add("Critical", "manifest", "_manifest.json が JSON として不正", "%s: %s" % (mp, e))
        return []
    if man.get("area") != area:
        add("Major", "manifest", "area がディレクトリ名と不一致", "%s: %r" % (mp, man.get("area")))
    tables = man.get("tables")
    if not isinstance(tables, list):
        add("Critical", "manifest", "tables が配列でない", mp)
        return []
    out = []
    for t in tables:
        tid = t.get("id")
        if not tid or not KEBAB.match(tid):
            add("Major", "manifest", "table id が kebab-case でない", "%s: %r" % (area, tid))
        for k in ("title_ja", "file", "primary_key", "confidence"):
            if not t.get(k):
                add("Major", "manifest", "必須キー欠落", "%s/%s: %s" % (area, tid, k))
        if t.get("confidence") not in CONFIDENCE:
            add("Major", "manifest", "confidence が enum 外", "%s/%s: %r" % (area, tid, t.get("confidence")))
        src = t.get("source")
        if not src:
            add("Major", "manifest", "source が空", "%s/%s" % (area, tid))
        elif isinstance(src, list):
            for s in src:
                # "path (定数名)" 形式の注釈と glob を許容して実在確認する
                clean = re.sub(r"\s*\([^)]*\)\s*$", "", str(s)).strip()
                full = os.path.join(SRC_ROOT, clean.replace("/", os.sep))
                if any(ch in clean for ch in "*?["):
                    ok = bool(glob.glob(full))
                else:
                    ok = os.path.exists(full)
                if not ok:
                    add("Minor", "manifest", "source パスが実在しない",
                        "%s/%s: %r (解決先 %s)" % (area, tid, s, full))
        f = t.get("file")
        if f and not os.path.exists(os.path.join(d, f)):
            add("Critical", "manifest", "file が存在しない", "%s/%s: %s" % (area, tid, f))
        out.append(t)

    # manifest に載っていない CSV (孤立ファイル)
    listed = {t.get("file") for t in tables}
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".csv") and fn not in listed:
                add("Major", "manifest", "manifest 未収録の CSV (孤立)", "%s/%s" % (area, fn))
    return out


def check_tsv(repo, area, table, parsed):
    """build.py 生成 TSV が CSV と同内容か (タブ/改行 -> 半角スペース 1 個)。"""
    tid = table.get("id")
    tsv_path = os.path.join(repo, "data", area, os.path.splitext(table["file"])[0] + ".tsv")
    if not os.path.exists(tsv_path):
        add("Major", "tsv", "TSV が存在しない (build.py 未実行 or 出力先違い)", tsv_path)
        return
    raw = read_bytes(tsv_path)
    if raw[:3] != b"\xef\xbb\xbf":
        add("Major", "tsv", "TSV に BOM なし", tsv_path)
        body = raw
    else:
        body = raw[3:]
    if b"\r" in body:
        add("Major", "tsv", "TSV に CRLF", tsv_path)
    text = body.decode("utf-8", errors="replace")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    header, rows = parsed["header"], parsed["rows"]

    _TSV_BAD = re.compile(r"[\t\r\n]+")

    def san(v):
        # build.py の tsv_cell() と同一: 連続するタブ/改行を半角スペース 1 個に
        return _TSV_BAD.sub(" ", v)

    exp = ["\t".join(san(c) for c in header)] + ["\t".join(san(c) for c in r) for r in rows]
    if len(lines) != len(exp):
        add("Major", "tsv", "TSV 行数が CSV と不一致", "%s/%s: tsv=%d csv=%d" % (area, tid, len(lines), len(exp)))
        return
    diffs = []
    for i, (a, b) in enumerate(zip(lines, exp)):
        if a != b:
            diffs.append((i + 1, a[:80], b[:80]))
            if len(diffs) >= 5:
                break
    if diffs:
        add("Major", "tsv", "TSV 内容が CSV と不一致", "%s/%s: %s" % (area, tid, diffs))


def check_index_json(repo, all_tables):
    p = os.path.join(repo, "data", "index.json")
    if not os.path.exists(p):
        add("Critical", "index", "data/index.json が存在しない", p)
        return
    try:
        idx = json.loads(open(p, encoding="utf-8").read())
    except Exception as e:
        add("Critical", "index", "index.json が JSON として不正", "%s: %s" % (p, e))
        return
    # 形は builder 実装依存なので緩く検証
    txt = json.dumps(idx, ensure_ascii=False)
    ids = {t.get("id") for t in all_tables}
    missing = [i for i in ids if i not in txt]
    if missing:
        add("Major", "index", "index.json に未収録のテーブル id", str(missing))
    for t in all_tables:
        if t.get("id") in txt and str(t.get("row_count")) not in txt:
            add("Minor", "index", "index.json に row_count が反映されていない可能性", t.get("id"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo")
    ap.add_argument("--json", default="")
    a = ap.parse_args()
    repo = a.repo

    all_tables = []
    seen_ids = {}
    for area in ("equip", "world"):
        tables = check_manifest(repo, area)
        for t in tables:
            tid = t.get("id")
            if tid in seen_ids:
                add("Critical", "manifest", "table id が area 間で重複", "%s: %s / %s" % (tid, seen_ids[tid], area))
            seen_ids[tid] = area
            all_tables.append(t)
            csv_path = os.path.join(repo, "data", area, t.get("file", ""))
            parsed = check_table(repo, area, t, csv_path)
            if parsed:
                check_tsv(repo, area, t, parsed)

    check_index_json(repo, all_tables)

    # 集計
    order = {"Critical": 0, "Major": 1, "Minor": 2}
    findings.sort(key=lambda f: (order[f["severity"]], f["area"]))
    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    print("=" * 78)
    print("テーブル数: %d  (%s)" % (len(all_tables), ", ".join(sorted(seen_ids))))
    print("指摘: Critical=%d Major=%d Minor=%d" % (counts.get("Critical", 0), counts.get("Major", 0), counts.get("Minor", 0)))
    print("=" * 78)
    for f in findings:
        print("[%s] %-12s %s" % (f["severity"], f["area"], f["message"]))
        if f["evidence"]:
            print("           %s" % f["evidence"])
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"findings": findings, "tables": sorted(seen_ids)}, f, ensure_ascii=False, indent=1)
        print("\nJSON: %s" % a.json)
    return 1 if (counts.get("Critical") or counts.get("Major")) else 0


if __name__ == "__main__":
    sys.exit(main())
