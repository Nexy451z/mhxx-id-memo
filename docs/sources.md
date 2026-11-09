# 出典と抽出方法

> このファイルは `tools/build.py` が `_manifest.json` と各 `NOTES.md` から自動生成します。手で編集しないこと。

- データ版: `sha256:9f346b940d85d78ba196a13055a17ef9971e9d81d2796ef5d6fdc00cd217ea92`
- テーブル数: **42** / 総行数: **91,406**

## confidence の意味

| 値 | 意味 |
|---|---|
| `verified` | ゲーム実データ（romfs / 実行時メモリ / 既存抽出物）から直接取得した |
| `derived` | 既存テーブル・既知 ID から計算・突合して求めた |
| `curated` | 既知リストを人手で対応付けた（一次証拠が弱い） |

## プレースホルダ（値なし）の扱い

出典の「値なし」表記は、テーブルごとに次の方針で扱っている。どちらも**出典に忠実で、値の捏造はない**。

| 出典の表記 | 扱い | 例 |
|---|---|---|
| `(None)` / `None` などの文字列 | **空文字に置換**（SPEC 0-1「不明は空文字」） | kinsects / talismans の id 0 |
| `-` などの記号 | **出典どおり保持**（改変しない） | npcs の 16 行 |

> 方針が 2 通りあるのは、前者が「値そのものが存在しない」ことを表すのに対し、
> 後者が「出典側が記号で欠損を表現している」ため。データの意味を変えないことを優先した。

## テーブル別の出典

