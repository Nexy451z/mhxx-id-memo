# -*- coding: utf-8 -*-
"""装備ボックスレコードの配置仕様を実セーブで検証し、equip-record-layout.json を生成する。

    python tools/verify_equip_record_layout.py            # 検証のみ
    python tools/verify_equip_record_layout.py --json     # 検証 + JSON 再生成

仕様 (LAYOUT) はこのファイルが単一の情報源。JSON はここから書き出し、
.md は人間向けの説明として別に置いてある。

出典:
  mhnxeditor/crates/mhnx-core/src/equip.rs        (レコード 36 B / 2000 枠 / head word のビット割り)
  mhnxeditor/crates/mhnx-core/src/charm.rs        (護石レコードの各バイト)
  mhnxeditor/crates/mhnx-core/src/save.rs         (OFF_EQUIPMENT_BOX = 0x62EE ほか)
  mhnxeditor/crates/mhnx-core/src/hbedit.rs       (一覧のスクロールモデル / page_move)
  mhnxeditor/crates/mhnx-core/tests/scroll_ui.rs  (装備ボックスの 1 画面 = 9 行)
  mhnxeditor/.work/finalaudit/refsrc/docs/07-equipment.md
  mhnxeditor_docs_backup/review_save_layout.md
"""
import argparse
import csv
import json
import os
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.dirname(ROOT)                     # C:\anyWorkspace\nx\mhxx
DATA = os.path.join(ROOT, "data", "equip")
JSON_OUT = os.path.join(DATA, "equip-record-layout.json")

# ---------------------------------------------------------------- 仕様

RECORD_BYTES = 36
RECORD_COUNT = 2000
BOX_BYTES = RECORD_BYTES * RECORD_COUNT          # 72,000
OFF_BOX = 0x62EE
OFF_PALICO_BOX = 0x17C2E
SAVE_HEADER = 36
SLOT_BASE_PTRS = (0x10, 0x14, 0x18)
SLOT_DATA_SIZE = 0x11D088
SLOT_FOOTER = 0x1738

# 装備ボックスの 1 画面 (エディタの一覧) = 9 行。
# hbedit.rs の page_move の doc コメント「the equipment box shows nine and a
# warning strip takes one」と、tests/scroll_ui.rs の
# 「The track the equipment box uses: nine 56px rows.」(TRACK = 504 = 9 * 56)
# および「Nine rows on screen means nine rows a page」が根拠。
SLOTS_PER_PAGE = 9
ROW_HEIGHT_PX = 56
SCROLL_TRACK_PX = SLOTS_PER_PAGE * ROW_HEIGHT_PX
PAGE_COUNT = (RECORD_COUNT + SLOTS_PER_PAGE - 1) // SLOTS_PER_PAGE

# type -> 何を指すか。id から引く表と式。
TYPE_MAP = [
    {"type": 0, "kind": "empty", "table": None, "id_formula": None,
     "desc_ja": "空き枠。レコード 36 バイトがすべて 0"},
    {"type": 1, "kind": "armor", "part_id": 0, "table": "armor.csv",
     "id_formula": "armor_id = id * 5 + 0", "desc_ja": "防具（頭）"},
    {"type": 2, "kind": "armor", "part_id": 1, "table": "armor.csv",
     "id_formula": "armor_id = id * 5 + 1", "desc_ja": "防具（胴）"},
    {"type": 3, "kind": "armor", "part_id": 2, "table": "armor.csv",
     "id_formula": "armor_id = id * 5 + 2", "desc_ja": "防具（腕）"},
    {"type": 4, "kind": "armor", "part_id": 3, "table": "armor.csv",
     "id_formula": "armor_id = id * 5 + 3", "desc_ja": "防具（腰）"},
    {"type": 5, "kind": "armor", "part_id": 4, "table": "armor.csv",
     "id_formula": "armor_id = id * 5 + 4", "desc_ja": "防具（脚）"},
    {"type": 6, "kind": "talisman", "table": "talismans.csv",
     "id_formula": None,
     "desc_ja": "護石。id は使わず +0x0C 以降の護石ブロックを見る"},
]
for _t in range(7, 22):
    if _t == 12:
        TYPE_MAP.append({"type": 12, "kind": "unused", "table": None, "id_formula": None,
                         "desc_ja": "未使用（weapon_type_id 5 の欠番に対応）"})
    else:
        _wt = _t - 7
        TYPE_MAP.append({"type": _t, "kind": "weapon", "weapon_type_id": _wt,
                         "table": "weapons.csv",
                         "id_formula": "weapon_id = (type - 7) * 10000 + id * 10 (form 0)",
                         "desc_ja": "武器（weapon_type_id %d）" % _wt})

