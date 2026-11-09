# -*- coding: utf-8 -*-
"""MHXX 装備・アイテム系 ID テーブル抽出 (mhxx-id-memo / analyst-equip).

romfs の実テーブル + mhnxeditor の静的テーブル + 既存 jp_names CSV から
data/equip/*.csv と _manifest.json を生成する。再現性のため全ロジックをこの 1 本に置く。

    python tools/extract_equip_tables.py [--romfs DIR] [--refsrc DIR] [--jpnames DIR]

出典 (どれも読み取り専用):
  romfs/nativeNX/table/*.gmd / *.itm / *.ict / *.skt / *.skd / *.deco / *.isd / *.hta / *.asd / *.amlt
  mhnxeditor/crates/mhnx-core/src/gamedata.rs    (英語名/ID 対応表)
  extract/jp_names/*.csv                         (既存の日本語名抽出)
  mhnxeditor/.work/finalaudit/refsrc/data/*.csv  (装飾品スキル/護石テーブル/オトモ行動/狩技英語名)
"""
import argparse
import csv
import json
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.dirname(ROOT)                           # C:\anyWorkspace\nx\mhxx
DEFAULT_ROMFS = os.path.join(WORK, "romfs", "nativeNX")
DEFAULT_REF = os.path.join(WORK, "mhnxeditor", ".work", "finalaudit", "refsrc", "data")
DEFAULT_JP = os.path.join(WORK, "extract", "jp_names")
GAMEDATA_RS = os.path.join(WORK, "mhnxeditor", "crates", "mhnx-core", "src", "gamedata.rs")
OUT = os.path.join(ROOT, "data", "equip")

CR = chr(13)
IDEOGRAPHIC_SPACE = chr(0x3000)
DASH = chr(0x2015)

# ---------------------------------------------------------------- utilities

def norm(text):
    """値内の改行を LF に統一し、末尾の空白を落とす。"""
    if text is None:
        return ""
    return text.replace(CR, "").rstrip()


def read_gmd(path):
    """GMD の文字列ブロックを順に返す (mhnxeditor romfstables.rs の記述に従う)。"""
    with open(path, "rb") as f:
        b = f.read()
    if b[:4] != b"GMD" + bytes([0]):
        raise ValueError("not a gmd: " + path)
    count = struct.unpack_from("<I", b, 0x18)[0]
    block_len = struct.unpack_from("<I", b, 0x20)[0]
    key_len = struct.unpack_from("<I", b, 0x24)[0]
    after_key = 0x28 + key_len + 1
    if 0 < block_len <= len(b) and len(b) - block_len >= after_key:
        start = len(b) - block_len
    else:
        start = after_key
    out, cur = [], bytearray()
    for c in b[start:]:
        if c == 0:
            out.append(cur.decode("utf-8", "replace"))
            cur = bytearray()
            if len(out) == count:
                break
        else:
            cur.append(c)
    return out


def read_records(path, size):
    """先頭 8 バイト (f32 version + u32 count) の後に固定長レコードが並ぶテーブル。"""
    with open(path, "rb") as f:
        b = f.read()
    n = struct.unpack_from("<I", b, 4)[0]
    if len(b) != 8 + n * size:
        raise ValueError("%s: size %d != 8 + %d*%d" % (path, len(b), n, size))
    return [b[8 + size * k: 8 + size * (k + 1)] for k in range(n)]


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_gamedata(path):
    """gamedata.rs の pub static NAME: &[&str] = &[...] / &[i32] を dict にする。"""
    with open(path, encoding="utf-8") as f:
        src = f.read()
    out = {}
    for chunk in src.split("pub ")[1:]:
        head, sep, rest = chunk.partition("=")
        if not sep:
            continue
        words = head.split(":")
        if len(words) < 2:
            continue
        decl = words[0].split()
        if len(decl) != 2 or decl[0] not in ("static", "const"):
            continue
        name = decl[1]
        if "[" not in head:
            continue
        start = rest.find("[")
        if start < 0:
            continue
        depth, j = 0, start
        while j < len(rest):
            if rest[j] == "[":
                depth += 1
            elif rest[j] == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = rest[start + 1:j]
        strs = []
        k = 0
        while k < len(body):
            if body[k] == '"':
                k += 1
                buf = []
                while k < len(body) and body[k] != '"':
                    if body[k] == chr(92):
                        k += 1
                    buf.append(body[k])
                    k += 1
                strs.append("".join(buf))
            k += 1
        if strs:
            out[name] = strs
        else:
            out[name] = [int(x) for x in re.findall(r"-?[0-9]+", body)]
    return out


def write_csv(name, header, rows):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print("  -> %-28s %6d rows" % (name, len(rows)))
    return len(rows)


def col(name, ctype, ja, en):
    return {"name": name, "type": ctype, "desc_ja": ja, "desc_en": en}


def en_name(text):
    """gamedata.rs の英語名テーブルは index 0 が "(None)"。

    SPEC 0-5「空値は空文字（NULL 等の文字列は使わない）」に従い空文字にする。
    """
    return "" if text == "(None)" else text


# ---------------------------------------------------------------- main

