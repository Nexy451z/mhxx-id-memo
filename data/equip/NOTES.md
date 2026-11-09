# data/equip — 装備・アイテム系 ID テーブル

Monster Hunter XX (Nintendo Switch) の装備・アイテム系 ID を、**romfs の実テーブル**から抽出したもの。
推測値は入れていない。値が取れない列は空文字にしてある。

- 生成: `python tools/extract_equip_tables.py`
- 検証: `python tools/verify_equip_tables.py`
- 文字コード: CSV は UTF-8 BOM 付き / 改行 LF / 値内の改行も LF に統一。`_manifest.json` は BOM なし UTF-8。

> **TSV は `tools/build.py` が CSV から生成する（analyst は作らない）。** このディレクトリに
> 残っている `*.tsv` は builder の生成物なので、CSV を更新したら builder 側で再生成が必要。

---

## 1. テーブル一覧

### 第 1 バッチ（SPEC 5 章の担当表 + 追加 1）

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

### 第 2 バッチ（追加 7）

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

### 主キーについて

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

## 2. 出典と抽出方法

読み取り専用。いずれも `C:\anyWorkspace\nx\mhxx\` 配下。

### 2.1 romfs の実テーブル (`romfs/nativeNX/table/`)

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

### 2.2 mhnxeditor の静的テーブル (`crates/mhnx-core/src/gamedata.rs`)

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

### 2.3 既存の日本語名抽出 (`extract/jp_names/`)

`items.csv` / `weapons.csv` / `armor_series.csv` / `skills.csv` / `amulet.csv` /
`palico_weapon.csv` / `palico_armor.csv`。romfs から生成済みのものは romfs を直接読み直して同じ結果になることを確認した。

### 2.4 refsrc のデータ (`mhnxeditor/.work/finalaudit/refsrc/data/`)

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

## 3. ID 対応の根拠（ここが弱いと表が崩れる箇所）

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

### 狩技の武器種の決め方

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

## 4. 検証結果

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

## 5. 未解決点・残課題

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

---

## 6. 再生成手順

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