FIELDS = [
    {"offset": 0x00, "size": 2, "type": "u16le", "name": "head",
     "desc_ja": "type / level-1 / transmog_level-1 を 5 ビットずつ詰めたワード",
     "desc_en": "Packed word: type, level-1, transmog level-1", "confidence": "verified"},
    {"offset": 0x02, "size": 2, "type": "u16le", "name": "id",
     "desc_ja": "武器/防具の ID。防具は series_id、武器は武器種ごとの weapon_index。護石では未使用（0）",
     "desc_en": "Armour series id or per-class weapon index", "confidence": "verified"},
    {"offset": 0x04, "size": 2, "type": "u16le", "name": "transmog_id",
     "desc_ja": "着せ替え（重ね着）元の装備 ID。0 = なし",
     "desc_en": "Transmog (layered) id, 0 = none", "confidence": "verified"},
    {"offset": 0x06, "size": 2, "type": "u16le", "name": "deco1",
     "desc_ja": "装飾品 1 のアイテム ID（2638..2899）。0 = 空き",
     "desc_en": "Decoration 1 item id, 0 = empty", "confidence": "verified"},
    {"offset": 0x08, "size": 2, "type": "u16le", "name": "deco2",
     "desc_ja": "装飾品 2 のアイテム ID。0 = 空き",
     "desc_en": "Decoration 2 item id, 0 = empty", "confidence": "verified"},
    {"offset": 0x0A, "size": 2, "type": "u16le", "name": "deco3",
     "desc_ja": "装飾品 3 のアイテム ID。0 = 空き",
     "desc_en": "Decoration 3 item id, 0 = empty", "confidence": "verified"},
    {"offset": 0x0C, "size": 24, "type": "bytes", "name": "tail",
     "desc_ja": "type ごとの追加データ。type 6 = 護石ブロック、type 20 = 猟虫ブロック。"
                "それ以外の type では通常 0 だが、前の持ち主のバイトが残ることがある（下記 unknown 参照）",
     "desc_en": "Type specific tail: talisman block (6), kinsect block (20)", "confidence": "verified"},
]

HEAD_BITS = [
    {"bits": "0..4", "mask": "0x001F", "shift": 0, "name": "type",
     "desc_ja": "種類。0 が空き、1..5 が防具、6 が護石、7..21 が武器（12 は未使用）"},
    {"bits": "5..9", "mask": "0x03E0", "shift": 5, "name": "level_minus_1",
     "desc_ja": "強化レベル - 1（0 始まり）。読むときは +1 する"},
    {"bits": "10..14", "mask": "0x7C00", "shift": 10, "name": "transmog_level_minus_1",
     "desc_ja": "着せ替え元のレベル - 1。着せ替えしていないレコードでは 0（= Lv1）"},
    {"bits": "15", "mask": "0x8000", "shift": 15, "name": "unused",
     "desc_ja": "未使用。実セーブ 2,331 レコードで 1 度も立っていない"},
]

