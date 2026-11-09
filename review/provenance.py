#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: 出典整合 (reviewer).

各テーブルから無作為に N 行を抽出し、一次資料と突き合わせる。
比較時は改行を LF に正規化する (SPEC §0.6 の LF 規約に合わせる)。

使い方:
    python review/provenance.py [--repo DIR] [--n 20] [--seed 20260101] [--table items]
"""
import argparse
import csv
import io
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources as S

REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"
PARTS = ["頭", "胴", "腕", "腰", "脚"]
results = []
notes_out = []


def note(tid, msg):
    """不一致ではないが記録すべき差 (表記差・プレースホルダ扱いなど)。"""
    notes_out.append({"table": tid, "note": msg})


def rec(tid, checked, mismatches, note="", skipped=False):
    results.append({"table": tid, "checked": checked, "mismatches": mismatches,
                    "note": note, "skipped": skipped})


def read_csv(path):
    raw = open(path, "rb").read()
    body = raw[3:] if raw[:3] == b"\xef\xbb\xbf" else raw
    rdr = csv.reader(io.StringIO(body.decode("utf-8", errors="replace"), newline=""))
    rows = list(rdr)
    return (rows[0], rows[1:]) if rows else ([], [])


def col(header, *cands):
    low = {h.lower(): i for i, h in enumerate(header)}
    for c in cands:
        if c.lower() in low:
            return low[c.lower()]
    return None


def val(row, i):
    return row[i] if (i is not None and i < len(row)) else ""


def nl(s):
    """改行を LF に正規化 (SPEC §0.6)。"""
    return (s or "").replace("\r\n", "\n").replace("\r", "\n")


def sample(rows, n, seed, tid):
    if len(rows) <= n:
        return list(range(len(rows)))
    rnd = random.Random("%s:%s" % (seed, tid))
    return sorted(rnd.sample(range(len(rows)), n))


# ==========================================================================
# アダプタ
# ==========================================================================
def a_items(header, rows, idxs):
    src = S.items_src()
    i_id, i_ja = col(header, "item_id"), col(header, "name_ja")
    i_desc = col(header, "desc_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        s = src.get(int(rid))
        if s is None:
            bad.append((r + 2, "item_id", "itemData に存在", rid)); continue
        if i_ja is not None and val(row, i_ja) != s["name"]:
            bad.append((r + 2, "name_ja", s["name"], val(row, i_ja)))
        if i_desc is not None and nl(val(row, i_desc)) != nl(s["desc"]):
            bad.append((r + 2, "desc_ja", nl(s["desc"])[:50], nl(val(row, i_desc))[:50]))
    return n, bad, "items.csv (itemData_jpn.gmd) と name/desc を突合"


def a_weapons(header, rows, idxs):
    src = S.weapons_src()
    i_t = col(header, "weapon_type_id", "type_id")
    i_w = col(header, "weapon_index", "weapon_id")
    i_f = col(header, "form")
    i_ja, i_lv = col(header, "name_ja"), col(header, "levels")
    bad, n = [], 0
    if None in (i_t, i_w, i_f):
        return 0, [], "weapon_type_id/weapon_index/form が見つからない"
    for r in idxs:
        row = rows[r]
        t, w, f = val(row, i_t), val(row, i_w), val(row, i_f)
        if not (t.isdigit() and w.isdigit() and f.isdigit()):
            continue
        n += 1
        s = src.get((int(t), int(w), int(f)))
        if s is None:
            bad.append((r + 2, "(type,index,form)", "weaponNNMsgData に存在", (t, w, f))); continue
        if i_ja is not None and val(row, i_ja) != s["name"]:
            bad.append((r + 2, "name_ja", s["name"], val(row, i_ja)))
        if i_lv is not None and val(row, i_lv) != s["levels"]:
            bad.append((r + 2, "levels", s["levels"], val(row, i_lv)))
    return n, bad, "weapons.csv (weaponNNMsgData_jpn.gmd) と name/levels を突合"


def a_armor(header, rows, idxs):
    src = S.armor_src()
    i_s, i_p = col(header, "series_id"), col(header, "part_id")
    i_ja, i_desc = col(header, "name_ja"), col(header, "desc_ja")
    bad, n = [], 0
    if None in (i_s, i_p):
        return 0, [], "series_id/part_id が見つからない"
    for r in idxs:
        row = rows[r]
        s_id, p_id = val(row, i_s), val(row, i_p)
        if not (s_id.isdigit() and p_id.isdigit() and int(p_id) < len(PARTS)):
            continue
        n += 1
        s = src.get((int(s_id), PARTS[int(p_id)]))
        if s is None:
            bad.append((r + 2, "(series_id,part)", "armor_series に存在", (s_id, p_id))); continue
        if i_ja is not None and val(row, i_ja) != s["name"]:
            bad.append((r + 2, "name_ja", s["name"], val(row, i_ja)))
        if i_desc is not None and nl(val(row, i_desc)) != nl(s["desc"]):
            bad.append((r + 2, "desc_ja", nl(s["desc"])[:40], nl(val(row, i_desc))[:40]))
    return n, bad, "armor_series.csv と name/desc を突合"


def a_skills(header, rows, idxs):
    """skills.csv は SKILL_NAMES の ID 空間。日本語は skillTypeData の (name,desc) 対。"""
    gd = S.gamedata()
    sk = gd.get("SKILL_NAMES", [])
    st = (S.gmd("skillTypeData_jpn.gmd") or (None, []))[1]
    i_id = col(header, "skill_id", "id")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    i_desc = col(header, "desc_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if k < len(sk) and i_en is not None and val(row, i_en) != sk[k]:
            bad.append((r + 2, "name_en(SKILL_NAMES[%d])" % k, sk[k], val(row, i_en)))
        if 2 * k < len(st) and i_ja is not None and val(row, i_ja) != st[2 * k]:
            bad.append((r + 2, "name_ja(skillTypeData[%d])" % (2 * k), st[2 * k], val(row, i_ja)))
        if 2 * k + 1 < len(st) and i_desc is not None and nl(val(row, i_desc)) != nl(st[2 * k + 1]):
            bad.append((r + 2, "desc_ja(skillTypeData[%d])" % (2 * k + 1),
                        nl(st[2 * k + 1])[:40], nl(val(row, i_desc))[:40]))
    return n, bad, "SKILL_NAMES / skillTypeData_jpn.gmd と突合"


def a_skill_effects(header, rows, idxs):
    src = S.skills_src()
    i_id = col(header, "effect_id", "id")
    i_ja, i_desc = col(header, "name_ja"), col(header, "desc_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        s = src.get(int(rid))
        if s is None:
            bad.append((r + 2, "effect_id", "skillData に存在", rid)); continue
        if i_ja is not None and val(row, i_ja) != s["name"]:
            bad.append((r + 2, "name_ja", s["name"], val(row, i_ja)))
        if i_desc is not None and nl(val(row, i_desc)) != nl(s["desc"]):
            bad.append((r + 2, "desc_ja", nl(s["desc"])[:40], nl(val(row, i_desc))[:40]))
    return n, bad, "jp_names/skills.csv (skillData_jpn.gmd) と突合"


def a_decorations(header, rows, idxs):
    gd = S.gamedata()
    ids, names = gd.get("JWL_I_DS", []), gd.get("JWL_NAMES", [])
    items = S.items_src()
    i_id = col(header, "decoration_id", "id")
    i_item, i_en = col(header, "item_id"), col(header, "name_en")
    i_ja = col(header, "name_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        did, item = val(row, i_id), val(row, i_item)
        if not did.isdigit():
            continue
        n += 1
        k = int(did)
        if k < len(names) and i_en is not None and val(row, i_en) != names[k]:
            bad.append((r + 2, "name_en(JWL_NAMES[%d])" % k, names[k], val(row, i_en)))
        if k < len(ids) and item.isdigit() and int(item) != ids[k]:
            bad.append((r + 2, "item_id(JWL_I_DS[%d])" % k, ids[k], item))
        if item.isdigit():
            s = items.get(int(item))
            if s and i_ja is not None and val(row, i_ja) != s["name"]:
                bad.append((r + 2, "name_ja(itemData)", s["name"], val(row, i_ja)))
    return n, bad, "JWL_NAMES / JWL_I_DS / itemData と突合"


def a_talismans(header, rows, idxs):
    gd = S.gamedata()
    names, rar = gd.get("EQUIP_TALISMAN_NAMES", []), gd.get("TALISMAN_RARITY", [])
    i_id = col(header, "talisman_id", "id")
    i_en, i_r = col(header, "name_en"), col(header, "rarity")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if k >= len(names):
            bad.append((r + 2, "talisman_id", "< %d" % len(names), rid)); continue
        if i_en is not None:
            got = val(row, i_en)
            if got != names[k]:
                if names[k] == "(None)" and got == "":
                    note("talismans", "id %d: 出典の \"(None)\" を空文字に置換 (SPEC §2 の空文字方針)" % k)
                else:
                    bad.append((r + 2, "name_en", names[k], got))
        if i_r is not None and k < len(rar) and val(row, i_r) != str(rar[k]):
            bad.append((r + 2, "rarity", rar[k], val(row, i_r)))
    return n, bad, "EQUIP_TALISMAN_NAMES / TALISMAN_RARITY と突合"


def a_hunter_arts(header, rows, idxs):
    src = S.hunter_arts_src()
    i_id, i_en = col(header, "art_id", "id"), col(header, "name_en")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        s = src.get(int(rid))
        if s is None:
            bad.append((r + 2, "art_id", "hunter-arts.csv に存在", rid)); continue
        if i_en is not None and val(row, i_en) != s["name"]:
            bad.append((r + 2, "name_en", s["name"], val(row, i_en)))
    return n, bad, "refsrc hunter-arts.csv と突合"


def a_weapon_types(header, rows, idxs):
    """武器種 ID は 5 が欠番。HUNT_WEAPONS は密 (0..14) なので hunt_weapon_index 経由で照合。"""
    gd = S.gamedata()
    hw = gd.get("HUNT_WEAPONS", [])
    i_id = col(header, "weapon_type_id", "type_id", "id")
    i_en, i_hwi = col(header, "name_en"), col(header, "hunt_weapon_index")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        hwi = val(row, i_hwi)
        if i_hwi is not None:
            # hunt_weapon_index が空 = 欠番 (weapon 05)。比較しない。
            if hwi.isdigit() and int(hwi) < len(hw) and i_en is not None and val(row, i_en) != hw[int(hwi)]:
                bad.append((r + 2, "name_en(HUNT_WEAPONS[%s])" % hwi, hw[int(hwi)], val(row, i_en)))
        elif k < len(hw) and i_en is not None and val(row, i_en) != hw[k]:
            bad.append((r + 2, "name_en", hw[k], val(row, i_en)))
    return n, bad, "HUNT_WEAPONS (hunt_weapon_index 経由) と突合"


def a_kinsects(header, rows, idxs):
    gd = S.gamedata()
    kn, ins = gd.get("KINSECT_NAMES", []), (S.insect_data_gmd() or [])
    i_id = col(header, "kinsect_id", "id")
    i_en, i_ja = col(header, "name_en"), col(header, "name_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if i_en is not None and k < len(kn):
            got = val(row, i_en)
            if got != kn[k]:
                if kn[k] == "(None)" and got == "":
                    note("kinsects", "id %d: 出典の \"(None)\" を空文字に置換 (SPEC §2 の空文字方針)" % k)
                else:
                    bad.append((r + 2, "name_en", kn[k], got))
        if i_ja is not None and k < len(ins) and val(row, i_ja) != ins[k]:
            bad.append((r + 2, "name_ja", ins[k], val(row, i_ja)))
    return n, bad, "KINSECT_NAMES / insectData_jpn.gmd と突合"


def a_palico_weapons(header, rows, idxs):
    gd = S.gamedata()
    pn, src = gd.get("PALICO_WEAPON_NAMES", []), S.palico_weapon_src()
    i_id = col(header, "palico_weapon_id", "weapon_id", "id")
    i_en, i_ja = col(header, "name_en"), col(header, "name_ja")
    i_desc = col(header, "desc_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if i_en is not None and k < len(pn) and val(row, i_en) != pn[k]:
            bad.append((r + 2, "name_en", pn[k], val(row, i_en)))
        s = src.get(k)
        if s:
            if i_ja is not None and val(row, i_ja) != s["name"]:
                bad.append((r + 2, "name_ja", s["name"], val(row, i_ja)))
            if i_desc is not None and nl(val(row, i_desc)) != nl(s["desc"]):
                bad.append((r + 2, "desc_ja", nl(s["desc"])[:40], nl(val(row, i_desc))[:40]))
    return n, bad, "PALICO_WEAPON_NAMES / palico_weapon.csv と突合"


def a_palico_armor(header, rows, idxs):
    gd = S.gamedata()
    head, hids = gd.get("PALICO_HEAD_NAMES", []), gd.get("PALICO_HEAD_I_DS", [])
    body, bids = gd.get("PALICO_ARMOR_NAMES", []), gd.get("PALICO_ARMOR_I_DS", [])
    src = S.palico_armor_src()
    # series_id はゲーム ID。_NAMES は密 index なので _IDS で逆引きする。
    inv = {}
    for i, v in enumerate(hids):
        inv.setdefault(("0", v), i)
    for i, v in enumerate(bids):
        inv.setdefault(("1", v), i)
    i_s, i_p = col(header, "series_id"), col(header, "part_id")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    bad, n = [], 0
    if None in (i_s, i_p):
        return 0, [], "series_id/part_id が見つからない"
    for r in idxs:
        row = rows[r]
        s_id, p_id = val(row, i_s), val(row, i_p)
        if not (s_id.isdigit() and p_id.isdigit()):
            continue
        n += 1
        k = int(s_id)
        names = head if p_id == "0" else body
        idx = inv.get((p_id, k))
        if idx is None:
            bad.append((r + 2, "series_id", "_IDS に存在", k))
        elif i_en is not None and val(row, i_en) != names[idx]:
            bad.append((r + 2, "name_en(_NAMES[%d])" % idx, names[idx], val(row, i_en)))
        part = "頭" if p_id == "0" else "胴"
        s = src.get((k, part))
        if s and i_ja is not None and val(row, i_ja) != s["name"]:
            bad.append((r + 2, "name_ja", s["name"], val(row, i_ja)))
    return n, bad, "PALICO_HEAD/ARMOR_NAMES (逆引き _IDS) / otArmorData_jpn.gmd と突合"


def a_palico_skills(header, rows, idxs):
    gd = S.gamedata()
    ps = gd.get("PALICO_SKILLS", [])
    i_id = col(header, "palico_skill_id", "skill_id", "id")
    i_en = col(header, "name_en")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if i_en is not None and k < len(ps) and val(row, i_en) != ps[k]:
            bad.append((r + 2, "name_en", ps[k], val(row, i_en)))
    return n, bad, "PALICO_SKILLS と突合"


def a_palico_support(header, rows, idxs):
    gd = S.gamedata()
    ps = gd.get("PALICO_SUPPORT_MOVES", [])
    i_id = col(header, "support_move_id", "support_id", "move_id", "id")
    i_ja = col(header, "name_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if i_ja is not None and k < len(ps) and val(row, i_ja) != ps[k]:
            bad.append((r + 2, "name_ja", ps[k], val(row, i_ja)))
    return n, bad, "PALICO_SUPPORT_MOVES と突合"


def a_armor_parts(header, rows, idxs):
    i_id = col(header, "part_id", "id")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    gd = S.gamedata()
    et = gd.get("EQUIPMENT_TYPES", [])
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if k < len(PARTS) and i_ja is not None and val(row, i_ja) != PARTS[k]:
            bad.append((r + 2, "name_ja", PARTS[k], val(row, i_ja)))
        if k + 1 < len(et) and i_en is not None and val(row, i_en) != et[k + 1]:
            bad.append((r + 2, "name_en(EQUIPMENT_TYPES[%d])" % (k + 1), et[k + 1], val(row, i_en)))
    return n, bad, "gen.py PARTS / EQUIPMENT_TYPES と突合"


def a_item_categories(header, rows, idxs):
    cats = S.item_categories_gmd() or []
    i_id = col(header, "category_id", "id")
    i_ja = col(header, "name_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        if k >= len(cats):
            bad.append((r + 2, "category_id", "< %d" % len(cats), rid))
        elif i_ja is not None and val(row, i_ja) != cats[k]:
            bad.append((r + 2, "name_ja", cats[k], val(row, i_ja)))
    return n, bad, "itemCategoryTypeData_jpn.gmd と突合"


# ---------------- world ----------------
def a_monsters(header, rows, idxs):
    """monster_id はセーブの狩猟記録の添字 1..137。MONSTER_HUNT_NAMES は 0 始まりで同順。"""
    mi = S.monster_index()
    gd = S.gamedata()
    hunt = gd.get("MONSTER_HUNT_NAMES", [])
    i_id = col(header, "monster_id", "id", "index")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        s = mi.get(k)
        if s is None:
            bad.append((r + 2, "monster_id", "monster-index.csv に存在", rid))
        elif i_en is not None and val(row, i_en) and val(row, i_en) != s["monster"]:
            bad.append((r + 2, "name_en", s["monster"], val(row, i_en)))
        # MONSTER_HUNT_NAMES[k-1] が正 (docs: entry i-1)
        if i_ja is not None:
            if 1 <= k <= len(hunt):
                exp = hunt[k - 1]
                got = val(row, i_ja)
                if got != exp:
                    bad.append((r + 2, "name_ja(MONSTER_HUNT_NAMES[%d])" % (k - 1), exp, got))
            else:
                bad.append((r + 2, "monster_id", "1..%d" % len(hunt), rid))
    return n, bad, "monster-index.csv / MONSTER_HUNT_NAMES[id-1] と突合"


def a_stages(header, rows, idxs):
    """stage_id は questData .mib +0x14。1..27 と夜版 101..104。"""
    emap = S.questfields().get("ENUM_MAP_", [])
    qi = S.quest_info()
    used = set(int(x["stage"]) for x in qi.values()) if qi else set()
    i_id = col(header, "stage_id", "id")
    i_ja, i_night = col(header, "name_ja"), col(header, "night")
    i_base = col(header, "base_stage_id")
    i_cnt = col(header, "quest_count")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        # 1) quest-info.csv の stage 分布に含まれるか
        if used and k not in used:
            bad.append((r + 2, "stage_id", "quest-info.csv の stage に出現", rid))
        # 2) 夜版 101..104 は base_stage_id = id-100 であること
        if i_night is not None:
            night = val(row, i_night)
            if 101 <= k <= 104:
                if night != "yes":
                    bad.append((r + 2, "night", "yes", night))
                if i_base is not None and val(row, i_base) != str(k - 100):
                    bad.append((r + 2, "base_stage_id", k - 100, val(row, i_base)))
            elif 1 <= k <= 27 and night not in ("no", ""):
                bad.append((r + 2, "night", "no", night))
        # 3) ENUM_MAP_ との差は「別系統の表記」なので不一致とはせず記録のみ
        if 1 <= k <= 27 and i_ja is not None and k < len(emap):
            got = val(row, i_ja)
            exp = emap[k].replace("<昼>", "").replace("<夜>", "")
            if got and got != exp:
                note("stages", "stage %d: ENUM_MAP_=%r / 本表=%r (quest 本文由来の表記を採用)" % (k, exp, got))
    return n, bad, "quest-info.csv stage 分布 / night 系 / ENUM_MAP_ 表記 と突合"


def a_quests(header, rows, idxs):
    qi = S.quest_index()
    i_id, i_en = col(header, "quest_id", "id"), col(header, "name_en")
    i_idx = col(header, "quest_index")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        s = qi.get(int(rid))
        if s is None:
            bad.append((r + 2, "quest_id", "quest-index.csv に存在", rid)); continue
        if i_en is not None and val(row, i_en) and val(row, i_en) != s["name"]:
            bad.append((r + 2, "name_en", s["name"], val(row, i_en)))
        if i_idx is not None and val(row, i_idx) != s["index"]:
            bad.append((r + 2, "quest_index", s["index"], val(row, i_idx)))
    return n, bad, "refsrc quest-index.csv と突合"


def a_npcs(header, rows, idxs):
    """npc_id は連番でない。bit -> NpcName_jpn.gmd の添字。"""
    src = S.npc_index()
    nm = (S.gmd("NpcName_jpn.gmd") or (None, []))[1]
    i_id, i_bit = col(header, "npc_id", "id"), col(header, "bit")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid, bit = val(row, i_id), val(row, i_bit)
        if not rid.isdigit():
            continue
        n += 1
        s = src.get(int(rid))
        if s is None:
            bad.append((r + 2, "npc_id", "npc-index.csv に存在", rid))
        elif i_en is not None and val(row, i_en) and val(row, i_en) != s["name"]:
            bad.append((r + 2, "name_en", s["name"], val(row, i_en)))
        if bit.isdigit() and i_ja is not None:
            b = int(bit)
            if b < len(nm):
                if val(row, i_ja) != nm[b]:
                    bad.append((r + 2, "name_ja(NpcName[%d])" % b, nm[b], val(row, i_ja)))
            else:
                bad.append((r + 2, "bit", "< %d" % len(nm), bit))
    return n, bad, "refsrc npc-index.csv / NpcName_jpn.gmd と突合"


def a_awards(header, rows, idxs):
    """award_id = ビット番号。GC_Medal は 0..131 が名前、132..263 が説明。"""
    src = S.awards_src()
    gm = (S.gmd("GC_Medal_jpn.gmd") or (None, []))[1]
    i_id = col(header, "award_id", "id", "bit")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    i_desc = col(header, "desc_ja")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        k = int(rid)
        s = src.get(k)
        if s is None:
            bad.append((r + 2, "award_id", "awards.csv に存在", rid))
        elif i_en is not None and val(row, i_en) and val(row, i_en) != s["name"]:
            bad.append((r + 2, "name_en", s["name"], val(row, i_en)))
        if i_ja is not None and k < len(gm) and val(row, i_ja) != gm[k]:
            bad.append((r + 2, "name_ja(GC_Medal[%d])" % k, gm[k], val(row, i_ja)))
        if i_desc is not None and k + 132 < len(gm) and nl(val(row, i_desc)) != nl(gm[k + 132]):
            bad.append((r + 2, "desc_ja(GC_Medal[%d])" % (k + 132), nl(gm[k + 132])[:40], nl(val(row, i_desc))[:40]))
    return n, bad, "refsrc awards.csv / GC_Medal_jpn.gmd と突合"


def a_canteen(header, rows, idxs):
    """自然キー (kind, bit)。name_ja は Kitchen_jpn.gmd。"""
    src = S.canteen_src()
    kk = (S.gmd("Kitchen_jpn.gmd") or (None, []))[1]
    kset = set(kk)
    smap = {(x["kind"], x["bit"]): x for x in src}
    i_kind, i_bit = col(header, "kind"), col(header, "bit")
    i_ja, i_en = col(header, "name_ja"), col(header, "name_en")
    i_cat = col(header, "category")
    i_a, i_b = col(header, "ingredient_a"), col(header, "ingredient_b")
    bad, n = [], 0
    if None in (i_kind, i_bit):
        return 0, [], "kind/bit が見つからない"
    for r in idxs:
        row = rows[r]
        key = (val(row, i_kind), val(row, i_bit))
        n += 1
        s = smap.get(key)
        if s is None:
            bad.append((r + 2, "(kind,bit)", "refsrc canteen.csv に存在", key)); continue
        for label, i, f in (("name_en", i_en, "name"), ("category", i_cat, "category"),
                            ("ingredient_a", i_a, "ingredient_a"), ("ingredient_b", i_b, "ingredient_b")):
            if i is not None and val(row, i) != s.get(f, ""):
                bad.append((r + 2, label, s.get(f, ""), val(row, i)))
        if i_ja is not None and val(row, i_ja) and val(row, i_ja) not in kset:
            bad.append((r + 2, "name_ja", "Kitchen_jpn.gmd に存在", val(row, i_ja)))
    return n, bad, "refsrc canteen.csv / Kitchen_jpn.gmd と突合"


def a_provisions(header, rows, idxs):
    src = {int(x["item"]): x for x in (S.provisions_src() or [])}
    i_id = col(header, "item_id", "id")
    i_v = col(header, "value")
    i_g = [col(header, "group1"), col(header, "group2"), col(header, "group3")]
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        s = src.get(int(rid))
        if s is None:
            bad.append((r + 2, "item_id", "refsrc provisions.csv に存在", rid)); continue
        if i_v is not None and val(row, i_v) != s["value"]:
            bad.append((r + 2, "value", s["value"], val(row, i_v)))
        for j, gi in enumerate(i_g):
            if gi is not None and val(row, gi) != s["group%d" % (j + 1)]:
                bad.append((r + 2, "group%d" % (j + 1), s["group%d" % (j + 1)], val(row, gi)))
    return n, bad, "refsrc provisions.csv と突合"


def a_arena(header, rows, idxs):
    src = {int(x["index"]): x for x in (S.arena_src() or [])}
    i_id = col(header, "arena_index", "id")
    i_q = col(header, "quest_id")
    i_a, i_b, i_c = col(header, "grade_a"), col(header, "grade_b"), col(header, "grade_c")
    i_p = col(header, "prowler")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_id)
        if not rid.isdigit():
            continue
        n += 1
        s = src.get(int(rid))
        if s is None:
            bad.append((r + 2, "arena_index", "refsrc arena.csv に存在", rid)); continue
        for label, i, f in (("quest_id", i_q, "quest_id"), ("prowler", i_p, "prowler"),
                            ("grade_a", i_a, "grade_a"), ("grade_b", i_b, "grade_b"),
                            ("grade_c", i_c, "grade_c")):
            if i is not None and val(row, i) != s[f]:
                bad.append((r + 2, label, s[f], val(row, i)))
    return n, bad, "refsrc arena.csv と突合"


def a_quest_monsters(header, rows, idxs):
    src = S.quest_monsters_src() or []
    groups = {}
    for x in src:
        groups.setdefault(x["quest_id"], []).append(x)
    i_q, i_e = col(header, "quest_id"), col(header, "entry_no")
    i_m, i_s = col(header, "monster_id"), col(header, "size")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        q, e = val(row, i_q), val(row, i_e)
        if not (q.isdigit() and e.isdigit()):
            continue
        n += 1
        g = groups.get(q)
        if not g or int(e) >= len(g):
            bad.append((r + 2, "(quest_id,entry_no)", "refsrc に存在", (q, e))); continue
        x = g[int(e)]
        if i_m is not None and val(row, i_m) != x["monster"]:
            bad.append((r + 2, "monster_id", x["monster"], val(row, i_m)))
        if i_s is not None and val(row, i_s) != x["size"]:
            bad.append((r + 2, "size", x["size"], val(row, i_s)))
    return n, bad, "refsrc quest-monsters.csv (quest_id 内の順序) と突合"


def a_quest_rewards(header, rows, idxs):
    src = S.quest_rewards_src() or []
    smap = {(x["quest_id"], x["slot"]): x for x in src}
    i_q, i_s = col(header, "quest_id"), col(header, "slot")
    i_rem = col(header, "rem_id", "rem")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        key = (val(row, i_q), val(row, i_s))
        n += 1
        x = smap.get(key)
        if x is None:
            bad.append((r + 2, "(quest_id,slot)", "refsrc に存在", key)); continue
        if i_rem is not None and val(row, i_rem) != x["rem"]:
            bad.append((r + 2, "rem_id", x["rem"], val(row, i_rem)))
    return n, bad, "refsrc quest-rewards.csv と突合"


def a_monster_carves(header, rows, idxs):
    src = S.monster_carves_src() or []
    groups = {}
    for x in src:
        groups.setdefault((x["monster"], x["rank"], x["sets"], x["kind"]), []).append(x)
    i_m, i_r = col(header, "monster_id"), col(header, "rank")
    i_s, i_k = col(header, "sets"), col(header, "kind")
    i_e, i_item = col(header, "entry_no"), col(header, "item_id")
    i_c, i_ch = col(header, "count"), col(header, "chance")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        key = (val(row, i_m), val(row, i_r), val(row, i_s), val(row, i_k))
        e = val(row, i_e)
        if not e.isdigit():
            continue
        n += 1
        g = groups.get(key)
        if not g or int(e) >= len(g):
            bad.append((r + 2, "(monster,rank,sets,kind,entry_no)", "refsrc に存在", key + (e,))); continue
        x = g[int(e)]
        for label, i, f in (("item_id", i_item, "item"), ("count", i_c, "count"), ("chance", i_ch, "chance")):
            if i is not None and val(row, i) != x[f]:
                bad.append((r + 2, label, x[f], val(row, i)))
    return n, bad, "refsrc monster-carves.csv (同一キー内の順序) と突合"


def a_recipes(header, rows, idxs):
    src = S.recipes_src() or []
    groups = {}
    for x in src:
        groups.setdefault((x["kind"], x["id"], x["level"]), []).append(x)
    i_k, i_t = col(header, "kind"), col(header, "target_id", "id")
    i_l, i_no = col(header, "level"), col(header, "recipe_no")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        key = (val(row, i_k), val(row, i_t), val(row, i_l))
        no = val(row, i_no)
        if not no.isdigit():
            continue
        n += 1
        g = groups.get(key)
        if not g or int(no) >= len(g):
            bad.append((r + 2, "(kind,target_id,level,recipe_no)", "refsrc に存在", key + (no,))); continue
        x = g[int(no)]
        for f in ("item1", "count1", "item2", "count2", "item3", "count3", "item4", "count4"):
            i = col(header, f)
            if i is not None and val(row, i) != x[f]:
                bad.append((r + 2, f, x[f], val(row, i)))
    return n, bad, "refsrc recipes.csv (同一キー内の順序) と突合"


def _refsrc_positional(refsrc_file, colmap, desc):
    """refsrc の同名 CSV と「同一順」で突合する (row_id 連番 = 元の並び)。"""
    def f(header, rows, idxs):
        src = S.ref(refsrc_file) or []
        bad, n = [], 0
        for r in idxs:
            if r >= len(src):
                bad.append((r + 2, "(row)", "元 CSV の行数 < %d" % len(src), r + 1))
                continue
            row, s = rows[r], src[r]
            n += 1
            for scol, dcol in colmap:
                i = col(header, dcol)
                if i is None:
                    continue
                if val(row, i) != s.get(scol, ""):
                    bad.append((r + 2, dcol, s.get(scol, ""), val(row, i)))
        return n, bad, desc
    return f


def a_armor_skills(header, rows, idxs):
    """refsrc の part は 1..5、本表の part_id は 0..4 (armor.csv と同じ 0 始まり)。"""
    src = S.ref("armor-skills.csv") or []
    i_ser, i_part = col(header, "series_id"), col(header, "part_id")
    i_sk, i_pt = col(header, "skill_id"), col(header, "points")
    bad, n = [], 0
    for r in idxs:
        if r >= len(src):
            bad.append((r + 2, "(row)", "元 CSV の行数 < %d" % len(src), r + 1)); continue
        row, s = rows[r], src[r]
        n += 1
        if i_ser is not None and val(row, i_ser) != s["series"]:
            bad.append((r + 2, "series_id", s["series"], val(row, i_ser)))
        if i_part is not None:
            exp = str(int(s["part"]) - 1)
            if val(row, i_part) != exp:
                bad.append((r + 2, "part_id", exp, val(row, i_part)))
        if i_sk is not None and val(row, i_sk) != s["tree"]:
            bad.append((r + 2, "skill_id", s["tree"], val(row, i_sk)))
        if i_pt is not None and val(row, i_pt) != s["points"]:
            bad.append((r + 2, "points", s["points"], val(row, i_pt)))
    return n, bad, "refsrc armor-skills.csv と同一順で突合 (part は 1 始まり→0 始まり)"

a_combinations = _refsrc_positional(
    "combinations.csv",
    [("item1", "item1_id"), ("item2", "item2_id"), ("result", "result_item_id"), ("chance", "chance_percent")],
    "refsrc combinations.csv と同一順で突合")

a_palico_actions = _refsrc_positional(
    "palico-actions.csv",
    [("kind", "kind"), ("id", "action_id"), ("points", "points"), ("cost", "cost")],
    "refsrc palico-actions.csv と同一順で突合")

a_palico_levels = _refsrc_positional(
    "palico-levels.csv",
    [("level", "level"), ("support_slots", "support_slots"), ("skill_slots", "skill_slots")],
    "refsrc palico-levels.csv と同一順で突合")

a_smithy_lists = _refsrc_positional(
    "smithy-lists.csv",
    [("list", "list_name"), ("records", "records"), ("ids", "ids")],
    "refsrc smithy-lists.csv と同一順で突合")

a_talisman_tables = _refsrc_positional(
    "talisman-tables.csv",
    [("kind", "kind"), ("tier", "tier"), ("skill", "skill_id"), ("min", "min_points"), ("max", "max_points")],
    "refsrc talisman-tables.csv と同一順で突合")

a_weapon_tree = _refsrc_positional(
    "weapon-tree.csv",
    [("class", "weapon_type_id"), ("weapon", "weapon_index"),
     ("parent", "parent_weapon_index"), ("level", "required_level")],
    "refsrc weapon-tree.csv と同一順で突合")


def a_requests(header, rows, idxs):
    """依頼 index i の名前は activityData_jpn.gmd の 5*i 番目。他列は request-index.csv。"""
    src = S.request_index() or []
    ad = (S.gmd("activityData_jpn.gmd") or (None, []))[1]
    i_idx = col(header, "request_index", "id")
    i_ja = col(header, "name_ja")
    i_npc = col(header, "npc_id")
    i_qen = col(header, "quest_name_en")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        rid = val(row, i_idx)
        if not rid.isdigit():
            continue
        n += 1
        i = int(rid)
        if i >= len(src):
            bad.append((r + 2, "request_index", "< %d" % len(src), rid))
            continue
        s = src[i]
        for scol, dcol in (("kind", "kind"), ("stage", "stage"), ("village", "village"),
                           ("quest_id", "quest_id"), ("prereq_quest", "prereq_quest"),
                           ("reward_count", "reward_count"),
                           ("accept_flag", "accept_flag"), ("done_flag", "done_flag")):
            ci = col(header, dcol)
            if ci is not None and val(row, ci) != s.get(scol, ""):
                bad.append((r + 2, dcol, s.get(scol, ""), val(row, ci)))
        # reward_id は元 CSV が 16 進表記 (0x6da) なので数値で比較
        ci = col(header, "reward_id")
        if ci is not None:
            raw = s.get("reward_id", "")
            try:
                exp = str(int(raw, 16))
            except (TypeError, ValueError):
                exp = raw
            if val(row, ci) != exp:
                bad.append((r + 2, "reward_id", exp, val(row, ci)))
        # npc は元 CSV が 16 進表記 (0xe) なので数値で比較
        if i_npc is not None:
            raw = s.get("npc", "")
            try:
                exp = str(int(raw, 16))
            except (TypeError, ValueError):
                exp = raw
            if val(row, i_npc) != exp:
                bad.append((r + 2, "npc_id", exp, val(row, i_npc)))
        if i_qen is not None and val(row, i_qen) != s.get("quest_name", ""):
            bad.append((r + 2, "quest_name_en", s.get("quest_name", ""), val(row, i_qen)))
        if i_ja is not None and 5 * i < len(ad) and val(row, i_ja) != ad[5 * i]:
            bad.append((r + 2, "name_ja(activityData[%d])" % (5 * i), ad[5 * i], val(row, i_ja)))
    return n, bad, "refsrc request-index.csv / activityData_jpn.gmd (5*i) と突合"


ADAPTERS = {
    "items": a_items, "weapons": a_weapons, "armor": a_armor,
    "armor-parts": a_armor_parts, "armor-skills": a_armor_skills,
    "skills": a_skills, "skill-effects": a_skill_effects,
    "decorations": a_decorations, "talismans": a_talismans,
    "talisman-tables": a_talisman_tables, "combinations": a_combinations,
    "hunter-arts": a_hunter_arts, "kinsects": a_kinsects,
    "weapon-types": a_weapon_types, "weapon-tree": a_weapon_tree,
    "item-categories": a_item_categories, "smithy-lists": a_smithy_lists,
    "palico-weapons": a_palico_weapons, "palico-armor": a_palico_armor,
    "palico-skills": a_palico_skills, "palico-support": a_palico_support,
    "palico-actions": a_palico_actions, "palico-levels": a_palico_levels,
    "monsters": a_monsters, "stages": a_stages, "quests": a_quests,
    "npcs": a_npcs, "awards": a_awards, "canteen": a_canteen,
    "provisions": a_provisions, "arena": a_arena, "requests": a_requests,
    "quest-monsters": a_quest_monsters, "quest-rewards": a_quest_rewards,
    "monster-carves": a_monster_carves, "recipes": a_recipes,
}


def generic_name_check(header, rows, idxs, corpus):
    i_ja, i_en = col(header, "name_ja", "name"), col(header, "name_en")
    bad, n = [], 0
    for r in idxs:
        row = rows[r]
        n += 1
        for label, i in (("name_ja", i_ja), ("name_en", i_en)):
            v = val(row, i)
            if v and v.strip() and v.strip() not in corpus:
                bad.append((r + 2, label, "出典コーパスに存在", v))
    return n, bad, "出典コーパス照合 (汎用)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", default="20260101")
    ap.add_argument("--table", default="")
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    corpus = None
    tables = []
    for area in ("equip", "world"):
        mp = os.path.join(a.repo, "data", area, "_manifest.json")
        if not os.path.exists(mp):
            continue
        man = json.loads(open(mp, encoding="utf-8").read())
        for t in man.get("tables", []):
            tables.append((area, t))

    for area, t in tables:
        tid = t.get("id")
        if a.table and tid != a.table:
            continue
        p = os.path.join(a.repo, "data", area, t.get("file", ""))
        if not os.path.exists(p):
            rec(tid, 0, [], "CSV 不在", skipped=True); continue
        header, rows = read_csv(p)
        if not rows:
            rec(tid, 0, [], "データ行なし", skipped=True); continue
        idxs = sample(rows, a.n, a.seed, tid)
        ad = ADAPTERS.get(tid)
        if ad:
            n, bad, note = ad(header, rows, idxs)
            rec(tid, n, bad, note)
        else:
            if corpus is None:
                corpus = S.name_corpus()
            n, bad, note = generic_name_check(header, rows, idxs, corpus)
            rec(tid, n, bad, note + " [adapter なし]")

    total_bad = 0
    print("=" * 78)
    print("出典突合 (n=%d, seed=%s)" % (a.n, a.seed))
    print("=" * 78)
    for r in results:
        mark = "SKIP" if r["skipped"] else ("OK  " if not r["mismatches"] else "NG  ")
        print("[%s] %-18s checked=%-4d mismatches=%d  %s"
              % (mark, r["table"], r["checked"], len(r["mismatches"]), r["note"]))
        for m in r["mismatches"][:8]:
            print("       行%-6s %-34s 期待=%r 実=%r" % (m[0], m[1], m[2], m[3]))
        if len(r["mismatches"]) > 8:
            print("       ... 他 %d 件" % (len(r["mismatches"]) - 8))
        total_bad += len(r["mismatches"])
    if notes_out:
        print("-" * 78)
        print("記録のみ (不一致ではない): %d" % len(notes_out))
        for x in notes_out:
            print("  [%s] %s" % (x["table"], x["note"]))
    print("-" * 78)
    print("不一致合計: %d" % total_bad)
    if a.json:
        json.dump({"results": results, "notes": notes_out},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("JSON:", a.json)
    return 1 if total_bad else 0


if __name__ == "__main__":
    sys.exit(main())
