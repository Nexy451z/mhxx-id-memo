#!/usr/bin/env python3
r"""Build data/world/*.csv and data/world/_manifest.json for mhxx-id-memo.

Reproducible: every value comes from one of the sources below, read only.

    python tools/extract_world_tables.py [--repo DIR] [--romfs DIR] [--refsrc DIR]

Sources (read only):
  refsrc  C:\anyWorkspace\nx\mhxx\mhnxeditor\.work\finalaudit\refsrc
            data/*.csv      the reference project's extracted tables
            tools/quest_info.py  STAGE_TEXT, the stage -> questMessage entry map
  romfs   C:\anyWorkspace\nx\mhxx\romfs\nativeNX
            table/*.gmd     NpcName, GC_Medal, activityData, Kitchen
            arc/quest/q*.arc  questData .mib (quest id, map id) and _jpn text
  gamedata C:\anyWorkspace\nx\mhxx\mhnxeditor\crates\mhnx-core\src\gamedata.rs
            MONSTER_HUNT_NAMES, the game's 137 Japanese monster names

No value is invented. A name that no source carries is left empty.

GMD layout used here (MHXX Switch, version 0x00010302):
  +0x18 u32 string count, +0x20 u32 byte size of the text block, +0x24 u32 key length,
  +0x28 key + NUL, text block = the LAST <size> bytes of the file, count NUL-terminated
  UTF-8 strings.  Files whose +0x1C is not 0 (NpcName, GC_Medal, Kitchen, ...) keep a
  hashed entry table between the key and the text; the text block is still at the end.

ARC layout: 'ARC\0', u16 entry count at +6, entries of 0x50 B from +0xC (name 64 B,
then u32 compressed size, u32 uncompressed size, u32 offset, u32 unused); zlib when
the sizes differ.
"""
import argparse
import collections
import csv
import json
import os
import re
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(HERE)
DEFAULT_ROMFS = r'C:\anyWorkspace\nx\mhxx\romfs'
DEFAULT_REFSRC = r'C:\anyWorkspace\nx\mhxx\mhnxeditor\.work\finalaudit\refsrc'
GAMEDATA_RS = r'C:\anyWorkspace\nx\mhxx\mhnxeditor\crates\mhnx-core\src\gamedata.rs'

# ---------------------------------------------------------------- containers


def read_gmd(path):
    """The strings of a .gmd, in file order."""
    b = open(path, 'rb').read()
    if b[:4] != b'GMD\0':
        raise ValueError('not a gmd: %s' % path)
    count = struct.unpack_from('<I', b, 0x18)[0]
    size = struct.unpack_from('<I', b, 0x20)[0]
    keylen = struct.unpack_from('<I', b, 0x24)[0]
    key = b[0x28:0x28 + keylen].decode('utf-8', 'replace')
    text = b[len(b) - size:] if 0 < size <= len(b) else b[0x28 + keylen + 1:]
    return key, [x.decode('utf-8', 'replace') for x in text.split(b'\0')[:count]]


def read_arc(path):
    """{entry name: bytes} of a quest archive."""
    d = open(path, 'rb').read()
    if d[:4] != b'ARC\0':
        raise ValueError('not an arc: %s' % path)
    n = struct.unpack_from('<H', d, 6)[0]
    out = {}
    for i in range(n):
        e = d[0xC + i * 0x50:0xC + (i + 1) * 0x50]
        name = e[:64].split(b'\0')[0].decode('utf-8', 'replace')
        _, cs, ds, off = struct.unpack_from('<4I', e, 64)
        raw = d[off:off + cs]
        out[name] = zlib.decompress(raw) if (cs != ds & 0x1FFFFFFF or raw[:1] == b'\x78') else raw
    return out


def read_csv(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, header, rows):
    """Write a SPEC CSV: UTF-8 BOM, LF, and every line break inside a value as LF."""
    def clean(v):
        return v.replace('\r\n', '\n').replace('\r', '\n') if isinstance(v, str) else v
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        w.writerows([[clean(v) for v in r] for r in rows])
    return len(rows)


