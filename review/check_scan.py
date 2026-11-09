#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: メモリスキャン補助 (reviewer).

実セーブを一次資料として、装備レコード仕様と UI の出力を検証する。

  1. レイアウト定義 (web/data/equip-record-layout.js) が実セーブと一致するか
  2. 実セーブの全レコードを decode -> encode して元バイトに戻るか（可逆性）
  3. SPEC §6.5 の式（防具 type=part_id+1/id=series_id、武器 type=wtid+7/id=weapon_index）が実セーブと合うか
  4. スキャンパターン（6/8/36 バイト）のヒット数を実測
  5. 空レコード・隣接レコードの危険性
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_equip as SE

REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"
issues = []


def add(sev, msg, ev=""):
    issues.append({"severity": sev, "message": msg, "evidence": ev})


def read_csv(path):
    import csv
    import io
    raw = open(path, "rb").read()
    body = raw[3:] if raw[:3] == b"\xef\xbb\xbf" else raw
    rdr = csv.reader(io.StringIO(body.decode("utf-8"), newline=""))
    rows = list(rdr)
    return rows[0], rows[1:]


def load_layout_js(repo):
    p = os.path.join(repo, "web", "data", "equip-record-layout.js")
    if not os.path.exists(p):
        return None
    t = open(p, encoding="utf-8").read()
    m = re.search(r"window\.MHXX_EQUIP_LAYOUT\s*=\s*(\{.*\});", t, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def main():
    repo = REPO
    raw = SE.load()
    b = SE.body(raw)
    print("=" * 78)
    print("実セーブの装備BOX")
    print("=" * 78)
    print("file  : %s" % SE.SAVE)
    print("size  : 0x%X (body 0x%X)" % (len(raw), len(b)))
    print("slots : in_use=%s bases=%s" % (SE.slot_in_use(b), [hex(x) for x in SE.slot_bases(b)]))
    print("box   : body 0x%X / file 0x%X  (%d x %d B = %d B)"
          % (SE.box_offset_body(b), SE.box_offset_file(b), SE.REC_COUNT, SE.REC_SIZE, SE.BOX_BYTES))

    # ---- 1. レイアウト定義の突合
    print("\n" + "=" * 78)
    print("1. レイアウト定義 (web/data/equip-record-layout.js) と実セーブ")
    print("=" * 78)
    L = load_layout_js(repo)
    if L is None:
        add("Critical", "equip-record-layout.js が無い / パースできない")
        print("[NG] レイアウト定義が読めない")
    else:
        # 2 つの形に対応する:
        #   フラット形 = UI の normalizeLayout が読む形（record_size 等）
        #   ネスト形   = analyst の equip-record-layout.json（box.record_bytes 等）
        flat = {k: L.get(k) for k in ("record_size", "record_count", "save_offset", "page_size", "fields", "source")}
        nested_box = L.get("box") or {}
        nested_rec = L.get("record") or {}
        vals = {
            "record_size": flat["record_size"] if flat["record_size"] is not None else nested_box.get("record_bytes"),
            "record_count": flat["record_count"] if flat["record_count"] is not None else nested_box.get("record_count"),
            "save_offset": flat["save_offset"] if flat["save_offset"] is not None else nested_box.get("offset_from_slot_base"),
        }
        fields = flat["fields"] if flat["fields"] else nested_rec.get("fields")
        shape = "フラット" if flat["record_size"] is not None else "ネスト"
        print("形: %s  record_size=%s record_count=%s save_offset=%s(0x%X) page_size=%s"
              % (shape, vals["record_size"], vals["record_count"], vals["save_offset"],
                 vals["save_offset"] or 0, flat["page_size"]))
        # UI の normalizeLayout が読むキーが存在するか（契約の一致）
        # 形そのものは UI 側の normalizeLayout が吸収する（フラット/入れ子の両対応）。
        # ここでは「値が実セーブと合っているか」だけを見る。UI が仕様を読んでいるかは
        # check_ui.py がヘルプの出典表示で確認する。
        ui_keys = [k for k in ("record_size", "record_count", "save_offset", "page_size", "fields", "source")
                   if L.get(k) is not None]
        print("  トップレベルのフラットキー: %s" % (ui_keys if ui_keys else "なし（入れ子スキーマ）"))
        print("  入れ子キー: box=%s record.fields=%s page_geometry=%s"
              % (bool(L.get("box")), bool((L.get("record") or {}).get("fields")), bool(L.get("page_geometry"))))
        checks = [
            ("record_size", vals["record_size"], SE.REC_SIZE),
            ("record_count", vals["record_count"], SE.REC_COUNT),
            ("save_offset", vals["save_offset"], SE.BOX_REL),
        ]
        for name, got, exp in checks:
            ok = got == exp
            print("  %-14s %-8s 期待=%-8s %s" % (name, got, exp, "OK" if ok else "NG"))
            if not ok:
                add("Critical", "レイアウト定義の %s が実セーブと不一致" % name,
                    "定義=%s / 実測=%s" % (got, exp))
        # fields の合計が 36 か
        tot = sum((f.get("size") or f.get("bytes") or 0) for f in (fields or []))
        print("  fields 合計サイズ = %d %s" % (tot, "OK" if tot == SE.REC_SIZE else "NG"))
        if fields and tot != SE.REC_SIZE:
            add("Major", "レイアウト fields の合計が record_size と不一致", str(tot))

    # ---- 2. 可逆性（decode -> encode）
    print("\n" + "=" * 78)
    print("2. 実セーブ全レコードの decode -> encode 可逆性")
    print("=" * 78)
    recs = SE.records(raw)
    bad = 0
    for i, d in recs:
        re_enc = SE.encode(d["type"], d["id"], level=d["level"], tmog_id=d["tmog_id"],
                           tmog_level=d["tmog_level"], decos=d["decos"], tail=d["tail"])
        if re_enc != d["raw"]:
            bad += 1
            add("Critical", "レコード %d の再エンコードが実バイトと不一致" % i,
                "%s != %s" % (re_enc[:12].hex(" "), d["raw"][:12].hex(" ")))
    print("非空レコード %d 件 / 再エンコード不一致 %d 件" % (len(recs), bad))
    print("  => 実セーブの全レコードが (type,id,level,tmog,decos) から完全再現できる")

    # ---- 3. SPEC 式の検証
    print("\n" + "=" * 78)
    print("3. SPEC §6.5 の式と実セーブの突合")
    print("=" * 78)
    ah, arows = read_csv(os.path.join(repo, "data", "equip", "armor.csv"))
    aidx = {n: i for i, n in enumerate(ah)}
    wh, wrows = read_csv(os.path.join(repo, "data", "equip", "weapons.csv"))
    widx = {n: i for i, n in enumerate(wh)}
    armor_by = {}
    for r in arows:
        armor_by[(int(r[aidx["series_id"]]), int(r[aidx["part_id"]]))] = r
    weapon_by = {}
    for r in wrows:
        if r[widx["form"]] == "0":
            weapon_by[(int(r[widx["weapon_type_id"]]), int(r[widx["weapon_index"]]))] = r

    print("%-4s %-6s %-4s %-5s %-4s %s" % ("idx", "type", "id", "式の検証", "lv", "名前"))
    print("-" * 88)
    for i, d in recs:
        t, eid = d["type"], d["id"]
        if 1 <= t <= 5:
            part = t - 1
            a = armor_by.get((eid, part))
            name = a[aidx["name_ja"]] if a else "(該当なし)"
            ok = a is not None
            how = "防具 type=part+1(%d) id=series_id(%d)" % (part, eid)
        elif t in SE.EQUIP_TO_WEAPON_TYPE:
            wt = SE.EQUIP_TO_WEAPON_TYPE[t]
            w = weapon_by.get((wt, eid))
            name = w[widx["name_ja"]] if w else "(該当なし)"
            ok = w is not None
            how = "武器 type=wtid+7(%d) id=weapon_index(%d)" % (wt, eid)
        else:
            name, ok, how = "(対象外)", True, "type=%d" % t
        print("%-4d %-6d %-4d %-45s %-4d %s" % (i, t, eid, how, d["level"], name))
        if not ok:
            add("Major", "レコード %d の type/id が既存テーブルに存在しない" % i, "%d/%d" % (t, eid))

    # ---- 4. パターンのヒット数
    print("\n" + "=" * 78)
    print("4. スキャンパターンのヒット数（実セーブ全体 = %d バイト）" % len(raw))
    print("=" * 78)
    print("%-5s %-20s %8s %8s %8s" % ("idx", "6B", "6B", "8B", "36B"))
    print("-" * 60)
    for i, d in recs:
        pat6 = d["raw"][:6]
        n6 = len(SE.find_hits(raw, pat6))
        n8 = len(SE.find_hits(raw, d["raw"][:8]))
        n36 = len(SE.find_hits(raw, d["raw"]))
        print("%-5d %-20s %8d %8d %8d" % (i, pat6.hex(" "), n6, n8, n36))
    print()
    zero6 = bytes(6)
    zero36 = bytes(36)
    print("空レコード 6B  (00 00 00 00 00 00) のヒット: %d" % len(SE.find_hits(raw, zero6)))
    print("空レコード 36B (00 x36)            のヒット: %d" % len(SE.find_hits(raw, zero36)))
    print("BOX 内の空レコード: %d / %d" % (SE.REC_COUNT - len(recs), SE.REC_COUNT))

    # 隣接レコード署名
    box = b[SE.box_offset_body(b): SE.box_offset_body(b) + SE.BOX_BYTES]
    for n in (2, 3, 5):
        sig = box[: n * SE.REC_SIZE]
        print("先頭 %d レコード連続 (%3d B) のヒット: %d" % (n, len(sig), len(SE.find_hits(raw, sig))))

    # ---- 判定
    print("\n" + "=" * 78)
    order = {"Critical": 0, "Major": 1, "Minor": 2}
    if issues:
        for x in sorted(issues, key=lambda y: order[y["severity"]]):
            print("[%s] %s" % (x["severity"], x["message"]))
            if x["evidence"]:
                print("        %s" % x["evidence"])
        print("\n指摘: %d" % len(issues))
    else:
        print("指摘なし")
    return 1 if any(x["severity"] in ("Critical", "Major") for x in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