TALISMAN_FIELDS = [
    {"offset": 0x00, "size": 1, "type": "u8", "name": "type",
     "desc_ja": "常に 0x06（= type 6, level 1）", "observed": "650/650 が 0x06"},
    {"offset": 0x01, "size": 1, "type": "u8", "name": "zero",
     "desc_ja": "常に 0x00", "observed": "650/650 が 0x00"},
    {"offset": 0x02, "size": 1, "type": "u8", "name": "kind",
     "desc_ja": "護石の種類 (amuletData_jpn.gmd の行, 1..10)。0 も 2 件観測されている",
     "observed": "0:2, 4:2, 6:20, 7:46, 10:580"},
    {"offset": 0x03, "size": 1, "type": "u8", "name": "zero",
     "desc_ja": "常に 0x00", "observed": "650/650 が 0x00"},
    {"offset": 0x04, "size": 2, "type": "u16le", "name": "unused",
     "desc_ja": "常に 0（武器/防具の transmog_id にあたる位置だが護石では使わない）",
     "observed": "650/650 が 0"},
    {"offset": 0x06, "size": 6, "type": "3 x u16le", "name": "deco1..deco3",
     "desc_ja": "護石に挿した装飾品のアイテム ID。武器/防具と同じ位置・同じ意味",
     "observed": "15/650 が非 0。非 0 の個数は +0x10 のスロット数を超えない"},
    {"offset": 0x0C, "size": 1, "type": "u8", "name": "skill1_id",
     "desc_ja": "スキル 1 のスキル ID (skills.csv の skill_id)。0 = なし",
     "observed": "全件が skills.csv に存在"},
    {"offset": 0x0D, "size": 1, "type": "u8", "name": "skill2_id",
     "desc_ja": "スキル 2 のスキル ID。0 = なし", "observed": "全件が skills.csv に存在"},
    {"offset": 0x0E, "size": 1, "type": "i8", "name": "skill1_points",
     "desc_ja": "スキル 1 のポイント（符号あり）", "observed": "実測 -3..+10"},
    {"offset": 0x0F, "size": 1, "type": "i8", "name": "skill2_points",
     "desc_ja": "スキル 2 のポイント（符号あり）", "observed": "実測 -3..+10"},
    {"offset": 0x10, "size": 1, "type": "u8", "name": "slots",
     "desc_ja": "この護石の装飾品スロット数 (0..3)", "observed": "0:32, 1:10, 2:18, 3:590"},
    {"offset": 0x11, "size": 1, "type": "u8", "name": "zero",
     "desc_ja": "常に 0x00", "observed": "650/650 が 0x00"},
    {"offset": 0x12, "size": 1, "type": "u8", "name": "rarity",
     "desc_ja": "レア度 (97..100)。護石アイテム ID の下位バイト",
     "observed": "98:2, 99:68, 100:580"},
    {"offset": 0x13, "size": 1, "type": "u8", "name": "one",
     "desc_ja": "常に 0x01。+0x12 と合わせて u16 で護石アイテム ID (353..356) になる",
     "observed": "650/650 が 0x01"},
    {"offset": 0x14, "size": 16, "type": "bytes", "name": "zero",
     "desc_ja": "常に 0", "observed": "650/650 が全 0"},
]

KIND_RARITY = {1: 97, 2: 97, 3: 98, 4: 98, 5: 99, 6: 99, 7: 99, 8: 100, 9: 100, 10: 100}

SAVES = [
    {"key": "live", "path": os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Ryujinx",
                                         "bis", "user", "save", "0000000000000001", "0", "system"),
     "role_ja": "実機相当の現行セーブ（Ryujinx のセーブ）",
     "expect_used_slot0": 19},
    {"key": "sample", "path": os.path.join(WORK, "save_backups", "_conv", "system"),
     "role_ja": "サンプルセーブ（3 キャラすべてに装備あり。護石 650 件の検証に使う）",
     "expect_used_slot0": 789},
]


# ---------------------------------------------------------------- 読み込み