def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--romfs", default=DEFAULT_ROMFS)
    ap.add_argument("--refsrc", default=DEFAULT_REF)
    ap.add_argument("--jpnames", default=DEFAULT_JP)
    args = ap.parse_args(argv)
    TB = os.path.join(args.romfs, "table")
    G = parse_gamedata(GAMEDATA_RS)
    manifest = []

    def gmd(n):
        return read_gmd(os.path.join(TB, n))

    def rec(n, size):
        return read_records(os.path.join(TB, n), size)

    # ---- 武器種 ----
    # romfs の武器種 ID は weaponNN* の NN。05 が欠番 (武器ファイルが存在しない)。
    # 日本語名は weapons.csv の type 列、英語名は HUNT_WEAPONS
    # (0..14 の別採番。5=Light Bowgun, 14=Prowler) から引く。
    weapons_jp = read_csv(os.path.join(args.jpnames, "weapons.csv"))
    type_ja = {}
    for r in weapons_jp:
        type_ja[int(r["type_id"])] = r["type"]
    hunt = G["HUNT_WEAPONS"]
    weapon_type_rows = []
    for t in range(15):
        if t in type_ja:
            idx = t if t < 5 else t - 1
            weapon_type_rows.append([t, type_ja[t], hunt[idx], t + 7, idx, "yes"])
        else:
            weapon_type_rows.append([t, "", "", t + 7, "", "no"])
    write_csv("weapon-types.csv",
              ["weapon_type_id", "name_ja", "name_en", "equip_type_id", "hunt_weapon_index", "used"],
              weapon_type_rows)
    manifest.append({
        "id": "weapon-types", "title_ja": "武器種", "title_en": "Weapon types",
        "file": "weapon-types.csv", "primary_key": "weapon_type_id",
        "columns": [
            col("weapon_type_id", "int", "武器種ID (romfs の weaponNN の NN。5 は欠番)", "Weapon type ID"),
            col("name_ja", "str", "武器種名（日本語）", "Name (Japanese)"),
            col("name_en", "str", "武器種名（英語）", "Name (English)"),
            col("equip_type_id", "int", "EQUIPMENT_TYPES 上の装備種別ID (= weapon_type_id + 7)", "Equipment type ID"),
            col("hunt_weapon_index", "int", "HUNT_WEAPONS 上の添字 (0..13)", "Index into HUNT_WEAPONS"),
            col("used", "bool", "実在する武器種か", "Weapon class exists"),
        ],
        "source": ["romfs/nativeNX/table/weapon*MsgData_jpn.gmd", "extract/jp_names/weapons.csv",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (HUNT_WEAPONS, EQUIPMENT_TYPES)"],
        "confidence": "verified",
        "notes_ja": "weapon_type_id は romfs の weaponNN ファイル名の NN。05 はファイルが存在しない欠番。"
                    "日本語名は weapons.csv の type 列、英語名は HUNT_WEAPONS (0..14 の別採番で 5=Light Bowgun, 14=Prowler) の"
                    "対応する添字から取った。equip_type_id は EQUIPMENT_TYPES の並び (7=Great Sword ... 21=Charge Blade、12 が欠番) と一致する。",
        "notes_en": "weapon_type_id is the NN of romfs weaponNN files; 05 is absent. English names come from HUNT_WEAPONS, which uses a different 0..14 numbering.",
    })

    # ---- 武器 ----
    # weaponNNMsgData_jpn.gmd は 6 文字列/武器 = 3 form x (名前, 説明)。
    # form 0 が素の名前で、セーブが保持するのは form 0。英語名テーブルも form 0 のみ。
    equip_names = {
        0: "EQUIP_GREAT_SWORD_NAMES", 1: "EQUIP_SWORDN_SHIELD_NAMES", 2: "EQUIP_HAMMER_NAMES",
        3: "EQUIP_LANCE_NAMES", 4: "EQUIP_HEAVY_BOWGUN_NAMES", 6: "EQUIP_LIGHT_BOWGUN_NAMES",
        7: "EQUIP_LONGSWORD_NAMES", 8: "EQUIP_SWITCH_AXE_NAMES", 9: "EQUIP_GUNLANCE_NAMES",
        10: "EQUIP_BOW_NAMES", 11: "EQUIP_DUAL_BLADES_NAMES", 12: "EQUIP_HUNTING_HORN_NAMES",
        13: "EQUIP_INSECT_GLAIVE_NAMES", 14: "EQUIP_CHARGE_BLADE_NAMES",
    }
    weapon_rows = []
    weapon_seen = set()
    for r in weapons_jp:
        t, wid, form = int(r["type_id"]), int(r["weapon_id"]), int(r["form"])
        if t not in equip_names:
            raise SystemExit("unknown weapon type %d" % t)
        en = G[equip_names[t]]
        if wid >= len(en):
            raise SystemExit("weapon id %d out of range for type %d" % (wid, t))
        key = t * 10000 + wid * 10 + form
        if key in weapon_seen:
            raise SystemExit("duplicate weapon key %d" % key)
        weapon_seen.add(key)
        weapon_rows.append([key, t, wid, form, norm(r["name"]),
                            en_name(en[wid]) if form == 0 else "", norm(r["desc"]), r["levels"]])
    weapon_rows.sort()
    write_csv("weapons.csv",
              ["weapon_id", "weapon_type_id", "weapon_index", "form", "name_ja", "name_en", "desc_ja", "levels"],
              weapon_rows)
    manifest.append({
        "id": "weapons", "title_ja": "武器", "title_en": "Weapons",
        "file": "weapons.csv", "primary_key": "weapon_id",
        "columns": [
            col("weapon_id", "int", "主キー。weapon_type_id*10000 + weapon_index*10 + form の合成ID", "Synthetic key"),
            col("weapon_type_id", "int", "武器種ID (weapon-types.csv)", "Weapon type ID"),
            col("weapon_index", "int", "武器種ごとの武器ID (0 始まり)", "Per-class weapon ID"),
            col("form", "int", "名前の段階 (0=素の名前, 1, 2=強化後の名前)", "Name stage"),
            col("name_ja", "str", "武器名（日本語）", "Name (Japanese)"),
            col("name_en", "str", "武器名（英語、form 0 のみ）", "Name (English, form 0 only)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
            col("levels", "str", "この名前になる強化レベル (セミコロン区切り)", "Levels using this name"),
        ],
        "source": ["romfs/nativeNX/table/weapon*MsgData_jpn.gmd", "romfs/nativeNX/table/weapon*LevelData.w*d",
                   "extract/jp_names/weapons.csv", "mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES)"],
        "confidence": "verified",
        "notes_ja": "ゲーム内の武器IDは武器種ごとに 0 から振られているため、主キーは "
                    "weapon_type_id*10000 + weapon_index*10 + form の合成IDにした (元の座標は各列に残してある)。"
                    "form は強化で名前が変わる段階で、セーブが保持するのは form 0 (equipnames.rs の記述)。"
                    "英語名テーブル EQUIP_*_NAMES は 1 武器 1 名 (form 0) なので form 1/2 の name_en は空。"
                    "各武器種の weapon_index 件数は EQUIP_*_NAMES の要素数と完全一致する "
                    "(大剣137/片手剣129/ハンマー132/ランス127/ヘビィ109/ライト110/太刀127/スラアク110/ガンランス115/弓108/双剣126/笛112/虫棍83/チャアク81)。",
        "notes_en": "The game numbers weapons per class, so the primary key is a synthetic type*10000+index*10+form. English names exist for form 0 only.",
    })

    # ---- 防具 ----
    # armorSeriesData_jpn.gmd は 10 文字列/系列 = 5 部位 x (名前, 説明)。
    # 防具ID は series*5 + part (equipnames.rs: "index = series * 5 + part")。
    armor_jp = read_csv(os.path.join(args.jpnames, "armor_series.csv"))
    asd = rec("armorSeriesData.asd", 127)
    part_names_ja = ["頭", "胴", "腕", "腰", "脚"]
    en_part = ["HEAD", "CHEST", "ARMS", "WAIST", "LEGS"]
    en_by_part = {}
    for p, key in enumerate(en_part):
        names = G["EQUIP_" + key + "_NAMES"]
        ids = G["EQUIP_" + key + "_I_DS"]
        en_by_part[p] = dict(zip(ids, names))
        present = [k for k, r in enumerate(asd) if r[6 + p]]
        if present != ids:
            raise SystemExit("armor part %d: armorSeriesData parts-present != EQUIP_%s_I_DS" % (p, key))
    armor_rows = []
    for r in armor_jp:
        s, p = int(r["series_id"]), part_names_ja.index(r["part"])
        if not asd[s][6 + p]:
            continue                       # その部位が存在しない系列
        armor_rows.append([s * 5 + p, s, p, norm(r["name"]), en_name(en_by_part[p].get(s, "")), norm(r["desc"])])
    armor_rows.sort()
    write_csv("armor.csv", ["armor_id", "series_id", "part_id", "name_ja", "name_en", "desc_ja"], armor_rows)
    manifest.append({
        "id": "armor", "title_ja": "防具", "title_en": "Armor",
        "file": "armor.csv", "primary_key": "armor_id",
        "columns": [
            col("armor_id", "int", "防具ID = series_id*5 + part_id", "Armor ID"),
            col("series_id", "int", "シリーズID (armorSeriesData のレコード番号)", "Series ID"),
            col("part_id", "int", "部位ID (armor-parts.csv)", "Part ID"),
            col("name_ja", "str", "防具名（日本語）", "Name (Japanese)"),
            col("name_en", "str", "防具名（英語）", "Name (English)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
        ],
        "source": ["romfs/nativeNX/table/armorSeriesData_jpn.gmd", "romfs/nativeNX/table/armorSeriesData.asd",
                   "extract/jp_names/armor_series.csv", "mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES/_IDS)"],
        "confidence": "verified",
        "notes_ja": "armorSeriesData.asd は 127 バイト/系列で、+6..+10 が部位の有無 (頭/胴/腕/腰/脚)。"
                    "この有無フラグは gamedata.rs の EQUIP_HEAD/CHEST/ARMS/WAIST/LEGS_I_DS と件数・並び順まで完全一致した "
                    "(1204/1189/1158/1108/1177)。部位が無い系列の行は出力していない。"
                    "armor_id = series*5 + part は mhnxeditor の equipnames.rs が明記している並び。",
        "notes_en": "armorSeriesData.asd +6..+10 holds the per-part presence flags, which match EQUIP_*_I_DS exactly. Rows for absent parts are omitted.",
    })

    # ---- 部位 ----
    armor_parts_rows = [[p, part_names_ja[p], G["EQUIPMENT_TYPES"][p + 1]] for p in range(5)]
    write_csv("armor-parts.csv", ["part_id", "name_ja", "name_en"], armor_parts_rows)
    manifest.append({
        "id": "armor-parts", "title_ja": "防具部位", "title_en": "Armor parts",
        "file": "armor-parts.csv", "primary_key": "part_id",
        "columns": [
            col("part_id", "int", "部位ID (0=頭 1=胴 2=腕 3=腰 4=脚)", "Part ID"),
            col("name_ja", "str", "部位名（日本語）", "Name (Japanese)"),
            col("name_en", "str", "部位名（英語）", "Name (English)"),
        ],
        "source": ["romfs/nativeNX/table/armorSeriesData_jpn.gmd", "extract/jp_names/gen.py (PARTS)",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIPMENT_TYPES)"],
        "confidence": "verified",
        "notes_ja": "armorSeriesData_jpn.gmd の 10 文字列 = 5 部位 x (名前, 説明) の並び (頭,胴,腕,腰,脚)。"
                    "英語名は EQUIPMENT_TYPES の 1..5 (Head, Chest, Arms, Waist, Legs)。",
        "notes_en": "Order taken from the 10-strings-per-series layout of armorSeriesData_jpn.gmd.",
    })

    # ---- アイテム ----
    item_names = gmd("itemData_jpn.gmd")
    itm = rec("itemData.itm", 44)
    icn = gmd("itemCategoryTypeData_jpn.gmd")
    ict = rec("itemCategoryTypeData.ict", 7)
    if len(item_names) != 2 * len(itm):
        raise SystemExit("itemData: %d strings vs %d records" % (len(item_names), len(itm)))
    item_rows = []
    for k, r in enumerate(itm):
        mat = struct.unpack_from("<H", r, 28)[0]
        if mat >= len(ict):
            raise SystemExit("item %d: material category %d out of range" % (k, mat))
        item_rows.append([k, norm(item_names[2 * k]), "", norm(item_names[2 * k + 1]), r[16], mat])
    write_csv("items.csv", ["item_id", "name_ja", "name_en", "desc_ja", "category_id", "material_category_id"], item_rows)
    manifest.append({
        "id": "items", "title_ja": "アイテム", "title_en": "Items",
        "file": "items.csv", "primary_key": "item_id",
        "columns": [
            col("item_id", "int", "アイテムID (0..2990)", "Item ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語、未取得）", "Name (English, unavailable)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
            col("category_id", "int", "アイテム分類ID (itemData.itm +16 の u8。0..105、名前テーブルは未発見)", "Item category group"),
            col("material_category_id", "int", "素材カテゴリID (item-categories.csv)", "Material category ID"),
        ],
        "source": ["romfs/nativeNX/table/itemData_jpn.gmd", "romfs/nativeNX/table/itemData.itm",
                   "romfs/nativeNX/table/itemCategoryTypeData.ict"],
        "confidence": "verified",
        "notes_ja": "itemData_jpn.gmd は 2 文字列/アイテム (名前, 説明)、itemData.itm は 44 バイト/アイテムで "
                    "レコード数 2991 が一致する。日本語版 romfs しか手元に無いため name_en は全行空 "
                    "(英語版の itemData_eng.gmd が必要)。"
                    "category_id は itemData.itm +16 の u8 で、値ごとにアイテムが意味的にまとまる "
                    "(22=回復薬系, 24=罠, 26=タル爆弾, 43=調合書, 44=原珠/珠, 52=お守り など) ことを確認したが、"
                    "この分類の名前テーブルは romfs の gmd に見つからないため数値のみ。"
                    "material_category_id は +28 の u16 で itemCategoryTypeData の ID (0..337)。",
        "notes_en": "Only the Japanese romfs is available, so name_en is empty. category_id is the u8 at itemData.itm +16; its name table was not found.",
    })

    # ---- アイテムカテゴリ ----
    cat_rows = []
    for k, r in enumerate(ict):
        cat_rows.append([k, norm(icn[k]), r[6], "%02x%02x" % (r[4], r[5])])
    write_csv("item-categories.csv", ["category_id", "name_ja", "variant_index", "raw_tag"], cat_rows)
    manifest.append({
        "id": "item-categories", "title_ja": "アイテムカテゴリ（素材分類）", "title_en": "Item categories (material)",
        "file": "item-categories.csv", "primary_key": "category_id",
        "columns": [
            col("category_id", "int", "カテゴリID (0..337)", "Category ID"),
            col("name_ja", "str", "カテゴリ名（日本語）", "Name (Japanese)"),
            col("variant_index", "int", "レコード 3 バイト目。同名の 3 連レコードで 0,1,2 と巡回する", "Third byte of the record"),
            col("raw_tag", "str", "レコード先頭 2 バイト (16進、意味未確定)", "First two bytes, hex"),
        ],
        "source": ["romfs/nativeNX/table/itemCategoryTypeData.ict", "romfs/nativeNX/table/itemCategoryTypeData_jpn.gmd"],
        "confidence": "verified",
        "notes_ja": "itemCategoryTypeData.ict は 7 バイト/レコードで 338 件、itemCategoryTypeData_jpn.gmd の 338 文字列と 1:1 対応する。"
                    "名前は素材の分類 (モンスター素材, 鉱石素材, マッカォ素材 ...) で、同名が 3 件ずつ並び 3 バイト目が 0,1,2 と巡回する。"
                    "先頭 2 バイトの意味は未確定のため 16 進の生値で残した。items.material_category_id がこの ID を指す。",
        "notes_en": "338 records of 7 bytes, one name each. The first two bytes are unexplained and kept as hex.",
    })

    # ---- 装飾品 ----
    jwl_names = G["JWL_NAMES"]
    jwl_ids = G["JWL_I_DS"]
    deco = rec("decoData.deco", 5)
    ref_deco = read_csv(os.path.join(args.refsrc, "decorations.csv"))
    deco_by_item = {}
    for k, r in enumerate(deco):
        item = 2638 + k
        entries = []
        for j in range(2):
            tree, pts = struct.unpack_from("<Bb", r, 1 + 2 * j)
            if tree and pts:
                entries.append((tree, pts))
        if r[0] > 3:
            raise SystemExit("deco %d: slot size %d" % (item, r[0]))
        deco_by_item[item] = (r[0], entries)
    # refsrc の decorations.csv と突き合わせる (同じ表を別実装で読んだ結果の照合)
    ref_pairs = sorted((int(x["item"]), int(x["slots"]), int(x["tree"]), int(x["points"])) for x in ref_deco)
    mine_pairs = sorted((item, slot, t, p) for item, (slot, es) in deco_by_item.items() for t, p in es)
    if ref_pairs != mine_pairs:
        raise SystemExit("decoData と refsrc/decorations.csv が一致しない")
    skt_jp_names = gmd("skillTypeData_jpn.gmd")
    skill_ja = {k: norm(skt_jp_names[2 * k]) for k in range(len(G["SKILL_NAMES"]))}
    deco_rows = []
    for did in range(1, len(jwl_names)):
        item = jwl_ids[did]
        slot, entries = deco_by_item.get(item, ("", []))
        e1 = entries[0] if len(entries) > 0 else ("", "")
        e2 = entries[1] if len(entries) > 1 else ("", "")
        deco_rows.append([
            did, jwl_names[did], norm(item_names[2 * item]) if 2 * item + 1 < len(item_names) else "",
            item, slot,
            e1[0], skill_ja.get(e1[0], ""), e1[1],
            e2[0], skill_ja.get(e2[0], ""), e2[1],
            "yes" if item not in deco_by_item else "no",
        ])
    write_csv("decorations.csv",
              ["decoration_id", "name_en", "name_ja", "item_id", "slot_size",
               "skill1_id", "skill1_name_ja", "skill1_points",
               "skill2_id", "skill2_name_ja", "skill2_points", "is_dummy"],
              deco_rows)
    manifest.append({
        "id": "decorations", "title_ja": "装飾品（珠）", "title_en": "Decorations",
        "file": "decorations.csv", "primary_key": "decoration_id",
        "columns": [
            col("decoration_id", "int", "装飾品ID (1..262)", "Decoration ID"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
            col("name_ja", "str", "名前（日本語、対応するアイテム名）", "Name (Japanese)"),
            col("item_id", "int", "対応するアイテムID", "Item ID"),
            col("slot_size", "int", "必要スロット数 (1..3)", "Slot size"),
            col("skill1_id", "int", "スキル1のスキルID (skills.csv)", "Skill 1 ID"),
            col("skill1_name_ja", "str", "スキル1の名前（日本語）", "Skill 1 name (Japanese)"),
            col("skill1_points", "int", "スキル1のポイント", "Skill 1 points"),
            col("skill2_id", "int", "スキル2のスキルID (skills.csv)", "Skill 2 ID"),
            col("skill2_name_ja", "str", "スキル2の名前（日本語）", "Skill 2 name (Japanese)"),
            col("skill2_points", "int", "スキル2のポイント（マイナスあり）", "Skill 2 points"),
            col("is_dummy", "bool", "decoData に実体が無いダミー行か", "Dummy row"),
        ],
        "source": ["romfs/nativeNX/table/decoData.deco", "romfs/nativeNX/table/skillTypeData_jpn.gmd",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (JWL_NAMES, JWL_I_DS)",
                   "mhnxeditor/.work/finalaudit/refsrc/data/decorations.csv"],
        "confidence": "verified",
        "notes_ja": "decoData.deco は 5 バイト/レコードで 251 件、レコード k がアイテム 2638+k。"
                    "JWL_I_DS は decoration_id k -> アイテム 2637+k で、全 262 件でこの関係が成立することを確認した。"
                    "decoData から復元した (アイテム, スロット, スキル, ポイント) 424 行は refsrc の decorations.csv と完全一致した。"
                    "decoration_id 252..262 は JWL_NAMES にのみ存在する Dummy Jwl 10..20 で、decoData に実体が無いため "
                    "スキル列は空・is_dummy=yes にしてある。スキルID は skills.csv のスキルIDを指す。",
        "notes_en": "decoData.deco has 251 five-byte records; record k is item 2638+k. The 424 rows reproduce refsrc decorations.csv exactly.",
    })

    # ---- 護石 ----
    amulet = read_csv(os.path.join(args.jpnames, "amulet.csv"))
    tal_names = G["EQUIP_TALISMAN_NAMES"]
    tal_rarity = G["TALISMAN_RARITY"]
    tal_tab = read_csv(os.path.join(args.refsrc, "talisman-tables.csv"))
    max_slots = {int(r["tier"]): int(r["max"]) for r in tal_tab if r["kind"] == "slots"}
    tal_rows = []
    for r in amulet:
        k = int(r["amulet_id"])
        rar = tal_rarity[k]
        tal_rows.append([k, norm(r["name"]), en_name(tal_names[k]), rar, max_slots.get(rar, "") if rar else ""])
    write_csv("talismans.csv", ["talisman_id", "name_ja", "name_en", "rarity", "max_slots"], tal_rows)
    manifest.append({
        "id": "talismans", "title_ja": "護石", "title_en": "Talismans",
        "file": "talismans.csv", "primary_key": "talisman_id",
        "columns": [
            col("talisman_id", "int", "護石ID (0..10)", "Talisman ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
            col("rarity", "int", "レア度 (TALISMAN_RARITY。0 は装備なし)", "Rarity tier"),
            col("max_slots", "int", "そのレア度で付く最大スロット数", "Max slots"),
        ],
        "source": ["romfs/nativeNX/table/amuletData_jpn.gmd", "extract/jp_names/amulet.csv",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_TALISMAN_NAMES, TALISMAN_RARITY)",
                   "mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv"],
        "confidence": "verified",
        "notes_ja": "amuletData_jpn.gmd は 2 文字列/護石で 11 件、amulet.csv と一致。"
                    "レア度は gamedata.rs の TALISMAN_RARITY (0,97,97,98,98,99,99,99,100,100,100) で、"
                    "97=神秘 98=閃光 99=風化 100=歴戦。max_slots は talisman-tables.csv の slots 行 (97->1, 98->2, 99->3, 100->3)。"
                    "護石の抽選スキル範囲は talisman-tables.csv を参照。",
        "notes_en": "11 talismans. Rarity tiers 97..100 map to Mystery/Shining/Timeworn/Enduring.",
    })

    # ---- スキル ----
    skt = rec("skillTypeData.skt", 19)
    skill_names_en = G["SKILL_NAMES"]
    if len(skt) != len(skill_names_en) or len(skt_jp_names) != 2 * len(skt):
        raise SystemExit("skillTypeData counts differ")
    skill_rows = []
    for k, r in enumerate(skt):
        tree = struct.unpack_from("<I", r)[0]
        if tree != k:
            raise SystemExit("skillTypeData id %d != index %d" % (tree, k))
        ids = struct.unpack_from("<7H", r, 5)
        pos = [x for x in ids[3:6] if x]
        neg = [x for x in ids[0:3] if x]
        skill_rows.append([k, norm(skt_jp_names[2 * k]), en_name(skill_names_en[k]), norm(skt_jp_names[2 * k + 1]),
                           r[4], len(set(pos)), len(set(neg))])
    write_csv("skills.csv", ["skill_id", "name_ja", "name_en", "desc_ja", "kind", "max_level", "min_level"], skill_rows)
    manifest.append({
        "id": "skills", "title_ja": "スキル", "title_en": "Skills",
        "file": "skills.csv", "primary_key": "skill_id",
        "columns": [
            col("skill_id", "int", "スキルID (skillTypeData のレコード番号。防具/装飾品/護石が指す)", "Skill ID"),
            col("name_ja", "str", "スキル名（日本語）", "Name (Japanese)"),
            col("name_en", "str", "スキル名（英語）", "Name (English)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
            col("kind", "int", "種別 (0=通常, 1=二つ名スキル【魂】, 2=【魂・極】)", "Kind"),
            col("max_level", "int", "最大レベル (プラス段階で発動するスキルの種類数)", "Max level"),
            col("min_level", "int", "マイナス側の段階数", "Negative levels"),
        ],
        "source": ["romfs/nativeNX/table/skillTypeData.skt", "romfs/nativeNX/table/skillTypeData_jpn.gmd",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (SKILL_NAMES)"],
        "confidence": "derived",
        "notes_ja": "skillTypeData.skt は 19 バイト/スキルで 206 件: u32 スキルID, u8 kind, u16 x7 が "
                    "-20/-15/-10/+10/+15/+20/+25 ポイントで発動するスキル (skill-effects.csv の ID)。"
                    "名前と説明は skillTypeData_jpn.gmd (2 文字列/件) から取った。"
                    "max_level は +10/+15/+20 で発動するスキルの種類数、min_level は -10/-15/-20 の種類数として算出した "
                    "(攻撃=3/3, 気絶=2/1, 体力=2/2 など、既知の段階数と一致することを確認)。"
                    "kind の 1/2 は 144..161 / 162..179 の二つ名スキルにだけ付く。",
        "notes_en": "19-byte records: u32 id, u8 kind, 7 u16 skill ids for -20/-15/-10/+10/+15/+20/+25 points. max_level counts distinct positive tiers.",
    })

    # ---- スキル効果 (SPEC 外の追加テーブル) ----
    skill_effects = read_csv(os.path.join(args.jpnames, "skills.csv"))
    se_rows = [[int(r["index"]), norm(r["name"]), norm(r["desc"])] for r in skill_effects]
    se_rows.sort()
    write_csv("skill-effects.csv", ["effect_id", "name_ja", "desc_ja"], se_rows)
    manifest.append({
        "id": "skill-effects", "title_ja": "スキル効果（発動後のスキル名）", "title_en": "Skill effects",
        "file": "skill-effects.csv", "primary_key": "effect_id",
        "columns": [
            col("effect_id", "int", "スキル効果ID (skillData のレコード番号)", "Skill effect ID"),
            col("name_ja", "str", "スキル名（日本語）", "Name (Japanese)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
        ],
        "source": ["romfs/nativeNX/table/skillData_jpn.gmd", "extract/jp_names/skills.csv"],
        "confidence": "verified",
        "notes_ja": "skillData_jpn.gmd は 2 文字列/件で 328 件 (スキル無し, 毒耐性, 毒倍加, 麻痺無効 ...)。"
                    "skills.csv のスキルIDとは別の ID 空間で、skills.csv の各段階がここを指す。"
                    "SPEC の担当表には無いが、skills.csv の段階を解決するために追加した (Lead に報告)。",
        "notes_en": "328 skillData records; skills.csv tiers point into this table. Added beyond the SPEC table list.",
    })

    # ---- 狩技 ----
    hta = rec("hunterArtsData.hta", 25)
    hta_jp = gmd("hunterArtsData_jpn.gmd")
    if len(hta_jp) != 4 * len(hta):
        raise SystemExit("hunterArtsData counts differ")
    arts_en = {int(r["id"]): r["name"] for r in read_csv(os.path.join(args.refsrc, "hunter-arts.csv"))}
    # 狩技は武器種ごとにブロックで並ぶ。art_group (+8) の範囲と武器種の対応は
    # 各ブロック先頭の説明文がその武器を明記していることで 1 対 1 に確認した。
    ART_BLOCKS = [(1, 10, None), (11, 15, 0), (16, 18, 1), (19, 22, 2), (23, 26, 3), (27, 30, 4),
                  (31, 34, 5), (35, 38, 6), (39, 42, 7), (43, 46, 8), (47, 50, 9), (51, 54, 10),
                  (55, 58, 11), (59, 62, 12), (63, 66, 13), (67, 70, 14)]
    group_type = {}
    for lo, hi, t in ART_BLOCKS:
        for g in range(lo, hi + 1):
            group_type[g] = t
    art_rows = []
    for k, r in enumerate(hta):
        name = norm(hta_jp[4 * k])
        if not name or name == IDEOGRAPHIC_SPACE:
            continue                       # 71..82 は空のプレースホルダ
        g = struct.unpack_from("<I", r, 8)[0]
        if g == 0:
            continue                       # id 0 = 装備なし (art_group 0)
        if g not in group_type:
            raise SystemExit("art %d: group %d outside the block table" % (k, g))
        t = group_type[g]
        art_rows.append([k, name, arts_en.get(k, ""),
                         "" if t is None else t,
                         "共通" if t is None else type_ja[t],
                         struct.unpack_from("<H", r, 19)[0], g,
                         norm(hta_jp[4 * k + 3])])
    write_csv("hunter-arts.csv",
              ["art_id", "name_ja", "name_en", "weapon_type_id", "weapon_type_ja", "cost", "art_group", "desc_ja"],
              art_rows)
    manifest.append({
        "id": "hunter-arts", "title_ja": "狩技", "title_en": "Hunter arts",
        "file": "hunter-arts.csv", "primary_key": "art_id",
        "columns": [
            col("art_id", "int", "狩技ID (1..190。71..82 は空レコード)", "Hunter art ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
            col("weapon_type_id", "int", "武器種ID (weapon-types.csv)。空=全武器共通", "Weapon type ID (empty = common)"),
            col("weapon_type_ja", "str", "武器種名（日本語、共通含む）", "Weapon type (Japanese)"),
            col("cost", "int", "狩技ゲージ量 (hunterArtsData.hta +19 の u16)", "Gauge cost"),
            col("art_group", "int", "狩技ファミリーID (hta +8 の u32。I/II/III が同じ値)", "Art family ID"),
            col("desc_ja", "str", "説明（日本語、長文）", "Description (Japanese)"),
        ],
        "source": ["romfs/nativeNX/table/hunterArtsData.hta", "romfs/nativeNX/table/hunterArtsData_jpn.gmd",
                   "mhnxeditor/.work/finalaudit/refsrc/data/hunter-arts.csv"],
        "confidence": "derived",
        "notes_ja": "hunterArtsData.hta は 25 バイト/レコードで 191 件 (0=装備なし, 1..190=狩技)。"
                    "hunterArtsData_jpn.gmd は 4 文字列/件 (名前, 名前, 短い説明, 長い説明)。"
                    "ID 71..82 は名前が全角空白のみのプレースホルダなので出力していない (英語名テーブル hunter-arts.csv も同じ 178 件)。"
                    "hta 自体に武器種の列は無い。レコードは art_group (+8) ごとに武器種ブロックの順で並んでおり、"
                    "各ブロック先頭の説明文がその武器を明記している (11-15=大剣, 19-22=ハンマー, 23-26=ランス, "
                    "27-30=ヘビィボウガン, 35-38=ライトボウガン, 39-42=太刀, 43-46=スラッシュアックス, 47-50=ガンランス, "
                    "51-54=弓, 55-58=双剣, 59-62=狩猟笛, 63-66=操虫棍, 67-70=チャージアックス) ため、"
                    "その対応を weapon_type_id に入れた (1-10 は全武器共通)。31-34 は空きブロック。"
                    "cost は hta +19 の u16 で、+21 の f32 がちょうど 3.5 倍になることだけ確認済み (意味は未確定)。",
        "notes_en": "25-byte records; ids 71..82 are blank placeholders. The weapon type comes from the art-group block order, cross-checked against the weapon named in each block's description.",
    })

    # ---- 猟虫 ----
    insect_jp = gmd("insectData_jpn.gmd")
    kinsect_en = G["KINSECT_NAMES"]
    if len(insect_jp) != len(kinsect_en):
        raise SystemExit("insectData counts differ")
    kinsect_rows = [[k, norm(insect_jp[k]), en_name(kinsect_en[k])] for k in range(len(insect_jp))]
    write_csv("kinsects.csv", ["kinsect_id", "name_ja", "name_en"], kinsect_rows)
    manifest.append({
        "id": "kinsects", "title_ja": "猟虫", "title_en": "Kinsects",
        "file": "kinsects.csv", "primary_key": "kinsect_id",
        "columns": [
            col("kinsect_id", "int", "猟虫ID (0..31)", "Kinsect ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
        ],
        "source": ["romfs/nativeNX/table/insectData_jpn.gmd", "mhnxeditor/crates/mhnx-core/src/gamedata.rs (KINSECT_NAMES)"],
        "confidence": "verified",
        "notes_ja": "insectData_jpn.gmd は 1 文字列/虫で 32 件、insectData.isd も 47 バイト x 32 件。"
                    "日本語名 (クルドローン...) と英語名 (Culldrone...) は添字で 1:1 対応する。説明文は romfs に無い。",
        "notes_en": "32 kinsects; names align by index between the Japanese gmd and KINSECT_NAMES.",
    })

    # ---- オトモ武器 ----
    otw = read_csv(os.path.join(args.jpnames, "palico_weapon.csv"))
    palico_w_en = G["PALICO_WEAPON_NAMES"]
    if len(otw) != len(palico_w_en):
        raise SystemExit("otWeaponData counts differ")
    pw_rows = [[int(r["weapon_id"]), norm(r["name"]), en_name(palico_w_en[int(r["weapon_id"])]), norm(r["desc"])] for r in otw]
    pw_rows.sort()
    write_csv("palico-weapons.csv", ["palico_weapon_id", "name_ja", "name_en", "desc_ja"], pw_rows)
    manifest.append({
        "id": "palico-weapons", "title_ja": "オトモ武器", "title_en": "Palico weapons",
        "file": "palico-weapons.csv", "primary_key": "palico_weapon_id",
        "columns": [
            col("palico_weapon_id", "int", "オトモ武器ID (0..508)", "Palico weapon ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
        ],
        "source": ["romfs/nativeNX/table/otWeaponData_jpn.gmd", "extract/jp_names/palico_weapon.csv",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_WEAPON_NAMES)"],
        "confidence": "verified",
        "notes_ja": "otWeaponData_jpn.gmd は 2 文字列/武器で 509 件、otWeaponData.owp も 31 バイト x 509 件。"
                    "ID 0 は 1234567890 という開発用ダミー文字列で、英語名テーブルの該当行もプレースホルダなので空にしてある。",
        "notes_en": "509 records; id 0 is a developer placeholder string.",
    })

    # ---- オトモ防具 ----
    oa_jp = read_csv(os.path.join(args.jpnames, "palico_armor.csv"))
    head_en = dict(zip(G["PALICO_HEAD_I_DS"], G["PALICO_HEAD_NAMES"]))
    body_en = dict(zip(G["PALICO_ARMOR_I_DS"], G["PALICO_ARMOR_NAMES"]))
    pa_rows = []
    for r in oa_jp:
        s = int(r["series_id"])
        p = 0 if r["part"] == "頭" else 1
        name = norm(r["name"])
        if name in (DASH, "Invalid Message", ""):
            continue                       # その部位が存在しない系列 (名前が全角ダッシュ)
        raw_en = (head_en if p == 0 else body_en).get(s, "")
        if not raw_en:
            raise SystemExit("palico armor series %d part %d has no English name" % (s, p))
        pa_rows.append([s * 2 + p, s, p, name, en_name(raw_en), norm(r["desc"])])
    pa_rows.sort()
    write_csv("palico-armor.csv", ["palico_armor_id", "series_id", "part_id", "name_ja", "name_en", "desc_ja"], pa_rows)
    manifest.append({
        "id": "palico-armor", "title_ja": "オトモ防具", "title_en": "Palico armor",
        "file": "palico-armor.csv", "primary_key": "palico_armor_id",
        "columns": [
            col("palico_armor_id", "int", "オトモ防具ID = series_id*2 + part_id", "Palico armor ID"),
            col("series_id", "int", "シリーズID (otArmorData.oar のレコード番号)", "Series ID"),
            col("part_id", "int", "部位ID (0=頭 1=胴)", "Part ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
            col("desc_ja", "str", "説明（日本語）", "Description (Japanese)"),
        ],
        "source": ["romfs/nativeNX/table/otArmorData_jpn.gmd", "extract/jp_names/palico_armor.csv",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_HEAD_NAMES/_IDS, PALICO_ARMOR_NAMES/_IDS)"],
        "confidence": "verified",
        "notes_ja": "otArmorData_jpn.gmd は 4 文字列/系列 (頭名, 胴名, 頭説明, 胴説明) で 527 系列。"
                    "部位が無い系列は名前が全角ダッシュ (U+2015) になっているので、その行は出力していない "
                    "(生存 頭 502 件 / 胴 524 件 = PALICO_HEAD_I_DS / PALICO_ARMOR_I_DS の件数と一致。"
                    "系列 0 は両部位とも「装備なし」で、これは ID 0/1 の意味を残すため出力している)。"
                    "英語名は PALICO_HEAD/ARMOR_NAMES を _IDS で引いた。",
        "notes_en": "527 series x (head, body). Series whose part name is a dash are omitted; the counts match PALICO_HEAD_I_DS / PALICO_ARMOR_I_DS.",
    })

    # ---- オトモスキル ----
    palico_skill_ja = G["PALICO_SKILL_NAMES"]
    palico_skill_en = G["PALICO_SKILLS"]
    if len(palico_skill_ja) != len(palico_skill_en):
        raise SystemExit("palico skill counts differ")
    actions = read_csv(os.path.join(args.refsrc, "palico-actions.csv"))
    skill_meta = {int(r["id"]): (int(r["cost"]) if r["cost"] else "", int(r["points"]))
                  for r in actions if r["kind"] == "skill"}
    ps_rows = []
    for k in range(len(palico_skill_ja)):
        if palico_skill_en[k].startswith("NULL"):
            continue                       # 96 は gamedata.rs 側のプレースホルダ
        cost, points = skill_meta.get(k, ("", ""))
        ps_rows.append([k, norm(palico_skill_ja[k]), palico_skill_en[k], cost, points])
    write_csv("palico-skills.csv", ["palico_skill_id", "name_ja", "name_en", "cost", "points"], ps_rows)
    manifest.append({
        "id": "palico-skills", "title_ja": "オトモスキル（術）", "title_en": "Palico skills",
        "file": "palico-skills.csv", "primary_key": "palico_skill_id",
        "columns": [
            col("palico_skill_id", "int", "オトモスキルID (0..95)", "Palico skill ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("name_en", "str", "名前（英語）", "Name (English)"),
            col("cost", "int", "スロットコスト (ot_skl +5)", "Slot cost"),
            col("points", "int", "抽選ポイント (1..3、固有スキルは 0)", "Draw points"),
        ],
        "source": ["romfs/nativeNX/table/ot_skl_jpn.gmd",
                   "mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SKILLS, PALICO_SKILL_NAMES)",
                   "mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv"],
        "confidence": "verified",
        "notes_ja": "ot_skl_jpn.gmd は 2 文字列/スキルで 96 件、gamedata.rs の PALICO_SKILL_NAMES 0..95 と "
                    "位置まで一致することを mhnxeditor の romfstables.rs が検証済み。"
                    "PALICO_SKILL_NAMES/SKILLS の 97 件目 (index 96) は NULL [96] のプレースホルダなので出力していない。"
                    "ID 0 はスキル無し。cost と points は refsrc の palico-actions.csv (ot_skl の +5 と抽選ポイント) から。",
        "notes_en": "96 skills; index 96 in gamedata.rs is a NULL placeholder and is omitted.",
    })

    # ---- オトモ支援行動 ----
    moves_ja = G["PALICO_SUPPORT_MOVES"]
    move_meta = {int(r["id"]): int(r["points"]) for r in actions if r["kind"] == "move"}
    sup_rows = []
    for k, name in enumerate(moves_ja):
        if name.startswith("NULL"):
            continue
        if k not in move_meta:
            raise SystemExit("support move %d has no palico-actions row" % k)
        sup_rows.append([k, norm(name), move_meta[k]])
    write_csv("palico-support.csv", ["support_move_id", "name_ja", "points"], sup_rows)
    manifest.append({
        "id": "palico-support", "title_ja": "オトモ支援行動", "title_en": "Palico support moves",
        "file": "palico-support.csv", "primary_key": "support_move_id",
        "columns": [
            col("support_move_id", "int", "支援行動ID (0..56)", "Support move ID"),
            col("name_ja", "str", "名前（日本語）", "Name (Japanese)"),
            col("points", "int", "抽選ポイント (1..3、固有行動は 0)", "Draw points"),
        ],
        "source": ["mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SUPPORT_MOVES)",
                   "mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv"],
        "confidence": "derived",
        "notes_ja": "PALICO_SUPPORT_MOVES は 58 件で、57 件目が NULL [57] のプレースホルダなので 0..56 の 57 件を出力した。"
                    "romfs に支援行動名の gmd は無く、日本語名は gamedata.rs の表だけが持つ。英語名は無い。"
                    "points は refsrc の palico-actions.csv (otSupportIni1..3pt の抽選テーブル) から。",
        "notes_en": "57 real moves; entry 57 of PALICO_SUPPORT_MOVES is a NULL placeholder. No English names exist.",
    })

    # ================================================================
    # 第2バッチ: refsrc 由来の追加テーブル
    # ================================================================

    # ---- 防具スキル ----
    ref_armor_skills = read_csv(os.path.join(args.refsrc, "armor-skills.csv"))
    armor_ids = set(row[0] for row in armor_rows)
    ask_rows = []
    for i, r in enumerate(ref_armor_skills, 1):
        s, part = int(r["series"]), int(r["part"])
        aid = s * 5 + (part - 1)
        if aid not in armor_ids:
            raise SystemExit("armor-skills: armor_id %d is not in armor.csv" % aid)
        ask_rows.append([i, aid, s, part - 1, int(r["tree"]), int(r["points"])])
    write_csv("armor-skills.csv",
              ["row_id", "armor_id", "series_id", "part_id", "skill_id", "points"], ask_rows)
    manifest.append({
        "id": "armor-skills", "title_ja": "防具スキルポイント", "title_en": "Armor skill points",
        "file": "armor-skills.csv", "primary_key": "row_id",
        "columns": [
            col("row_id", "int", "連番 (1 始まり)。(armor_id, skill_id) が複合キーのため便宜上の主キー", "Sequential key"),
            col("armor_id", "int", "防具ID (armor.csv)。= series_id*5 + part_id", "Armor ID"),
            col("series_id", "int", "シリーズID", "Series ID"),
            col("part_id", "int", "部位ID (0=頭 1=胴 2=腕 3=腰 4=脚)", "Part ID"),
            col("skill_id", "int", "スキルID (skills.csv)", "Skill ID"),
            col("points", "int", "スキルポイント (マイナスあり)", "Skill points"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/armor-skills.csv",
                   "romfs/nativeNX/table/armorSeriesData.asd"],
        "confidence": "derived",
        "notes_ja": "armorSeriesData.asd の +28 から 15 バイト/部位 = 5 x (u16 スキルID, i8 ポイント) を読んだ結果 "
                    "(mhnxeditor の tools/skill_tables.py と同じ手順)。1 部位に最大 5 スキルが付くため複合キーになり、"
                    "SPEC 準拠で 1 列目に連番 row_id を置いた。refsrc の part は 1..5 (頭..脚) なので part_id = part-1 に直し、"
                    "armor.csv の armor_id と直接結合できるようにした。"
                    "14639 行すべてで armor_id が armor.csv に存在し、skill_id が skills.csv に存在することを確認済み。",
        "notes_en": "Read from armorSeriesData.asd +28 (5 x (u16 skill, i8 points) per part). row_id is a sequential key because (armor_id, skill_id) is composite.",
    })

    # ---- 武器派生 ----
    ref_tree = read_csv(os.path.join(args.refsrc, "weapon-tree.csv"))
    weapon_keys = set((row[1], row[2]) for row in weapon_rows if row[3] == 0)
    tree_rows = []
    for i, r in enumerate(ref_tree, 1):
        c, w, par, lv = int(r["class"]), int(r["weapon"]), int(r["parent"]), int(r["level"])
        if (c, w) not in weapon_keys:
            raise SystemExit("weapon-tree: weapon %d/%d is not in weapons.csv" % (c, w))
        if (c, par) not in weapon_keys:
            raise SystemExit("weapon-tree: parent %d/%d is not in weapons.csv" % (c, par))
        tree_rows.append([i, c, w, par, lv, c * 10000 + w * 10, c * 10000 + par * 10])
    write_csv("weapon-tree.csv",
              ["row_id", "weapon_type_id", "weapon_index", "parent_weapon_index",
               "required_level", "weapon_id", "parent_weapon_id"], tree_rows)
    manifest.append({
        "id": "weapon-tree", "title_ja": "武器派生", "title_en": "Weapon upgrade tree",
        "file": "weapon-tree.csv", "primary_key": "row_id",
        "columns": [
            col("row_id", "int", "連番 (1 始まり)。1 武器が最大 5 本へ派生するため複合キーになるので便宜上の主キー", "Sequential key"),
            col("weapon_type_id", "int", "武器種ID (weapon-types.csv)", "Weapon type ID"),
            col("weapon_index", "int", "派生先の武器ID (武器種ごと)", "Child weapon index"),
            col("parent_weapon_index", "int", "派生元の武器ID", "Parent weapon index"),
            col("required_level", "int", "派生に必要な派生元の強化レベル", "Required level"),
            col("weapon_id", "int", "派生先の weapons.csv の weapon_id (form 0)", "Child weapon_id"),
            col("parent_weapon_id", "int", "派生元の weapons.csv の weapon_id (form 0)", "Parent weapon_id"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/weapon-tree.csv",
                   "romfs/nativeNX/table/weapon*BaseData.w*d"],
        "confidence": "derived",
        "notes_ja": "weaponNNBaseData の末尾 10 バイト = 5 x (u8 必要レベル, u8 派生先武器ID) を読んだ結果 "
                    "(mhnxeditor の tools/equip_recipes.py と同じ手順)。1 武器が最大 5 本へ派生するため複合キーになり、"
                    "1 列目に連番 row_id を置いた。798 行すべてで派生先・派生元の (class, weapon) が "
                    "weapons.csv の form 0 に存在することを確認済み。",
        "notes_en": "Read from the last 10 bytes of weaponNNBaseData (5 x (u8 level, u8 child id)). row_id is sequential because the key is composite.",
    })

    # ---- 護石スキル範囲 ----
    tt_rows = []
    for i, r in enumerate(tal_tab, 1):
        tt_rows.append([i, r["kind"], int(r["tier"]), r["skill"], int(r["min"]), int(r["max"])])
    write_csv("talisman-tables.csv",
              ["row_id", "kind", "tier", "skill_id", "min_points", "max_points"], tt_rows)
    manifest.append({
        "id": "talisman-tables", "title_ja": "護石スキル抽選範囲", "title_en": "Talisman skill ranges",
        "file": "talisman-tables.csv", "primary_key": "row_id",
        "columns": [
            col("row_id", "int", "連番 (1 始まり)。(kind, tier, skill_id) が複合キーのため便宜上の主キー", "Sequential key"),
            col("kind", "str", "種別 (skill1=第1スキル, skill2=第2スキル, slots=スロット数)", "Kind"),
            col("tier", "int", "レア度 (97=神秘 98=閃光 99=風化 100=歴戦)", "Rarity tier"),
            col("skill_id", "int", "スキルID (skills.csv)。kind=slots の行は空", "Skill ID"),
            col("min_points", "int", "そのスキルに付くポイントの下限", "Min points"),
            col("max_points", "int", "上限。kind=slots の行では最大スロット数を表す", "Max points / max slots"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv",
                   "romfs/nativeNX/arc/resident.arc (amuletSkillDataNN, amuletSlotDataNN)"],
        "confidence": "derived",
        "notes_ja": "resident.arc の amuletSkillDataNN (4 バイト: u16 スキルID, i8 下限, i8 上限) と "
                    "amuletSlotDataNN から作った表 (mhnxeditor の tools/talisman_tables.py と同じ手順)。"
                    "自然キーは (kind, tier, skill_id) で、525 行すべてで一意になることを確認した "
                    "(kind=slots の 4 行は skill_id が空なので、この 3 列だけで一意)。"
                    "SPEC の「1 列目は主キー・ID 列は整数」に合わせて 1 列目に連番 row_id を置き、自然キーの 3 列はそのまま残した。"
                    "tier t は第1スキルにテーブル 2(t-97)、第2スキルに 2(t-97)+1、スロットに t-97 を使う。"
                    "神秘 (97) の第2スキルは空テーブルなので行が無い。kind=slots の 4 行は min_points=0 で "
                    "max_points がそのレア度の最大スロット数 (97->1, 98->2, 99->3, 100->3)。"
                    "525 行すべてで skill_id が skills.csv に存在することを確認済み。",
        "notes_en": "Built from amuletSkillDataNN / amuletSlotDataNN in resident.arc. The natural key is (kind, tier, skill_id), unique over all 525 rows; row_id is a sequential key so that column 1 is an integer primary key. For kind=slots, max_points is the maximum slot count.",
    })

    # ---- 調合 ----
    ref_combo = read_csv(os.path.join(args.refsrc, "combinations.csv"))
    item_name = {row[0]: row[1] for row in item_rows}
    combo_rows = []
    for i, r in enumerate(ref_combo, 1):
        a, b, res, ch = int(r["item1"]), int(r["item2"]), int(r["result"]), int(r["chance"])
        for x in (a, b, res):
            if x not in item_name:
                raise SystemExit("combinations: item %d is not in items.csv" % x)
        combo_rows.append([i, a, b, res, ch, item_name[a], item_name[b], item_name[res]])
    write_csv("combinations.csv",
              ["row_id", "item1_id", "item2_id", "result_item_id", "chance_percent",
               "item1_name_ja", "item2_name_ja", "result_name_ja"], combo_rows)
    manifest.append({
        "id": "combinations", "title_ja": "調合", "title_en": "Item combinations",
        "file": "combinations.csv", "primary_key": "row_id",
        "columns": [
            col("row_id", "int", "連番 (1 始まり)。(item1_id, item2_id) が複合キーのため便宜上の主キー", "Sequential key"),
            col("item1_id", "int", "材料1のアイテムID (items.csv)", "Material 1 item ID"),
            col("item2_id", "int", "材料2のアイテムID (items.csv)", "Material 2 item ID"),
            col("result_item_id", "int", "調合結果のアイテムID (items.csv)", "Result item ID"),
            col("chance_percent", "int", "調合成功率 (%)", "Success chance (%)"),
            col("item1_name_ja", "str", "材料1の名前（日本語）", "Material 1 name (Japanese)"),
            col("item2_name_ja", "str", "材料2の名前（日本語）", "Material 2 name (Japanese)"),
            col("result_name_ja", "str", "結果の名前（日本語）", "Result name (Japanese)"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/combinations.csv",
                   "romfs/nativeNX/table/itemPreData.itp", "romfs/nativeNX/table/itemData_jpn.gmd"],
        "confidence": "derived",
        "notes_ja": "itemPreData の 24 バイト/レコード 183 件 (+2 と +6 が材料, +10 が結果, +14 が成功率%) を "
                    "読んだ結果 (mhnxeditor の tools/item_combos.py と同じ手順)。(item1, item2) は 183 行で重複なし。"
                    "数値だけでは読めないので、items.csv から引いた名前 3 列を併記した (参照先が単一なので値の揺れは無い)。"
                    "183 行すべてで 3 つのアイテムIDが items.csv に存在することを確認済み。",
        "notes_en": "Read from itemPreData (24-byte records: materials at +2/+6, result at +10, chance% at +14). Item names are joined from items.csv.",
    })

    # ---- 鍛冶屋リスト ----
    ref_smithy = read_csv(os.path.join(args.refsrc, "smithy-lists.csv"))
    smithy_rows = []
    for i, r in enumerate(ref_smithy, 1):
        lst = r["list"]
        kind, _, sub = lst.partition(":")
        class_id = sub if (kind in ("weapon", "armor") and sub.isdigit()) else ""
        smithy_rows.append([i, lst, kind, class_id, int(r["records"]), r["ids"]])
    write_csv("smithy-lists.csv",
              ["row_id", "list_name", "kind", "class_id", "records", "ids"], smithy_rows)
    manifest.append({
        "id": "smithy-lists", "title_ja": "鍛冶屋リスト", "title_en": "Smithy lists",
        "file": "smithy-lists.csv", "primary_key": "row_id",
        "columns": [
            col("row_id", "int", "連番 (1 始まり)。元のキーが文字列 (list) なので便宜上の主キー", "Sequential key"),
            col("list_name", "str", "元データのリスト名 (weapon:0, armor:1, deco, palico:helm ...)", "List name"),
            col("kind", "str", "list_name の前半 (weapon / armor / deco / palico)", "List kind"),
            col("class_id", "int", "kind が weapon / armor のときの武器種ID・部位ID。それ以外は空", "Class or part id"),
            col("records", "int", "そのリストのレコード数", "Record count"),
            col("ids", "str", "レコードごとの 1 桁コードの並び (armor のみ。意味未確定)", "Per-record code string"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/smithy-lists.csv",
                   "romfs/nativeNX/arc/facility/blacksmith.arc"],
        "confidence": "derived",
        "notes_ja": "blacksmith.arc の weaponCreateWNN / armorCreateANN / decoCreate / otWeaponCreate / otArmorCreate の "
                    "レコード数を数えたもの (mhnxeditor の tools/smithy_lists.py)。"
                    "元の主キーは list という文字列なので、SPEC の「1 列目は主キー・ID は整数」に合わせて "
                    "連番 row_id を 1 列目に置き、list_name をそのまま残した。kind / class_id は list_name から機械的に分割しただけ。"
                    "ids 列は armor の 5 行だけ値が入る 1 桁コードの並びで、意味は未確定のため生のまま残した。",
        "notes_en": "Record counts of the blacksmith.arc create tables. row_id is sequential because the original key is a string.",
    })

    # ---- オトモ行動 ----
    move_names = {row[0]: row[1] for row in sup_rows}
    skill_names_map = {row[0]: row[1] for row in ps_rows}
    pact_rows = []
    for i, r in enumerate(actions, 1):
        kind, aid = r["kind"], int(r["id"])
        nm = move_names.get(aid, "") if kind == "move" else skill_names_map.get(aid, "")
        pact_rows.append([i, kind, aid, int(r["points"]), r["cost"], nm])
    write_csv("palico-actions.csv",
              ["row_id", "kind", "action_id", "points", "cost", "name_ja"], pact_rows)
    manifest.append({
        "id": "palico-actions", "title_ja": "オトモ行動（支援行動・スキル）", "title_en": "Palico actions",
        "file": "palico-actions.csv", "primary_key": "row_id",
        "columns": [
            col("row_id", "int", "連番 (1 始まり)。(kind, action_id) が複合キーのため便宜上の主キー", "Sequential key"),
            col("kind", "str", "種別 (move=支援行動, skill=オトモスキル)", "Kind"),
            col("action_id", "int", "kind ごとの ID (palico-support.csv / palico-skills.csv)", "Action ID"),
            col("points", "int", "抽選ポイント (1..3、固有のものは 0)", "Draw points"),
            col("cost", "int", "スロットコスト (skill のみ。move は空)", "Slot cost"),
            col("name_ja", "str", "名前（日本語）。palico-support / palico-skills から引いた", "Name (Japanese)"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv",
                   "romfs/nativeNX/arc/resident.arc (otomo/ot_skl, otomo/support/spt_act_base, table/lobby/otSupportIni*pt, otSkillIni*pt)"],
        "confidence": "derived",
        "notes_ja": "resident.arc の otomo/ot_skl (11 バイト: u32 ID, u8 ID, +5 スロットコスト) と "
                    "otomo/support/spt_act_base、table/lobby/otSupportIni{1,2,3}pt / otSkillIni{1,2,3}pt (抽選ポイント) から作った表 "
                    "(mhnxeditor の tools/palico_tables.py と同じ手順)。"
                    "move 58 件 + skill 96 件 = 154 件。(kind, action_id) が複合キーなので連番 row_id を 1 列目に置いた。"
                    "move の id 57 は spt_act_base にレコードがあるが gamedata.rs 側の名前が NULL プレースホルダなので name_ja が空。"
                    "name_ja は palico-support.csv / palico-skills.csv から引いた (参照先が単一なので値の揺れは無い)。",
        "notes_en": "Built from ot_skl / spt_act_base / otSupportIni*pt / otSkillIni*pt in resident.arc. 58 moves + 96 skills.",
    })

    # ---- オトモレベル ----
    ref_levels = read_csv(os.path.join(args.refsrc, "palico-levels.csv"))
    pl_rows = [[int(r["level"]), int(r["support_slots"]), int(r["skill_slots"])] for r in ref_levels]
    pl_rows.sort()
    write_csv("palico-levels.csv", ["level", "support_slots", "skill_slots"], pl_rows)
    manifest.append({
        "id": "palico-levels", "title_ja": "オトモレベル", "title_en": "Palico levels",
        "file": "palico-levels.csv", "primary_key": "level",
        "columns": [
            col("level", "int", "オトモレベル (1..99)", "Palico level"),
            col("support_slots", "int", "自由に付けられる支援行動スロット数 (ot_lvl +10)", "Support move slots"),
            col("skill_slots", "int", "装備できるオトモスキルのスロット数 (ot_lvl +11)", "Skill slots"),
        ],
        "source": ["mhnxeditor/.work/finalaudit/refsrc/data/palico-levels.csv",
                   "romfs/nativeNX/arc/resident.arc (otomo/ot_lvl)"],
        "confidence": "derived",
        "notes_ja": "resident.arc の otomo/ot_lvl (15 バイト/レベル, 99 件) の +10 と +11 を読んだもの "
                    "(mhnxeditor の tools/palico_tables.py と同じ手順)。level は 1..99 で重複なしなのでそのまま主キーにした。",
        "notes_en": "Read from otomo/ot_lvl +10 and +11 (99 levels).",
    })

    # ---- manifest ----
    for t in manifest:
        path = os.path.join(OUT, t["file"])
        with open(path, encoding="utf-8-sig", newline="") as f:
            r = csv.reader(f)
            header = next(r)
            rows = list(r)
        names = [c["name"] for c in t["columns"]]
        if header != names:
            raise SystemExit("%s: header %s != manifest %s" % (t["file"], header, names))
        if header[0] != t["primary_key"]:
            raise SystemExit("%s: first column is not the primary key" % t["file"])
        keys = [row[0] for row in rows]
        if len(set(keys)) != len(keys):
            raise SystemExit("%s: duplicate primary key" % t["file"])
        t["row_count"] = len(rows)
        t["id_range"] = [min(int(k) for k in keys), max(int(k) for k in keys)] if keys else None
        print("  ok %-28s rows=%d id_range=%s" % (t["file"], len(rows), t["id_range"]))
    manifest.sort(key=lambda t: t["id"])
    with open(os.path.join(OUT, "_manifest.json"), "w", encoding="utf-8", newline="") as f:
        json.dump({"area": "equip", "tables": manifest}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    total = sum(t["row_count"] for t in manifest)
    print("")
    print("%d tables, %d rows total" % (len(manifest), total))


if __name__ == "__main__":
    main(sys.argv[1:])