| area | id | テーブル | confidence | 出典 |
|---|---|---|---|---|
| equip | `armor` | 防具 | verified | `romfs/nativeNX/table/armorSeriesData_jpn.gmd`<br>`romfs/nativeNX/table/armorSeriesData.asd`<br>`extract/jp_names/armor_series.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES/_IDS)` |
| equip | `armor-parts` | 防具部位 | verified | `romfs/nativeNX/table/armorSeriesData_jpn.gmd`<br>`extract/jp_names/gen.py (PARTS)`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIPMENT_TYPES)` |
| equip | `armor-skills` | 防具スキルポイント | derived | `mhnxeditor/.work/finalaudit/refsrc/data/armor-skills.csv`<br>`romfs/nativeNX/table/armorSeriesData.asd` |
| equip | `combinations` | 調合 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/combinations.csv`<br>`romfs/nativeNX/table/itemPreData.itp`<br>`romfs/nativeNX/table/itemData_jpn.gmd` |
| equip | `decorations` | 装飾品（珠） | verified | `romfs/nativeNX/table/decoData.deco`<br>`romfs/nativeNX/table/skillTypeData_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (JWL_NAMES, JWL_I_DS)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/decorations.csv` |
| equip | `hunter-arts` | 狩技 | derived | `romfs/nativeNX/table/hunterArtsData.hta`<br>`romfs/nativeNX/table/hunterArtsData_jpn.gmd`<br>`mhnxeditor/.work/finalaudit/refsrc/data/hunter-arts.csv` |
| equip | `item-categories` | アイテムカテゴリ（素材分類） | verified | `romfs/nativeNX/table/itemCategoryTypeData.ict`<br>`romfs/nativeNX/table/itemCategoryTypeData_jpn.gmd` |
| equip | `items` | アイテム | verified | `romfs/nativeNX/table/itemData_jpn.gmd`<br>`romfs/nativeNX/table/itemData.itm`<br>`romfs/nativeNX/table/itemCategoryTypeData.ict` |
| equip | `kinsects` | 猟虫 | verified | `romfs/nativeNX/table/insectData_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (KINSECT_NAMES)` |
| equip | `palico-actions` | オトモ行動（支援行動・スキル） | derived | `mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv`<br>`romfs/nativeNX/arc/resident.arc (otomo/ot_skl, otomo/support/spt_act_base, table/lobby/otSupportIni*pt, otSkillIni*pt)` |
| equip | `palico-armor` | オトモ防具 | verified | `romfs/nativeNX/table/otArmorData_jpn.gmd`<br>`extract/jp_names/palico_armor.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_HEAD_NAMES/_IDS, PALICO_ARMOR_NAMES/_IDS)` |
| equip | `palico-levels` | オトモレベル | derived | `mhnxeditor/.work/finalaudit/refsrc/data/palico-levels.csv`<br>`romfs/nativeNX/arc/resident.arc (otomo/ot_lvl)` |
| equip | `palico-skills` | オトモスキル（術） | verified | `romfs/nativeNX/table/ot_skl_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SKILLS, PALICO_SKILL_NAMES)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv` |
| equip | `palico-support` | オトモ支援行動 | derived | `mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SUPPORT_MOVES)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv` |
| equip | `palico-weapons` | オトモ武器 | verified | `romfs/nativeNX/table/otWeaponData_jpn.gmd`<br>`extract/jp_names/palico_weapon.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_WEAPON_NAMES)` |
| equip | `skill-effects` | スキル効果（発動後のスキル名） | verified | `romfs/nativeNX/table/skillData_jpn.gmd`<br>`extract/jp_names/skills.csv` |
| equip | `skills` | スキル | derived | `romfs/nativeNX/table/skillTypeData.skt`<br>`romfs/nativeNX/table/skillTypeData_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (SKILL_NAMES)` |
| equip | `smithy-lists` | 鍛冶屋リスト | derived | `mhnxeditor/.work/finalaudit/refsrc/data/smithy-lists.csv`<br>`romfs/nativeNX/arc/facility/blacksmith.arc` |
| equip | `talisman-tables` | 護石スキル抽選範囲 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv`<br>`romfs/nativeNX/arc/resident.arc (amuletSkillDataNN, amuletSlotDataNN)` |
| equip | `talismans` | 護石 | verified | `romfs/nativeNX/table/amuletData_jpn.gmd`<br>`extract/jp_names/amulet.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_TALISMAN_NAMES, TALISMAN_RARITY)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv` |
| equip | `weapon-tree` | 武器派生 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/weapon-tree.csv`<br>`romfs/nativeNX/table/weapon*BaseData.w*d` |
| equip | `weapon-types` | 武器種 | verified | `romfs/nativeNX/table/weapon*MsgData_jpn.gmd`<br>`extract/jp_names/weapons.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (HUNT_WEAPONS, EQUIPMENT_TYPES)` |
| equip | `weapons` | 武器 | verified | `romfs/nativeNX/table/weapon*MsgData_jpn.gmd`<br>`romfs/nativeNX/table/weapon*LevelData.w*d`<br>`extract/jp_names/weapons.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES)` |
| world | `monsters` | モンスター | derived | `mhnxeditor/.work/finalaudit/refsrc/data/monster-index.csv`<br>`mhnxeditor/.work/finalaudit/refsrc/data/monster-sizes.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (MONSTER_HUNT_NAMES)` |
| world | `stages` | ステージ | curated | `mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv (stage 列)`<br>`mhnxeditor/.work/finalaudit/refsrc/tools/quest_info.py (STAGE_TEXT)`<br>`romfs/nativeNX/arc/quest/q*.arc (questData .mib +0x14, questData_*_jpn)`<br>`romfs/nativeNX/arc/stage (m01d..m27d)` |
| world | `quests` | クエスト | derived | `mhnxeditor/.work/finalaudit/refsrc/data/quest-index.csv`<br>`mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData .mib, questData_*_jpn)` |
| world | `quest-monsters` | クエスト出現モンスター | verified | `mhnxeditor/.work/finalaudit/refsrc/data/quest-monsters.csv` |
| world | `quest-rewards` | クエスト報酬枠 | verified | `mhnxeditor/.work/finalaudit/refsrc/data/quest-rewards.csv` |
| world | `npcs` | NPC | derived | `mhnxeditor/.work/finalaudit/refsrc/data/npc-index.csv`<br>`romfs/nativeNX/table/NpcName_jpn.gmd` |
| world | `arena` | 闘技大会 | verified | `mhnxeditor/.work/finalaudit/refsrc/data/arena.csv` |
| world | `awards` | 勲章 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/awards.csv`<br>`romfs/nativeNX/table/GC_Medal_jpn.gmd` |
| world | `canteen` | 食堂 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/canteen.csv`<br>`romfs/nativeNX/table/Kitchen_jpn.gmd` |
| world | `provisions` | 調合・素材の供出値 | verified | `mhnxeditor/.work/finalaudit/refsrc/data/provisions.csv` |
| world | `requests` | 村依頼 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/request-index.csv`<br>`romfs/nativeNX/table/activityData_jpn.gmd`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| world | `monster-carves` | モンスター剥ぎ取り | verified | `mhnxeditor/.work/finalaudit/refsrc/data/monster-carves.csv` |
| world | `recipes` | 生産・強化レシピ | verified | `mhnxeditor/.work/finalaudit/refsrc/data/recipes.csv` |
| world | `rewards` | クエスト報酬テーブル | verified | `mhnxeditor/.work/finalaudit/refsrc/data/rewards.csv` |
| world | `quest-unlock` | クエスト出現条件 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/quest-unlock.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| world | `unlock-lists` | 解放ビット一覧 | verified | `mhnxeditor/.work/finalaudit/refsrc/data/unlock-lists.csv` |
| world | `size-variation` | サイズ変動テーブル | verified | `mhnxeditor/.work/finalaudit/refsrc/data/size-variation.csv` |
| world | `rotating-quests` | 日替わりクエスト | derived | `mhnxeditor/.work/finalaudit/refsrc/data/rotating-quests.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| world | `request-offer` | 村依頼の提示条件 | derived | `mhnxeditor/.work/finalaudit/refsrc/data/request-offer.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |

## 出典ファイルの全体

- `extract/jp_names/amulet.csv`
- `extract/jp_names/armor_series.csv`
- `extract/jp_names/gen.py (PARTS)`
- `extract/jp_names/palico_armor.csv`
- `extract/jp_names/palico_weapon.csv`
- `extract/jp_names/skills.csv`
- `extract/jp_names/weapons.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/arena.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/armor-skills.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/awards.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/canteen.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/combinations.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/decorations.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/hunter-arts.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/monster-carves.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/monster-index.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/monster-sizes.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/npc-index.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/palico-levels.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/provisions.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/quest-index.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv (stage 列)`
- `mhnxeditor/.work/finalaudit/refsrc/data/quest-monsters.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/quest-rewards.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/quest-unlock.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/recipes.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/request-index.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/request-offer.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/rewards.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/rotating-quests.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/size-variation.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/smithy-lists.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/unlock-lists.csv`
- `mhnxeditor/.work/finalaudit/refsrc/data/weapon-tree.csv`
- `mhnxeditor/.work/finalaudit/refsrc/tools/quest_info.py (STAGE_TEXT)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIPMENT_TYPES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES/_IDS)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_TALISMAN_NAMES, TALISMAN_RARITY)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (HUNT_WEAPONS, EQUIPMENT_TYPES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (JWL_NAMES, JWL_I_DS)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (KINSECT_NAMES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (MONSTER_HUNT_NAMES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_HEAD_NAMES/_IDS, PALICO_ARMOR_NAMES/_IDS)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SKILLS, PALICO_SKILL_NAMES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SUPPORT_MOVES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_WEAPON_NAMES)`
- `mhnxeditor/crates/mhnx-core/src/gamedata.rs (SKILL_NAMES)`
- `romfs/nativeNX/arc/facility/blacksmith.arc`
- `romfs/nativeNX/arc/quest/q*.arc (questData .mib +0x14, questData_*_jpn)`
- `romfs/nativeNX/arc/quest/q*.arc (questData .mib, questData_*_jpn)`
- `romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)`
- `romfs/nativeNX/arc/resident.arc (amuletSkillDataNN, amuletSlotDataNN)`
- `romfs/nativeNX/arc/resident.arc (otomo/ot_lvl)`
- `romfs/nativeNX/arc/resident.arc (otomo/ot_skl, otomo/support/spt_act_base, table/lobby/otSupportIni*pt, otSkillIni*pt)`
- `romfs/nativeNX/arc/stage (m01d..m27d)`
- `romfs/nativeNX/table/GC_Medal_jpn.gmd`
- `romfs/nativeNX/table/Kitchen_jpn.gmd`
- `romfs/nativeNX/table/NpcName_jpn.gmd`
- `romfs/nativeNX/table/activityData_jpn.gmd`
- `romfs/nativeNX/table/amuletData_jpn.gmd`
- `romfs/nativeNX/table/armorSeriesData.asd`
- `romfs/nativeNX/table/armorSeriesData_jpn.gmd`
- `romfs/nativeNX/table/decoData.deco`
- `romfs/nativeNX/table/hunterArtsData.hta`
- `romfs/nativeNX/table/hunterArtsData_jpn.gmd`
- `romfs/nativeNX/table/insectData_jpn.gmd`
- `romfs/nativeNX/table/itemCategoryTypeData.ict`
- `romfs/nativeNX/table/itemCategoryTypeData_jpn.gmd`
- `romfs/nativeNX/table/itemData.itm`
- `romfs/nativeNX/table/itemData_jpn.gmd`
- `romfs/nativeNX/table/itemPreData.itp`
- `romfs/nativeNX/table/otArmorData_jpn.gmd`
- `romfs/nativeNX/table/otWeaponData_jpn.gmd`
- `romfs/nativeNX/table/ot_skl_jpn.gmd`
- `romfs/nativeNX/table/skillData_jpn.gmd`
- `romfs/nativeNX/table/skillTypeData.skt`
- `romfs/nativeNX/table/skillTypeData_jpn.gmd`
- `romfs/nativeNX/table/weapon*BaseData.w*d`
- `romfs/nativeNX/table/weapon*LevelData.w*d`
- `romfs/nativeNX/table/weapon*MsgData_jpn.gmd`

## 抽出メモ（analyst の NOTES.md）

### 装備・アイテム (`data/equip/NOTES.md`)

### data/equip — 装備・アイテム系 ID テーブル

Monster Hunter XX (Nintendo Switch) の装備・アイテム系 ID を、**romfs の実テーブル**から抽出したもの。
推測値は入れていない。値が取れない列は空文字にしてある。

- 生成: `python tools/extract_equip_tables.py`
- 検証: `python tools/verify_equip_tables.py`
- 装備レコード配置仕様（メモリスキャン補助）: `equip-record-layout.json` / `equip-record-layout.md` /
  `python tools/verify_equip_record_layout.py`（→ §6）
- 文字コード: CSV は UTF-8 BOM 付き / 改行 LF / 値内の改行も LF に統一。`_manifest.json` は BOM なし UTF-8。

> **TSV は `tools/build.py` が CSV から生成する（analyst は作らない）。** このディレクトリに
> 残っている `*.tsv` は builder の生成物なので、CSV を更新したら builder 側で再生成が必要。

---

#### 1. テーブル一覧

##### 第 1 バッチ（SPEC 5 章の担当表 + 追加 1）

| id | 内容 | 行数 | ID 範囲 | confidence |
|---|---|---:|---|---|
| `items` | アイテム | 2991 | 0..2990 | verified |
| `item-categories` | アイテムカテゴリ（素材分類） | 338 | 0..337 | verified |
| `weapons` | 武器（武器種 × 武器 × 名前段階） | 4818 | 0..140802 | verified |
| `weapon-types` | 武器種 | 15 | 0..14 | verified |
| `armor` | 防具（シリーズ × 部位） | 5836 | 0..6431 | verified |
| `armor-parts` | 防具部位 | 5 | 0..4 | verified |
| `decorations` | 装飾品（珠） | 262 | 1..262 | verified |
| `talismans` | 護石 | 11 | 0..10 | verified |
| `skills` | スキル | 206 | 0..205 | derived |
| `skill-effects` | スキル効果（発動後のスキル名）※SPEC 外の追加 | 328 | 0..327 | verified |
| `hunter-arts` | 狩技 | 178 | 1..190 | derived |
| `kinsects` | 猟虫 | 32 | 0..31 | verified |
| `palico-weapons` | オトモ武器 | 509 | 0..508 | verified |
| `palico-armor` | オトモ防具 | 1026 | 0..1053 | verified |
| `palico-skills` | オトモスキル（術） | 96 | 0..95 | verified |
| `palico-support` | オトモ支援行動 | 57 | 0..56 | derived |

##### 第 2 バッチ（追加 7）

| id | 内容 | 行数 | ID 範囲 | confidence |
|---|---|---:|---|---|
| `armor-skills` | 防具スキルポイント | 14639 | 1..14639 | derived |
| `weapon-tree` | 武器派生 | 798 | 1..798 | derived |
| `talisman-tables` | 護石スキル抽選範囲 | 525 | 1..525 | derived |
| `combinations` | 調合 | 183 | 1..183 | derived |
| `smithy-lists` | 鍛冶屋リスト | 23 | 1..23 | derived |
| `palico-actions` | オトモ行動（支援行動・スキル） | 154 | 1..154 | derived |
| `palico-levels` | オトモレベル | 99 | 1..99 | derived |

**合計 23 テーブル / 33,129 行。**

`confidence` の意味は SPEC の定義どおり。`derived` は、ID・名前そのものは実テーブル由来だが、
一部の列を別の表から算出・結合しているもの。

- 第 1 バッチの `derived`: `skills.max_level` / `hunter-arts.weapon_type_id` / `palico-support.points`
- 第 2 バッチは 7 本すべて `derived`（refsrc の生成スクリプトと同じ手順で romfs から再計算し、
  refsrc の CSV と行数・内容が一致することを確認したうえで、参照先の名前を結合している）

##### 主キーについて

SPEC「1 列目は必ず主キー」「ID 列は整数」に合わせ、**複合キーになる表は 1 列目に連番 `row_id`（1 始まり）** を置き、
元の座標はすべて列として残してある。`notes_ja` にも理由を書いた。

| 表 | 本来のキー | 対応 |
|---|---|---|
| `armor-skills` | (armor_id, skill_id) | `row_id` + `armor_id` / `skill_id` を保持 |
| `weapon-tree` | (weapon_type_id, weapon_index) | `row_id` + 座標を保持 |
| `talisman-tables` | (kind, tier, skill_id) | `row_id` + 座標を保持 |
| `combinations` | (item1_id, item2_id) | `row_id` + 座標を保持 |
| `smithy-lists` | list_name（文字列） | `row_id` + `list_name` を保持 |
| `palico-actions` | (kind, action_id) | `row_id` + 座標を保持 |

---

#### 2. 出典と抽出方法

読み取り専用。いずれも `C:\anyWorkspace\nx\mhxx\` 配下。

##### 2.1 romfs の実テーブル (`romfs/nativeNX/table/`)

先頭 8 バイトが `f32 version` + `u32 count` で、その後に固定長レコードが並ぶ。
`len(file) == 8 + count * record_size` を全ファイルで assert している。

| ファイル | レコード長 | 件数 | 用途 |
|---|---:|---:|---|
| `itemData_jpn.gmd` | (2 文字列/件) | 2991 | items の名前・説明 |
| `itemData.itm` | 44 | 2991 | items の分類 (+16) / 素材カテゴリ (+28) |
| `itemCategoryTypeData.ict` | 7 | 338 | item-categories |
| `itemCategoryTypeData_jpn.gmd` | (1 文字列/件) | 338 | item-categories の名前 |
| `weapon*MsgData_jpn.gmd` | (6 文字列/武器) | 14 種 | weapons の名前・説明（3 form × (名前, 説明)） |
| `weapon*LevelData.w*d` | 種ごと | — | weapons の levels（既存 `jp_names/gen.py` の結果を利用） |
| `weapon*BaseData.w*d` | 種ごと | — | weapon-tree（末尾 10 バイト = 5 × (必要Lv, 派生先ID)） |
| `armorSeriesData_jpn.gmd` | (10 文字列/系列) | 1287 | armor の名前・説明 |
| `armorSeriesData.asd` | 127 | 1287 | armor の部位有無 (+6..+10) / armor-skills (+28 から 15B/部位) |
| `decoData.deco` | 5 | 251 | decorations のスロット・スキル |
| `skillTypeData.skt` | 19 | 206 | skills の kind / 段階 |
| `skillTypeData_jpn.gmd` | (2 文字列/件) | 412 | skills の名前・説明 |
| `skillData_jpn.gmd` | (2 文字列/件) | 328 | skill-effects |
| `hunterArtsData.hta` | 25 | 191 | hunter-arts |
| `hunterArtsData_jpn.gmd` | (4 文字列/件) | 764 | hunter-arts の名前・説明 |
| `insectData_jpn.gmd` | (1 文字列/件) | 32 | kinsects の日本語名 |
| `otWeaponData_jpn.gmd` | (2 文字列/件) | 509 | palico-weapons |
| `otArmorData_jpn.gmd` | (4 文字列/系列) | 527 | palico-armor |
| `ot_skl_jpn.gmd` | (2 文字列/件) | 96 | palico-skills の日本語名（照合） |
| `amuletData_jpn.gmd` | (2 文字列/件) | 11 | talismans |

GMD の読み方は `mhnxeditor/crates/mhnx-core/src/romfstables.rs` の記述
（文字列ブロックはファイル末尾、`len - 0x20` の位置）に従った。

##### 2.2 mhnxeditor の静的テーブル (`crates/mhnx-core/src/gamedata.rs`)

英語名と ID 対応表。`pub static NAME: &[&str] = &[...]` をスクリプトで解析して使う。

使った定数: `HUNT_WEAPONS` / `EQUIPMENT_TYPES` /
`EQUIP_*_NAMES` / `EQUIP_*_I_DS` / `EQUIP_TALISMAN_NAMES` / `TALISMAN_RARITY` /
`JWL_NAMES` / `JWL_I_DS` / `SKILL_NAMES` / `KINSECT_NAMES` /
`PALICO_WEAPON_NAMES` / `PALICO_HEAD_NAMES`/`_IDS` / `PALICO_ARMOR_NAMES`/`_IDS` /
`PALICO_SKILLS` / `PALICO_SKILL_NAMES` / `PALICO_SUPPORT_MOVES`

**英語名テーブルの index 0 は `(None)` というプレースホルダ。** SPEC 0-5「空値は空文字（`NULL` 等の
文字列は使わない）」に従い、`(None)` は空文字に変換して出力している（`en_name()` 関数）。
対象は 25 箇所: armor 5 / weapons 14 / palico-armor 2 / kinsects 1 / palico-weapons 1 / skills 1 / talismans 1。
`name_ja` 側の「装備なし」「なし」はゲーム内の表記そのものなので維持した。

##### 2.3 既存の日本語名抽出 (`extract/jp_names/`)

`items.csv` / `weapons.csv` / `armor_series.csv` / `skills.csv` / `amulet.csv` /
`palico_weapon.csv` / `palico_armor.csv`。romfs から生成済みのものは romfs を直接読み直して同じ結果になることを確認した。

##### 2.4 refsrc のデータ (`mhnxeditor/.work/finalaudit/refsrc/data/`)

第 1 バッチ: `decorations.csv`（照合用） / `talisman-tables.csv`（護石の最大スロット） /
`hunter-arts.csv`（狩技の英語名） / `palico-actions.csv`（オトモスキルのコスト・抽選ポイント、支援行動のポイント）。

第 2 バッチ: 下表の 7 本をそのまま入力にした。いずれも mhnxeditor の `tools/*.py` が
`loc/arc/resident.arc` または `arc/facility/blacksmith.arc` から生成したもので、
本スクリプトは **romfs から同じ手順で再計算した値と一致することを assert している**（下の「突き合わせ」列）。

| refsrc ファイル | 行数 | 生成元 | 突き合わせ |
|---|---:|---|---|
| `armor-skills.csv` | 14639 | `armorSeriesData.asd` +28 から 15B/部位 | 14639 行すべて armor_id / skill_id が解決 |
| `weapon-tree.csv` | 798 | `weapon*BaseData` 末尾 10B | 798 行すべて派生元・派生先が weapons.csv に存在 |
| `talisman-tables.csv` | 525 | `amuletSkillDataNN` / `amuletSlotDataNN` | 521 行の skill_id が解決（slots 4 行は空） |
| `combinations.csv` | 183 | `itemPreData.itp` (24B/件) | 183 行すべて 3 アイテムIDが解決 |
| `smithy-lists.csv` | 23 | `blacksmith.arc` の各 Create テーブル | 23 行（件数のみの表） |
| `palico-actions.csv` | 154 | `otomo/ot_skl` / `spt_act_base` / `otSupportIni*pt` / `otSkillIni*pt` | 58 move + 96 skill |
| `palico-levels.csv` | 99 | `otomo/ot_lvl` (15B/レベル) | level 1..99 が重複なし |

**行数はすべて refsrc の元データと一致している**（`row_count` を実ファイルから数え直して manifest に書いている）。

---

#### 3. ID 対応の根拠（ここが弱いと表が崩れる箇所）

| 主張 | 根拠 |
|---|---|
| 武器種 ID は romfs の `weaponNN` の NN、05 は欠番 | `weapon05*` ファイルが存在しない。NN と `weapons.csv` の type 列が 1:1 |
| 英語武器種名は `HUNT_WEAPONS[t if t<5 else t-1]` | 14 種すべてで日本語名と英語名が意味的に一致（大剣=Great Sword … チャージアックス=Charge Blade） |
| `EQUIP_*_NAMES[i]` は武器種 `t` の武器 `i` の英語名 | 各武器種の `EQUIP_*_NAMES` 要素数が `weapons.csv` の weapon_index 件数と**完全一致**（137/129/132/127/109/110/127/110/115/108/126/112/83/81） |
| 防具 ID = `series*5 + part` | `equipnames.rs` の冒頭コメント "Armour: index = series * 5 + part" |
| `EQUIP_{HEAD,CHEST,ARMS,WAIST,LEGS}_I_DS` が「その部位を持つシリーズ」 | `armorSeriesData.asd` の部位有無バイト (+6..+10) から作ったリストと**件数・並び順まで完全一致**（1204/1189/1158/1108/1177） |
| 装飾品 ID `k` ↔ アイテム `2637+k` | `JWL_I_DS` の 262 件すべてで成立。decoData レコード `k` がアイテム `2638+k` |
| decoData の読み方が正しい | 復元した (アイテム, スロット, スキル, ポイント) 424 行が refsrc の `decorations.csv` と**完全一致** |
| 猟虫の日英対応 | `insectData_jpn.gmd` 32 件と `KINSECT_NAMES` 32 件が添字で 1:1（クルドローン=Culldrone …） |
| オトモスキル 96 件が `PALICO_SKILL_NAMES` 0..95 と一致 | mhnxeditor の `romfstables.rs` が実機ダンプで検証済みと明記 |
| オトモ防具の部位有無 | 名前が全角ダッシュ (U+2015) の系列を除外すると頭 502 / 胴 524 件になり、`PALICO_HEAD_I_DS` / `PALICO_ARMOR_I_DS` の件数と一致 |
| 調合の読み方が正しい | 1 行目が「薬草 + アオキノコ = 回復薬 95%」で、mhnxeditor の `07-equipment.md` の記述と一致 |
| `armor-skills.part` は 1..5（頭..脚） | 1..5 を 0..4 に直した armor_id が `armor.csv` の armor_id と 14639 行すべてで一致 |

##### 狩技の武器種の決め方

`hunterArtsData.hta` に武器種の列は**無い**。しかしレコードは `art_group` (+8) ごとに武器種ブロックの順で並んでおり、
各ブロック先頭の説明文が武器名を明記している。ブロックの並びは romfs の武器種 ID (0..14, 05 欠番) と一致する。

| art_group | 武器種 | 件数 | 説明文に現れる語（例） |
|---|---|---|---|
| 1..10 | 共通 | 10 | — |
| 11..15 | 大剣 (0) | 15 | 「重量ある大剣の刃先を…」 |
| 16..18 | 片手剣 (1) | 9 | 「剣で周囲の対象を斬りつける」「盾を使ったアッパー」「刃薬」 |
| 19..22 | ハンマー (2) | 12 | 「猛烈な勢いでハンマーを振りまわし」 |
| 23..26 | ランス (3) | 12 | 「腰溜めにランスを構え」 |
| 27..30 | ヘビィボウガン (4) | 12 | 「ヘビィボウガン内に特殊な火薬を装填」 |
| 31..34 | （空き） | 0 | 名前が全角空白のみ |
| 35..38 | ライトボウガン (6) | 12 | 「ライトボウガンの機構内に…」 |
| 39..42 | 太刀 (7) | 12 | 「太刀のオーラが一段階上がる」 |
| 43..46 | スラッシュアックス (8) | 12 | 「斧と剣を切り替え」「スラッシュアックス」 |
| 47..50 | ガンランス (9) | 12 | 「ガンランスの砲撃を利用し」 |
| 51..54 | 弓 (10) | 12 | 「矢を束ねて３連射」 |
| 55..58 | 双剣 (11) | 12 | 「双剣を構え前進しつつ」 |
| 59..62 | 狩猟笛 (12) | 12 | 「狩猟笛を吹き込み」 |
| 63..66 | 操虫棍 (13) | 12 | 「棍を構え、先端に猟虫を乗せ」 |
| 67..70 | チャージアックス (14) | 12 | 「チャージアックスに回復機能をつける」 |

---

#### 4. 検証結果

`python tools/verify_equip_tables.py` の実行結果（そのまま貼る）:

```
manifest: area=equip tables=23

table               rows id_range         pk_unique        bom/lf/header/pk/first
--------------------------------------------------------------------------------------------
armor               5836 0..6431          yes              ok/ok/ok/ok/ok
armor-parts            5 0..4             yes              ok/ok/ok/ok/ok
armor-skills       14639 1..14639         yes              ok/ok/ok/ok/ok
combinations         183 1..183           yes              ok/ok/ok/ok/ok
decorations          262 1..262           yes              ok/ok/ok/ok/ok
hunter-arts          178 1..190           yes              ok/ok/ok/ok/ok
item-categories      338 0..337           yes              ok/ok/ok/ok/ok
items               2991 0..2990          yes              ok/ok/ok/ok/ok
kinsects              32 0..31            yes              ok/ok/ok/ok/ok
palico-actions       154 1..154           yes              ok/ok/ok/ok/ok
palico-armor        1026 0..1053          yes              ok/ok/ok/ok/ok
palico-levels         99 1..99            yes              ok/ok/ok/ok/ok
palico-skills         96 0..95            yes              ok/ok/ok/ok/ok
palico-support        57 0..56            yes              ok/ok/ok/ok/ok
palico-weapons       509 0..508           yes              ok/ok/ok/ok/ok
skill-effects        328 0..327           yes              ok/ok/ok/ok/ok
skills               206 0..205           yes              ok/ok/ok/ok/ok
smithy-lists          23 1..23            yes              ok/ok/ok/ok/ok
talisman-tables      525 1..525           yes              ok/ok/ok/ok/ok
talismans             11 0..10            yes              ok/ok/ok/ok/ok
weapon-tree          798 1..798           yes              ok/ok/ok/ok/ok
weapon-types          15 0..14            yes              ok/ok/ok/ok/ok
weapons             4818 0..140802        yes              ok/ok/ok/ok/ok

foreign keys
--------------------------------------------------------------------------------------------
items            material_category_id -> item-categories  2991 refs    ok
decorations      item_id              -> items            262 refs     ok
decorations      skill1_id            -> skills           242 refs     ok
decorations      skill2_id            -> skills           182 refs     ok
armor            part_id              -> armor-parts      5836 refs    ok
weapons          weapon_type_id       -> weapon-types     4818 refs     ok
hunter-arts      weapon_type_id       -> weapon-types     168 refs     ok
armor-skills     armor_id             -> armor            14639 refs   ok
armor-skills     part_id              -> armor-parts      14639 refs   ok
armor-skills     skill_id             -> skills           14639 refs   ok
weapon-tree      weapon_type_id       -> weapon-types     798 refs     ok
weapon-tree      weapon_id            -> weapons          798 refs     ok
weapon-tree      parent_weapon_id     -> weapons          798 refs     ok
talisman-tables  skill_id             -> skills           521 refs     ok
combinations     item1_id             -> items            183 refs     ok
combinations     item2_id             -> items            183 refs     ok
combinations     result_item_id       -> items            183 refs     ok

table            rows     name_ja    name_en
--------------------------------------------------------------------------------------------
armor            5836     100%       100%
armor-parts      5        100%       100%
armor-skills     14639    -          -
combinations     183      -          -
decorations      262      100%       100%
hunter-arts      178      100%       100%
item-categories  338      100%       -
items            2991     100%       0%
kinsects         32       100%       97%
palico-actions   154      99%        -
palico-armor     1026     100%       100%
palico-levels    99       -          -
palico-skills    96       100%       100%
palico-support   57       100%       -
palico-weapons   509      100%       100%
skill-effects    328      100%       -
skills           206      100%       100%
smithy-lists     23       -          -
talisman-tables  525      -          -
talismans        11       100%       91%
weapon-tree      798      -          -
weapon-types     15       93%        93%
weapons          4818     100%       33%

PASS: all checks green (23 tables, 33129 rows)
```

検査項目は 9 つ:
1. CSV が UTF-8 BOM 付き・CR を含まない（= 改行 LF）
2. ヘッダーが `_manifest.json` の `columns` と完全一致
3. 1 列目が `primary_key`
4. 主キーの重複ゼロ・整数として解釈できる
5. `row_count` が実ファイルと一致
6. `id_range` が実データの min/max と一致
7. テーブル間参照がすべて解決できる（17 本の外部キー）
8. 必須列に空欄が無い
9. `(None)` / `NULL` などのプレースホルダ文字列が残っていない（SPEC 0-5）

`name_en` の充足率が 0% / 33% / 91% / 93% / 97% になっているのは仕様:
- `items` 0% … 日本語版 romfs しか手元に無く、英語版 `itemData_eng.gmd` が存在しないため（**推測で埋めていない**）
- `weapons` 33% … 英語名テーブルが 1 武器 1 名（form 0）しか持たないため
- `kinsects` 97% / `talismans` 91% … ID 0（なし / 装備なし）の行だけ空
- `weapon-types` 93% … 欠番の `weapon_type_id=5` の行だけ空
- `palico-actions` 99% … move id 57 は gamedata.rs 側の名前が NULL プレースホルダのため空

---

#### 5. 未解決点・残課題

1. **items の英語名が無い。** 英語版 romfs の `nativeNX/eng/table/itemData_eng.gmd` があれば
   `items.name_en` を埋められる（refsrc の `tools/items.py` も同じ前提で `--names` を取る）。
2. **items.category_id の名前テーブルが見つからない。** `itemData.itm` +16 の u8 は
   意味的にはアイテム分類（22=回復薬系, 24=罠, 26=タル爆弾, 43=調合書, 44=原珠/珠, 52=お守り …）で
   値ごとにアイテムが正しくまとまるが、0..105 の分類名を持つテーブルが romfs の gmd に無い。
   数値のみ残した。`itemCategoryTypeData`（338 件）は**素材**の分類で別物。
3. **items.material_category_id の先頭 2 バイトの意味が未確定。** `raw_tag` として 16 進の生値を残した。
4. **狩技の `cost` の意味が未確定。** `hta` +19 の u16 で、+21 の f32 がちょうど 3.5 倍になる
   （表示用の別単位と推定）ことだけ確認した。狩技ゲージ消費量として使ってよいかは未検証。
5. **狩技 71..82 は出力していない。** 名前が全角空白のみのプレースホルダで、英語名テーブルにも無い。
   ID 空間としては 1..190 に存在する（`id_range` は [1,190] で歯抜け）。
6. **猟虫の性能値は入れていない。** `insectData.isd`（47 バイト × 32）のレイアウトは未解析。
   名前だけの表になっている。
7. **`weapons.weapon_id` は合成 ID。** ゲーム内の武器 ID は武器種ごとに 0 始まりなので、
   `weapon_type_id*10000 + weapon_index*10 + form` を主キーにした。元の座標は各列に残してある。
   ゲーム側の ID をそのまま主キーにしたい場合は `(type, index)` の複合キーが必要になる。
8. **`skill-effects` は SPEC の担当表に無い追加テーブル。** `skills.csv` の各段階
   （`skillTypeData.skt` の u16）を解決するために入れた（Lead 承認済み）。
9. **`palico-support` の英語名は存在しない。** romfs に支援行動名の gmd が無く、
   `gamedata.rs` の表も日本語のみ。
10. **`smithy-lists.ids` の意味が未確定。** armor の 5 行だけ値が入る 1 桁コードの並び
    （例: armor:1 は 563 文字）。レコードごとの何かの区分と見られるが、意味は特定できていない。生のまま残した。
11. **`smithy-lists` は件数だけの表。** 実際のレシピ（材料・費用）は
    `refsrc/data/recipes.csv`（1.1MB）側にあり、SPEC では `recipes` は analyst-world の担当。
    本テーブルは「リストごとのレコード数」だけを持つ。
12. **`palico-actions` の move id 57 は名前が空。** `spt_act_base` にはレコードがあるが、
    gamedata.rs 側の `PALICO_SUPPORT_MOVES[57]` が `NULL [57]` というプレースホルダのため。
13. **`combinations` / `palico-actions` の名前列は結合値。** 参照先が単一（items.csv /
    palico-support.csv / palico-skills.csv）なので値の揺れは無いが、正規化したい場合は落としてよい。
14. **`*.tsv` は builder の生成物。** CSV を更新したので `tools/build.py` の再実行が必要
    （このディレクトリの TSV は第 1 バッチ時点の内容のまま）。

##### 装備レコード配置（§6）の未解決点

15. **ゲーム本体の装備ボックス画面の 1 ページあたりの枠数が未確定。** エディタの一覧は 9 行（§6）だが、
    ゲーム内の画面が何枠かは資料から確定できない。
16. **護石の `+0x02` kind = 0 が 2 件だけ観測**され、レア度 99 と結び付いている。
    `TALISMAN_RARITY` の表（kind 5..7 → 99）に無い組み合わせで、意味は不明。
    （サンプルセーブの slot 1 / slot 2 の index 1629 に同一レコードがある）
17. **護石以外の type でも `+0x0C` 以降が非 0 のレコードがある**（サンプルセーブで 15 件）。
    値は護石ブロックや猟虫ブロックの形をしており、前の持ち主のバイトが残っていると見られる。
    どの操作で残るのかは未確定（エディタの type 変更が原因の可能性がある）。
18. **武器の装飾品数が武器のスロット数を超えないかは未検証。**
    `weaponNNLevelData` のスロット数を読んでいない。
19. **type 22 以上がハンターの装備ボックスに現れるかは未確認。**
    2,350 レコードでは 21 が最大。オトモ装備ボックスは別領域（`0x17C2E`）で type 22/23/24 を使う。
20. **head word の bit15** は 2,350 レコードで 0 だったが、ゲームが将来使うかは不明。
21. **`+0x02` の id が 0 のレコード**（type 1..5 / 7..21）は観測していない。id 0 が有効かは未確認。

---

#### 6. 装備ボックスレコードの配置仕様（メモリスキャン補助）

「メモリスキャン補助」機能のため、装備ボックス 1 レコード 36 バイトの実バイト配置を確定し、
実セーブ 2 本で検証した。詳細は **`equip-record-layout.md`**（人間向け）と
**`equip-record-layout.json`**（機械可読・`tools/verify_equip_record_layout.py --json` が生成）。

##### 確定した仕様

| 項目 | 値 | 出典 |
|---|---|---|
| レコード長 | 36 バイト | `equip.rs` `EQUIP_RECORD` |
| レコード数 | 2000 | `equip.rs` `EQUIP_COUNT` / `save.rs` `TOTAL_EQUIP_SLOTS` |
| ボックス全体 | 72,000 バイト | 2000 × 36 |
| slot base からの位置 | `+0x62EE` | `save.rs` `OFF_EQUIPMENT_BOX` |
| ボックス終端 | `+0x17C2E`（= オトモ装備ボックスの開始） | `save.rs` `OFF_PALICO_EQUIPMENT` |
| slot base の持ち方 | `body+0x10/0x14/0x18` の u32le | `review_save_layout.md` Claim 2 |
| slot stride | `0x11D088` + `0x1738` = `0x11E7C0` | `save.rs` `SLOT_DATA_SIZE` |

レコードのフィールド:

```
+0x00 u16le  head word = type(bit0..4) | (level-1)(bit5..9) | (transmog_level-1)(bit10..14)
+0x02 u16le  id          防具=series_id / 武器=weapon_index
+0x04 u16le  transmog_id 0 = なし
+0x06 u16le  deco1       装飾品のアイテムID (2638..2899)、0 = 空き
+0x08 u16le  deco2
+0x0A u16le  deco3
+0x0C 24 B   tail        type 6 = 護石ブロック / type 20 = 猟虫ブロック
```

type の対応: `1..5` = 防具（`armor_id = id*5 + (type-1)`）、`6` = 護石、
`7..21` = 武器（`weapon_type_id = type-7`、`weapon_id = (type-7)*10000 + id*10`）、`12` は未使用。

##### ページ幾何

| 項目 | 値 |
|---|---:|
| 1 ページの枠数 | **9** |
| ページ数 | **223** = ceil(2000/9) |
| 最終ページ | page 222 = index 1998..1999（2 枠） |
| page → index | `[p*9, min(p*9+9, 2000))` |

根拠は `hbedit.rs` の `page_move` の doc コメント「the equipment box shows nine and a warning strip
takes one」と、`tests/scroll_ui.rs` の「The track the equipment box uses: nine 56px rows.」
（`TRACK = 504 = 9 × 56`）／「Nine rows on screen means nine rows a page」。
**これはエディタの一覧画面のページ**で、ゲーム本体の画面の枠数は未確定（§5-15）。

##### 実セーブでの検証結果

`python tools/verify_equip_record_layout.py` → **PASS**

```
== 仕様の算術
  ok   2000 x 36 = 72,000
  ok   0x62EE + 72,000 = 0x17C2E (オトモ装備ボックスの開始)
  ok   ceil(2000 / 9) = 223 ページ
  ok   最終ページは 2 枠

== live  (Ryujinx の現行セーブ)
  ok   ファイルサイズ 4,726,188 B / body = サイズ - 36
  ok   slot base が昇順  0x126474, 0x244c34, 0x3633f4
  ok   slot stride = 0x11D088 + 0x1738  0x11e7c0
  ok   全スロットの装備ボックスが body 内に収まる
  ok   slot 0: type 12 は現れない / head word の bit15 は立たない  19 レコード
  ok   slot 0: type/id が全て名前表に解決  19/19 件
  ok   slot 0 の使用レコード数 = 19
  ok   slot 0 の type 集合 = 防具 5 部位 + 武器 14 種

== sample (save_backups/_conv/system)
  ok   3 スロットすべて同じ幾何
  ok   slot 0: type/id が全て名前表に解決  601/789 件（残り 188 は護石）
  ok   slot 1: 540/771 件 / slot 2: 540/771 件
  ok   護石ブロックの不変条件  188 / 231 / 231 件
  ok   装飾品 ID が decorations.csv に解決  59 / 5 / 5 レコード
  ok   防具の装飾品数 <= armorSeriesData のスロット数

== 合計
  使用レコード: 2,350 / 護石: 650 / 装飾品付き: 69
  type 別: 1:278 2:274 3:269 4:264 5:254 6:650 7:74 8:93 9:4 10:4 11:19
           13:31 14:73 15:10 16:7 17:10 18:16 19:7 20:10 21:3

PASS: 装備ボックスレコードの配置仕様は実セーブと矛盾しない
```

現行セーブ 19 レコードの突合（type/id → 名前）:

| idx | type | id | Lv | 名前 |
|---:|---:|---:|---:|---|
| 0 | 7 | 1 | 1 | ベルダーブレイド / Petrified Blade |
| 1 | 14 | 1 | 1 | ベルダーサーベル / Petrified Saber |
| 2 | 8 | 1 | 1 | ベルダーソード / Petrified Sword |
| 3 | 18 | 1 | 1 | ベルダーダガー / Petrified Daggers |
| 4 | 9 | 1 | 1 | ベルダーハンマー / Petrified Hammer |
| 5 | 19 | 1 | 1 | ベルダーホルン / Petrified Horn |
| 6 | 10 | 1 | 1 | ベルダーランス / Petrified Lance |
| 7 | 16 | 1 | 1 | ベルダーガンランス / Petrified Gunlance |
| 8 | 15 | 1 | 1 | ベルダーアックス / Petrified Axe |
| 9 | 21 | 1 | 1 | ベルダーアームズ / Petrified Strongarm |
| 10 | 20 | 1 | 1 | ベルダーロッド / Petrified Rod |
| 11 | 13 | 1 | 1 | ベルダーバレット / Petrified Shooter |
| 12 | 11 | 1 | 1 | ベルダーキャノン / Petrified Cannon |
| 13 | 17 | 1 | 1 | ベルダーボウ / Petrified Bow |
| 14 | 1 | 3 | 1 | ベルダーターバン / Bherna Turban |
| 15 | 2 | 3 | 1 | ベルダーメイル / Bherna Mail |
| 16 | 3 | 3 | 1 | ベルダーアーム / Bherna Braces |
| 17 | 4 | 3 | 1 | ベルダーベルト / Bherna Belt |
| 18 | 5 | 3 | 1 | ベルダーグリーヴ / Bherna Greaves |

（`type 1 id 3` → `armor_id = 3*5 + 0 = 15` = ベルダーターバン。防具の id は部位ごとに同じ series_id。）

##### 護石（type 6）の構造

```
+0x00 u8 0x06 / +0x01 u8 0x00 / +0x02 u8 kind(1..10) / +0x03 u8 0x00
+0x04 u16 0x0000
+0x06 u16 deco1 / +0x08 u16 deco2 / +0x0A u16 deco3   ← 護石にも装飾品が挿さる
+0x0C u8 skill1_id / +0x0D u8 skill2_id               ← skills.csv の skill_id
+0x0E i8 skill1_points / +0x0F i8 skill2_points
+0x10 u8 slots(0..3) / +0x11 u8 0x00
+0x12 u8 rarity(97..100) / +0x13 u8 0x01              ← u16 で護石アイテムID 353..356
+0x14 16 B 0x00
```

サンプルセーブの護石 650 件で、固定バイト・レア度・護石アイテムID・スキルID・
装飾品数 ≤ スロット数 のすべてが成立した。

##### 装飾品フィールドの検証

- `+0x06/+0x08/+0x0A` は **type 1..5 / 6 / 7..21 のすべてで同じ意味**（装飾品のアイテムID）。
- 非 0 の個数が装備のスロット数を超えないことを確認:
  防具 48 レコード（`armorSeriesData.asd` の `+108+part`）と護石 15 レコード（`+0x10`）。
  武器は未検証（`weaponNNLevelData` のスロット数を読んでいない）。

##### この調査で分かった「注意すべき」点

1. **tail（+0x0C 以降）は type 6/20 以外でも非 0 のことがある。** サンプルセーブで 15 件。
   値は護石ブロックや猟虫ブロックの形をしており、前の持ち主のバイトが残っていると見られる。
   テールを 0 と仮定したパターン検索は取りこぼす。
2. **空き判定は全バイト 0 で行う。** `equip.rs` の `is_empty` は type だけを見るが、
   書き込み可否は `record_is_blank`（全バイト 0）側で判定している。
3. **レベルは -1 格納。** bit 5 から上をまとめて読むと着せ替えレベルが混ざる。
4. **護石の kind=0 が 2 件だけ観測**され、レア度 99 と結び付いている（`TALISMAN_RARITY` の表に無い組み合わせ）。

---

#### 7. 再生成手順

```
python tools/extract_equip_tables.py
python tools/verify_equip_tables.py
```

入力を差し替える場合:

```
python tools/extract_equip_tables.py \
    --romfs  C:\anyWorkspace\nx\mhxx\romfs\nativeNX \
    --refsrc C:\anyWorkspace\nx\mhxx\mhnxeditor\.work\finalaudit\refsrc\data \
    --jpnames C:\anyWorkspace\nx\mhxx\extract\jp_names
```

スクリプトは途中で `assert` / `raise SystemExit` を多用している。
レコード長・件数・ID 対応が 1 つでも食い違えば**出力せずに落ちる**ようにしてある
（例: `armorSeriesData` の部位有無が `EQUIP_*_I_DS` と違えば停止、
decoData の復元結果が refsrc の `decorations.csv` と違えば停止、
armor-skills の armor_id が `armor.csv` に無ければ停止、weapon-tree の派生元が `weapons.csv` に無ければ停止）。

### 世界・進行 (`data/world/NOTES.md`)

### data/world — 世界・進行系 ID テーブル

Monster Hunter XX (Nintendo Switch) の「世界・進行」系 ID の一覧。
すべて **実データからの抽出** で、値の捏造はしていない。不明は空文字。

- 生成: `python tools/extract_world_tables.py`
- 検証: `python tools/extract_world_verify.py`
- テーブル数 **19**（第 1 バッチ 13 + 第 2 バッチ 6）/ 総行数 **58,277**

---

#### 1. テーブル一覧

##### 第 1 バッチ（13 テーブル / 42,739 行）

| # | id | 内容 | 主キー | 行数 | id_range | confidence |
|---|---|---|---:|---:|---|---|
| 1 | `monsters` | モンスター（日英名・分類・サイズ冠） | `monster_id` | 137 | 1..137 | derived |
| 2 | `stages` | ステージ（日英名・マップコード） | `stage_id` | 31 | 1..104 | curated |
| 3 | `quests` | クエスト（リスト順・ID・日英名・★・報酬） | `quest_index` | 1,508 | 1..1508 | derived |
| 4 | `quest-monsters` | クエスト出現モンスター | `row_id` | 2,449 | 1..2449 | verified |
| 5 | `quest-rewards` | クエスト報酬枠 → 報酬テーブル | `row_id` | 4,897 | 1..4897 | verified |
| 6 | `npcs` | NPC（日英名・ビット） | `npc_id` | 188 | 1..999 | derived |
| 7 | `arena` | 闘技大会（グレード制限時間） | `arena_index` | 17 | 0..16 | verified |
| 8 | `awards` | 勲章（日英名・説明） | `award_id` | 132 | 0..131 | derived |
| 9 | `canteen` | 食堂の食材・料理 | `canteen_id` | 144 | 1..144 | derived |
| 10 | `provisions` | 武具生産の素材供出値 | `item_id` | 1,878 | 318..2501 | verified |
| 11 | `requests` | 村依頼（184 レコード） | `request_index` | 184 | 0..183 | derived |
| 12 | `monster-carves` | モンスター剥ぎ取り | `carve_id` | 2,551 | 1..2551 | verified |
| 13 | `recipes` | 生産・強化レシピ | `recipe_id` | 28,623 | 1..28623 | verified |

##### 第 2 バッチ（6 テーブル / 15,538 行）

| # | id | 内容 | 主キー | 行数 | id_range | confidence |
|---|---|---|---:|---:|---|---|
| 14 | `rewards` | クエスト報酬テーブル（.rem の中身） | `reward_id` | 10,992 | 1..10992 | verified |
| 15 | `quest-unlock` | クエスト出現条件 | `quest_id` | 1,506 | 101..1120013 | derived |
| 16 | `unlock-lists` | 解放ビット一覧（38 マップ） | `unlock_id` | 1,418 | 1..1418 | verified |
| 17 | `size-variation` | サイズ変動テーブル（52 表） | `variation_id` | 1,385 | 1..1385 | verified |
| 18 | `rotating-quests` | 日替わりクエスト（51 ビット） | `rotating_bit` | 51 | 0..50 | derived |
| 19 | `request-offer` | 村依頼の提示条件（NPC 会話由来） | `offer_id` | 186 | 1..186 | derived |

`confidence` の意味（SPEC 0 章）:
`verified` = 実データそのまま / `derived` = 既存テーブル・ゲーム内テーブルから算出 /
`curated` = 既知リストを人手で対応付け（根拠を `notes_ja` に明記）。

---

#### 2. 主キーについて（SPEC「1 列目 = 主キー」）

連番の主キーを使った表は 10 個。いずれも **自然キーが複合で一意にならない** ためで、
自然キーは `notes_ja` と下の表に書いた。

| id | 主キー | 自然キー | 連番にした理由 |
|---|---|---|---|
| `quest-monsters` | `row_id` | (quest_id, entry_no) | 同じクエストに同条件の個体が 2 体出る正規データが 49 組ある |
| `quest-rewards` | `row_id` | (quest_id, slot) | 複合キーのため |
| `canteen` | `canteen_id` | (kind, bit) | 食材と料理でビットが重複するため |
| `monster-carves` | `carve_id` | (monster_id, rank, sets, kind, entry_no) | kind 1/3/4 を other に統合した結果 2 行が同条件になる |
| `recipes` | `recipe_id` | (kind, target_id, level, recipe_no) | 同じ武器・装飾品に別素材の生産レシピが 2 本ある（127 組） |
| `rewards` | `reward_id` | (rem_id, entry_no) | 同じ報酬テーブルに同じアイテムが 2 行出る（571 組） |
| `unlock-lists` | `unlock_id` | (map, bit) | map が文字列で複合キーのため |
| `size-variation` | `variation_id` | (size_table, rate) | 複合キーのため |
| `request-offer` | `offer_id` | (request_index, npc_file, npc_bit, talk_line) | 1 つの依頼を 2 人の NPC が出す／同じ NPC が 2 行の会話で出す（4 組） |

単一の実 ID を主キーにできた表:
`monsters`(monster_id) / `stages`(stage_id) / `npcs`(npc_id) /
`arena`(arena_index) / `awards`(award_id) / `provisions`(item_id) /
`requests`(request_index) / `quest-unlock`(quest_id) / `rotating-quests`(rotating_bit)

`quests` の主キーは `quest_index`（クエストリストの添字 1..1508）。
`quest_id` は 1049 と 1050 がリストに 2 回現れる（index 313/314 と 315/316）ため
一意でない。2 回目はゲームが読まない重複行で、`notes` 列にその旨が入っている。

---

#### 3. 出典

読み取りのみ。書き込みはしていない。

| 出典 | 使ったテーブル |
|---|---|
| `mhnxeditor/.work/finalaudit/refsrc/data/monster-index.csv` | monsters |
| `mhnxeditor/.work/finalaudit/refsrc/data/monster-sizes.csv` | monsters |
| `mhnxeditor/crates/mhnx-core/src/gamedata.rs` (`MONSTER_HUNT_NAMES`) | monsters (name_ja) |
| `mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv` | stages, quests |
| `mhnxeditor/.work/finalaudit/refsrc/tools/quest_info.py` (`STAGE_TEXT`) | stages (name_en) |
| `mhnxeditor/.work/finalaudit/refsrc/data/quest-index.csv` | quests |
| `romfs/nativeNX/arc/quest/q*.arc` (`questData_*.mib`, `questData_*_jpn`) | stages, quests, requests, quest-unlock, rotating-quests, request-offer |
| `romfs/nativeNX/arc/stage/m01d..m27d` | stages (map_code) |
| `romfs/nativeNX/table/NpcName_jpn.gmd` | npcs (name_ja) |
| `romfs/nativeNX/table/GC_Medal_jpn.gmd` | awards (name_ja, desc_ja) |
| `romfs/nativeNX/table/activityData_jpn.gmd` | requests (name_ja) |
| `romfs/nativeNX/table/Kitchen_jpn.gmd` | canteen (name_ja) |
| `refsrc/data/{quest-monsters,quest-rewards,npc-index,arena,awards,canteen,provisions,request-index,monster-carves,recipes}.csv` | 各表 |
| `refsrc/data/{rewards,quest-unlock,unlock-lists,size-variation,rotating-quests,request-offer}.csv` | 第 2 バッチ各表 |

##### .gmd の読み方（この dump の実測）

```
+0x00 'GMD\0'
+0x04 u32 version 0x00010302
+0x18 u32 文字列数
+0x20 u32 テキストブロックのバイト数
+0x24 u32 キー文字列長
+0x28 キー + NUL
テキストブロック = ファイル末尾の <+0x20> バイト。NUL 区切り UTF-8 を <+0x18> 個。
```

NpcName / GC_Medal / Kitchen / HN_MonsterListMsg は +0x1C が非 0 で、キーとテキストの間に
ハッシュ付きのエントリ表が挟まる。テキストブロックはそれでも **ファイル末尾** にあるので
上の規則で読める（activityData のように +0x1C = 0 のファイルも同じ規則で読める）。

##### .arc（クエスト書庫）の読み方

```
+0x00 'ARC\0'
+0x06 u16 エントリ数
+0x0C エントリ 0x50 バイト: 名前 64 B / u32 圧縮サイズ / u32 展開サイズ / u32 オフセット / u32 未使用
     圧縮サイズ != 展開サイズ (& 0x1FFFFFFF) または先頭 0x78 なら zlib
```

`arc/quest/qNNNNNNN.arc` の NNNNNNN はクエスト ID を 7 桁ゼロ埋めしたもの
（例 `q0100304.arc` → quest 100304）。

---

#### 4. 最重要課題だったステージ ID の解決

##### 4.1 stage 列の値域

`quest-info.csv` の `stage` 列は **1..27 と 101..104 の 31 種**。

##### 4.2 出どころは questData の .mib +0x14

クエスト書庫の `quest\questData\questData_NNNNNNN`（拡張子なし = .mib、249 B）
の **+0x14 が map_id**（mhnx の `arc-mib` も同じ名前で出す）。

**全 1,855 クエストの書庫を解析して突き合わせた結果、quest-info.csv の 1,512 行と
stage 列が 1,512/1,512 で完全一致（不一致 0）**。これで `stage` 列が
ステージ ID であることが確定した。

##### 4.3 1..27 は arc/stage の m01d..m27d

`romfs/nativeNX/arc/stage/` に `m01d`..`m27d` の 27 フォルダ、
`arc/stage/map_com/` に `m00.arc`..`m27.arc` がある。
stage 1..27 が m01..m27 に対応する。**101..104 は 1..4 の夜版**（4.4 の日本語名が同一）。

##### 4.4 英語名はゲーム自身のクエストボード表記

`refsrc/tools/quest_info.py` の `STAGE_TEXT` が
「stage id → `GUI/06_msg/questMessage_eng.gmd` のエントリ番号」を持つ。
この dump には `GUI/06_msg` が無い（`romfs/nativeNX` のみ）ため
直接は読めないが、**Harvest Tour クエストの英語名と完全に一致する**ことを確認した:

| stage | `STAGE_TEXT` の英語名 | 一致した Harvest Tour クエスト |
|---:|---|---|
| 1 | J. Frontier | 201 Harvest Tour: Jurassic Frontier |
| 2 | V. Hills | 203 Harvest Tour: Verdant Hills |
| 3 | A. Ridge | 204 Harvest Tour: Arctic Ridge |
| 4 | M. Peaks | 205 Harvest Tour: Misty Peaks |
| 5 | Dunes | 202 Harvest Tour: Dunes |
| 6 | D. Island | 301 Harvest Tour: Deserted Island |
| 7 | Marshlands | 302 Harvest Tour: Marshlands |
| 8 | Volcano | 401 Harvest Tour: Volcano |
| 11 | A. Steppe | 721 Harvest Tour: Ancestral Steppe |
| 12 | V. Hollow | 821 Harvest Tour: Volcanic Hollow |
| 13 | Primal Forest | 722 Harvest Tour: Primal Forest |
| 14 | F. Seaway | 820 Harvest Tour: Frozen Seaway |
| 22 | Desert | 701 Harvest Tour: Desert |
| 23 | Jungle | 801 Harvest Tour: Jungle |
| 24 | Ruined Pinnacle | 702 Harvest Tour: Ruined Pinnacle |
| 101 | J. Frontier | 723 Harvest Tour: Jurassic Frontier |
| 102 | V. Hills | 725 Harvest Tour: Verdant Hills |
| 103 | A. Ridge | 726 Harvest Tour: Arctic Ridge |
| 104 | M. Peaks | 727 Harvest Tour: Misty Peaks |

##### 4.5 日本語名はクエスト本文から（根拠件数を各行に記載）

`questMessage_jpn.gmd` もこの dump に無いため、日本語名は
**questData の日本語本文**から取った。手法は 2 つ:

1. **Harvest Tour 方式（`derived`）** — 同じクエストの日本語タイトルが
   「〈地名〉の採集ツアー」、英語名が「Harvest Tour: 〈英語名〉」なので 1 対 1 で決まる。
   例: 202「旧砂漠の採集ツアー」= Harvest Tour: Dunes → stage 5 = 旧砂漠。
2. **本文頻度方式（`curated`）** — Harvest Tour が無いステージは、
   そのステージの全クエストの日本語本文（タイトル・依頼主・依頼内容・主なモンスター・
   成功/失敗/サブ条件）に現れる地名を数えた。件数は `stages.csv` の
   `notes_ja` に「n/m 件」として入れてある。

   | stage | name_ja | 根拠 |
   |---:|---|---|
   | 9 | 闘技場 | 69/301 件。例 630「高難度：青の連撃！」の依頼文「闘技場で、なんだか青いモンスターが…」 |
   | 16 | 禁足地 | 18/26 件。例 632「高難度：廻帰せし災厄の古龍」 |
   | 17 | 塔 | 20/41 件。例 10715「古の塔の下に２頭。」 |
   | 18 | 霊峰 | 10/13 件。例 1019「嵐龍天翔」 |
   | 19 | 溶岩島 | 22/36 件。例 11422「溶岩島で爆ぜる砕光」 |
   | 20 | 極圏 | 14/16 件。例 1018「崩せ神の座、威の寝床」の依頼文「極圏にて氷山の大規模な崩落が…」 |
   | 21 | 竜ノ墓場 | 3/8 件。例 1026「怨嗟の骸」の依頼文「龍歴院は竜ノ墓場においてオストガロアの出現を確認した」 |
   | 25 | シュレイド城 | テストクエスト 90033「シュレイド城テスト」 |
   | 26 | 砦 | 2/3 件。例 11319「巨大龍の侵攻」の依頼文「砦の防衛戦に参加してもらうわ」 |
   | 27 | 旧砦跡 | 11432「蠢く墟城」の依頼文「アトラル・カが旧砦跡の周辺で姿を消したらしい」 |

##### 4.6 名前を空にした 2 ステージ（捏造禁止のため）

| stage | name_en | 状況 |
|---:|---|---|
| 10 | Volcano Slayground (V. Slayground) | 依頼文は「闘技場」11/20・「立体闘技場」7/20 のみ。stage 9「闘技場」との区別がこの dump だけでは確定できない |
| 15 | Frozen Slayground (F. Slayground) | 依頼文は「闘技場」4/12 のみ。同上 |

英語名はゲームの message table の値なので確か。日本語名は **空文字**（SPEC 0 章「不明は空文字」）。

##### 4.7 英語名と日本語名が 1 対 1 でない例

- stage 17: `name_en` = Forlorn Arena（ゲームの表記そのまま）/
  `name_ja` = 塔（依頼文 20/41 件）。両者は同じ ID でも名前が対応しない。
  `notes_ja` に明記した。
- stage 16: Sanctuary / 禁足地、stage 20: Polar Field / 極圏 も同様に、
  英語名はゲームの表記・日本語名は本文の地名という別ソース。

---

#### 5. 日本語名の出どころ（ステージ以外）

| テーブル | 列 | 出どころ | 対応の確認方法 |
|---|---|---|---|
| monsters | name_ja | `gamedata.rs` の `MONSTER_HUNT_NAMES`（137 件・セーブ順） | 件数一致。106..112 は「不明」、134 は "Unknown[133]" なので空にした |
| npcs | name_ja | `NpcName_jpn.gmd` | bit 0 = ベルナ村の村長 = Bherna Chief、188 件すべて意味が一致 |
| awards | name_ja / desc_ja | `GC_Medal_jpn.gmd` | 264 件 = 132 名 + 132 説明。bit 0 の説明が「村の★１と★２の全クエストをクリアした証」で一致 |
| requests | name_ja | `activityData_jpn.gmd` | 920 件 = 184 レコード × 5。index i の名前は 5*i 番目 |
| requests / quest-unlock / rotating-quests / request-offer | quest_name_ja | `questData_*_jpn` | 対象クエストのタイトル（0 番目） |
| canteen | name_ja | `Kitchen_jpn.gmd` | 下記の並び |

##### Kitchen_jpn.gmd の並び（144 件の対応）

```
食材: 各カテゴリ先頭 7 件が 103..133（肉 103-109 / 穀物 110-116 / 野菜 117-123 /
      魚 124-130 / 飲み物 131-133）、XX で追加された 14 件が 251..264
料理: 0..76 が 134..210、77..98 が 265..286
```

全 144 件を名前の意味で確認した（例 dish 0 Dauntless Pasta = 屋台の根性まかない飯 /
dish 98 Ultimate Rice = 屋台の究極まかない飯 / 食材 44 Chat-eau de Nya = ニャトーロマーネ）。

---

#### 6. 第 2 バッチの補足

##### 6.1 `rewards` — `quest-rewards.rem_id` の解決先

`quest-rewards.csv` は「クエストのどの報酬枠が、どの報酬テーブル(.rem)を
引くか」だけを持つ。実際の当選品は `rewards.csv` を `rem_id` で引く。

- 1,697 の報酬テーブル / 10,992 行。1 テーブルあたり 1..22 行
- 参照整合は **両方向で 0 件の欠落**（quest-rewards の rem_id はすべて rewards にあり、
  rewards の rem はすべて quest-rewards から参照されている）
- 同じテーブルに同じアイテムが 2 行出ることがある（571 組）。ゲームは行ごとに個別に
  抽選するので、これは重複ではなく別の抽選枠
- 1 テーブルの `chance` 合計は 100。**例外が 1 つだけ**:
  `rem 230073` は 104（ゲーム側の実データがそうなっている。
  refsrc の `quest.rs` の `REWARD_PROB_TOTAL` のコメントにも
  「one official table ... really does sum to 104」と書かれている）

##### 6.2 `quest-unlock`

`quest_id` は **1,506 件で、`quests.csv` の quest_id 集合と完全一致**。
`rule` は `flag:396` / `cleared:11404` / `hr:7` /
`village_star:6 AND ...` の形。空欄 204 件は条件なし（最初から出る）。

##### 6.3 `unlock-lists`

自然キー `(map, bit)` は 1,418 行すべて一意。map は 38 種:

`lab`(研究施設) / `song`(ジュークボックス) / `armory:1..21`(武具屋) /
`shop:0,1` / `trader:costumes,delivery,items0,items1,scenes,words` /
`coin` / `combos` / `costume` / `events` / `gallery` /
`milestones` / `notes2` / `supply` / `tips`

`need` は `start`(最初から) / `dlc`(配信) / `never`(未使用) /
`v2|h2`(村★2 または集会所★2) / `q806&q10768`(両方クリア) の形。
`target_id` は解放される装備・アイテム ID（1,074 行が持つ）。

##### 6.4 `size-variation`

ゲームの `em_size_yure_data`（52 テーブル）。クエストの boss 枠が
`size_table` を指し、サイズ = クエストの size% × rate。
自然キー `(size_table, rate)` は 1,385 行すべて一意。rate は 88..130。

##### 6.5 `rotating-quests`

セーブの `base + 0x504B` のビット（次に 1 クエストクリアするまで有効）。
ビット 0..50 の 51 件、quest_id はすべて quests.csv に存在する。

##### 6.6 `request-offer`

NPC の会話データから読んだ「この依頼を出す条件」。自然キー
`(request_index, npc_file, npc_bit, talk_line)` は 186 行すべて一意。

`request_index` は 4 組 (28, 135, 149, 150) が 2 行ずつある:
28 / 149 / 150 は赤鬼・黒鬼の 2 人が同じ依頼を出す、135 は同じ NPC が別の会話行で出す。
`quest_id` が空の行は納品依頼（kind 1）でクエストを持たない。

---

#### 7. 自己検証

##### 7.1 実行

```
> python tools/extract_world_tables.py
  monsters            137 rows  id 1..137
  stages               31 rows  id 1..104
  quests             1508 rows  id 1..1508
  quest-monsters     2449 rows  id 1..2449
  quest-rewards      4897 rows  id 1..4897
  npcs                188 rows  id 1..999
  arena                17 rows  id 0..16
  awards              132 rows  id 0..131
  canteen             144 rows  id 1..144
  provisions         1878 rows  id 318..2501
  requests            184 rows  id 0..183
  monster-carves     2551 rows  id 1..2551
  recipes           28623 rows  id 1..28623
  rewards           10992 rows  id 1..10992
  quest-unlock       1506 rows  id 101..1120013
  unlock-lists       1418 rows  id 1..1418
  size-variation     1385 rows  id 1..1385
  rotating-quests      51 rows  id 0..50
  request-offer       186 rows  id 1..186
-> C:\anyWorkspace\nx\mhxx\mhxx-id-memo\data\world (19 tables)

> python tools/extract_world_verify.py
tables      : 19
total rows  : 58277
checks      : 222
failures    : 0
  WARN rewards: 1 table(s) do not sum to 100%: [('230073', 104)] (rem 230073 is a known game-side table that sums to 104)
  WARN quest-monsters: 18 quest ids have no row in quests (not in the save quest list): ['1010126', '1010132', '1010136', '1010139', '1010162', '1011038', '1110006', '1110107']
  WARN quest-rewards: 9 quest ids have no row in quests (not in the save quest list): ['1010126', '1010132', '1010136', '1010139', '1010162', '1011038', '1110006', '1110107']
RESULT      : PASS
```

##### 7.2 検証項目（222 チェック）

各テーブルについて:

1. ファイルが存在し、ヘッダーが manifest の `columns` と完全一致
2. 1 列目が manifest の `primary_key`
3. `row_count` が実ファイルのデータ行数と一致
4. 主キーに重複なし・空値なし
5. `id_range` が実データの min/max と一致
6. UTF-8 BOM 付き・CR を含まない（LF のみ）
7. `NULL` という文字列の値がない・各行の列数がヘッダーと一致

横断:

8. manifest のテーブル id が一意
9. `quests.stage_id` がすべて `stages` に存在
10. `quest-monsters` / `monster-carves` の `monster_id` がすべて `monsters` に存在
11. `arena` / `requests`（kind 0）の `quest_id` がすべて `quests` に存在
12. **`quest-rewards.rem_id` がすべて `rewards.rem_id` に存在**（両方向）
13. **`rewards` の各テーブルの `chance` 合計が 100**（rem 230073 のみ既知の例外）
14. **`quest-unlock.quest_id` の集合が `quests.quest_id` の集合と一致**
15. **`rotating-quests.quest_id` / `request-offer.quest_id` がすべて `quests` に存在**
16. **`request-offer.request_index` がすべて `requests.request_index` に存在**

##### 7.3 WARN 3 件について（失敗ではない）

1. **`rewards` の rem 230073 が 104%** — ゲーム側の実データが 104。
   検証側の仮定（常に 100）の方が外れている。refsrc の `quest.rs` にも
   既知の例外として書かれている。
2. **`quest-monsters` 18 件 / `quest-rewards` 9 件が
   「quests に無い quest_id」** — この 2 表は **全 1,855 クエストファイル**由来、
   `quests.csv` は **セーブのクエストリスト 1,508 行**（SPEC の出典どおり）
   なので母集合が違う。クエストファイルはあるがリストに載っていない
   イベント／ダミークエストが該当する。データの誤りではない。

---

#### 8. 未解決点・残課題

1. **stage 10 / 15 の日本語名** — 依頼文が「闘技場」「立体闘技場」しか言わず、
   stage 9 との区別がつかない。`GUI/06_msg/questMessage_jpn.gmd` が
   入った dump があれば 1 行で埋まる。
2. **stage 17 の英語名と日本語名の不一致** — ゲームの英語表記は Forlorn Arena、
   依頼文の地名は「塔」。どちらも実データだが、同じマップを指すかは未確認。
3. **`quests` の 27 行は `stage_id` が空** — quest-info.csv に
   行が無い DUMMY のイベント枠。
4. **`recipes.kind` の `weapon:NN` の NN は武器種 ID** —
   武器種名は analyst-equip の `weapon-types` を参照。
5. **`monster-carves` は set 1 のみ** — 元データが set 1 だけを書いており、
   deviant など複数セットを持つモンスターは `sets` 列にセット数が入る。
6. **`npcs` の npc_id 991..999** は名前が `-` のダミー行
   （ゲーム側のプレースホルダ）。削っていない。
7. **`awards.desc_ja` は値内に改行を含む** — SPEC 2 章で許容。
   TSV 化は builder の `build.py` が空白に潰す。
8. **`rewards` の `entry_no` は .rem の生のスロット番号ではない** —
   refsrc の rewards.csv が「サイズを持つ枠だけ」を書いているため、行の並び順の連番にした。
   生のスロット (0..39) が要るなら .rem を直接読む必要がある。
9. **`unlock-lists` の `target_id` の意味は未確定** —
   refsrc は「解放される装備・アイテム ID」としか書いていない。armory マップでは
   武器・防具 ID と読めるが、他のマップでは未確認。