def write_text(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def to_int(v, default=None):
    v = (v or '').strip()
    if not v:
        return default
    return int(v, 0) if v.lower().startswith('0x') else int(v)


def to_bool(v):
    return 'yes' if str(v).strip() in ('1', 'yes', 'True', 'true') else 'no'


# ---------------------------------------------------------------- stage names
#
# The stage id is byte +0x14 of a quest's .mib (tools/quest_info.py in the reference
# project calls it "stage"; the editor's arc-mib calls it map_id).  Its English name is
# the game's own board "Locale" text: questMessage_<lang>.gmd entry STAGE_TEXT[id]
# (reference project, tools/quest_info.py).  The Japanese name is not in this dump --
# GUI/06_msg is not part of romfs/nativeNX -- so it is taken from the quest texts:
# either the Harvest Tour quest of that stage, whose Japanese title is
# "<place>の採集ツアー" while the English one is "Harvest Tour: <name>", or, where no
# Harvest Tour exists, the place name the quest descriptions of that stage use.
# The script counts the evidence and writes the count into notes_ja.
STAGE_TEXT = {
    1: 'J. Frontier', 101: 'J. Frontier', 2: 'V. Hills', 102: 'V. Hills',
    3: 'A. Ridge', 103: 'A. Ridge', 4: 'M. Peaks', 104: 'M. Peaks',
    5: 'Dunes', 6: 'D. Island', 7: 'Marshlands', 8: 'Volcano', 9: 'Arena',
    10: 'V. Slayground', 11: 'A. Steppe', 12: 'V. Hollow', 13: 'Primal Forest',
    14: 'F. Seaway', 15: 'F. Slayground', 16: 'Sanctuary', 17: 'Forlorn Arena',
    18: 'S. Pinnacle', 19: 'Ingle Isle', 20: 'Polar Field', 21: "Wyvern's End",
    22: 'Desert', 23: 'Jungle', 24: 'Ruined Pinnacle', 25: 'Castle Schrade',
    26: 'Fortress', 27: 'Forlorn Citadel',
}
STAGE_FULL = {
    1: 'Jurassic Frontier', 101: 'Jurassic Frontier', 2: 'Verdant Hills',
    102: 'Verdant Hills', 3: 'Arctic Ridge', 103: 'Arctic Ridge',
    4: 'Misty Peaks', 104: 'Misty Peaks', 5: 'Dunes', 6: 'Deserted Island',
    7: 'Marshlands', 8: 'Volcano', 9: 'Arena', 10: 'Volcano Slayground',
    11: 'Ancestral Steppe', 12: 'Volcanic Hollow', 13: 'Primal Forest',
    14: 'Frozen Seaway', 15: 'Frozen Slayground', 16: 'Sanctuary',
    17: 'Forlorn Arena', 18: 'Sacred Pinnacle', 19: 'Ingle Isle',
    20: 'Polar Field', 21: "Wyvern's End", 22: 'Desert', 23: 'Jungle',
    24: 'Ruined Pinnacle', 25: 'Castle Schrade', 26: 'Fortress',
    27: 'Forlorn Citadel',
}
# stage id -> (Japanese name, confidence, why)
STAGE_JA = {
    1: ('古代林', 'derived', 'Harvest Tour 201「古代林の採集ツアー」'),
    2: ('森丘', 'derived', 'Harvest Tour 203「森丘の採集ツアー」'),
    3: ('雪山', 'derived', 'Harvest Tour 204「雪山の採集ツアー」'),
    4: ('渓流', 'derived', 'Harvest Tour 205「渓流の採集ツアー」'),
    5: ('旧砂漠', 'derived', 'Harvest Tour 202「旧砂漠の採集ツアー」'),
    6: ('孤島', 'derived', 'Harvest Tour 301「孤島の採集ツアー」'),
    7: ('沼地', 'derived', 'Harvest Tour 302「沼地の採集ツアー」'),
    8: ('火山', 'derived', 'Harvest Tour 401「火山の採集ツアー」'),
    9: ('闘技場', 'curated', '依頼文の「闘技場」'),
    10: ('', 'curated', '依頼文の「闘技場」「立体闘技場」'),
    11: ('遺跡平原', 'derived', 'Harvest Tour 721「遺跡平原の採集ツアー」'),
    12: ('地底火山', 'derived', 'Harvest Tour 821「地底火山の採集ツアー」'),
    13: ('原生林', 'derived', 'Harvest Tour 722「原生林の採集ツアー」'),
    14: ('氷海', 'derived', 'Harvest Tour 820「氷海の採集ツアー」'),
    15: ('', 'curated', '依頼文の「闘技場」'),
    16: ('禁足地', 'curated', '依頼文の「禁足地」'),
    17: ('塔', 'curated', '依頼文の「塔」'),
    18: ('霊峰', 'curated', '依頼文の「霊峰」'),
    19: ('溶岩島', 'curated', '依頼文の「溶岩島」'),
    20: ('極圏', 'curated', '依頼文の「極圏」'),
    21: ('竜ノ墓場', 'curated', '依頼文の「竜ノ墓場」'),
    22: ('砂漠', 'derived', 'Harvest Tour 701「砂漠の採集ツアー」'),
    23: ('密林', 'derived', 'Harvest Tour 801「密林の採集ツアー」'),
    24: ('遺群嶺', 'derived', 'Harvest Tour 702「遺群嶺の採集ツアー」'),
    25: ('シュレイド城', 'curated', '依頼文の「シュレイド城」'),
    26: ('砦', 'curated', '依頼文の「砦」'),
    27: ('旧砦跡', 'curated', '依頼文の「旧砦跡」'),
    101: ('古代林', 'derived', 'Harvest Tour 723「古代林の採集ツアー」'),
    102: ('森丘', 'derived', 'Harvest Tour 725「森丘の採集ツアー」'),
    103: ('雪山', 'derived', 'Harvest Tour 726「雪山の採集ツアー」'),
    104: ('渓流', 'derived', 'Harvest Tour 727「渓流の採集ツアー」'),
}
# the word whose count is the evidence for STAGE_JA.  Two stages keep their name empty
# because the only word their quests use is 闘技場, which stage 9 already owns; the count
# is still recorded so the reader can see why.
STAGE_JA_WORD = {s: v[0] for s, v in STAGE_JA.items()}
STAGE_JA_WORD[10] = '闘技場'
STAGE_JA_WORD[15] = '闘技場'


def monster_hunt_names():
    """MONSTER_HUNT_NAMES from gamedata.rs: the game's 137 Japanese monster names."""
    src = open(GAMEDATA_RS, encoding='utf-8').read()
    m = re.search(r'MONSTER_HUNT_NAMES: &\[&str\] = &\[(.*?)\n\];', src, re.S)
    if not m:
        raise SystemExit('MONSTER_HUNT_NAMES not found in %s' % GAMEDATA_RS)
    names = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))
    if len(names) != 137:
        raise SystemExit('MONSTER_HUNT_NAMES has %d entries, expected 137' % len(names))
    return names


def quest_arcs(romfs):
    """{quest id: {'map': int, 'mib': bytes, 'text': [str]}} from arc/quest/q*.arc."""
    root = os.path.join(romfs, 'nativeNX', 'arc', 'quest')
    out = {}
    for name in sorted(os.listdir(root)):
        if not re.fullmatch(r'q\d{7}\.arc', name):
            continue
        entries = read_arc(os.path.join(root, name))
        mib = text = None
        for k, v in entries.items():
            lk = k.lower()
            if lk.startswith('quest\\questdata\\questdata_') and not lk.endswith('_jpn'):
                mib = v
            elif lk.endswith('_jpn'):
                text = v
        if mib is None:
            continue
        qid = struct.unpack_from('<I', mib, 0x0C)[0]
        out[qid] = {
            'map': mib[0x14],
            'kind': mib[0x10],
            'level': mib[0x12],
            'village_rank': mib[0x11],
            'time_limit': mib[0x16],
            'revive_count': mib[0x17],
            'text': read_gmd_text(text) if text else [],
        }
    return out


def read_gmd_text(b):
    count = struct.unpack_from('<I', b, 0x18)[0]
    size = struct.unpack_from('<I', b, 0x20)[0]
    return [x.decode('utf-8', 'replace') for x in b[len(b) - size:].split(b'\0')[:count]]


# ---------------------------------------------------------------- column specs