def read_csv(name):
    with open(os.path.join(DATA, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def load_save(path):
    with open(path, "rb") as f:
        raw = f.read()
    return raw, raw[SAVE_HEADER:]


def slot_bases(body):
    return [struct.unpack_from("<I", body, o)[0] for o in SLOT_BASE_PTRS]


def decode(rec):
    head = struct.unpack_from("<H", rec, 0)[0]
    return {
        "type": head & 0x1F,
        "level": ((head >> 5) & 0x1F) + 1,
        "transmog_level": ((head >> 10) & 0x1F) + 1,
        "bit15": (head >> 15) & 1,
        "id": struct.unpack_from("<H", rec, 2)[0],
        "transmog_id": struct.unpack_from("<H", rec, 4)[0],
        "decos": [struct.unpack_from("<H", rec, 6 + 2 * k)[0] for k in range(3)],
    }


def iter_records(body, base):
    box = base + OFF_BOX
    for i in range(RECORD_COUNT):
        rec = body[box + i * RECORD_BYTES: box + (i + 1) * RECORD_BYTES]
        if any(rec):
            yield i, rec


# ---------------------------------------------------------------- 検証

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="equip-record-layout.json を書き出す")
    args = ap.parse_args(argv)

    failures = []

    def check(ok, label, detail=""):
        print("  %-4s %s%s" % ("ok" if ok else "FAIL", label, ("  " + detail) if detail else ""))
        if not ok:
            failures.append(label + (" / " + detail if detail else ""))

    armor = {r["armor_id"]: r for r in read_csv("armor.csv")}
    weapons = {r["weapon_id"]: r for r in read_csv("weapons.csv") if r["form"] == "0"}
    skills = {r["skill_id"] for r in read_csv("skills.csv")}
    deco_items = {r["item_id"] for r in read_csv("decorations.csv")}

    # 防具のスロット数 (armorSeriesData.asd の +108+part)
    asd_path = os.path.join(WORK, "romfs", "nativeNX", "table", "armorSeriesData.asd")
    asd = None
    if os.path.exists(asd_path):
        with open(asd_path, "rb") as f:
            b = f.read()
        n = struct.unpack_from("<I", b, 4)[0]
        asd = [b[8 + 127 * k: 8 + 127 * (k + 1)] for k in range(n)]

    print("== 仕様の算術")
    check(BOX_BYTES == 72000, "2000 x 36 = 72,000")
    check(OFF_BOX + BOX_BYTES == OFF_PALICO_BOX, "0x62EE + 72,000 = 0x17C2E (オトモ装備ボックスの開始)")
    check(PAGE_COUNT == 223, "ceil(2000 / 9) = 223 ページ")
    check(PAGE_COUNT * SLOTS_PER_PAGE - RECORD_COUNT == 7, "最終ページは 2 枠 (9*223 - 2000 = 7 の余り)")

    verification = {"saves": [], "checks": []}
    totals = {"records": 0, "by_type": {}, "talismans": 0, "with_decos": 0}

    for spec in SAVES:
        path = spec["path"]
        print("")
        print("== %s (%s)" % (spec["key"], path))
        if not os.path.exists(path):
            check(False, "セーブが見つからない", path)
            continue
        raw, body = load_save(path)
        check(len(raw) == 4726188, "ファイルサイズ 4,726,188 B", str(len(raw)))
        check(len(body) == len(raw) - SAVE_HEADER, "body = ファイルサイズ - 36")
        bases = slot_bases(body)
        check(all(bases[i] < bases[i + 1] for i in range(len(bases) - 1)),
              "slot base が昇順", ", ".join(hex(x) for x in bases))
        check(all(base + OFF_PALICO_BOX <= len(body) for base in bases),
              "全スロットの装備ボックスが body 内に収まる")
        if len(bases) > 1:
            check(bases[1] - bases[0] == SLOT_DATA_SIZE + SLOT_FOOTER,
                  "slot stride = 0x11D088 + 0x1738", hex(bases[1] - bases[0]))

        save_info = {"key": spec["key"], "path": path, "role_ja": spec["role_ja"],
                     "size_bytes": len(raw), "slot_bases_hex": [hex(x) for x in bases],
                     "slots": []}
        for si, base in enumerate(bases):
            used = 0
            by_type = {}
            talismans = 0
            with_decos = 0
            names_ok = 0
            names_bad = []
            tal_bad = []
            deco_bad = []
            armor_deco_bad = []
            bit15 = 0
            for i, rec in iter_records(body, base):
                d = decode(rec)
                t = d["type"]
                used += 1
                by_type[t] = by_type.get(t, 0) + 1
                totals["by_type"][t] = totals["by_type"].get(t, 0) + 1
                if d["bit15"]:
                    bit15 += 1
                if t == 6:
                    talismans += 1
                    totals["talismans"] += 1
                    if rec[0] != 6 or rec[1] != 0 or rec[0x11] != 0 or rec[0x13] != 1:
                        tal_bad.append((si, i, "fixed byte"))
                    if rec[0x12] not in (97, 98, 99, 100):
                        tal_bad.append((si, i, "rarity %d" % rec[0x12]))
                    charm_item = struct.unpack_from("<H", rec, 0x12)[0]
                    if not (353 <= charm_item <= 356):
                        tal_bad.append((si, i, "charm item %d" % charm_item))
                    for off in (0x0C, 0x0D):
                        if rec[off] and str(rec[off]) not in skills:
                            tal_bad.append((si, i, "skill %d" % rec[off]))
                    if sum(1 for x in d["decos"] if x) > rec[0x10]:
                        tal_bad.append((si, i, "decos > slots"))
                elif 1 <= t <= 5:
                    aid = str(d["id"] * 5 + (t - 1))
                    if aid in armor:
                        names_ok += 1
                    else:
                        names_bad.append((si, i, t, d["id"]))
                    if asd is not None and d["id"] < len(asd):
                        slots = asd[d["id"]][108 + (t - 1)]
                        if sum(1 for x in d["decos"] if x) > slots:
                            armor_deco_bad.append((si, i, t, d["id"], slots))
                elif 7 <= t <= 21:
                    wid = str((t - 7) * 10000 + d["id"] * 10)
                    if wid in weapons:
                        names_ok += 1
                    else:
                        names_bad.append((si, i, t, d["id"]))
                elif t != 0:
                    names_bad.append((si, i, t, d["id"]))
                if any(d["decos"]):
                    with_decos += 1
                    totals["with_decos"] += 1
                    for v in d["decos"]:
                        if v and str(v) not in deco_items:
                            deco_bad.append((si, i, v))
            totals["records"] += used
            check(12 not in by_type, "slot %d: type 12 は現れない" % si)
            check(bit15 == 0, "slot %d: head word の bit15 は立たない" % si,
                  "%d レコード" % used)
            check(not names_bad, "slot %d: type/id が全て名前表に解決" % si,
                  "%d/%d 件" % (names_ok, used) if not names_bad else str(names_bad[:3]))
            check(not tal_bad, "slot %d: 護石ブロックの不変条件" % si,
                  "%d 件の護石" % talismans if not tal_bad else str(tal_bad[:3]))
            check(not deco_bad, "slot %d: 装飾品 ID が decorations.csv に解決" % si,
                  "%d レコードに装飾品" % with_decos if not deco_bad else str(deco_bad[:3]))
            check(not armor_deco_bad, "slot %d: 防具の装飾品数 <= armorSeriesData のスロット数" % si,
                  "" if not armor_deco_bad else str(armor_deco_bad[:3]))
            if spec["key"] == "live" and si == 0:
                check(used == spec["expect_used_slot0"],
                      "slot 0 の使用レコード数 = %d" % spec["expect_used_slot0"], str(used))
                check(sorted(by_type) == [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21],
                      "slot 0 の type 集合 = 防具 5 部位 + 武器 14 種")
            save_info["slots"].append({
                "slot": si, "base_hex": hex(base), "box_offset_hex": hex(base + OFF_BOX),
                "used": used, "talismans": talismans, "with_decorations": with_decos,
                "by_type": {str(k): v for k, v in sorted(by_type.items())},
            })
        verification["saves"].append(save_info)

    # ---- ページ幾何 ----
    print("")
    print("== ページ幾何")
    covered = 0
    for p in range(PAGE_COUNT):
        lo = p * SLOTS_PER_PAGE
        hi = min(lo + SLOTS_PER_PAGE, RECORD_COUNT)
        if p == PAGE_COUNT - 1:
            check(hi - lo == 2, "最終ページ (%d) は 2 枠" % p, "%d..%d" % (lo, hi - 1))
        covered += hi - lo
    check(covered == RECORD_COUNT, "全ページで 0..1999 を重複なく覆う", str(covered))

    # ---- 現行セーブの 19 レコード ----
    print("")
    print("== 現行セーブ (live) の 19 レコード")
    live = next((s for s in verification["saves"] if s["key"] == "live"), None)
    detail = []
    if live:
        raw, body = load_save(SAVES[0]["path"])
        base = slot_bases(body)[0]
        print("  %-4s %-5s %-6s %-4s %-4s %-6s %s" % ("idx", "type", "id", "lv", "tlv", "deco", "name"))
        for i, rec in iter_records(body, base):
            d = decode(rec)
            t = d["type"]
            if 1 <= t <= 5:
                row = armor.get(str(d["id"] * 5 + (t - 1)), {})
                table = "armor.csv"
            elif 7 <= t <= 21:
                row = weapons.get(str((t - 7) * 10000 + d["id"] * 10), {})
                table = "weapons.csv"
            else:
                row = {}
                table = None
            name = row.get("name_ja", "")
            en = row.get("name_en", "")
            print("  %-4d %-5d %-6d %-4d %-4d %-6s %s %s" % (
                i, t, d["id"], d["level"], d["transmog_level"],
                ",".join(str(x) for x in d["decos"]), name, en))
            detail.append({"index": i, "type": t, "id": d["id"], "level": d["level"],
                           "transmog_id": d["transmog_id"], "transmog_level": d["transmog_level"],
                           "decorations": d["decos"], "table": table,
                           "name_ja": name, "name_en": en})
        check(all(x["name_ja"] for x in detail), "19 レコードすべてに名前が付く")

    # ---- まとめ ----
    print("")
    print("== 合計")
    print("  使用レコード: %d / 護石: %d / 装飾品付き: %d" % (
        totals["records"], totals["talismans"], totals["with_decos"]))
    print("  type 別: %s" % ", ".join("%d:%d" % (k, v) for k, v in sorted(totals["by_type"].items())))

    verification["checks"] = [] if not failures else failures
    verification["totals"] = {
        "records": totals["records"],
        "talismans": totals["talismans"],
        "with_decorations": totals["with_decos"],
        "by_type": {str(k): v for k, v in sorted(totals["by_type"].items())},
    }

    if args.json:
        doc = build_json(verification, detail)
        with open(JSON_OUT, "w", encoding="utf-8", newline="") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=False)
            f.write("\n")
        print("")
        print("  wrote %s" % JSON_OUT)

    print("")
    if failures:
        print("FAIL (%d)" % len(failures))
        for f in failures:
            print("  - " + f)
        return 1
    print("PASS: 装備ボックスレコードの配置仕様は実セーブと矛盾しない")
    return 0


