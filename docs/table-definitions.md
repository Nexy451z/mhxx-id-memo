# テーブル定義

> このファイルは `tools/build.py` が `_manifest.json` から自動生成します。手で編集しないこと。

- テーブル数: **42**
- 総行数: **91,406**
- データ版: `sha256:9f346b940d85d78ba196a13055a17ef9971e9d81d2796ef5d6fdc00cd217ea92`

## 目次

### 装備・アイテム (`equip`)

| id | テーブル | 行数 | 主キー | ID 範囲 | confidence |
|---|---|---:|---|---|---|
| [`armor`](#armor) | 防具 | 5,836 | `armor_id` | 0–6431 | verified |
| [`armor-parts`](#armor-parts) | 防具部位 | 5 | `part_id` | 0–4 | verified |
| [`armor-skills`](#armor-skills) | 防具スキルポイント | 14,639 | `row_id` | 1–14639 | derived |
| [`combinations`](#combinations) | 調合 | 183 | `row_id` | 1–183 | derived |
| [`decorations`](#decorations) | 装飾品（珠） | 262 | `decoration_id` | 1–262 | verified |
| [`hunter-arts`](#hunter-arts) | 狩技 | 178 | `art_id` | 1–190 | derived |
| [`item-categories`](#item-categories) | アイテムカテゴリ（素材分類） | 338 | `category_id` | 0–337 | verified |
| [`items`](#items) | アイテム | 2,991 | `item_id` | 0–2990 | verified |
| [`kinsects`](#kinsects) | 猟虫 | 32 | `kinsect_id` | 0–31 | verified |
| [`palico-actions`](#palico-actions) | オトモ行動（支援行動・スキル） | 154 | `row_id` | 1–154 | derived |
| [`palico-armor`](#palico-armor) | オトモ防具 | 1,026 | `palico_armor_id` | 0–1053 | verified |
| [`palico-levels`](#palico-levels) | オトモレベル | 99 | `level` | 1–99 | derived |
| [`palico-skills`](#palico-skills) | オトモスキル（術） | 96 | `palico_skill_id` | 0–95 | verified |
| [`palico-support`](#palico-support) | オトモ支援行動 | 57 | `support_move_id` | 0–56 | derived |
| [`palico-weapons`](#palico-weapons) | オトモ武器 | 509 | `palico_weapon_id` | 0–508 | verified |
| [`skill-effects`](#skill-effects) | スキル効果（発動後のスキル名） | 328 | `effect_id` | 0–327 | verified |
| [`skills`](#skills) | スキル | 206 | `skill_id` | 0–205 | derived |
| [`smithy-lists`](#smithy-lists) | 鍛冶屋リスト | 23 | `row_id` | 1–23 | derived |
| [`talisman-tables`](#talisman-tables) | 護石スキル抽選範囲 | 525 | `row_id` | 1–525 | derived |
| [`talismans`](#talismans) | 護石 | 11 | `talisman_id` | 0–10 | verified |
| [`weapon-tree`](#weapon-tree) | 武器派生 | 798 | `row_id` | 1–798 | derived |
| [`weapon-types`](#weapon-types) | 武器種 | 15 | `weapon_type_id` | 0–14 | verified |
| [`weapons`](#weapons) | 武器 | 4,818 | `weapon_id` | 0–140802 | verified |

### 世界・進行 (`world`)

| id | テーブル | 行数 | 主キー | ID 範囲 | confidence |
|---|---|---:|---|---|---|
| [`monsters`](#monsters) | モンスター | 137 | `monster_id` | 1–137 | derived |
| [`stages`](#stages) | ステージ | 31 | `stage_id` | 1–104 | curated |
| [`quests`](#quests) | クエスト | 1,508 | `quest_index` | 1–1508 | derived |
| [`quest-monsters`](#quest-monsters) | クエスト出現モンスター | 2,449 | `row_id` | 1–2449 | verified |
| [`quest-rewards`](#quest-rewards) | クエスト報酬枠 | 4,897 | `row_id` | 1–4897 | verified |
| [`npcs`](#npcs) | NPC | 188 | `npc_id` | 1–999 | derived |
| [`arena`](#arena) | 闘技大会 | 17 | `arena_index` | 0–16 | verified |
| [`awards`](#awards) | 勲章 | 132 | `award_id` | 0–131 | derived |
| [`canteen`](#canteen) | 食堂 | 144 | `canteen_id` | 1–144 | derived |
| [`provisions`](#provisions) | 調合・素材の供出値 | 1,878 | `item_id` | 318–2501 | verified |
| [`requests`](#requests) | 村依頼 | 184 | `request_index` | 0–183 | derived |
| [`monster-carves`](#monster-carves) | モンスター剥ぎ取り | 2,551 | `carve_id` | 1–2551 | verified |
| [`recipes`](#recipes) | 生産・強化レシピ | 28,623 | `recipe_id` | 1–28623 | verified |
| [`rewards`](#rewards) | クエスト報酬テーブル | 10,992 | `reward_id` | 1–10992 | verified |
| [`quest-unlock`](#quest-unlock) | クエスト出現条件 | 1,506 | `quest_id` | 101–1120013 | derived |
| [`unlock-lists`](#unlock-lists) | 解放ビット一覧 | 1,418 | `unlock_id` | 1–1418 | verified |
| [`size-variation`](#size-variation) | サイズ変動テーブル | 1,385 | `variation_id` | 1–1385 | verified |
| [`rotating-quests`](#rotating-quests) | 日替わりクエスト | 51 | `rotating_bit` | 0–50 | derived |
| [`request-offer`](#request-offer) | 村依頼の提示条件 | 186 | `offer_id` | 1–186 | derived |

---

## 装備・アイテム (`equip`)

### 防具 <a id="armor"></a>

`armor`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/armor.csv` / `data/equip/armor.tsv` |
| 主キー | `armor_id` |
| 行数 | 5,836 |
| ID 範囲 | 0–6431 |
| confidence | `verified` |
| 英語名 | Armor |
| 出典 | `romfs/nativeNX/table/armorSeriesData_jpn.gmd`<br>`romfs/nativeNX/table/armorSeriesData.asd`<br>`extract/jp_names/armor_series.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES/_IDS)` |
| 備考 | armorSeriesData.asd は 127 バイト/系列で、+6..+10 が部位の有無 (頭/胴/腕/腰/脚)。この有無フラグは gamedata.rs の EQUIP_HEAD/CHEST/ARMS/WAIST/LEGS_I_DS と件数・並び順まで完全一致した (1204/1189/1158/1108/1177)。部位が無い系列の行は出力していない。armor_id = series*5 + part は mhnxeditor の equipnames.rs が明記している並び。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `armor_id` | int | 防具ID = series_id*5 + part_id | Armor ID |
| 2 | `series_id` | int | シリーズID (armorSeriesData のレコード番号) | Series ID |
| 3 | `part_id` | int | 部位ID (armor-parts.csv) | Part ID |
| 4 | `name_ja` | str | 防具名（日本語） | Name (Japanese) |
| 5 | `name_en` | str | 防具名（英語） | Name (English) |
| 6 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |

### 防具部位 <a id="armor-parts"></a>

`armor-parts`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/armor-parts.csv` / `data/equip/armor-parts.tsv` |
| 主キー | `part_id` |
| 行数 | 5 |
| ID 範囲 | 0–4 |
| confidence | `verified` |
| 英語名 | Armor parts |
| 出典 | `romfs/nativeNX/table/armorSeriesData_jpn.gmd`<br>`extract/jp_names/gen.py (PARTS)`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIPMENT_TYPES)` |
| 備考 | armorSeriesData_jpn.gmd の 10 文字列 = 5 部位 x (名前, 説明) の並び (頭,胴,腕,腰,脚)。英語名は EQUIPMENT_TYPES の 1..5 (Head, Chest, Arms, Waist, Legs)。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `part_id` | int | 部位ID (0=頭 1=胴 2=腕 3=腰 4=脚) | Part ID |
| 2 | `name_ja` | str | 部位名（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 部位名（英語） | Name (English) |

### 防具スキルポイント <a id="armor-skills"></a>

`armor-skills`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/armor-skills.csv` / `data/equip/armor-skills.tsv` |
| 主キー | `row_id` |
| 行数 | 14,639 |
| ID 範囲 | 1–14639 |
| confidence | `derived` |
| 英語名 | Armor skill points |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/armor-skills.csv`<br>`romfs/nativeNX/table/armorSeriesData.asd` |
| 備考 | armorSeriesData.asd の +28 から 15 バイト/部位 = 5 x (u16 スキルID, i8 ポイント) を読んだ結果 (mhnxeditor の tools/skill_tables.py と同じ手順)。1 部位に最大 5 スキルが付くため複合キーになり、SPEC 準拠で 1 列目に連番 row_id を置いた。refsrc の part は 1..5 (頭..脚) なので part_id = part-1 に直し、armor.csv の armor_id と直接結合できるようにした。14639 行すべてで armor_id が armor.csv に存在し、skill_id が skills.csv に存在することを確認済み。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番 (1 始まり)。(armor_id, skill_id) が複合キーのため便宜上の主キー | Sequential key |
| 2 | `armor_id` | int | 防具ID (armor.csv)。= series_id*5 + part_id | Armor ID |
| 3 | `series_id` | int | シリーズID | Series ID |
| 4 | `part_id` | int | 部位ID (0=頭 1=胴 2=腕 3=腰 4=脚) | Part ID |
| 5 | `skill_id` | int | スキルID (skills.csv) | Skill ID |
| 6 | `points` | int | スキルポイント (マイナスあり) | Skill points |

### 調合 <a id="combinations"></a>

`combinations`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/combinations.csv` / `data/equip/combinations.tsv` |
| 主キー | `row_id` |
| 行数 | 183 |
| ID 範囲 | 1–183 |
| confidence | `derived` |
| 英語名 | Item combinations |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/combinations.csv`<br>`romfs/nativeNX/table/itemPreData.itp`<br>`romfs/nativeNX/table/itemData_jpn.gmd` |
| 備考 | itemPreData の 24 バイト/レコード 183 件 (+2 と +6 が材料, +10 が結果, +14 が成功率%) を 読んだ結果 (mhnxeditor の tools/item_combos.py と同じ手順)。(item1, item2) は 183 行で重複なし。数値だけでは読めないので、items.csv から引いた名前 3 列を併記した (参照先が単一なので値の揺れは無い)。183 行すべてで 3 つのアイテムIDが items.csv に存在することを確認済み。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番 (1 始まり)。(item1_id, item2_id) が複合キーのため便宜上の主キー | Sequential key |
| 2 | `item1_id` | int | 材料1のアイテムID (items.csv) | Material 1 item ID |
| 3 | `item2_id` | int | 材料2のアイテムID (items.csv) | Material 2 item ID |
| 4 | `result_item_id` | int | 調合結果のアイテムID (items.csv) | Result item ID |
| 5 | `chance_percent` | int | 調合成功率 (%) | Success chance (%) |
| 6 | `item1_name_ja` | str | 材料1の名前（日本語） | Material 1 name (Japanese) |
| 7 | `item2_name_ja` | str | 材料2の名前（日本語） | Material 2 name (Japanese) |
| 8 | `result_name_ja` | str | 結果の名前（日本語） | Result name (Japanese) |

### 装飾品（珠） <a id="decorations"></a>

`decorations`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/decorations.csv` / `data/equip/decorations.tsv` |
| 主キー | `decoration_id` |
| 行数 | 262 |
| ID 範囲 | 1–262 |
| confidence | `verified` |
| 英語名 | Decorations |
| 出典 | `romfs/nativeNX/table/decoData.deco`<br>`romfs/nativeNX/table/skillTypeData_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (JWL_NAMES, JWL_I_DS)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/decorations.csv` |
| 備考 | decoData.deco は 5 バイト/レコードで 251 件、レコード k がアイテム 2638+k。JWL_I_DS は decoration_id k -> アイテム 2637+k で、全 262 件でこの関係が成立することを確認した。decoData から復元した (アイテム, スロット, スキル, ポイント) 424 行は refsrc の decorations.csv と完全一致した。decoration_id 252..262 は JWL_NAMES にのみ存在する Dummy Jwl 10..20 で、decoData に実体が無いため スキル列は空・is_dummy=yes にしてある。スキルID は skills.csv のスキルIDを指す。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `decoration_id` | int | 装飾品ID (1..262) | Decoration ID |
| 2 | `name_en` | str | 名前（英語） | Name (English) |
| 3 | `name_ja` | str | 名前（日本語、対応するアイテム名） | Name (Japanese) |
| 4 | `item_id` | int | 対応するアイテムID | Item ID |
| 5 | `slot_size` | int | 必要スロット数 (1..3) | Slot size |
| 6 | `skill1_id` | int | スキル1のスキルID (skills.csv) | Skill 1 ID |
| 7 | `skill1_name_ja` | str | スキル1の名前（日本語） | Skill 1 name (Japanese) |
| 8 | `skill1_points` | int | スキル1のポイント | Skill 1 points |
| 9 | `skill2_id` | int | スキル2のスキルID (skills.csv) | Skill 2 ID |
| 10 | `skill2_name_ja` | str | スキル2の名前（日本語） | Skill 2 name (Japanese) |
| 11 | `skill2_points` | int | スキル2のポイント（マイナスあり） | Skill 2 points |
| 12 | `is_dummy` | bool | decoData に実体が無いダミー行か | Dummy row |

### 狩技 <a id="hunter-arts"></a>

`hunter-arts`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/hunter-arts.csv` / `data/equip/hunter-arts.tsv` |
| 主キー | `art_id` |
| 行数 | 178 |
| ID 範囲 | 1–190 |
| confidence | `derived` |
| 英語名 | Hunter arts |
| 出典 | `romfs/nativeNX/table/hunterArtsData.hta`<br>`romfs/nativeNX/table/hunterArtsData_jpn.gmd`<br>`mhnxeditor/.work/finalaudit/refsrc/data/hunter-arts.csv` |
| 備考 | hunterArtsData.hta は 25 バイト/レコードで 191 件 (0=装備なし, 1..190=狩技)。hunterArtsData_jpn.gmd は 4 文字列/件 (名前, 名前, 短い説明, 長い説明)。ID 71..82 は名前が全角空白のみのプレースホルダなので出力していない (英語名テーブル hunter-arts.csv も同じ 178 件)。hta 自体に武器種の列は無い。レコードは art_group (+8) ごとに武器種ブロックの順で並んでおり、各ブロック先頭の説明文がその武器を明記している (11-15=大剣, 19-22=ハンマー, 23-26=ランス, 27-30=ヘビィボウガン, 35-38=ライトボウガン, 39-42=太刀, 43-46=スラッシュアックス, 47-50=ガンランス, 51-54=弓, 55-58=双剣, 59-62=狩猟笛, 63-66=操虫棍, 67-70=チャージアックス) ため、その対応を weapon_type_id に入れた (1-10 は全武器共通)。31-34 は空きブロック。cost は hta +19 の u16 で、+21 の f32 がちょうど 3.5 倍になることだけ確認済み (意味は未確定)。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `art_id` | int | 狩技ID (1..190。71..82 は空レコード) | Hunter art ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語） | Name (English) |
| 4 | `weapon_type_id` | int | 武器種ID (weapon-types.csv)。空=全武器共通 | Weapon type ID (empty = common) |
| 5 | `weapon_type_ja` | str | 武器種名（日本語、共通含む） | Weapon type (Japanese) |
| 6 | `cost` | int | 狩技ゲージ量 (hunterArtsData.hta +19 の u16) | Gauge cost |
| 7 | `art_group` | int | 狩技ファミリーID (hta +8 の u32。I/II/III が同じ値) | Art family ID |
| 8 | `desc_ja` | str | 説明（日本語、長文） | Description (Japanese) |

### アイテムカテゴリ（素材分類） <a id="item-categories"></a>

`item-categories`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/item-categories.csv` / `data/equip/item-categories.tsv` |
| 主キー | `category_id` |
| 行数 | 338 |
| ID 範囲 | 0–337 |
| confidence | `verified` |
| 英語名 | Item categories (material) |
| 出典 | `romfs/nativeNX/table/itemCategoryTypeData.ict`<br>`romfs/nativeNX/table/itemCategoryTypeData_jpn.gmd` |
| 備考 | itemCategoryTypeData.ict は 7 バイト/レコードで 338 件、itemCategoryTypeData_jpn.gmd の 338 文字列と 1:1 対応する。名前は素材の分類 (モンスター素材, 鉱石素材, マッカォ素材 ...) で、同名が 3 件ずつ並び 3 バイト目が 0,1,2 と巡回する。先頭 2 バイトの意味は未確定のため 16 進の生値で残した。items.material_category_id がこの ID を指す。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `category_id` | int | カテゴリID (0..337) | Category ID |
| 2 | `name_ja` | str | カテゴリ名（日本語） | Name (Japanese) |
| 3 | `variant_index` | int | レコード 3 バイト目。同名の 3 連レコードで 0,1,2 と巡回する | Third byte of the record |
| 4 | `raw_tag` | str | レコード先頭 2 バイト (16進、意味未確定) | First two bytes, hex |

### アイテム <a id="items"></a>

`items`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/items.csv` / `data/equip/items.tsv` |
| 主キー | `item_id` |
| 行数 | 2,991 |
| ID 範囲 | 0–2990 |
| confidence | `verified` |
| 英語名 | Items |
| 出典 | `romfs/nativeNX/table/itemData_jpn.gmd`<br>`romfs/nativeNX/table/itemData.itm`<br>`romfs/nativeNX/table/itemCategoryTypeData.ict` |
| 備考 | itemData_jpn.gmd は 2 文字列/アイテム (名前, 説明)、itemData.itm は 44 バイト/アイテムで レコード数 2991 が一致する。日本語版 romfs しか手元に無いため name_en は全行空 (英語版の itemData_eng.gmd が必要)。category_id は itemData.itm +16 の u8 で、値ごとにアイテムが意味的にまとまる (22=回復薬系, 24=罠, 26=タル爆弾, 43=調合書, 44=原珠/珠, 52=お守り など) ことを確認したが、この分類の名前テーブルは romfs の gmd に見つからないため数値のみ。material_category_id は +28 の u16 で itemCategoryTypeData の ID (0..337)。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `item_id` | int | アイテムID (0..2990) | Item ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語、未取得） | Name (English, unavailable) |
| 4 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |
| 5 | `category_id` | int | アイテム分類ID (itemData.itm +16 の u8。0..105、名前テーブルは未発見) | Item category group |
| 6 | `material_category_id` | int | 素材カテゴリID (item-categories.csv) | Material category ID |

### 猟虫 <a id="kinsects"></a>

`kinsects`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/kinsects.csv` / `data/equip/kinsects.tsv` |
| 主キー | `kinsect_id` |
| 行数 | 32 |
| ID 範囲 | 0–31 |
| confidence | `verified` |
| 英語名 | Kinsects |
| 出典 | `romfs/nativeNX/table/insectData_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (KINSECT_NAMES)` |
| 備考 | insectData_jpn.gmd は 1 文字列/虫で 32 件、insectData.isd も 47 バイト x 32 件。日本語名 (クルドローン...) と英語名 (Culldrone...) は添字で 1:1 対応する。説明文は romfs に無い。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `kinsect_id` | int | 猟虫ID (0..31) | Kinsect ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語） | Name (English) |

### オトモ行動（支援行動・スキル） <a id="palico-actions"></a>

`palico-actions`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/palico-actions.csv` / `data/equip/palico-actions.tsv` |
| 主キー | `row_id` |
| 行数 | 154 |
| ID 範囲 | 1–154 |
| confidence | `derived` |
| 英語名 | Palico actions |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv`<br>`romfs/nativeNX/arc/resident.arc (otomo/ot_skl, otomo/support/spt_act_base, table/lobby/otSupportIni*pt, otSkillIni*pt)` |
| 備考 | resident.arc の otomo/ot_skl (11 バイト: u32 ID, u8 ID, +5 スロットコスト) と otomo/support/spt_act_base、table/lobby/otSupportIni{1,2,3}pt / otSkillIni{1,2,3}pt (抽選ポイント) から作った表 (mhnxeditor の tools/palico_tables.py と同じ手順)。move 58 件 + skill 96 件 = 154 件。(kind, action_id) が複合キーなので連番 row_id を 1 列目に置いた。move の id 57 は spt_act_base にレコードがあるが gamedata.rs 側の名前が NULL プレースホルダなので name_ja が空。name_ja は palico-support.csv / palico-skills.csv から引いた (参照先が単一なので値の揺れは無い)。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番 (1 始まり)。(kind, action_id) が複合キーのため便宜上の主キー | Sequential key |
| 2 | `kind` | str | 種別 (move=支援行動, skill=オトモスキル) | Kind |
| 3 | `action_id` | int | kind ごとの ID (palico-support.csv / palico-skills.csv) | Action ID |
| 4 | `points` | int | 抽選ポイント (1..3、固有のものは 0) | Draw points |
| 5 | `cost` | int | スロットコスト (skill のみ。move は空) | Slot cost |
| 6 | `name_ja` | str | 名前（日本語）。palico-support / palico-skills から引いた | Name (Japanese) |

### オトモ防具 <a id="palico-armor"></a>

`palico-armor`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/palico-armor.csv` / `data/equip/palico-armor.tsv` |
| 主キー | `palico_armor_id` |
| 行数 | 1,026 |
| ID 範囲 | 0–1053 |
| confidence | `verified` |
| 英語名 | Palico armor |
| 出典 | `romfs/nativeNX/table/otArmorData_jpn.gmd`<br>`extract/jp_names/palico_armor.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_HEAD_NAMES/_IDS, PALICO_ARMOR_NAMES/_IDS)` |
| 備考 | otArmorData_jpn.gmd は 4 文字列/系列 (頭名, 胴名, 頭説明, 胴説明) で 527 系列。部位が無い系列は名前が全角ダッシュ (U+2015) になっているので、その行は出力していない (生存 頭 502 件 / 胴 524 件 = PALICO_HEAD_I_DS / PALICO_ARMOR_I_DS の件数と一致。系列 0 は両部位とも「装備なし」で、これは ID 0/1 の意味を残すため出力している)。英語名は PALICO_HEAD/ARMOR_NAMES を _IDS で引いた。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `palico_armor_id` | int | オトモ防具ID = series_id*2 + part_id | Palico armor ID |
| 2 | `series_id` | int | シリーズID (otArmorData.oar のレコード番号) | Series ID |
| 3 | `part_id` | int | 部位ID (0=頭 1=胴) | Part ID |
| 4 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 5 | `name_en` | str | 名前（英語） | Name (English) |
| 6 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |

### オトモレベル <a id="palico-levels"></a>

`palico-levels`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/palico-levels.csv` / `data/equip/palico-levels.tsv` |
| 主キー | `level` |
| 行数 | 99 |
| ID 範囲 | 1–99 |
| confidence | `derived` |
| 英語名 | Palico levels |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/palico-levels.csv`<br>`romfs/nativeNX/arc/resident.arc (otomo/ot_lvl)` |
| 備考 | resident.arc の otomo/ot_lvl (15 バイト/レベル, 99 件) の +10 と +11 を読んだもの (mhnxeditor の tools/palico_tables.py と同じ手順)。level は 1..99 で重複なしなのでそのまま主キーにした。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `level` | int | オトモレベル (1..99) | Palico level |
| 2 | `support_slots` | int | 自由に付けられる支援行動スロット数 (ot_lvl +10) | Support move slots |
| 3 | `skill_slots` | int | 装備できるオトモスキルのスロット数 (ot_lvl +11) | Skill slots |

### オトモスキル（術） <a id="palico-skills"></a>

`palico-skills`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/palico-skills.csv` / `data/equip/palico-skills.tsv` |
| 主キー | `palico_skill_id` |
| 行数 | 96 |
| ID 範囲 | 0–95 |
| confidence | `verified` |
| 英語名 | Palico skills |
| 出典 | `romfs/nativeNX/table/ot_skl_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SKILLS, PALICO_SKILL_NAMES)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv` |
| 備考 | ot_skl_jpn.gmd は 2 文字列/スキルで 96 件、gamedata.rs の PALICO_SKILL_NAMES 0..95 と 位置まで一致することを mhnxeditor の romfstables.rs が検証済み。PALICO_SKILL_NAMES/SKILLS の 97 件目 (index 96) は NULL [96] のプレースホルダなので出力していない。ID 0 はスキル無し。cost と points は refsrc の palico-actions.csv (ot_skl の +5 と抽選ポイント) から。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `palico_skill_id` | int | オトモスキルID (0..95) | Palico skill ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語） | Name (English) |
| 4 | `cost` | int | スロットコスト (ot_skl +5) | Slot cost |
| 5 | `points` | int | 抽選ポイント (1..3、固有スキルは 0) | Draw points |

### オトモ支援行動 <a id="palico-support"></a>

`palico-support`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/palico-support.csv` / `data/equip/palico-support.tsv` |
| 主キー | `support_move_id` |
| 行数 | 57 |
| ID 範囲 | 0–56 |
| confidence | `derived` |
| 英語名 | Palico support moves |
| 出典 | `mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_SUPPORT_MOVES)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/palico-actions.csv` |
| 備考 | PALICO_SUPPORT_MOVES は 58 件で、57 件目が NULL [57] のプレースホルダなので 0..56 の 57 件を出力した。romfs に支援行動名の gmd は無く、日本語名は gamedata.rs の表だけが持つ。英語名は無い。points は refsrc の palico-actions.csv (otSupportIni1..3pt の抽選テーブル) から。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `support_move_id` | int | 支援行動ID (0..56) | Support move ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `points` | int | 抽選ポイント (1..3、固有行動は 0) | Draw points |

### オトモ武器 <a id="palico-weapons"></a>

`palico-weapons`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/palico-weapons.csv` / `data/equip/palico-weapons.tsv` |
| 主キー | `palico_weapon_id` |
| 行数 | 509 |
| ID 範囲 | 0–508 |
| confidence | `verified` |
| 英語名 | Palico weapons |
| 出典 | `romfs/nativeNX/table/otWeaponData_jpn.gmd`<br>`extract/jp_names/palico_weapon.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (PALICO_WEAPON_NAMES)` |
| 備考 | otWeaponData_jpn.gmd は 2 文字列/武器で 509 件、otWeaponData.owp も 31 バイト x 509 件。ID 0 は 1234567890 という開発用ダミー文字列で、英語名テーブルの該当行もプレースホルダなので空にしてある。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `palico_weapon_id` | int | オトモ武器ID (0..508) | Palico weapon ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語） | Name (English) |
| 4 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |

### スキル効果（発動後のスキル名） <a id="skill-effects"></a>

`skill-effects`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/skill-effects.csv` / `data/equip/skill-effects.tsv` |
| 主キー | `effect_id` |
| 行数 | 328 |
| ID 範囲 | 0–327 |
| confidence | `verified` |
| 英語名 | Skill effects |
| 出典 | `romfs/nativeNX/table/skillData_jpn.gmd`<br>`extract/jp_names/skills.csv` |
| 備考 | skillData_jpn.gmd は 2 文字列/件で 328 件 (スキル無し, 毒耐性, 毒倍加, 麻痺無効 ...)。skills.csv のスキルIDとは別の ID 空間で、skills.csv の各段階がここを指す。SPEC の担当表には無いが、skills.csv の段階を解決するために追加した (Lead に報告)。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `effect_id` | int | スキル効果ID (skillData のレコード番号) | Skill effect ID |
| 2 | `name_ja` | str | スキル名（日本語） | Name (Japanese) |
| 3 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |

### スキル <a id="skills"></a>

`skills`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/skills.csv` / `data/equip/skills.tsv` |
| 主キー | `skill_id` |
| 行数 | 206 |
| ID 範囲 | 0–205 |
| confidence | `derived` |
| 英語名 | Skills |
| 出典 | `romfs/nativeNX/table/skillTypeData.skt`<br>`romfs/nativeNX/table/skillTypeData_jpn.gmd`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (SKILL_NAMES)` |
| 備考 | skillTypeData.skt は 19 バイト/スキルで 206 件: u32 スキルID, u8 kind, u16 x7 が -20/-15/-10/+10/+15/+20/+25 ポイントで発動するスキル (skill-effects.csv の ID)。名前と説明は skillTypeData_jpn.gmd (2 文字列/件) から取った。max_level は +10/+15/+20 で発動するスキルの種類数、min_level は -10/-15/-20 の種類数として算出した (攻撃=3/3, 気絶=2/1, 体力=2/2 など、既知の段階数と一致することを確認)。kind の 1/2 は 144..161 / 162..179 の二つ名スキルにだけ付く。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `skill_id` | int | スキルID (skillTypeData のレコード番号。防具/装飾品/護石が指す) | Skill ID |
| 2 | `name_ja` | str | スキル名（日本語） | Name (Japanese) |
| 3 | `name_en` | str | スキル名（英語） | Name (English) |
| 4 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |
| 5 | `kind` | int | 種別 (0=通常, 1=二つ名スキル【魂】, 2=【魂・極】) | Kind |
| 6 | `max_level` | int | 最大レベル (プラス段階で発動するスキルの種類数) | Max level |
| 7 | `min_level` | int | マイナス側の段階数 | Negative levels |

### 鍛冶屋リスト <a id="smithy-lists"></a>

`smithy-lists`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/smithy-lists.csv` / `data/equip/smithy-lists.tsv` |
| 主キー | `row_id` |
| 行数 | 23 |
| ID 範囲 | 1–23 |
| confidence | `derived` |
| 英語名 | Smithy lists |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/smithy-lists.csv`<br>`romfs/nativeNX/arc/facility/blacksmith.arc` |
| 備考 | blacksmith.arc の weaponCreateWNN / armorCreateANN / decoCreate / otWeaponCreate / otArmorCreate の レコード数を数えたもの (mhnxeditor の tools/smithy_lists.py)。元の主キーは list という文字列なので、SPEC の「1 列目は主キー・ID は整数」に合わせて 連番 row_id を 1 列目に置き、list_name をそのまま残した。kind / class_id は list_name から機械的に分割しただけ。ids 列は armor の 5 行だけ値が入る 1 桁コードの並びで、意味は未確定のため生のまま残した。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番 (1 始まり)。元のキーが文字列 (list) なので便宜上の主キー | Sequential key |
| 2 | `list_name` | str | 元データのリスト名 (weapon:0, armor:1, deco, palico:helm ...) | List name |
| 3 | `kind` | str | list_name の前半 (weapon / armor / deco / palico) | List kind |
| 4 | `class_id` | int | kind が weapon / armor のときの武器種ID・部位ID。それ以外は空 | Class or part id |
| 5 | `records` | int | そのリストのレコード数 | Record count |
| 6 | `ids` | str | レコードごとの 1 桁コードの並び (armor のみ。意味未確定) | Per-record code string |

### 護石スキル抽選範囲 <a id="talisman-tables"></a>

`talisman-tables`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/talisman-tables.csv` / `data/equip/talisman-tables.tsv` |
| 主キー | `row_id` |
| 行数 | 525 |
| ID 範囲 | 1–525 |
| confidence | `derived` |
| 英語名 | Talisman skill ranges |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv`<br>`romfs/nativeNX/arc/resident.arc (amuletSkillDataNN, amuletSlotDataNN)` |
| 備考 | resident.arc の amuletSkillDataNN (4 バイト: u16 スキルID, i8 下限, i8 上限) と amuletSlotDataNN から作った表 (mhnxeditor の tools/talisman_tables.py と同じ手順)。自然キーは (kind, tier, skill_id) で、525 行すべてで一意になることを確認した (kind=slots の 4 行は skill_id が空なので、この 3 列だけで一意)。SPEC の「1 列目は主キー・ID 列は整数」に合わせて 1 列目に連番 row_id を置き、自然キーの 3 列はそのまま残した。tier t は第1スキルにテーブル 2(t-97)、第2スキルに 2(t-97)+1、スロットに t-97 を使う。神秘 (97) の第2スキルは空テーブルなので行が無い。kind=slots の 4 行は min_points=0 で max_points がそのレア度の最大スロット数 (97->1, 98->2, 99->3, 100->3)。525 行すべてで skill_id が skills.csv に存在することを確認済み。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番 (1 始まり)。(kind, tier, skill_id) が複合キーのため便宜上の主キー | Sequential key |
| 2 | `kind` | str | 種別 (skill1=第1スキル, skill2=第2スキル, slots=スロット数) | Kind |
| 3 | `tier` | int | レア度 (97=神秘 98=閃光 99=風化 100=歴戦) | Rarity tier |
| 4 | `skill_id` | int | スキルID (skills.csv)。kind=slots の行は空 | Skill ID |
| 5 | `min_points` | int | そのスキルに付くポイントの下限 | Min points |
| 6 | `max_points` | int | 上限。kind=slots の行では最大スロット数を表す | Max points / max slots |

### 護石 <a id="talismans"></a>

`talismans`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/talismans.csv` / `data/equip/talismans.tsv` |
| 主キー | `talisman_id` |
| 行数 | 11 |
| ID 範囲 | 0–10 |
| confidence | `verified` |
| 英語名 | Talismans |
| 出典 | `romfs/nativeNX/table/amuletData_jpn.gmd`<br>`extract/jp_names/amulet.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_TALISMAN_NAMES, TALISMAN_RARITY)`<br>`mhnxeditor/.work/finalaudit/refsrc/data/talisman-tables.csv` |
| 備考 | amuletData_jpn.gmd は 2 文字列/護石で 11 件、amulet.csv と一致。レア度は gamedata.rs の TALISMAN_RARITY (0,97,97,98,98,99,99,99,100,100,100) で、97=神秘 98=閃光 99=風化 100=歴戦。max_slots は talisman-tables.csv の slots 行 (97->1, 98->2, 99->3, 100->3)。護石の抽選スキル範囲は talisman-tables.csv を参照。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `talisman_id` | int | 護石ID (0..10) | Talisman ID |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語） | Name (English) |
| 4 | `rarity` | int | レア度 (TALISMAN_RARITY。0 は装備なし) | Rarity tier |
| 5 | `max_slots` | int | そのレア度で付く最大スロット数 | Max slots |

### 武器派生 <a id="weapon-tree"></a>

`weapon-tree`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/weapon-tree.csv` / `data/equip/weapon-tree.tsv` |
| 主キー | `row_id` |
| 行数 | 798 |
| ID 範囲 | 1–798 |
| confidence | `derived` |
| 英語名 | Weapon upgrade tree |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/weapon-tree.csv`<br>`romfs/nativeNX/table/weapon*BaseData.w*d` |
| 備考 | weaponNNBaseData の末尾 10 バイト = 5 x (u8 必要レベル, u8 派生先武器ID) を読んだ結果 (mhnxeditor の tools/equip_recipes.py と同じ手順)。1 武器が最大 5 本へ派生するため複合キーになり、1 列目に連番 row_id を置いた。798 行すべてで派生先・派生元の (class, weapon) が weapons.csv の form 0 に存在することを確認済み。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番 (1 始まり)。1 武器が最大 5 本へ派生するため複合キーになるので便宜上の主キー | Sequential key |
| 2 | `weapon_type_id` | int | 武器種ID (weapon-types.csv) | Weapon type ID |
| 3 | `weapon_index` | int | 派生先の武器ID (武器種ごと) | Child weapon index |
| 4 | `parent_weapon_index` | int | 派生元の武器ID | Parent weapon index |
| 5 | `required_level` | int | 派生に必要な派生元の強化レベル | Required level |
| 6 | `weapon_id` | int | 派生先の weapons.csv の weapon_id (form 0) | Child weapon_id |
| 7 | `parent_weapon_id` | int | 派生元の weapons.csv の weapon_id (form 0) | Parent weapon_id |

### 武器種 <a id="weapon-types"></a>

`weapon-types`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/weapon-types.csv` / `data/equip/weapon-types.tsv` |
| 主キー | `weapon_type_id` |
| 行数 | 15 |
| ID 範囲 | 0–14 |
| confidence | `verified` |
| 英語名 | Weapon types |
| 出典 | `romfs/nativeNX/table/weapon*MsgData_jpn.gmd`<br>`extract/jp_names/weapons.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (HUNT_WEAPONS, EQUIPMENT_TYPES)` |
| 備考 | weapon_type_id は romfs の weaponNN ファイル名の NN。05 はファイルが存在しない欠番。日本語名は weapons.csv の type 列、英語名は HUNT_WEAPONS (0..14 の別採番で 5=Light Bowgun, 14=Prowler) の対応する添字から取った。equip_type_id は EQUIPMENT_TYPES の並び (7=Great Sword ... 21=Charge Blade、12 が欠番) と一致する。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `weapon_type_id` | int | 武器種ID (romfs の weaponNN の NN。5 は欠番) | Weapon type ID |
| 2 | `name_ja` | str | 武器種名（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 武器種名（英語） | Name (English) |
| 4 | `equip_type_id` | int | EQUIPMENT_TYPES 上の装備種別ID (= weapon_type_id + 7) | Equipment type ID |
| 5 | `hunt_weapon_index` | int | HUNT_WEAPONS 上の添字 (0..13) | Index into HUNT_WEAPONS |
| 6 | `used` | bool | 実在する武器種か | Weapon class exists |

### 武器 <a id="weapons"></a>

`weapons`

| 項目 | 値 |
|---|---|
| ファイル | `data/equip/weapons.csv` / `data/equip/weapons.tsv` |
| 主キー | `weapon_id` |
| 行数 | 4,818 |
| ID 範囲 | 0–140802 |
| confidence | `verified` |
| 英語名 | Weapons |
| 出典 | `romfs/nativeNX/table/weapon*MsgData_jpn.gmd`<br>`romfs/nativeNX/table/weapon*LevelData.w*d`<br>`extract/jp_names/weapons.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (EQUIP_*_NAMES)` |
| 備考 | ゲーム内の武器IDは武器種ごとに 0 から振られているため、主キーは weapon_type_id*10000 + weapon_index*10 + form の合成IDにした (元の座標は各列に残してある)。form は強化で名前が変わる段階で、セーブが保持するのは form 0 (equipnames.rs の記述)。英語名テーブル EQUIP_*_NAMES は 1 武器 1 名 (form 0) なので form 1/2 の name_en は空。各武器種の weapon_index 件数は EQUIP_*_NAMES の要素数と完全一致する (大剣137/片手剣129/ハンマー132/ランス127/ヘビィ109/ライト110/太刀127/スラアク110/ガンランス115/弓108/双剣126/笛112/虫棍83/チャアク81)。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `weapon_id` | int | 主キー。weapon_type_id*10000 + weapon_index*10 + form の合成ID | Synthetic key |
| 2 | `weapon_type_id` | int | 武器種ID (weapon-types.csv) | Weapon type ID |
| 3 | `weapon_index` | int | 武器種ごとの武器ID (0 始まり) | Per-class weapon ID |
| 4 | `form` | int | 名前の段階 (0=素の名前, 1, 2=強化後の名前) | Name stage |
| 5 | `name_ja` | str | 武器名（日本語） | Name (Japanese) |
| 6 | `name_en` | str | 武器名（英語、form 0 のみ） | Name (English, form 0 only) |
| 7 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |
| 8 | `levels` | str | この名前になる強化レベル (セミコロン区切り) | Levels using this name |

---

## 世界・進行 (`world`)

### モンスター <a id="monsters"></a>

`monsters`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/monsters.csv` / `data/world/monsters.tsv` |
| 主キー | `monster_id` |
| 行数 | 137 |
| ID 範囲 | 1–137 |
| confidence | `derived` |
| 英語名 | Monsters |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/monster-index.csv`<br>`mhnxeditor/.work/finalaudit/refsrc/data/monster-sizes.csv`<br>`mhnxeditor/crates/mhnx-core/src/gamedata.rs (MONSTER_HUNT_NAMES)` |
| 備考 | monster_id はセーブの狩猟記録の添字 1..137（docs/02-monster-records.md）。name_ja は gamedata.rs の MONSTER_HUNT_NAMES（ゲーム内の名称テーブル由来、137 件・同順）。106..112 は「不明」、134 は空スロットのため name_ja を空にした。name_en は monster-index.csv。サイズ系の列は monster-sizes.csv を index で結合。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `monster_id` | int | モンスターID（セーブの狩猟記録の添字） | Monster ID (hunt-record index) |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語） | Name (English) |
| 4 | `category` | str | large / small / unused | large / small / unused |
| 5 | `class` | str | 種別（飛竜種など） | Monster class |
| 6 | `has_size_record` | bool | サイズ記録を持つか | Has a size record |
| 7 | `base_size_cm` | float | 基準サイズ(cm) | Base size (cm) |
| 8 | `mini_le` | int | 最小冠の閾値(%) | Mini crown threshold (%) |
| 9 | `silver_ge` | int | 銀冠の閾値(%) | Silver crown threshold (%) |
| 10 | `gold_ge` | int | 金冠の閾値(%) | Gold crown threshold (%) |
| 11 | `fixed_size` | bool | サイズ変動なし | Fixed size |
| 12 | `crown_awards` | bool | 冠の勲章対象 | Counts for crown awards |
| 13 | `card_pos` | int | ギルドカードの並び位置 | Guild Card position |
| 14 | `notes_bit` | int | 狩猟ノートのビット | Hunter's Notes bit |
| 15 | `family_of` | int | 派生元モンスターID | Base monster ID (variants) |
| 16 | `confidence` | str | 名前の確度（元データ） | Name confidence (source) |
| 17 | `notes_en` | str | 元データの注記（英語） | Source note |

### ステージ <a id="stages"></a>

`stages`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/stages.csv` / `data/world/stages.tsv` |
| 主キー | `stage_id` |
| 行数 | 31 |
| ID 範囲 | 1–104 |
| confidence | `curated` |
| 英語名 | Stages |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv (stage 列)`<br>`mhnxeditor/.work/finalaudit/refsrc/tools/quest_info.py (STAGE_TEXT)`<br>`romfs/nativeNX/arc/quest/q*.arc (questData .mib +0x14, questData_*_jpn)`<br>`romfs/nativeNX/arc/stage (m01d..m27d)` |
| 備考 | テーブル全体の confidence は行の弱い方に合わせて curated。うち 19 行（1-8, 11-14, 22-24, 101-104）は Harvest Tour の日英タイトルが1 対 1 で対応するため derived、残り 12 行（9, 10, 15-21, 25-27）が curated。stage_id は questData .mib の +0x14。quest-info.csv の stage 列と1855 クエスト中 1512 件で全一致（不一致 0）。1..27 は arc/stage の m01d..m27d に対応し、101..104 は 1..4 の夜版（Harvest Tour の日本語名が同一）。name_en はゲーム自身の questMessage_eng の短縮名（refsrc の STAGE_TEXT）を正式名に展開したもの。name_ja は questData の日本語本文からの対応付けで、根拠件数を各行の notes_ja に書いた。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `stage_id` | int | ステージID（questData .mib +0x14） | Stage ID (questData .mib +0x14) |
| 2 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 3 | `name_en` | str | 名前（英語・正式） | Name (English, full) |
| 4 | `short_en` | str | クエストボードの短縮名（英語） | Quest-board short name (English) |
| 5 | `map_code` | str | ステージのリソース名 | Stage resource name |
| 6 | `night` | bool | 夜版か | Night variant |
| 7 | `base_stage_id` | int | 夜版の元ステージID | Day stage of a night variant |
| 8 | `quest_count` | int | quests.csv の該当行数 | Rows in quests.csv |
| 9 | `confidence` | str | 確度 | Confidence |
| 10 | `notes_ja` | str | 根拠 | Evidence |

### クエスト <a id="quests"></a>

`quests`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/quests.csv` / `data/world/quests.tsv` |
| 主キー | `quest_index` |
| 行数 | 1,508 |
| ID 範囲 | 1–1508 |
| confidence | `derived` |
| 英語名 | Quests |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/quest-index.csv`<br>`mhnxeditor/.work/finalaudit/refsrc/data/quest-info.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData .mib, questData_*_jpn)` |
| 備考 | 主キーは quest_index（クエストリストの添字 1..1508）。quest_id は 1049 と 1050 がリストに 2 回現れる（index 313/314 と 315/316）ため一意でない。name_ja は questData_*_jpn の 0 番目（タイトル）。stage_id は .mib +0x14。quest_kind/time_limit/revive_count も .mib から。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `quest_index` | int | クエストリストの添字（ビットマップ位置） | Quest list index (bitmap position) |
| 2 | `quest_id` | int | クエストID | Quest ID |
| 3 | `category` | str | Village / Hub / Arena / Training / Special Permit / Event など | Category |
| 4 | `prowler` | bool | ニャンター専用か | Prowler only |
| 5 | `rank` | str | ★レベル（1-10、G級は G1-G4、空欄は不明） | Star rank (1-10, G1-G4, empty = unknown) |
| 6 | `name_en` | str | クエスト名（英語） | Quest name (English) |
| 7 | `name_ja` | str | クエスト名（日本語） | Quest name (Japanese) |
| 8 | `stage_id` | int | ステージID | Stage ID |
| 9 | `group` | int | quest_group のグループ番号 | quest_group group byte |
| 10 | `alt` | int | グループ内の代替セット | Alternative set in the group |
| 11 | `expansion` | bool | XX 追加クエストか | Added by the XX expansion |
| 12 | `sets` | str | クエストセット番号（空白区切り） | Quest set numbers (space separated) |
| 13 | `quest_kind` | int | クエスト種類（.mib +0x10） | Quest kind (.mib +0x10) |
| 14 | `time_limit` | int | 制限時間（分） | Time limit (minutes) |
| 15 | `revive_count` | int | 復活回数 | Revive count |
| 16 | `reward` | int | 報酬金(z) | Reward (z) |
| 17 | `hrp` | int | HRポイント | Hunter Rank points |
| 18 | `fee` | int | 契約金(z) | Contract fee (z) |
| 19 | `sub_reward` | int | サブ報酬金(z) | Subquest reward (z) |
| 20 | `sub_hrp` | int | サブHRポイント | Subquest HR points |
| 21 | `notes` | str | 元データの注記 | Source note |

### クエスト出現モンスター <a id="quest-monsters"></a>

`quest-monsters`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/quest-monsters.csv` / `data/world/quest-monsters.tsv` |
| 主キー | `row_id` |
| 行数 | 2,449 |
| ID 範囲 | 1–2449 |
| confidence | `verified` |
| 英語名 | Quest monsters |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/quest-monsters.csv` |
| 備考 | 元 CSV は (quest_id, monster_id, size, size_table) が 49 組重複する（同じクエストに同条件の個体が 2 体出る正規のデータ）。主キーは連番 row_id とし、自然キーは (quest_id, entry_no)。entry_no は quest_sizes.py が書き出した順（クエスト内のボス枠順、サイズを持つ枠のみ）の 0 始まり連番。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番（主キー） | Serial primary key |
| 2 | `quest_id` | int | クエストID | Quest ID |
| 3 | `entry_no` | int | クエスト内の出現順（0 始まり） | Boss entry ordinal in the quest (0-based) |
| 4 | `monster_id` | int | モンスターID | Monster ID |
| 5 | `size` | int | サイズ(%) | Size (%) |
| 6 | `size_table` | int | サイズ変動テーブル番号 | Size variation table |

### クエスト報酬枠 <a id="quest-rewards"></a>

`quest-rewards`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/quest-rewards.csv` / `data/world/quest-rewards.tsv` |
| 主キー | `row_id` |
| 行数 | 4,897 |
| ID 範囲 | 1–4897 |
| confidence | `verified` |
| 英語名 | Quest rewards |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/quest-rewards.csv` |
| 備考 | 自然キーは (quest_id, slot)（4897 行すべて一意）。主キーは連番 row_id。rem_id は報酬抽選テーブル .rem の番号で、実際の当選品は refsrc/data/rewards.csv（rem 単位）を引く。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `row_id` | int | 連番（主キー） | Serial primary key |
| 2 | `quest_id` | int | クエストID | Quest ID |
| 3 | `slot` | int | 報酬枠番号 0..4 | Reward slot 0..4 |
| 4 | `rem_id` | int | 報酬テーブル(.rem)番号 | Reward table (.rem) id |

### NPC <a id="npcs"></a>

`npcs`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/npcs.csv` / `data/world/npcs.tsv` |
| 主キー | `npc_id` |
| 行数 | 188 |
| ID 範囲 | 1–999 |
| confidence | `derived` |
| 英語名 | NPCs |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/npc-index.csv`<br>`romfs/nativeNX/table/NpcName_jpn.gmd` |
| 備考 | npc-index.csv の bit を NpcName_jpn.gmd の添字にそのまま使った（bit 0 → ベルナ村の村長 = Bherna Chief、以下 188 件すべて対応）。npc_id は 1..812 で連番ではない。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `npc_id` | int | NPC ID | NPC ID |
| 2 | `bit` | int | NPC ビットマップのビット番号 | Per-NPC bitmap bit |
| 3 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 4 | `name_en` | str | 名前（英語） | Name (English) |
| 5 | `talk_file` | bool | 会話ファイルを持つか | Has a talk file |

### 闘技大会 <a id="arena"></a>

`arena`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/arena.csv` / `data/world/arena.tsv` |
| 主キー | `arena_index` |
| 行数 | 17 |
| ID 範囲 | 0–16 |
| confidence | `verified` |
| 英語名 | Arena |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/arena.csv` |
| 備考 | 闘技大会 17 件（ハンター 11・ニャンター 6）。grade_* はグレード取得の制限時間（秒）。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `arena_index` | int | 闘技大会の並び順 | Arena record index |
| 2 | `quest_id` | int | クエストID | Quest ID |
| 3 | `prowler` | bool | ニャンター部門か | Prowler division |
| 4 | `grade_a` | int | A グレードのタイム(秒) | Grade A time (seconds) |
| 5 | `grade_b` | int | B グレードのタイム(秒) | Grade B time (seconds) |
| 6 | `grade_c` | int | C グレードのタイム(秒) | Grade C time (seconds) |
| 7 | `sets` | str | クエストセット番号（空白区切り） | Quest set numbers |

### 勲章 <a id="awards"></a>

`awards`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/awards.csv` / `data/world/awards.tsv` |
| 主キー | `award_id` |
| 行数 | 132 |
| ID 範囲 | 0–131 |
| confidence | `derived` |
| 英語名 | Awards |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/awards.csv`<br>`romfs/nativeNX/table/GC_Medal_jpn.gmd` |
| 備考 | GC_Medal_jpn.gmd は 264 件で、0..131 が勲章名、132..263 が同じ順の説明。award_id = ビット番号。名前は bit、説明は 132+bit で引いた（例: bit 0 = ベルナ村長の飾り帯 / 「村の★１と★２の全クエストをクリアした証」）。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `award_id` | int | 勲章ビット番号 | Award bit |
| 2 | `grid` | str | ギルドカードのページ | Guild Card page |
| 3 | `name_ja` | str | 勲章名（日本語） | Award name (Japanese) |
| 4 | `name_en` | str | 勲章名（英語） | Award name (English) |
| 5 | `desc_ja` | str | 説明（日本語） | Description (Japanese) |

### 食堂 <a id="canteen"></a>

`canteen`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/canteen.csv` / `data/world/canteen.tsv` |
| 主キー | `canteen_id` |
| 行数 | 144 |
| ID 範囲 | 1–144 |
| confidence | `derived` |
| 英語名 | Canteen |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/canteen.csv`<br>`romfs/nativeNX/table/Kitchen_jpn.gmd` |
| 備考 | 自然キーは (kind, bit)。主キーは連番 canteen_id。Kitchen_jpn.gmd の並びは、各カテゴリ先頭 7 件の食材が 103..133、XX で追加された 14 件が 251..264、料理 0..76 が 134..210、料理 77..98 が 265..286。名前の意味（例 dish 0 Dauntless Pasta = 屋台の根性まかない飯、dish 98 Ultimate Rice = 屋台の究極まかない飯）で全 144 件を確認した。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `canteen_id` | int | 連番（主キー） | Serial primary key |
| 2 | `kind` | str | ingredient（食材）/ dish（料理） | ingredient / dish |
| 3 | `bit` | int | 食材・料理のビット番号 | Ingredient / dish bit |
| 4 | `name_ja` | str | 名前（日本語） | Name (Japanese) |
| 5 | `name_en` | str | 名前（英語） | Name (English) |
| 6 | `category` | str | 肉・穀物・野菜・魚・飲み物・special・starter | Category |
| 7 | `ingredient_a` | str | 料理の食材1（食材ビット） | Dish ingredient 1 (bit) |
| 8 | `ingredient_b` | str | 料理の食材2（食材ビット） | Dish ingredient 2 (bit) |

### 調合・素材の供出値 <a id="provisions"></a>

`provisions`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/provisions.csv` / `data/world/provisions.tsv` |
| 主キー | `item_id` |
| 行数 | 1,878 |
| ID 範囲 | 318–2501 |
| confidence | `verified` |
| 英語名 | Provisions |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/provisions.csv` |
| 備考 | 武具の生産・強化で「素材の供出」に使う値。itemData の +27（値）と +28 の u16 x3（グループ）。グループ 4 は鉱石系（鉄鉱石 1 など）。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `item_id` | int | アイテムID | Item ID |
| 2 | `value` | int | 供出値 | Provision value |
| 3 | `group1` | int | 供出グループ1 | Provision group 1 |
| 4 | `group2` | int | 供出グループ2 | Provision group 2 |
| 5 | `group3` | int | 供出グループ3 | Provision group 3 |

### 村依頼 <a id="requests"></a>

`requests`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/requests.csv` / `data/world/requests.tsv` |
| 主キー | `request_index` |
| 行数 | 184 |
| ID 範囲 | 0–183 |
| confidence | `derived` |
| 英語名 | Requests |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/request-index.csv`<br>`romfs/nativeNX/table/activityData_jpn.gmd`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| 備考 | activityData_jpn.gmd は 920 件 = 184 レコード x 5。依頼 index i の名前は 5*i 番目（例 i=0「しっかり者の村人の依頼１」、i=3「ベルナ村の受付嬢の依頼１」）。quest_name_ja は対象クエストの questData タイトル。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `request_index` | int | 依頼レコード番号 0..183 | Request record index |
| 2 | `kind` | int | 0 クエスト / 1 納品 / 2 不明 / 3 終端 | 0 quest / 1 delivery / 2 unknown / 3 end |
| 3 | `stage` | int | 解放される村・集会所の段階 | Progress stage |
| 4 | `npc_id` | int | 依頼主 NPC の番号 | Requesting NPC |
| 5 | `village` | str | 依頼が出る村 | Village |
| 6 | `quest_id` | int | 対象クエストID | Quest ID |
| 7 | `quest_name_en` | str | クエスト名（英語） | Quest name (English) |
| 8 | `quest_name_ja` | str | クエスト名（日本語） | Quest name (Japanese) |
| 9 | `prereq_quest` | int | 前提クエストID | Prerequisite quest |
| 10 | `reward_id` | int | 報酬アイテムID | Reward item ID |
| 11 | `reward_count` | int | 報酬個数 | Reward count |
| 12 | `accept_flag` | int | 受注フラグ番号 | Accepted flag index |
| 13 | `done_flag` | int | 報告済みフラグ番号 | Completed flag index |
| 14 | `name_ja` | str | 依頼名（日本語） | Request name (Japanese) |

### モンスター剥ぎ取り <a id="monster-carves"></a>

`monster-carves`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/monster-carves.csv` / `data/world/monster-carves.tsv` |
| 主キー | `carve_id` |
| 行数 | 2,551 |
| ID 範囲 | 1–2551 |
| confidence | `verified` |
| 英語名 | Monster carves |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/monster-carves.csv` |
| 備考 | 自然キーは (monster_id, rank, sets, kind, entry_no)。元 CSV は (monster_id, rank, sets, kind, item_id) が 2 件だけ重複する（モンスター38 の kind=other に別テーブルの同アイテムが 2 行）。entry_no は同じ (monster,rank,sets,kind) 内の 0 始まり連番。1 テーブルの確率合計は 100。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `carve_id` | int | 連番（主キー） | Serial primary key |
| 2 | `monster_id` | int | モンスターID | Monster ID |
| 3 | `rank` | str | low / high / g | low / high / g |
| 4 | `sets` | int | 剥ぎ取りセット番号 | Carve set number |
| 5 | `kind` | str | body / tail / shiny / other | body / tail / shiny / other |
| 6 | `entry_no` | int | 同セット内の行番号（0 始まり） | Row ordinal within the table |
| 7 | `item_id` | int | アイテムID | Item ID |
| 8 | `count` | int | 個数 | Count |
| 9 | `chance` | int | 確率(%) | Chance (%) |

### 生産・強化レシピ <a id="recipes"></a>

`recipes`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/recipes.csv` / `data/world/recipes.tsv` |
| 主キー | `recipe_id` |
| 行数 | 28,623 |
| ID 範囲 | 1–28623 |
| confidence | `verified` |
| 英語名 | Recipes |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/recipes.csv` |
| 備考 | 自然キーは (kind, target_id, level, recipe_no)。元 CSV は (kind, id, level) が 127 組重複する（同じ武器・装飾品に別素材の生産レシピが 2 本ある正規のデータ）。recipe_no はその 0 始まり連番。素材なしは item=0 / count=0。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `recipe_id` | int | 連番（主キー） | Serial primary key |
| 2 | `kind` | str | weapon:<武器種> / armor / deco | weapon:<class> / armor / deco |
| 3 | `target_id` | int | 生産対象の武器ID・防具ID・装飾品アイテムID | Weapon / armor / decoration ID |
| 4 | `level` | int | 0 = 生産、1 以上 = そのレベルへの強化 | 0 forge, 1+ upgrade level |
| 5 | `recipe_no` | int | 同じ (kind, target_id, level) 内の 0 始まり連番 | Ordinal within (kind, target_id, level) |
| 6 | `item1` | int | 素材1のアイテムID | Material 1 item ID |
| 7 | `count1` | int | 素材1の個数 | Material 1 count |
| 8 | `item2` | int | 素材2のアイテムID | Material 2 item ID |
| 9 | `count2` | int | 素材2の個数 | Material 2 count |
| 10 | `item3` | int | 素材3のアイテムID | Material 3 item ID |
| 11 | `count3` | int | 素材3の個数 | Material 3 count |
| 12 | `item4` | int | 素材4のアイテムID | Material 4 item ID |
| 13 | `count4` | int | 素材4の個数 | Material 4 count |
| 14 | `provision_group` | int | 供出グループ | Provision group |
| 15 | `provision_value` | int | 供出値 | Provision value |

### クエスト報酬テーブル <a id="rewards"></a>

`rewards`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/rewards.csv` / `data/world/rewards.tsv` |
| 主キー | `reward_id` |
| 行数 | 10,992 |
| ID 範囲 | 1–10992 |
| confidence | `verified` |
| 英語名 | Reward tables |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/rewards.csv` |
| 備考 | quest-rewards.csv の rem_id を引く先。rem_id ごとに 1..22 行あり、同じ rem に同じアイテムが 2 行出ることがある（571 組）ので、自然キーは (rem_id, entry_no)。(rem_id, item_id, count, chance) も10,992 行すべて一意。chance は 1..100 で、1 テーブルの合計は 100。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `reward_id` | int | 連番（主キー） | Serial primary key |
| 2 | `rem_id` | int | 報酬テーブル(.rem)番号 | Reward table (.rem) id |
| 3 | `entry_no` | int | テーブル内の行番号（0 始まり） | Row ordinal within the table |
| 4 | `item_id` | int | アイテムID | Item ID |
| 5 | `count` | int | 個数 | Count |
| 6 | `chance` | int | 確率(%) | Chance (%) |

### クエスト出現条件 <a id="quest-unlock"></a>

`quest-unlock`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/quest-unlock.csv` / `data/world/quest-unlock.tsv` |
| 主キー | `quest_id` |
| 行数 | 1,506 |
| ID 範囲 | 101–1120013 |
| confidence | `derived` |
| 英語名 | Quest unlock rules |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/quest-unlock.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| 備考 | quest_id は 1,506 件で、quests.csv の quest_id 集合と完全に一致する。rule は "flag:396" "cleared:11404" "hr:7" "village_star:6 AND ..." の形で、空欄 204 件は条件なし（最初から出る）。name_ja は questData のタイトル。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `quest_id` | int | クエストID | Quest ID |
| 2 | `name_en` | str | クエスト名（英語） | Quest name (English) |
| 3 | `name_ja` | str | クエスト名（日本語） | Quest name (Japanese) |
| 4 | `rule` | str | 出現条件（flag: / cleared: / hr: / village_star: など） | Unlock rule |

### 解放ビット一覧 <a id="unlock-lists"></a>

`unlock-lists`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/unlock-lists.csv` / `data/world/unlock-lists.tsv` |
| 主キー | `unlock_id` |
| 行数 | 1,418 |
| ID 範囲 | 1–1418 |
| confidence | `verified` |
| 英語名 | Unlock maps |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/unlock-lists.csv` |
| 備考 | 自然キーは (map, bit)（1,418 行すべて一意）。map は 38 種で、研究施設 lab・ジュークボックス song・武具屋 armory:1..21・交易商 trader:*・shop:0/1 など。need は "start"（最初から）"dlc"（配信）"never"（未使用）や "v2|h2"（村★2 または 集会所★2）"q806&q10768"（両方クリア）の形。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `unlock_id` | int | 連番（主キー） | Serial primary key |
| 2 | `map` | str | 解放マップ名（lab / song / armory:7 / trader:words など） | Unlock map name |
| 3 | `bit` | int | マップ内のビット番号 | Bit in the map |
| 4 | `target_id` | int | 解放される装備・アイテムID（無い行は空） | Unlocked equipment / item id |
| 5 | `need` | str | 解放条件（start / dlc / v2|h2 / q806&q10768 など） | Unlock condition |

### サイズ変動テーブル <a id="size-variation"></a>

`size-variation`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/size-variation.csv` / `data/world/size-variation.tsv` |
| 主キー | `variation_id` |
| 行数 | 1,385 |
| ID 範囲 | 1–1385 |
| confidence | `verified` |
| 英語名 | Size variation tables |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/size-variation.csv` |
| 備考 | ゲームの em_size_yure_data（52 テーブル）。クエストの boss 枠がsize_table を指し、サイズ = クエストの size% × rate。自然キーは (size_table, rate)（1,385 行すべて一意）。rate は 88..130、chance 0 の行は元データに無い。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `variation_id` | int | 連番（主キー） | Serial primary key |
| 2 | `size_table` | int | サイズ変動テーブル番号 0..51 | Size variation table 0..51 |
| 3 | `rate` | int | 倍率（%・整数） | Scale rate (%) |
| 4 | `chance` | int | 確率(%) | Chance (%) |

### 日替わりクエスト <a id="rotating-quests"></a>

`rotating-quests`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/rotating-quests.csv` / `data/world/rotating-quests.tsv` |
| 主キー | `rotating_bit` |
| 行数 | 51 |
| ID 範囲 | 0–50 |
| confidence | `derived` |
| 英語名 | Rotating quests |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/rotating-quests.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| 備考 | セーブの base + 0x504B のビットで、次に 1 クエストクリアするまで有効。ビット 0..50 の 51 件で、quest_id はすべて quests.csv に存在する。name_ja は questData のタイトル。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `rotating_bit` | int | 日替わりビット 0..50 | Rotating bit 0..50 |
| 2 | `quest_id` | int | クエストID | Quest ID |
| 3 | `param_hex` | str | クエストパラメータ（16 進） | Quest parameter (hex) |
| 4 | `name_en` | str | クエスト名（英語） | Quest name (English) |
| 5 | `name_ja` | str | クエスト名（日本語） | Quest name (Japanese) |

### 村依頼の提示条件 <a id="request-offer"></a>

`request-offer`

| 項目 | 値 |
|---|---|
| ファイル | `data/world/request-offer.csv` / `data/world/request-offer.tsv` |
| 主キー | `offer_id` |
| 行数 | 186 |
| ID 範囲 | 1–186 |
| confidence | `derived` |
| 英語名 | Request offers |
| 出典 | `mhnxeditor/.work/finalaudit/refsrc/data/request-offer.csv`<br>`romfs/nativeNX/arc/quest/q*.arc (questData_*_jpn)` |
| 備考 | NPC の会話データから読んだ「この依頼を出す条件」。自然キーは (request_index, npc_file, npc_bit, talk_line) で 186 行すべて一意。request_index は 4 組 (28, 135, 149, 150) が 2 行ずつあり、28/149/150 は赤鬼/黒鬼の 2 人、135 は同じ NPC の別の会話行。quest_id が空の行は納品依頼（kind 1）でクエストを持たない。 |

| # | 列名 | 型 | 説明 (ja) | 説明 (en) |
|---:|---|---|---|---|
| 1 | `offer_id` | int | 連番（主キー） | Serial primary key |
| 2 | `request_index` | int | requests.csv の request_index | requests.csv request_index |
| 3 | `quest_id` | int | クエストID | Quest ID |
| 4 | `quest_name_en` | str | クエスト名（英語） | Quest name (English) |
| 5 | `quest_name_ja` | str | クエスト名（日本語） | Quest name (Japanese) |
| 6 | `npc_file` | int | 会話ファイル番号 | Talk file number |
| 7 | `npc_bit` | int | 会話ファイル内の NPC ビット | NPC bit in the talk file |
| 8 | `npc_name` | str | NPC 名（英語） | NPC name (English) |
| 9 | `talk_kind` | int | 会話の種類 | Talk kind |
| 10 | `talk_line` | int | 会話行番号 | Talk line |
| 11 | `accept_flag` | int | 受注フラグ番号 | Accepted flag index |
| 12 | `also` | str | 同時に設定・解除するフラグ | Flags set or cleared with it |
| 13 | `offer` | str | 提示条件（village_star: / flag: / cleared: など） | Offer condition |
