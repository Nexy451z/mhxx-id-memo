# -*- coding: utf-8 -*-
"""data/equip の自己検証。extract_equip_tables.py の出力を独立に読み直して検査する。

    python tools/verify_equip_tables.py

検査項目:
  1. 各 CSV が UTF-8 BOM 付き・CR を含まない (改行 LF)
  2. ヘッダーが _manifest.json の columns と完全一致
  3. 1 列目が primary_key
  4. 主キーの重複ゼロ・整数として解釈できる
  5. row_count が実ファイルと一致
  6. id_range が実データの min/max と一致
  7. テーブル間の参照 (外部キー) がすべて解決できる
  8. name_ja / name_en の充足率を表示 (空欄は仕様どおり)
"""
import csv
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "data", "equip")

# (子テーブル, 列, 親テーブル, 親の主キー)
FOREIGN_KEYS = [
    ("items", "material_category_id", "item-categories", "category_id"),
    ("decorations", "item_id", "items", "item_id"),
    ("decorations", "skill1_id", "skills", "skill_id"),
    ("decorations", "skill2_id", "skills", "skill_id"),
    ("armor", "part_id", "armor-parts", "part_id"),
    ("weapons", "weapon_type_id", "weapon-types", "weapon_type_id"),
    ("hunter-arts", "weapon_type_id", "weapon-types", "weapon_type_id"),
    ("armor-skills", "armor_id", "armor", "armor_id"),
    ("armor-skills", "part_id", "armor-parts", "part_id"),
    ("armor-skills", "skill_id", "skills", "skill_id"),
    ("weapon-tree", "weapon_type_id", "weapon-types", "weapon_type_id"),
    ("weapon-tree", "weapon_id", "weapons", "weapon_id"),
    ("weapon-tree", "parent_weapon_id", "weapons", "weapon_id"),
    ("talisman-tables", "skill_id", "skills", "skill_id"),
    ("combinations", "item1_id", "items", "item_id"),
    ("combinations", "item2_id", "items", "item_id"),
    ("combinations", "result_item_id", "items", "item_id"),
]

# name_en が空でよいのは「装備なし」等のプレースホルダ行だけ。
# items は英語版 romfs が無いため全行空 (NOTES 参照) なのでこの検査から外す。
NAME_EN_UNAVAILABLE = {"items", "weapon-types"}
NONE_LABELS = {"装備なし", "なし", "スキル無し", "-----", "1234567890"}

# 空欄を許さない列 (主キー以外)
REQUIRED = {
    # weapon-types は欠番 (weapon_type_id=5, used=no) の行だけ空欄を許す
    "weapon-types": [],
    "weapons": ["name_ja"],
    "armor": ["name_ja"],
    "armor-parts": ["name_ja", "name_en"],
    "items": ["name_ja", "desc_ja"],
    "item-categories": ["name_ja"],
    "decorations": ["name_en", "name_ja"],
    "talismans": ["name_ja"],
    "skills": ["name_ja", "desc_ja"],
    "skill-effects": ["name_ja"],
    "hunter-arts": ["name_ja", "weapon_type_ja"],
    "kinsects": ["name_ja"],
    "palico-weapons": ["name_ja"],
    "palico-armor": ["name_ja"],
    "palico-skills": ["name_ja", "name_en"],
    "palico-support": ["name_ja"],
    "armor-skills": [],
    "weapon-tree": [],
    "talisman-tables": ["kind"],
    "combinations": ["item1_name_ja", "item2_name_ja", "result_name_ja"],
    "smithy-lists": ["list_name", "kind"],
    "palico-actions": ["kind"],
    "palico-levels": [],
}


def load(path):
    with open(path, "rb") as f:
        raw = f.read()
    return raw