def build_json(verification, detail):
    return {
        "schema": "mhxx-id-memo/equip-record-layout",
        "schema_version": 1,
        "title_ja": "MHXX 装備ボックスレコード配置仕様",
        "game": "Monster Hunter XX (Nintendo Switch)",
        "generated_by": "tools/verify_equip_record_layout.py --json",
        "confidence": "verified",
        "summary_ja": "装備ボックスは 1 レコード 36 バイト x 2000 枠。先頭 2 バイトのワードに type と 2 つのレベルが"
                      "5 ビットずつ入り、+0x02 が ID、+0x04 が着せ替え、+0x06/+0x08/+0x0A が装飾品 3 枠。"
                      "type 6 と type 20 だけ +0x0C 以降に独自のブロックを持つ。",
        "save_file": {
            "size_bytes": 4726188,
            "header_bytes": SAVE_HEADER,
            "body_offset": SAVE_HEADER,
            "body_bytes": 4726152,
            "header_note_ja": "先頭 36 バイトは Switch のセーブヘッダ。装備ボックスの位置は body 先頭からの相対値で持つ",
            "slot_base_pointer_offsets": ["0x%02X" % o for o in SLOT_BASE_PTRS],
            "slot_base_pointer_type": "u32le",
            "slot_count": 3,
            "slot_data_size_hex": "0x%X" % SLOT_DATA_SIZE,
            "slot_footer_hex": "0x%X" % SLOT_FOOTER,
            "slot_stride_note_ja": "slot stride = SLOT_DATA_SIZE + フッタ = 0x11D088 + 0x1738 = 0x11E7C0。"
                                   "ただし stride はセーブから読まずに body+0x10/0x14/0x18 の 3 つのポインタを使う方が安全",
        },
        "box": {
            "offset_from_slot_base": OFF_BOX,
            "offset_from_slot_base_hex": "0x%04X" % OFF_BOX,
            "record_bytes": RECORD_BYTES,
            "record_count": RECORD_COUNT,
            "box_bytes": BOX_BYTES,
            "end_offset_from_slot_base_hex": "0x%05X" % (OFF_BOX + BOX_BYTES),
            "order_note_ja": "レコードの並びはゲーム内ボックスの並びと同じ（refsrc docs/07-equipment.md）",
            "after_box_ja": "オトモ装備ボックス (1000 枠 x 36 バイト = 36,000 バイト) が続く",
        },
        "record": {
            "fields": FIELDS,
            "head_word": {
                "offset": 0,
                "type": "u16le",
                "bits": HEAD_BITS,
                "decode_python": "head = rec[0] | (rec[1] << 8); type = head & 0x1F; "
                                 "level = ((head >> 5) & 0x1F) + 1; "
                                 "transmog_level = ((head >> 10) & 0x1F) + 1",
            },
            "empty_record_ja": "36 バイトすべてが 0 のレコードが空き枠。type だけ 0 で他のバイトが残っている"
                               "レコードもあり得るので、空き判定は全バイト 0 で行う（equip.rs の is_empty は type だけを見るが、"
                               "書き込み可否の判定は record_is_blank 側）",
        },
        "type_map": TYPE_MAP,
        "talisman": {
            "type": 6,
            "fields": TALISMAN_FIELDS,
            "kind_to_rarity": {str(k): v for k, v in sorted(KIND_RARITY.items())},
            "charm_item_id_range": [353, 356],
            "note_ja": "護石は +0x12/+0x13 の u16 が護石アイテム ID (353..356) で、下位バイトがレア度、"
                       "上位バイトが常に 1。+0x02 の kind は TALISMAN_RARITY でレア度に結び付くが、"
                       "kind=0 のレコードが 2 件だけ観測され、そのレア度は 99 で表と一致しない（unknown 参照）。",
        },
        "decoration_fields": {
            "offsets": ["0x06", "0x08", "0x0A"],
            "type": "u16le x 3",
            "item_id_range": [2638, 2899],
            "zero_means": "空き",
            "applies_to": "type 1..5 (防具), 6 (護石), 7..21 (武器)",
            "note_ja": "装飾品はサイズ (1..3) に関係なく 1 枠を 1 個で使い、先頭から詰める"
                       "（refsrc docs/07-equipment.md）。非 0 の個数は装備のスロット数を超えない。",
        },
        "page_geometry": {
            "slots_per_page": SLOTS_PER_PAGE,
            "page_count": PAGE_COUNT,
            "row_height_px": ROW_HEIGHT_PX,
            "scroll_track_px": SCROLL_TRACK_PX,
            "page_to_index_range": "page p (0 始まり) -> [p * 9, min(p * 9 + 9, 2000))",
            "index_to_page": "page = index // 9, 行内位置 = index % 9",
            "last_page": {"page": PAGE_COUNT - 1, "first_index": (PAGE_COUNT - 1) * SLOTS_PER_PAGE,
                          "last_index": RECORD_COUNT - 1, "rows": RECORD_COUNT - (PAGE_COUNT - 1) * SLOTS_PER_PAGE},
            "source_ja": "hbedit.rs の page_move の doc コメント「the equipment box shows nine and a warning strip "
                         "takes one」と tests/scroll_ui.rs の「The track the equipment box uses: nine 56px rows.」"
                         "(TRACK = 504 = 9 x 56) /「Nine rows on screen means nine rows a page」",
            "scope_ja": "これはエディタの一覧画面のページ。ゲーム本体の装備ボックス画面が 1 ページ何枠かは"
                        "手元の資料からは確定できない（unknown 参照）",
        },
        "verification": verification,
        "live_save_records": detail,
        "unknown": [
            "ゲーム本体の装備ボックス画面の 1 ページあたりの枠数。エディタの一覧は 9 行だが、ゲーム内の画面は未確認。",
            "type 6 (護石) の +0x02 kind=0 が 2 件だけ観測され、レア度 99 と結び付いている。"
            "TALISMAN_RARITY の表 (kind 5..7 -> 99) に無い組み合わせで、意味は不明。",
            "護石以外の type でも +0x0C 以降が非 0 のレコードがある（サンプルセーブで 15 件）。"
            "値は護石ブロックや猟虫ブロックの形をしており、前の持ち主のバイトが残っていると見られる。"
            "どの操作で残るのかは未確定。",
            "武器の装飾品数が武器のスロット数を超えないかは未検証（weaponNNLevelData のスロット数を読んでいない）。",
            "type 22 以上がハンターの装備ボックスに現れるかは未確認（サンプル 2,331 レコードでは 21 が最大）。",
            "head word の bit15 は 2,331 レコードで 0 だったが、ゲームが将来使うかは不明。",
        ],
    }


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