def col(name, typ, ja, en):
    return {'name': name, 'type': typ, 'desc_ja': ja, 'desc_en': en}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default=DEFAULT_REPO)
    ap.add_argument('--romfs', default=DEFAULT_ROMFS)
    ap.add_argument('--refsrc', default=DEFAULT_REFSRC)
    a = ap.parse_args()

    out_dir = os.path.join(a.repo, 'data', 'world')
    os.makedirs(out_dir, exist_ok=True)
    ref = lambda n: os.path.join(a.refsrc, 'data', n)
    tab = lambda n: os.path.join(a.romfs, 'nativeNX', 'table', n)

    tables = []
    problems = []

    # ------------------------------------------------------------ monsters
    mi = read_csv(ref('monster-index.csv'))
    ms = {int(r['index']): r for r in read_csv(ref('monster-sizes.csv'))}
    ja_names = monster_hunt_names()
    rows = []
    for r in mi:
        i = int(r['index'])
        s = ms[i]
        ja = ja_names[i - 1]
        if ja in ('不明',) or ja.startswith('Unknown'):
            ja = ''
        rows.append([
            i, ja, r['monster'], r['category'], s['class'], r['has_size_record'],
            s['base_cm'], s['mini_le'], s['silver_ge'], s['gold_ge'],
            s['fixed_size'], s['crown_awards'], s['card_pos'], s['notes_bit'],
            s['family_of'], r['confidence'], r['notes'],
        ])
    tables.append({
        'id': 'monsters', 'title_ja': 'モンスター', 'title_en': 'Monsters',
        'file': 'monsters.csv', 'primary_key': 'monster_id',
        'header': ['monster_id', 'name_ja', 'name_en', 'category', 'class',
                   'has_size_record', 'base_size_cm', 'mini_le', 'silver_ge',
                   'gold_ge', 'fixed_size', 'crown_awards', 'card_pos',
                   'notes_bit', 'family_of', 'confidence', 'notes_en'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('monster_id', 'int', 'モンスターID（セーブの狩猟記録の添字）', 'Monster ID (hunt-record index)'),
            col('name_ja', 'str', '名前（日本語）', 'Name (Japanese)'),
            col('name_en', 'str', '名前（英語）', 'Name (English)'),
            col('category', 'str', 'large / small / unused', 'large / small / unused'),
            col('class', 'str', '種別（飛竜種など）', 'Monster class'),
            col('has_size_record', 'bool', 'サイズ記録を持つか', 'Has a size record'),
            col('base_size_cm', 'float', '基準サイズ(cm)', 'Base size (cm)'),
            col('mini_le', 'int', '最小冠の閾値(%)', 'Mini crown threshold (%)'),
            col('silver_ge', 'int', '銀冠の閾値(%)', 'Silver crown threshold (%)'),
            col('gold_ge', 'int', '金冠の閾値(%)', 'Gold crown threshold (%)'),
            col('fixed_size', 'bool', 'サイズ変動なし', 'Fixed size'),
            col('crown_awards', 'bool', '冠の勲章対象', 'Counts for crown awards'),
            col('card_pos', 'int', 'ギルドカードの並び位置', 'Guild Card position'),
            col('notes_bit', 'int', '狩猟ノートのビット', "Hunter's Notes bit"),
            col('family_of', 'int', '派生元モンスターID', 'Base monster ID (variants)'),
            col('confidence', 'str', '名前の確度（元データ）', 'Name confidence (source)'),
            col('notes_en', 'str', '元データの注記（英語）', 'Source note'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/monster-index.csv',
                   'mhnxeditor/.work/finalaudit/refsrc/data/monster-sizes.csv',
                   'mhnxeditor/crates/mhnx-core/src/gamedata.rs (MONSTER_HUNT_NAMES)'],
        'confidence': 'derived',
        'notes_ja': ('monster_id はセーブの狩猟記録の添字 1..137（docs/02-monster-records.md）。'
                     'name_ja は gamedata.rs の MONSTER_HUNT_NAMES（ゲーム内の名称テーブル由来、'
                     '137 件・同順）。106..112 は「不明」、134 は空スロットのため name_ja を空にした。'
                     'name_en は monster-index.csv。サイズ系の列は monster-sizes.csv を index で結合。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ stages
    arcs = quest_arcs(a.romfs)
    qi = {int(r['quest_id']): r for r in read_csv(ref('quest-info.csv'))}
    qidx = read_csv(ref('quest-index.csv'))
    stage_rows_ids = collections.Counter()
    for r in qidx:
        info = qi.get(int(r['quest_id']))
        if info:
            stage_rows_ids[int(info['stage'])] += 1
    # evidence counts for the Japanese names
    ev = collections.Counter()
    ev_total = collections.Counter()
    for qid, e in arcs.items():
        ev_total[e['map']] += 1
        word = STAGE_JA_WORD.get(e['map'])
        if word and word in ' '.join(e['text']):
            ev[e['map']] += 1
    rows = []
    for sid in sorted(STAGE_TEXT):
        ja, conf, why = STAGE_JA[sid]
        base = sid % 100
        night = 'yes' if sid >= 101 else 'no'
        note = why
        if ja:
            note = '%s（%d/%d 件の依頼文に一致）' % (why, ev[sid], ev_total[sid])
        else:
            note = ('%s（%d/%d 件）のみで、stage 9「闘技場」との日本語名の区別が'
                    'この dump だけでは確定できないため name_ja は空' % (why, ev[sid], ev_total[sid]))
        if sid == 17:
            note += ('。ゲーム内の英語短縮名は Forlorn Arena で、日本語の「塔」とは'
                     '一対一に対応しない（英語名はゲームの message table のまま）')
        rows.append([
            sid, ja, STAGE_FULL[sid], STAGE_TEXT[sid], 'm%02d' % base, night,
            base if night == 'yes' else '', stage_rows_ids.get(sid, 0),
            conf, note,
        ])
    tables.append({
        'id': 'stages', 'title_ja': 'ステージ', 'title_en': 'Stages',
        'file': 'stages.csv', 'primary_key': 'stage_id',
        'header': ['stage_id', 'name_ja', 'name_en', 'short_en', 'map_code',
                   'night', 'base_stage_id', 'quest_count', 'confidence', 'notes_ja'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('stage_id', 'int', 'ステージID（questData .mib +0x14）', 'Stage ID (questData .mib +0x14)'),
            col('name_ja', 'str', '名前（日本語）', 'Name (Japanese)'),
            col('name_en', 'str', '名前（英語・正式）', 'Name (English, full)'),
            col('short_en', 'str', 'クエストボードの短縮名（英語）', 'Quest-board short name (English)'),
            col('map_code', 'str', 'ステージのリソース名', 'Stage resource name'),
            col('night', 'bool', '夜版か', 'Night variant'),
            col('base_stage_id', 'int', '夜版の元ステージID', 'Day stage of a night variant'),
            col('quest_count', 'int', 'quests.csv の該当行数', 'Rows in quests.csv'),
            col('confidence', 'str', '確度', 'Confidence'),
            col('notes_ja', 'str', '根拠', 'Evidence'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv (stage 列)',
                   'mhnxeditor/.work/finalaudit/refsrc/tools/quest_info.py (STAGE_TEXT)',
                   'romfs/nativeNX/arc/quest/q*.arc (questData .mib +0x14, questData_*_jpn)',
                   'romfs/nativeNX/arc/stage (m01d..m27d)'],
        'confidence': 'curated',
        'notes_ja': ('テーブル全体の confidence は行の弱い方に合わせて curated。'
                     'うち 19 行（1-8, 11-14, 22-24, 101-104）は Harvest Tour の日英タイトルが'
                     '1 対 1 で対応するため derived、残り 12 行（9, 10, 15-21, 25-27）が curated。'
                     'stage_id は questData .mib の +0x14。quest-info.csv の stage 列と'
                     '1855 クエスト中 1512 件で全一致（不一致 0）。1..27 は arc/stage の '
                     'm01d..m27d に対応し、101..104 は 1..4 の夜版（Harvest Tour の日本語名が'
                     '同一）。name_en はゲーム自身の questMessage_eng の短縮名（refsrc の '
                     'STAGE_TEXT）を正式名に展開したもの。name_ja は questData の日本語本文から'
                     'の対応付けで、根拠件数を各行の notes_ja に書いた。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ quests
    rows = []
    for r in qidx:
        qid = int(r['quest_id'])
        info = qi.get(qid, {})
        arc = arcs.get(qid, {})
        text = arc.get('text') or []
        rows.append([
            int(r['index']), qid, r['category'], r['prowler'], r['rank'],
            r['name'], text[0] if text else '',
            to_int(info.get('stage'), ''), int(r['group']), int(r['alt']),
            to_bool(r['expansion']), r['sets'],
            arc.get('kind', ''), arc.get('time_limit', ''), arc.get('revive_count', ''),
            to_int(info.get('reward'), ''), to_int(info.get('hrp'), ''),
            to_int(info.get('fee'), ''), to_int(info.get('sub_reward'), ''),
            to_int(info.get('sub_hrp'), ''), r['notes'],
        ])
    tables.append({
        'id': 'quests', 'title_ja': 'クエスト', 'title_en': 'Quests',
        'file': 'quests.csv', 'primary_key': 'quest_index',
        'header': ['quest_index', 'quest_id', 'category', 'prowler', 'rank',
                   'name_en', 'name_ja', 'stage_id', 'group', 'alt', 'expansion',
                   'sets', 'quest_kind', 'time_limit', 'revive_count', 'reward',
                   'hrp', 'fee', 'sub_reward', 'sub_hrp', 'notes'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('quest_index', 'int', 'クエストリストの添字（ビットマップ位置）', 'Quest list index (bitmap position)'),
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('category', 'str', 'Village / Hub / Arena / Training / Special Permit / Event など', 'Category'),
            col('prowler', 'bool', 'ニャンター専用か', 'Prowler only'),
            col('rank', 'str', '★レベル（1-10、G級は G1-G4、空欄は不明）', 'Star rank (1-10, G1-G4, empty = unknown)'),
            col('name_en', 'str', 'クエスト名（英語）', 'Quest name (English)'),
            col('name_ja', 'str', 'クエスト名（日本語）', 'Quest name (Japanese)'),
            col('stage_id', 'int', 'ステージID', 'Stage ID'),
            col('group', 'int', 'quest_group のグループ番号', 'quest_group group byte'),
            col('alt', 'int', 'グループ内の代替セット', 'Alternative set in the group'),
            col('expansion', 'bool', 'XX 追加クエストか', 'Added by the XX expansion'),
            col('sets', 'str', 'クエストセット番号（空白区切り）', 'Quest set numbers (space separated)'),
            col('quest_kind', 'int', 'クエスト種類（.mib +0x10）', 'Quest kind (.mib +0x10)'),
            col('time_limit', 'int', '制限時間（分）', 'Time limit (minutes)'),
            col('revive_count', 'int', '復活回数', 'Revive count'),
            col('reward', 'int', '報酬金(z)', 'Reward (z)'),
            col('hrp', 'int', 'HRポイント', 'Hunter Rank points'),
            col('fee', 'int', '契約金(z)', 'Contract fee (z)'),
            col('sub_reward', 'int', 'サブ報酬金(z)', 'Subquest reward (z)'),
            col('sub_hrp', 'int', 'サブHRポイント', 'Subquest HR points'),
            col('notes', 'str', '元データの注記', 'Source note'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/quest-index.csv',
                   'mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv',
                   'romfs/nativeNX/arc/quest/q*.arc (questData .mib, questData_*_jpn)'],
        'confidence': 'derived',
        'notes_ja': ('主キーは quest_index（クエストリストの添字 1..1508）。quest_id は 1049 と '
                     '1050 がリストに 2 回現れる（index 313/314 と 315/316）ため一意でない。'
                     'name_ja は questData_*_jpn の 0 番目（タイトル）。stage_id は .mib +0x14。'
                     'quest_kind/time_limit/revive_count も .mib から。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ quest-monsters
    rows = []
    seen = collections.Counter()
    for r in read_csv(ref('quest-monsters.csv')):
        k = r['quest_id']
        seen[k] += 1
        rows.append([len(rows) + 1, int(k), seen[k] - 1, int(r['monster']),
                     int(r['size']), int(r['table'])])
    tables.append({
        'id': 'quest-monsters', 'title_ja': 'クエスト出現モンスター',
        'title_en': 'Quest monsters', 'file': 'quest-monsters.csv',
        'primary_key': 'row_id',
        'header': ['row_id', 'quest_id', 'entry_no', 'monster_id', 'size', 'size_table'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('row_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('entry_no', 'int', 'クエスト内の出現順（0 始まり）', 'Boss entry ordinal in the quest (0-based)'),
            col('monster_id', 'int', 'モンスターID', 'Monster ID'),
            col('size', 'int', 'サイズ(%)', 'Size (%)'),
            col('size_table', 'int', 'サイズ変動テーブル番号', 'Size variation table'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/quest-monsters.csv'],
        'confidence': 'verified',
        'notes_ja': ('元 CSV は (quest_id, monster_id, size, size_table) が 49 組重複する'
                     '（同じクエストに同条件の個体が 2 体出る正規のデータ）。主キーは連番 '
                     'row_id とし、自然キーは (quest_id, entry_no)。entry_no は quest_sizes.py が'
                     '書き出した順（クエスト内のボス枠順、サイズを持つ枠のみ）の 0 始まり連番。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ quest-rewards
    rows = []
    for r in read_csv(ref('quest-rewards.csv')):
        rows.append([len(rows) + 1, int(r['quest_id']), int(r['slot']), int(r['rem'])])
    tables.append({
        'id': 'quest-rewards', 'title_ja': 'クエスト報酬枠',
        'title_en': 'Quest rewards', 'file': 'quest-rewards.csv',
        'primary_key': 'row_id',
        'header': ['row_id', 'quest_id', 'slot', 'rem_id'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('row_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('slot', 'int', '報酬枠番号 0..4', 'Reward slot 0..4'),
            col('rem_id', 'int', '報酬テーブル(.rem)番号', 'Reward table (.rem) id'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/quest-rewards.csv'],
        'confidence': 'verified',
        'notes_ja': ('自然キーは (quest_id, slot)（4897 行すべて一意）。主キーは連番 row_id。'
                     'rem_id は報酬抽選テーブル .rem の番号で、実際の当選品は '
                     'refsrc/data/rewards.csv（rem 単位）を引く。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ npcs
    npc_ja = read_gmd(tab('NpcName_jpn.gmd'))[1]
    rows = []
    for r in read_csv(ref('npc-index.csv')):
        bit = int(r['bit'])
        rows.append([int(r['npc_id']), bit, npc_ja[bit] if bit < len(npc_ja) else '',
                     r['name'], r['talk_file']])
    tables.append({
        'id': 'npcs', 'title_ja': 'NPC', 'title_en': 'NPCs', 'file': 'npcs.csv',
        'primary_key': 'npc_id',
        'header': ['npc_id', 'bit', 'name_ja', 'name_en', 'talk_file'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('npc_id', 'int', 'NPC ID', 'NPC ID'),
            col('bit', 'int', 'NPC ビットマップのビット番号', 'Per-NPC bitmap bit'),
            col('name_ja', 'str', '名前（日本語）', 'Name (Japanese)'),
            col('name_en', 'str', '名前（英語）', 'Name (English)'),
            col('talk_file', 'bool', '会話ファイルを持つか', 'Has a talk file'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/npc-index.csv',
                   'romfs/nativeNX/table/NpcName_jpn.gmd'],
        'confidence': 'derived',
        'notes_ja': ('npc-index.csv の bit を NpcName_jpn.gmd の添字にそのまま使った'
                     '（bit 0 → ベルナ村の村長 = Bherna Chief、以下 188 件すべて対応）。'
                     'npc_id は 1..812 で連番ではない。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ arena
    rows = []
    for r in read_csv(ref('arena.csv')):
        rows.append([int(r['index']), int(r['quest_id']), r['prowler'],
                     int(r['grade_a']), int(r['grade_b']), int(r['grade_c']), r['sets']])
    tables.append({
        'id': 'arena', 'title_ja': '闘技大会', 'title_en': 'Arena', 'file': 'arena.csv',
        'primary_key': 'arena_index',
        'header': ['arena_index', 'quest_id', 'prowler', 'grade_a', 'grade_b',
                   'grade_c', 'sets'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('arena_index', 'int', '闘技大会の並び順', 'Arena record index'),
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('prowler', 'bool', 'ニャンター部門か', 'Prowler division'),
            col('grade_a', 'int', 'A グレードのタイム(秒)', 'Grade A time (seconds)'),
            col('grade_b', 'int', 'B グレードのタイム(秒)', 'Grade B time (seconds)'),
            col('grade_c', 'int', 'C グレードのタイム(秒)', 'Grade C time (seconds)'),
            col('sets', 'str', 'クエストセット番号（空白区切り）', 'Quest set numbers'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/arena.csv'],
        'confidence': 'verified',
        'notes_ja': '闘技大会 17 件（ハンター 11・ニャンター 6）。grade_* はグレード取得の制限時間（秒）。',
        'notes_en': '',
    })

    # ------------------------------------------------------------ awards
    medal = read_gmd(tab('GC_Medal_jpn.gmd'))[1]
    rows = []
    for r in read_csv(ref('awards.csv')):
        bit = int(r['bit'])
        rows.append([bit, r['grid'], medal[bit], r['name'],
                     medal[132 + bit] if 132 + bit < len(medal) else ''])
    tables.append({
        'id': 'awards', 'title_ja': '勲章', 'title_en': 'Awards', 'file': 'awards.csv',
        'primary_key': 'award_id',
        'header': ['award_id', 'grid', 'name_ja', 'name_en', 'desc_ja'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('award_id', 'int', '勲章ビット番号', 'Award bit'),
            col('grid', 'str', 'ギルドカードのページ', 'Guild Card page'),
            col('name_ja', 'str', '勲章名（日本語）', 'Award name (Japanese)'),
            col('name_en', 'str', '勲章名（英語）', 'Award name (English)'),
            col('desc_ja', 'str', '説明（日本語）', 'Description (Japanese)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/awards.csv',
                   'romfs/nativeNX/table/GC_Medal_jpn.gmd'],
        'confidence': 'derived',
        'notes_ja': ('GC_Medal_jpn.gmd は 264 件で、0..131 が勲章名、132..263 が同じ順の説明。'
                     'award_id = ビット番号。名前は bit、説明は 132+bit で引いた'
                     '（例: bit 0 = ベルナ村長の飾り帯 / 「村の★１と★２の全クエストをクリアした証」）。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ canteen
    kitchen = read_gmd(tab('Kitchen_jpn.gmd'))[1]
    # Ingredient bit -> Kitchen entry.  The first seven of each category are in the base
    # block at 103; the rest were appended by XX at 251, in category order.
    ING_BASE = {0: 103, 9: 110, 19: 117, 29: 124, 39: 131}
    ING_CAT = {'meat': 0, 'grain': 9, 'vegetable': 19, 'fish': 29, 'drink': 39}
    ing_index = {}
    for cat, base_bit in ING_CAT.items():
        for k in range(7):
            ing_index[base_bit + k] = ING_BASE[base_bit] + k
    extra = [7, 8, 16, 17, 18, 26, 27, 28, 36, 37, 38, 42, 43, 44]
    for k, bit in enumerate(extra):
        ing_index[bit] = 251 + k
    rows = []
    for r in read_csv(ref('canteen.csv')):
        kind, bit = r['kind'], int(r['bit'])
        if kind == 'ingredient':
            idx = ing_index[bit]
        else:
            idx = 134 + bit if bit <= 76 else 265 + (bit - 77)
        rows.append([len(rows) + 1, kind, bit, kitchen[idx], r['name'], r['category'],
                     r['ingredient_a'], r['ingredient_b']])
    tables.append({
        'id': 'canteen', 'title_ja': '食堂', 'title_en': 'Canteen', 'file': 'canteen.csv',
        'primary_key': 'canteen_id',
        'header': ['canteen_id', 'kind', 'bit', 'name_ja', 'name_en', 'category',
                   'ingredient_a', 'ingredient_b'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('canteen_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('kind', 'str', 'ingredient（食材）/ dish（料理）', 'ingredient / dish'),
            col('bit', 'int', '食材・料理のビット番号', 'Ingredient / dish bit'),
            col('name_ja', 'str', '名前（日本語）', 'Name (Japanese)'),
            col('name_en', 'str', '名前（英語）', 'Name (English)'),
            col('category', 'str', '肉・穀物・野菜・魚・飲み物・special・starter', 'Category'),
            col('ingredient_a', 'str', '料理の食材1（食材ビット）', 'Dish ingredient 1 (bit)'),
            col('ingredient_b', 'str', '料理の食材2（食材ビット）', 'Dish ingredient 2 (bit)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/canteen.csv',
                   'romfs/nativeNX/table/Kitchen_jpn.gmd'],
        'confidence': 'derived',
        'notes_ja': ('自然キーは (kind, bit)。主キーは連番 canteen_id。'
                     'Kitchen_jpn.gmd の並びは、各カテゴリ先頭 7 件の食材が 103..133、'
                     'XX で追加された 14 件が 251..264、料理 0..76 が 134..210、'
                     '料理 77..98 が 265..286。名前の意味（例 dish 0 Dauntless Pasta = '
                     '屋台の根性まかない飯、dish 98 Ultimate Rice = 屋台の究極まかない飯）で'
                     '全 144 件を確認した。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ provisions
    rows = [[int(r['item']), int(r['value']), int(r['group1']),
             int(r['group2']), int(r['group3'])]
            for r in read_csv(ref('provisions.csv'))]
    tables.append({
        'id': 'provisions', 'title_ja': '調合・素材の供出値',
        'title_en': 'Provisions', 'file': 'provisions.csv', 'primary_key': 'item_id',
        'header': ['item_id', 'value', 'group1', 'group2', 'group3'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('item_id', 'int', 'アイテムID', 'Item ID'),
            col('value', 'int', '供出値', 'Provision value'),
            col('group1', 'int', '供出グループ1', 'Provision group 1'),
            col('group2', 'int', '供出グループ2', 'Provision group 2'),
            col('group3', 'int', '供出グループ3', 'Provision group 3'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/provisions.csv'],
        'confidence': 'verified',
        'notes_ja': ('武具の生産・強化で「素材の供出」に使う値。itemData の +27（値）と '
                     '+28 の u16 x3（グループ）。グループ 4 は鉱石系（鉄鉱石 1 など）。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ requests
    act = read_gmd(tab('activityData_jpn.gmd'))[1]
    rows = []
    for r in read_csv(ref('request-index.csv')):
        i = int(r['index'])
        qid = to_int(r['quest_id'])
        arc = arcs.get(qid) if qid is not None else None
        rows.append([
            i, int(r['kind']), int(r['stage']), int(r['npc'], 0), r['village'],
            qid if qid is not None else '', r['quest_name'],
            (arc['text'][0] if arc and arc['text'] else ''),
            to_int(r['prereq_quest'], ''), to_int(r['reward_id'], ''),
            to_int(r['reward_count'], ''), int(r['accept_flag']), int(r['done_flag']),
            act[5 * i] if 5 * i < len(act) else '',
        ])
    tables.append({
        'id': 'requests', 'title_ja': '村依頼', 'title_en': 'Requests',
        'file': 'requests.csv', 'primary_key': 'request_index',
        'header': ['request_index', 'kind', 'stage', 'npc_id', 'village', 'quest_id',
                   'quest_name_en', 'quest_name_ja', 'prereq_quest', 'reward_id',
                   'reward_count', 'accept_flag', 'done_flag', 'name_ja'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('request_index', 'int', '依頼レコード番号 0..183', 'Request record index'),
            col('kind', 'int', '0 クエスト / 1 納品 / 2 不明 / 3 終端', '0 quest / 1 delivery / 2 unknown / 3 end'),
            col('stage', 'int', '解放される村・集会所の段階', 'Progress stage'),
            col('npc_id', 'int', '依頼主 NPC の番号', 'Requesting NPC'),
            col('village', 'str', '依頼が出る村', 'Village'),
            col('quest_id', 'int', '対象クエストID', 'Quest ID'),
            col('quest_name_en', 'str', 'クエスト名（英語）', 'Quest name (English)'),
            col('quest_name_ja', 'str', 'クエスト名（日本語）', 'Quest name (Japanese)'),
            col('prereq_quest', 'int', '前提クエストID', 'Prerequisite quest'),
            col('reward_id', 'int', '報酬アイテムID', 'Reward item ID'),
            col('reward_count', 'int', '報酬個数', 'Reward count'),
            col('accept_flag', 'int', '受注フラグ番号', 'Accepted flag index'),
            col('done_flag', 'int', '報告済みフラグ番号', 'Completed flag index'),
            col('name_ja', 'str', '依頼名（日本語）', 'Request name (Japanese)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/request-index.csv',
                   'romfs/nativeNX/table/activityData_jpn.gmd',
                   'romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)'],
        'confidence': 'derived',
        'notes_ja': ('activityData_jpn.gmd は 920 件 = 184 レコード x 5。依頼 index i の名前は '
                     '5*i 番目（例 i=0「しっかり者の村人の依頼１」、i=3「ベルナ村の受付嬢の依頼１」）。'
                     'quest_name_ja は対象クエストの questData タイトル。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ monster-carves
    rows = []
    seen = collections.Counter()
    for r in read_csv(ref('monster-carves.csv')):
        k = (r['monster'], r['rank'], r['sets'], r['kind'])
        seen[k] += 1
        rows.append([len(rows) + 1, int(r['monster']), r['rank'], int(r['sets']),
                     r['kind'], seen[k] - 1, int(r['item']), int(r['count']),
                     int(r['chance'])])
    tables.append({
        'id': 'monster-carves', 'title_ja': 'モンスター剥ぎ取り',
        'title_en': 'Monster carves', 'file': 'monster-carves.csv',
        'primary_key': 'carve_id',
        'header': ['carve_id', 'monster_id', 'rank', 'sets', 'kind', 'entry_no',
                   'item_id', 'count', 'chance'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('carve_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('monster_id', 'int', 'モンスターID', 'Monster ID'),
            col('rank', 'str', 'low / high / g', 'low / high / g'),
            col('sets', 'int', '剥ぎ取りセット番号', 'Carve set number'),
            col('kind', 'str', 'body / tail / shiny / other', 'body / tail / shiny / other'),
            col('entry_no', 'int', '同セット内の行番号（0 始まり）', 'Row ordinal within the table'),
            col('item_id', 'int', 'アイテムID', 'Item ID'),
            col('count', 'int', '個数', 'Count'),
            col('chance', 'int', '確率(%)', 'Chance (%)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/monster-carves.csv'],
        'confidence': 'verified',
        'notes_ja': ('自然キーは (monster_id, rank, sets, kind, entry_no)。元 CSV は '
                     '(monster_id, rank, sets, kind, item_id) が 2 件だけ重複する'
                     '（モンスター38 の kind=other に別テーブルの同アイテムが 2 行）。'
                     'entry_no は同じ (monster,rank,sets,kind) 内の 0 始まり連番。'
                     '1 テーブルの確率合計は 100。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ recipes
    rows = []
    seen = collections.Counter()
    for r in read_csv(ref('recipes.csv')):
        k = (r['kind'], r['id'], r['level'])
        seen[k] += 1
        rows.append([len(rows) + 1, r['kind'], int(r['id']), int(r['level']),
                     seen[k] - 1, int(r['item1']), int(r['count1']), int(r['item2']),
                     int(r['count2']), int(r['item3']), int(r['count3']),
                     int(r['item4']), int(r['count4']), int(r['group']),
                     int(r['value'])])
    tables.append({
        'id': 'recipes', 'title_ja': '生産・強化レシピ',
        'title_en': 'Recipes', 'file': 'recipes.csv', 'primary_key': 'recipe_id',
        'header': ['recipe_id', 'kind', 'target_id', 'level', 'recipe_no',
                   'item1', 'count1', 'item2', 'count2', 'item3', 'count3',
                   'item4', 'count4', 'provision_group', 'provision_value'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('recipe_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('kind', 'str', 'weapon:<武器種> / armor / deco', 'weapon:<class> / armor / deco'),
            col('target_id', 'int', '生産対象の武器ID・防具ID・装飾品アイテムID', 'Weapon / armor / decoration ID'),
            col('level', 'int', '0 = 生産、1 以上 = そのレベルへの強化', '0 forge, 1+ upgrade level'),
            col('recipe_no', 'int', '同じ (kind, target_id, level) 内の 0 始まり連番', 'Ordinal within (kind, target_id, level)'),
            col('item1', 'int', '素材1のアイテムID', 'Material 1 item ID'),
            col('count1', 'int', '素材1の個数', 'Material 1 count'),
            col('item2', 'int', '素材2のアイテムID', 'Material 2 item ID'),
            col('count2', 'int', '素材2の個数', 'Material 2 count'),
            col('item3', 'int', '素材3のアイテムID', 'Material 3 item ID'),
            col('count3', 'int', '素材3の個数', 'Material 3 count'),
            col('item4', 'int', '素材4のアイテムID', 'Material 4 item ID'),
            col('count4', 'int', '素材4の個数', 'Material 4 count'),
            col('provision_group', 'int', '供出グループ', 'Provision group'),
            col('provision_value', 'int', '供出値', 'Provision value'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/recipes.csv'],
        'confidence': 'verified',
        'notes_ja': ('自然キーは (kind, target_id, level, recipe_no)。元 CSV は '
                     '(kind, id, level) が 127 組重複する（同じ武器・装飾品に別素材の'
                     '生産レシピが 2 本ある正規のデータ）。recipe_no はその 0 始まり連番。'
                     '素材なしは item=0 / count=0。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ rewards
    # rewards.csv: one row per reward roll of one .rem table.  The same item can appear
    # twice in a table with different chances (the game rolls each row on its own), so
    # the only stable key is the row's position inside its table.
    rows = []
    seen = collections.Counter()
    for r in read_csv(ref('rewards.csv')):
        rem = r['rem']
        seen[rem] += 1
        rows.append([len(rows) + 1, int(rem), seen[rem] - 1, int(r['item']),
                     int(r['count']), int(r['chance'])])
    tables.append({
        'id': 'rewards', 'title_ja': 'クエスト報酬テーブル',
        'title_en': 'Reward tables', 'file': 'rewards.csv',
        'primary_key': 'reward_id',
        'header': ['reward_id', 'rem_id', 'entry_no', 'item_id', 'count', 'chance'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('reward_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('rem_id', 'int', '報酬テーブル(.rem)番号', 'Reward table (.rem) id'),
            col('entry_no', 'int', 'テーブル内の行番号（0 始まり）', 'Row ordinal within the table'),
            col('item_id', 'int', 'アイテムID', 'Item ID'),
            col('count', 'int', '個数', 'Count'),
            col('chance', 'int', '確率(%)', 'Chance (%)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/rewards.csv'],
        'confidence': 'verified',
        'notes_ja': ('quest-rewards.csv の rem_id を引く先。rem_id ごとに 1..22 行あり、'
                     '同じ rem に同じアイテムが 2 行出ることがある（571 組）ので、'
                     '自然キーは (rem_id, entry_no)。(rem_id, item_id, count, chance) も'
                     '10,992 行すべて一意。chance は 1..100 で、1 テーブルの合計は 100。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ quest-unlock
    rows = []
    for r in read_csv(ref('quest-unlock.csv')):
        qid = int(r['quest_id'])
        arc = arcs.get(qid) or {}
        text = arc.get('text') or []
        rows.append([qid, r['name'], text[0] if text else '', r['rule']])
    tables.append({
        'id': 'quest-unlock', 'title_ja': 'クエスト出現条件',
        'title_en': 'Quest unlock rules', 'file': 'quest-unlock.csv',
        'primary_key': 'quest_id',
        'header': ['quest_id', 'name_en', 'name_ja', 'rule'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('name_en', 'str', 'クエスト名（英語）', 'Quest name (English)'),
            col('name_ja', 'str', 'クエスト名（日本語）', 'Quest name (Japanese)'),
            col('rule', 'str', '出現条件（flag: / cleared: / hr: / village_star: など）', 'Unlock rule'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/quest-unlock.csv',
                   'romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)'],
        'confidence': 'derived',
        'notes_ja': ('quest_id は 1,506 件で、quests.csv の quest_id 集合と完全に一致する。'
                     'rule は "flag:396" "cleared:11404" "hr:7" "village_star:6 AND ..." の形で、'
                     '空欄 204 件は条件なし（最初から出る）。name_ja は questData のタイトル。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ unlock-lists
    rows = []
    for r in read_csv(ref('unlock-lists.csv')):
        rows.append([len(rows) + 1, r['map'], int(r['bit']),
                     to_int(r['id'], ''), r['need']])
    tables.append({
        'id': 'unlock-lists', 'title_ja': '解放ビット一覧',
        'title_en': 'Unlock maps', 'file': 'unlock-lists.csv',
        'primary_key': 'unlock_id',
        'header': ['unlock_id', 'map', 'bit', 'target_id', 'need'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('unlock_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('map', 'str', '解放マップ名（lab / song / armory:7 / trader:words など）', 'Unlock map name'),
            col('bit', 'int', 'マップ内のビット番号', 'Bit in the map'),
            col('target_id', 'int', '解放される装備・アイテムID（無い行は空）', 'Unlocked equipment / item id'),
            col('need', 'str', '解放条件（start / dlc / v2|h2 / q806&q10768 など）', 'Unlock condition'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/unlock-lists.csv'],
        'confidence': 'verified',
        'notes_ja': ('自然キーは (map, bit)（1,418 行すべて一意）。map は 38 種で、'
                     '研究施設 lab・ジュークボックス song・武具屋 armory:1..21・'
                     '交易商 trader:*・shop:0/1 など。need は "start"（最初から）'
                     '"dlc"（配信）"never"（未使用）や "v2|h2"（村★2 または 集会所★2）'
                     '"q806&q10768"（両方クリア）の形。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ size-variation
    rows = []
    for r in read_csv(ref('size-variation.csv')):
        rows.append([len(rows) + 1, int(r['table']), int(r['rate']), int(r['chance'])])
    tables.append({
        'id': 'size-variation', 'title_ja': 'サイズ変動テーブル',
        'title_en': 'Size variation tables', 'file': 'size-variation.csv',
        'primary_key': 'variation_id',
        'header': ['variation_id', 'size_table', 'rate', 'chance'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('variation_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('size_table', 'int', 'サイズ変動テーブル番号 0..51', 'Size variation table 0..51'),
            col('rate', 'int', '倍率（%・整数）', 'Scale rate (%)'),
            col('chance', 'int', '確率(%)', 'Chance (%)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/size-variation.csv'],
        'confidence': 'verified',
        'notes_ja': ('ゲームの em_size_yure_data（52 テーブル）。クエストの boss 枠が'
                     'size_table を指し、サイズ = クエストの size% × rate。'
                     '自然キーは (size_table, rate)（1,385 行すべて一意）。'
                     'rate は 88..130、chance 0 の行は元データに無い。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ rotating-quests
    rows = []
    for r in read_csv(ref('rotating-quests.csv')):
        qid = int(r['quest_id'])
        arc = arcs.get(qid) or {}
        text = arc.get('text') or []
        rows.append([int(r['bit']), qid, r['param_hex'], r['name'],
                     text[0] if text else ''])
    tables.append({
        'id': 'rotating-quests', 'title_ja': '日替わりクエスト',
        'title_en': 'Rotating quests', 'file': 'rotating-quests.csv',
        'primary_key': 'rotating_bit',
        'header': ['rotating_bit', 'quest_id', 'param_hex', 'name_en', 'name_ja'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('rotating_bit', 'int', '日替わりビット 0..50', 'Rotating bit 0..50'),
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('param_hex', 'str', 'クエストパラメータ（16 進）', 'Quest parameter (hex)'),
            col('name_en', 'str', 'クエスト名（英語）', 'Quest name (English)'),
            col('name_ja', 'str', 'クエスト名（日本語）', 'Quest name (Japanese)'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/rotating-quests.csv',
                   'romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)'],
        'confidence': 'derived',
        'notes_ja': ('セーブの base + 0x504B のビットで、次に 1 クエストクリアするまで有効。'
                     'ビット 0..50 の 51 件で、quest_id はすべて quests.csv に存在する。'
                     'name_ja は questData のタイトル。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ request-offer
    rows = []
    for r in read_csv(ref('request-offer.csv')):
        qid = to_int(r['quest_id'])
        arc = arcs.get(qid) if qid is not None else None
        rows.append([len(rows) + 1, int(r['index']), qid if qid is not None else '',
                     r['quest_name'],
                     (arc['text'][0] if arc and arc['text'] else ''),
                     int(r['npc_file']), int(r['npc_bit']), r['npc_name'],
                     int(r['talk_kind']), int(r['talk_line']),
                     int(r['accept_flag']), r['also'], r['offer']])
    tables.append({
        'id': 'request-offer', 'title_ja': '村依頼の提示条件',
        'title_en': 'Request offers', 'file': 'request-offer.csv',
        'primary_key': 'offer_id',
        'header': ['offer_id', 'request_index', 'quest_id', 'quest_name_en',
                   'quest_name_ja', 'npc_file', 'npc_bit', 'npc_name', 'talk_kind',
                   'talk_line', 'accept_flag', 'also', 'offer'],
        'rows': rows, 'id_col': 0,
        'columns': [
            col('offer_id', 'int', '連番（主キー）', 'Serial primary key'),
            col('request_index', 'int', 'requests.csv の request_index', 'requests.csv request_index'),
            col('quest_id', 'int', 'クエストID', 'Quest ID'),
            col('quest_name_en', 'str', 'クエスト名（英語）', 'Quest name (English)'),
            col('quest_name_ja', 'str', 'クエスト名（日本語）', 'Quest name (Japanese)'),
            col('npc_file', 'int', '会話ファイル番号', 'Talk file number'),
            col('npc_bit', 'int', '会話ファイル内の NPC ビット', 'NPC bit in the talk file'),
            col('npc_name', 'str', 'NPC 名（英語）', 'NPC name (English)'),
            col('talk_kind', 'int', '会話の種類', 'Talk kind'),
            col('talk_line', 'int', '会話行番号', 'Talk line'),
            col('accept_flag', 'int', '受注フラグ番号', 'Accepted flag index'),
            col('also', 'str', '同時に設定・解除するフラグ', 'Flags set or cleared with it'),
            col('offer', 'str', '提示条件（village_star: / flag: / cleared: など）', 'Offer condition'),
        ],
        'source': ['mhnxeditor/.work/finalaudit/refsrc/data/request-offer.csv',
                   'romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)'],
        'confidence': 'derived',
        'notes_ja': ('NPC の会話データから読んだ「この依頼を出す条件」。自然キーは '
                     '(request_index, npc_file, npc_bit, talk_line) で 186 行すべて一意。'
                     'request_index は 4 組 (28, 135, 149, 150) が 2 行ずつあり、'
                     '28/149/150 は赤鬼/黒鬼の 2 人、135 は同じ NPC の別の会話行。'
                     'quest_id が空の行は納品依頼（kind 1）でクエストを持たない。'),
        'notes_en': '',
    })

    # ------------------------------------------------------------ write
    manifest = {'area': 'world', 'tables': []}
    for t in tables:
        path = os.path.join(out_dir, t['file'])
        n = write_csv(path, t['header'], t['rows'])
        ids = [r[t['id_col']] for r in t['rows']]
        if len(set(ids)) != len(ids):
            problems.append('%s: duplicate primary key' % t['id'])
        if n != len(t['rows']):
            problems.append('%s: row count mismatch' % t['id'])
        manifest['tables'].append({
            'id': t['id'],
            'title_ja': t['title_ja'],
            'title_en': t['title_en'],
            'file': t['file'],
            'primary_key': t['primary_key'],
            'row_count': n,
            'id_range': [min(ids), max(ids)] if ids else None,
            'columns': t['columns'],
            'source': t['source'],
            'confidence': t['confidence'],
            'notes_ja': t['notes_ja'],
            'notes_en': t['notes_en'],
        })
        print('  %-16s %6d rows  id %s..%s' % (t['id'], n, min(ids), max(ids)))

    write_text(os.path.join(out_dir, '_manifest.json'),
               json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('-> %s (%d tables)' % (out_dir, len(tables)))
    if problems:
        for p in problems:
            print('PROBLEM:', p)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