def main():
    failures = []
    manifest_path = os.path.join(OUT, "_manifest.json")
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest.get("area") != "equip":
        failures.append("manifest.area != equip")
    tables = {t["id"]: t for t in manifest["tables"]}
    print("manifest: area=%s tables=%d" % (manifest.get("area"), len(tables)))
    print("")

    data = {}
    header_of = {}
    print("%-16s %7s %-16s %-16s %s" % ("table", "rows", "id_range", "pk_unique", "bom/lf/header/pk/first"))
    print("-" * 92)
    for tid in sorted(tables):
        t = tables[tid]
        path = os.path.join(OUT, t["file"])
        if not os.path.exists(path):
            failures.append("%s: file missing" % tid)
            continue
        raw = load(path)
        ok_bom = raw[:3] == b"\xef\xbb\xbf"
        ok_lf = b"\r" not in raw
        if not ok_bom:
            failures.append("%s: no UTF-8 BOM" % tid)
        if not ok_lf:
            failures.append("%s: contains CR" % tid)
        with open(path, encoding="utf-8-sig", newline="") as f:
            r = csv.reader(f)
            header = next(r)
            rows = list(r)
        header_of[tid] = header
        cols = [c["name"] for c in t["columns"]]
        ok_header = header == cols
        if not ok_header:
            failures.append("%s: header != manifest columns" % tid)
        ok_first = header[0] == t["primary_key"]
        if not ok_first:
            failures.append("%s: first column is not the primary key" % tid)
        keys = [row[0] for row in rows]
        ok_unique = len(set(keys)) == len(keys)
        if not ok_unique:
            failures.append("%s: duplicate primary key" % tid)
        try:
            ints = [int(k) for k in keys]
        except ValueError:
            failures.append("%s: primary key is not an integer" % tid)
            ints = []
        if t["row_count"] != len(rows):
            failures.append("%s: row_count %d != actual %d" % (tid, t["row_count"], len(rows)))
        rng = [min(ints), max(ints)] if ints else None
        if t["id_range"] != rng:
            failures.append("%s: id_range %s != actual %s" % (tid, t["id_range"], rng))
        for row in rows:
            if len(row) != len(cols):
                failures.append("%s: ragged row %r" % (tid, row[:2]))
                break
        # SPEC 0-5: 空値は空文字。プレースホルダ文字列が残っていないこと
        for row in rows:
            for value in row:
                if value in ("(None)", "NULL", "null", "None"):
                    failures.append("%s: placeholder value %r" % (tid, value))
                    break
            else:
                continue
            break
        # 空欄チェック
        idx = {c: i for i, c in enumerate(header)}
        for column in REQUIRED.get(tid, []):
            i = idx[column]
            empty = sum(1 for row in rows if row[i] == "")
            if empty:
                failures.append("%s.%s: %d empty cells" % (tid, column, empty))
        if "name_ja" in idx and "name_en" in idx and tid not in NAME_EN_UNAVAILABLE:
            # name_en が空なのは「装備なし」等の行だけであること
            ji, ei2 = idx["name_ja"], idx["name_en"]
            fi = idx.get("form")
            for row in rows:
                if fi is not None and row[fi] != "0":
                    continue        # weapons: 英語名テーブルは form 0 のみ
                if row[ei2] == "" and row[ji] not in NONE_LABELS:
                    failures.append("%s: name_en empty for %r (not a placeholder row)"
                                    % (tid, row[ji]))
                    break
        if tid == "weapon-types":
            # 実在する武器種 (used=yes) の行だけ名前が埋まっていることを要求する
            ui, ni, ei = idx["used"], idx["name_ja"], idx["name_en"]
            for row in rows:
                if row[ui] == "yes" and (row[ni] == "" or row[ei] == ""):
                    failures.append("weapon-types: used row %s has an empty name" % row[0])
                if row[ui] == "no" and (row[ni] != "" or row[ei] != ""):
                    failures.append("weapon-types: unused row %s has a name" % row[0])
        data[tid] = rows
        print("%-16s %7d %-16s %-16s %s" % (
            tid, len(rows), "%s..%s" % (rng[0], rng[1]) if rng else "-",
            "yes" if ok_unique else "NO",
            "%s/%s/%s/%s/%s" % ("ok" if ok_bom else "NG", "ok" if ok_lf else "NG",
                                "ok" if ok_header else "NG", "ok" if ok_first else "NG",
                                "ok" if ok_unique else "NG")))

    # ---- 外部キー ----
    print("")
    print("foreign keys")
    print("-" * 92)
    for child, column, parent, pk in FOREIGN_KEYS:
        if child not in data or parent not in data:
            failures.append("%s.%s: table missing" % (child, column))
            continue
        ci = header_of[child].index(column)
        pi = header_of[parent].index(pk)
        parent_keys = set(row[pi] for row in data[parent])
        values = [row[ci] for row in data[child] if row[ci] != ""]
        bad = [v for v in values if v not in parent_keys]
        print("%-16s %-20s -> %-16s %-12s %s" % (
            child, column, parent, "%d refs" % len(values),
            "ok" if not bad else "UNRESOLVED %d (e.g. %s)" % (len(bad), bad[:3])))
        if bad:
            failures.append("%s.%s: %d unresolved refs" % (child, column, len(bad)))

    # ---- 充足率 ----
    print("")
    print("%-16s %-8s %-10s %-10s" % ("table", "rows", "name_ja", "name_en"))
    print("-" * 92)
    for tid in sorted(data):
        header = header_of[tid]
        rows = data[tid]
        out = [tid, str(len(rows))]
        for column in ("name_ja", "name_en"):
            if column in header:
                i = header.index(column)
                filled = sum(1 for row in rows if row[i] != "")
                out.append("%d%%" % round(100.0 * filled / len(rows)) if rows else "-")
            else:
                out.append("-")
        print("%-16s %-8s %-10s %-10s" % tuple(out))

    print("")
    if failures:
        print("FAIL (%d)" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("PASS: all checks green (%d tables, %d rows)"
          % (len(tables), sum(len(v) for v in data.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
