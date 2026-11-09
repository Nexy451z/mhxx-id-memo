#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO レビュー用: 出典データのローダ群 (reviewer 専用).

リポジトリ外の元データを読み取り専用でロードする。
  - extract/jp_names/*.csv        (UTF-8 BOM)
  - mhnxeditor/.work/finalaudit/refsrc/data/*.csv  (UTF-8 BOM なし)
  - mhnxeditor/crates/mhnx-core/src/gamedata.rs    (Rust 定数)
"""
import csv
import io
import os
import re

SRC = r"C:\anyWorkspace\nx\mhxx"
JP = os.path.join(SRC, "extract", "jp_names")
REFSRC = os.path.join(SRC, "mhnxeditor", ".work", "finalaudit", "refsrc", "data")
GAMEDATA_RS = os.path.join(SRC, "mhnxeditor", "crates", "mhnx-core", "src", "gamedata.rs")


def read_csv(path):
    """BOM/改行を吸収して list[dict] を返す。存在しなければ None。"""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        raw = f.read()
    text = raw.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def jp(name):
    return read_csv(os.path.join(JP, name))


def ref(name):
    return read_csv(os.path.join(REFSRC, name))


# --------------------------------------------------------------------------
# gamedata.rs パーサ
# --------------------------------------------------------------------------
_STR_ARR = re.compile(r"pub\s+static\s+([A-Z0-9_]+)\s*:\s*&\[\s*&str\s*\]\s*=\s*&\[(.*?)\];", re.S)
_INT_ARR = re.compile(r"pub\s+static\s+([A-Z0-9_]+)\s*:\s*&\[\s*i32\s*\]\s*=\s*&\[(.*?)\];", re.S)
_STR_LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
_INT_LIT = re.compile(r"-?\d+")


def load_gamedata(path=GAMEDATA_RS):
    """{'NAME': [str,...] or [int,...]} を返す。"""
    if not os.path.exists(path):
        return {}
    src = open(path, encoding="utf-8").read()
    out = {}
    for m in _STR_ARR.finditer(src):
        out[m.group(1)] = [s.replace('\\"', '"').replace("\\\\", "\\") for s in _STR_LIT.findall(m.group(2))]
    for m in _INT_ARR.finditer(src):
        out[m.group(1)] = [int(x) for x in _INT_LIT.findall(m.group(2))]
    return out


# --------------------------------------------------------------------------
# 個別ローダ (遅延)
# --------------------------------------------------------------------------
_cache = {}


def _memo(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def gamedata():
    return _memo("gamedata", load_gamedata)


def items_src():
    """extract/jp_names/items.csv : item_id,name,desc"""
    def f():
        rows = jp("items.csv") or []
        return {int(r["item_id"]): r for r in rows}
    return _memo("items", f)


def weapons_src():
    """extract/jp_names/weapons.csv : type_id,type,weapon_id,form,levels,name,desc"""
    def f():
        rows = jp("weapons.csv") or []
        out = {}
        for r in rows:
            out[(int(r["type_id"]), int(r["weapon_id"]), int(r["form"]))] = r
        return out
    return _memo("weapons", f)


def armor_src():
    """extract/jp_names/armor_series.csv : series_id,part,name,desc"""
    def f():
        rows = jp("armor_series.csv") or []
        out = {}
        for r in rows:
            out[(int(r["series_id"]), r["part"])] = r
        return out
    return _memo("armor", f)


def skills_src():
    """extract/jp_names/skills.csv : index,name,desc"""
    def f():
        rows = jp("skills.csv") or []
        return {int(r["index"]): r for r in rows}
    return _memo("skills", f)


def amulet_src():
    def f():
        rows = jp("amulet.csv") or []
        return {int(r["amulet_id"]): r for r in rows}
    return _memo("amulet", f)


def palico_weapon_src():
    def f():
        rows = jp("palico_weapon.csv") or []
        return {int(r["weapon_id"]): r for r in rows}
    return _memo("palico_weapon", f)


def palico_armor_src():
    def f():
        rows = jp("palico_armor.csv") or []
        out = {}
        for r in rows:
            out.setdefault((int(r["series_id"]), r["part"]), r)
        return out
    return _memo("palico_armor", f)


def monster_index():
    def f():
        rows = ref("monster-index.csv") or []
        return {int(r["index"]): r for r in rows}
    return _memo("monster_index", f)


def quest_index():
    def f():
        rows = ref("quest-index.csv") or []
        return {int(r["quest_id"]): r for r in rows}
    return _memo("quest_index", f)


def quest_info():
    def f():
        rows = ref("quest-info.csv") or []
        return {int(r["quest_id"]): r for r in rows}
    return _memo("quest_info", f)


def npc_index():
    def f():
        rows = ref("npc-index.csv") or []
        return {int(r["npc_id"]): r for r in rows}
    return _memo("npc_index", f)


def awards_src():
    def f():
        rows = ref("awards.csv") or []
        return {int(r["bit"]): r for r in rows}
    return _memo("awards", f)


def canteen_src():
    def f():
        return ref("canteen.csv") or []
    return _memo("canteen", f)


def provisions_src():
    def f():
        return ref("provisions.csv") or []
    return _memo("provisions", f)


def request_index():
    def f():
        return ref("request-index.csv") or []
    return _memo("request_index", f)


def monster_carves_src():
    def f():
        return ref("monster-carves.csv") or []
    return _memo("monster_carves", f)


def recipes_src():
    def f():
        return ref("recipes.csv") or []
    return _memo("recipes", f)


def decorations_src():
    def f():
        return ref("decorations.csv") or []
    return _memo("decorations", f)


def hunter_arts_src():
    def f():
        rows = ref("hunter-arts.csv") or []
        return {int(r["id"]): r for r in rows}
    return _memo("hunter_arts", f)


def arena_src():
    def f():
        return ref("arena.csv") or []
    return _memo("arena", f)


def talisman_tables_src():
    def f():
        return ref("talisman-tables.csv") or []
    return _memo("talisman_tables", f)


def skill_trees_src():
    def f():
        return ref("skill-trees.csv") or []
    return _memo("skill_trees", f)


def quest_monsters_src():
    def f():
        return ref("quest-monsters.csv") or []
    return _memo("quest_monsters", f)


def quest_rewards_src():
    def f():
        return ref("quest-rewards.csv") or []
    return _memo("quest_rewards", f)


def name_corpus():
    """全出典の文字列値の集合 (捏造検出用)。"""
    def f():
        corpus = set()
        for fn in ("items.csv", "weapons.csv", "armor_series.csv", "skills.csv",
                   "amulet.csv", "palico_weapon.csv", "palico_armor.csv"):
            rows = jp(fn) or []
            for r in rows:
                for v in r.values():
                    if v:
                        corpus.add(v.strip())
        for fn in os.listdir(REFSRC) if os.path.isdir(REFSRC) else []:
            if not fn.endswith(".csv"):
                continue
            rows = ref(fn) or []
            for r in rows:
                for v in r.values():
                    if v:
                        corpus.add(v.strip())
        for vals in gamedata().values():
            for v in vals:
                if isinstance(v, str) and v:
                    corpus.add(v.strip())
        # romfs のゲーム内テキスト (GMD) も出典コーパスに含める
        import glob as _glob
        for p in sorted(_glob.glob(os.path.join(ROMFS_TB, "*.gmd"))):
            try:
                _k, vals = parse_gmd(open(p, "rb").read())
            except Exception:
                continue
            for v in vals:
                if v and v.strip():
                    corpus.add(v.strip())
        for vals in questfields().values():
            for v in vals:
                if v and v.strip():
                    corpus.add(v.strip())
        # クエスト ARC 内の questData_*_jpn (クエスト名・依頼文)
        for v in quest_texts():
            if v and v.strip():
                corpus.add(v.strip())
        return corpus
    return _memo("corpus", f)


# --------------------------------------------------------------------------
# romfs GMD (ゲーム内テキスト) — 一次資料
# --------------------------------------------------------------------------
ROMFS_TB = os.path.join(SRC, "romfs", "nativeNX", "table")
QUESTFIELDS_RS = os.path.join(SRC, "mhnxeditor", "crates", "mhnx-core", "src", "questfields.rs")


def parse_gmd(b):
    """GMD を (key, [str,...]) に分解する。

    MHXX Switch (version 0x00010302) のレイアウト:
      +0x18 u32 文字列数 / +0x20 u32 テキストブロックのバイト数 / +0x24 u32 key 長
      +0x28 key + NUL。テキストブロックは **ファイル末尾の size バイト**。
    +0x1C が 0 でないファイル (NpcName / GC_Medal / Kitchen / activityData 等) は
    key とテキストの間にハッシュ表が挟まるため、末尾基準でないと読めない。
    """
    if b[0:4] != b"GMD\x00":
        raise ValueError("not GMD")
    import struct
    count, = struct.unpack_from("<I", b, 0x18)
    size, = struct.unpack_from("<I", b, 0x20)
    key_len, = struct.unpack_from("<I", b, 0x24)
    key = b[0x28:0x28 + key_len].decode("utf-8", "replace")
    if 0 < size <= len(b):
        text = b[len(b) - size:]
    else:
        text = b[0x28 + key_len + 1:]
    return key, [x.decode("utf-8", "replace") for x in text.split(b"\0")[:count]]


def gmd(name):
    """romfs/nativeNX/table/<name> をパース。失敗時は None。"""
    def f():
        p = os.path.join(ROMFS_TB, name)
        if not os.path.exists(p):
            return None
        try:
            return parse_gmd(open(p, "rb").read())
        except Exception:
            return None
    return _memo("gmd:" + name, f)


ARC_QUEST = os.path.join(SRC, "romfs", "nativeNX", "arc", "quest")


def read_arc(path):
    """ARC を {entry 名: bytes} に展開する。"""
    import struct
    import zlib
    d = open(path, "rb").read()
    if d[:4] != b"ARC\x00":
        raise ValueError("not arc")
    n = struct.unpack_from("<H", d, 6)[0]
    out = {}
    for i in range(n):
        e = d[0xC + i * 0x50:0xC + (i + 1) * 0x50]
        if len(e) < 80:
            break
        name = e[:64].split(b"\0")[0].decode("utf-8", "replace")
        _, cs, ds, off = struct.unpack_from("<4I", e, 64)
        raw = d[off:off + cs]
        try:
            out[name] = zlib.decompress(raw) if (cs != (ds & 0x1FFFFFFF) or raw[:1] == b"\x78") else raw
        except Exception:
            out[name] = b""
    return out


def quest_texts():
    """クエスト ARC 内の questData_*_jpn (GMD) の文字列を全部集める。"""
    def f():
        import glob as _glob
        vals = []
        for p in sorted(_glob.glob(os.path.join(ARC_QUEST, "q*.arc"))):
            try:
                ents = read_arc(p)
            except Exception:
                continue
            for name, blob in ents.items():
                if not name.endswith("_jpn") or not blob:
                    continue
                try:
                    _k, ss = parse_gmd(blob)
                except Exception:
                    continue
                vals.extend(ss)
        return vals
    return _memo("quest_texts", f)


def item_categories_gmd():
    r = gmd("itemCategoryTypeData_jpn.gmd")
    return r[1] if r else None


def insect_data_gmd():
    r = gmd("insectData_jpn.gmd")
    return r[1] if r else None


def questfields():
    """questfields.rs の pub static ENUM_* を {name: [str]} で返す。"""
    def f():
        if not os.path.exists(QUESTFIELDS_RS):
            return {}
        src = open(QUESTFIELDS_RS, encoding="utf-8").read()
        out = {}
        for m in _STR_ARR.finditer(src):
            out[m.group(1)] = [s.replace('\\"', '"').replace("\\\\", "\\")
                               for s in _STR_LIT.findall(m.group(2))]
        return out
    return _memo("questfields", f)


if __name__ == "__main__":
    gd = gamedata()
    print("gamedata constants:", len(gd))
    for k in ("MONSTER_HUNT_NAMES", "HUNT_WEAPONS", "SKILL_NAMES", "JWL_NAMES", "JWL_I_DS",
              "EQUIP_TALISMAN_NAMES", "TALISMAN_RARITY", "KINSECT_NAMES", "PALICO_WEAPON_NAMES",
              "PALICO_SKILLS", "PALICO_SUPPORT_MOVES"):
        v = gd.get(k)
        print("  %-24s len=%s" % (k, len(v) if v is not None else "MISSING"))
    print("items_src:", len(items_src()))
    print("weapons_src:", len(weapons_src()))
    print("armor_src:", len(armor_src()))
    print("skills_src:", len(skills_src()))
    print("monster_index:", len(monster_index()))
    print("quest_index:", len(quest_index()))
    print("npc_index:", len(npc_index()))
    print("name_corpus:", len(name_corpus()))
