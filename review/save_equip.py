#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX 実セーブ（Ryujinx）の装備BOXリーダ (reviewer 専用).

一次資料として実セーブを直接パースする。データの書き換えは一切しない（read only）。

レイアウト（refsrc docs/01-container.md, 07-equipment.md で裏取り）:
  ファイル先頭 0x24 バイト = sSavedata コンテナヘッダ
  ボディ先頭 +0x04 = スロット使用フラグ (3 x u8)
  ボディ先頭 +0x07 = 最後にロードしたスロット
  ボディ先頭 +0x10 + 4*slot = キャラクタブロックのオフセット（ボディ相対）
  装備BOX = キャラクタブロック先頭 + 0x62EE、36 バイト x 2000

レコード 36 バイト:
  +0x00 u16 LE  type(5bit) | (level-1)(5bit) | (transmog_level-1)(5bit)
  +0x02 u16 LE  id（防具=series_id / 武器=weapon_index / 護石=talisman_id）
  +0x04 u16 LE  transmog id（0 = なし）
  +0x06 u16 LE  装飾品1 item_id
  +0x08 u16 LE  装飾品2
  +0x0A u16 LE  装飾品3
  +0x0C 24B     テール（護石スキル等。通常 00 埋め）
"""
import os
import struct

SAVE = r"C:\Users\haruk\AppData\Roaming\Ryujinx\bis\user\save\0000000000000001\0\system"
SAVE_BACKUP = SAVE + "_backup"
# 護石 650 件を含むサンプルセーブ（3 スロット使用）
SAMPLE_SAVE = r"C:\anyWorkspace\nx\mhxx\save_backups\_conv\system"
BODY_OFF = 0x24
BOX_REL = 0x62EE
REC_SIZE = 36
REC_COUNT = 2000
BOX_BYTES = REC_SIZE * REC_COUNT

# EQUIPMENT_TYPES (gamedata.rs, 22 entries; 12 = "IGNORE THIS" の欠番)
EQUIP_TYPES = ["(None)", "Head", "Chest", "Arms", "Waist", "Legs", "Talisman",
               "Great Sword", "Sword and Shield", "Hammer", "Lance", "Heavy Bowgun",
               "IGNORE THIS", "Light Bowgun", "Longsword", "Switch Axe", "Gunlance",
               "Bow", "Dual Blades", "Hunting Horn", "Insect Glaive", "Charge Blade"]
# equip_type_id -> weapon_type_id
EQUIP_TO_WEAPON_TYPE = {7: 0, 8: 1, 9: 2, 10: 3, 11: 4, 13: 6, 14: 7, 15: 8,
                        16: 9, 17: 10, 18: 11, 19: 12, 20: 13, 21: 14}
# weapon_type_id -> equip_type_id
WEAPON_TYPE_TO_EQUIP = {v: k for k, v in EQUIP_TO_WEAPON_TYPE.items()}


def load(path=SAVE):
    with open(path, "rb") as f:
        return f.read()


def body(raw):
    return raw[BODY_OFF:]


def slot_in_use(b):
    return [b[0x04 + i] for i in range(3)]


def slot_bases(b):
    """キャラクタブロックのオフセット（ボディ相対）。"""
    return [struct.unpack_from("<I", b, 0x10 + 4 * i)[0] for i in range(3)]


def box_offset_body(b, slot=0):
    """装備BOX先頭のボディ相対オフセット。"""
    return slot_bases(b)[slot] + BOX_REL


def box_offset_file(b, slot=0):
    """装備BOX先頭のファイル絶対オフセット。"""
    return box_offset_body(b, slot) + BODY_OFF


def decode(rec):
    """36 バイト -> dict。"""
    w0, eid, tmog, d0, d1, d2 = struct.unpack_from("<6H", rec, 0)
    return {
        "word0": w0,
        "type": w0 & 0x1F,
        "level": ((w0 >> 5) & 0x1F) + 1,
        "tmog_level": ((w0 >> 10) & 0x1F) + 1,
        "bit15": (w0 >> 15) & 1,
        "id": eid,
        "tmog_id": tmog,
        "decos": [d0, d1, d2],
        "tail": rec[12:36],
        "raw": rec,
    }


def encode(rec_type, eid, level=1, tmog_id=0, tmog_level=1, decos=(0, 0, 0), tail=None):
    """dict/値 -> 36 バイト（リトルエンディアン）。UI の出力と比較するための参照実装。"""
    w0 = ((rec_type & 0x1F)
          | (((level - 1) & 0x1F) << 5)
          | (((tmog_level - 1) & 0x1F) << 10))
    out = bytearray(REC_SIZE)
    struct.pack_into("<HHH", out, 0, w0, eid & 0xFFFF, tmog_id & 0xFFFF)
    for i, d in enumerate(decos[:3]):
        struct.pack_into("<H", out, 6 + 2 * i, d & 0xFFFF)
    if tail:
        out[12:36] = tail[:24]
    return bytes(out)


def records(raw, slot=0, skip_empty=True):
    """BOX 全 2000 レコードを [(index, dict)] で返す。"""
    b = body(raw)
    off = box_offset_body(b, slot)
    out = []
    for i in range(REC_COUNT):
        rec = b[off + i * REC_SIZE: off + (i + 1) * REC_SIZE]
        if len(rec) < REC_SIZE:
            break
        d = decode(rec)
        if skip_empty and not (d["type"] or d["id"] or d["tmog_id"] or any(d["decos"])):
            continue
        d["index"] = i
        out.append((i, d))
    return out


def decode_talisman(rec):
    """護石レコード（type 6）の +0x0C..+0x13 を読む。"""
    d = decode(rec)
    t = d["tail"]
    d.update({
        "skill1_id": t[0],
        "skill2_id": t[1],
        "skill1_points": struct.unpack("<b", t[2:3])[0],
        "skill2_points": struct.unpack("<b", t[3:4])[0],
        "slots": t[4],
        "rarity": t[6],
        "one13": t[7],
    })
    return d


def encode_talisman(kind, skill1_id, skill2_id, skill1_points, skill2_points,
                    slots, rarity, decos=(0, 0, 0), level=1):
    """護石レコードを組み立てる（+0x13 は常に 1）。"""
    out = bytearray(REC_SIZE)
    w0 = 6 | (((level - 1) & 0x1F) << 5)
    struct.pack_into("<HHH", out, 0, w0, kind & 0xFFFF, 0)
    for i, dd in enumerate(decos[:3]):
        struct.pack_into("<H", out, 6 + 2 * i, dd & 0xFFFF)
    out[12] = skill1_id & 0xFF
    out[13] = skill2_id & 0xFF
    out[14] = skill1_points & 0xFF
    out[15] = skill2_points & 0xFF
    out[16] = slots & 0xFF
    out[17] = 0
    out[18] = rarity & 0xFF
    out[19] = 1
    return bytes(out)


def talismans(raw, slot=0):
    """指定スロットの護石レコードを [(index, dict)] で返す。"""
    return [(i, decode_talisman(d["raw"])) for i, d in records(raw, slot=slot) if d["type"] == 6]


def find_hits(buf, pat):
    out, i = [], buf.find(pat)
    while i != -1:
        out.append(i)
        i = buf.find(pat, i + 1)
    return out


if __name__ == "__main__":
    raw = load()
    b = body(raw)
    print("save:", SAVE)
    print("size: 0x%X  body: 0x%X" % (len(raw), len(b)))
    print("slot in use:", slot_in_use(b), " last loaded:", b[0x07])
    print("slot bases (body):", [hex(x) for x in slot_bases(b)])
    print("box (body) 0x%X / (file) 0x%X" % (box_offset_body(b), box_offset_file(b)))
    recs = records(raw)
    print("non-empty records: %d" % len(recs))
    for i, d in recs:
        print("  [%4d] type=%-2d %-16s id=%-5d lv=%-2d tmog=%-2d decos=%s"
              % (i, d["type"], EQUIP_TYPES[d["type"]] if d["type"] < len(EQUIP_TYPES) else "?",
                 d["id"], d["level"], d["tmog_id"], d["decos"]))
