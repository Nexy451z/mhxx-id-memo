# MHXX ID MEMO — 制作契約 (SPEC)

このリポジトリは **Monster Hunter XX (Nintendo Switch)** の各種 ID（アイテム / 武器 / 防具 / 装飾品 / 護石 / スキル / 狩技 / モンスター / ステージ / クエスト / NPC など）の
**ID メモ** を、CSV / TSV / 単一 HTML ビューアで提供する。

司令塔 (Lead) が本 SPEC を管理する。担当者は作業前に必ず全文を読むこと。

---

## 0. 絶対ルール

1. **推測で値を埋めない。** 不明は空文字。捏造はレビューで即 FAIL。
2. **出典を必ず残す。** 各テーブルの `source` に実ファイルパス（`C:\\anyWorkspace\\nx\\mhxx\\...` からの相対）を書く。
3. **confidence を正直に書く。** `verified`（実データ由来）/ `derived`（既存テーブルから算出）/ `curated`（既知リストを人手で対応付け）。
4. **書き込みスコープを守る。** 他担当のディレクトリは読むだけ。編集禁止。
5. **文字コードは UTF-8。** CSV/TSV は BOM 付き（Excel 対応）、JSON/MD/PY/HTML は BOM なし。
6. **改行は LF。** CSV/TSV も LF（Python の `lineterminator="\n"`）。
7. **作業後は必ず自己検証**（件数・主キー重複・ID 範囲）し、結果を担当 NOTES に書く。

---

## 1. ディレクトリ構成

```
mhxx-id-memo/
├── SPEC.md                  # 本ファイル（Lead 管理）
├── README.md                # 利用者向け説明（builder 管理）
├── data/
│   ├── index.json           # 全テーブルカタログ（builder が manifest をマージして生成）
│   ├── equip/               # analyst-equip の担当
│   │   ├── _manifest.json
│   │   ├── NOTES.md
│   │   └── *.csv
│   └── world/               # analyst-world の担当
│       ├── _manifest.json
│       ├── NOTES.md
│       └── *.csv
├── docs/
│   ├── table-definitions.md # 各テーブル定義・ID 範囲・列の意味（builder）
│   └── sources.md           # 出典と抽出方法（builder、analyst の NOTES を統合）
├── tools/
│   ├── build.py             # CSV→TSV / index.json / web/data.js / web/index.html 生成（builder）
│   └── extract_*.py         # 抽出スクリプト（analyst が各自の担当分を置く）
├── web/
│   ├── index.html           # 単一ファイル・オフライン ID ビューア（builder）
│   ├── data.js              # window.MHXX_ID_MEMO = {...}（build.py 生成）
│   └── mhxx-id-memo.html    # 完全自己完結版（build.py --single-file 生成）
└── review/
    └── REVIEW.md            # レビュー結果（reviewer）
```

---

## 2. CSV 仕様

- 区切り: `,`（RFC4180、必要時のみダブルクォート）
- 先頭行はヘッダー
- **1 列目は必ず主キー**（例: `item_id`）
- 列名は `snake_case` の ASCII
- ID 列は整数（ゼロ埋めしない）
- 名前は `name_ja`（日本語）/ `name_en`（英語）。無い場合は空文字。
- 説明は `desc_ja` / `desc_en`。改行は値内に保持してよい（CSV は引用符で囲む）。
- 真偽値は `yes` / `no`
- 空値は空文字（`NULL` 等の文字列は使わない）

### プレースホルダの扱い（レビュー指摘により明文化）

出典が `(None)` を返す「装備なし」ダミー行は **空文字に正規化**する（`kinsects` / `talismans` / `armor` など）。
一方、出典が `-` のような**ゲーム内の意味を持つ記号**を返す場合は、そのまま保持する（`npcs` の 16 行など）。
判断基準は「その文字列がゲーム内で表示される値か（保持）／ライブラリの None が漏れただけか（空文字化）」。
迷った場合は `notes_ja` に判断理由を書く。

### TSV は build.py が CSV から自動生成する（analyst は作らない）
TSV では値内の `\t` と改行を半角スペース 1 個に置換する（表計算ソフトでの破損防止）。

---

## 3. `_manifest.json` 仕様

各データディレクトリ直下に 1 つ。**配列 `tables`** を持つ。

```json
{
  "area": "equip",
  "tables": [
    {
      "id": "items",
      "title_ja": "アイテム",
      "title_en": "Items",
      "file": "items.csv",
      "primary_key": "item_id",
      "row_count": 1234,
      "id_range": [0, 2999],
      "columns": [
        { "name": "item_id", "type": "int",  "desc_ja": "アイテムID", "desc_en": "Item ID" },
        { "name": "name_ja", "type": "str",  "desc_ja": "名前（日本語）", "desc_en": "Name (Japanese)" }
      ],
      "source": [
        "romfs/nativeNX/table/itemData_jpn.gmd",
        "extract/jp_names/items.csv"
      ],
      "confidence": "verified",
      "notes_ja": "itemData.itm のレコード数と一致。0 はダミー。",
      "notes_en": ""
    }
  ]
}
```

- `id`: 全体で一意な kebab-case。HTML のアンカーになる。
- `row_count`: ヘッダーを除くデータ行数。**実ファイルと一致必須**。
- `id_range`: `[min, max]`。主キーが文字列の表は `null`。
- `columns[].type`: `int` | `str` | `float` | `bool`
- `confidence`: `verified` | `derived` | `curated`

---

## 4. 担当と書き込みスコープ

| 担当 | 書き込み可 | 禁止 |
|---|---|---|
| **lead** | `SPEC.md`、`data/index.json`（最終統合時）、git 操作 | 各担当の成果物の中身 |
| **analyst-equip** | `data/equip/**`、`tools/extract_equip_*.py` | `data/world/**`、`web/**`、`README.md` |
| **analyst-world** | `data/world/**`、`tools/extract_world_*.py` | `data/equip/**`、`web/**`、`README.md` |
| **builder** | `web/**`、`tools/build.py`、`README.md`、`docs/**`、`data/index.json` | `data/equip/**`、`data/world/**` |
| **reviewer** | `review/**` のみ | それ以外すべて |

---

## 5. テーブル割り当て

### analyst-equip（装備・アイテム系）
| id | 内容 | 主な出典 |
|---|---|---|
| `items` | アイテム ID・名前・説明・カテゴリ | `extract/jp_names/items.csv`、`itemData.itm`、`itemCategoryTypeData.ict` |
| `item-categories` | アイテムカテゴリ ID | `itemCategoryTypeData.ict`、`itemCategoryTypeData_jpn.gmd` |
| `weapons` | 武器 ID（type/weapon/form）・名前・説明 | `extract/jp_names/weapons.csv`、`gamedata.rs` の `EQUIP_*_NAMES` |
| `weapon-types` | 武器種 ID（0..14） | `gamedata.rs` `HUNT_WEAPONS`、`jp_names/gen.py` の WTYPES |
| `armor` | 防具（シリーズ×部位）ID・名前・説明 | `extract/jp_names/armor_series.csv`、`EQUIP_*_NAMES`/`_IDS` |
| `armor-parts` | 部位 ID（頭/胴/腕/腰/脚） | 同上 |
| `decorations` | 装飾品（珠）ID・スキル・スロット | `refsrc/data/decorations.csv`、`JWL_NAMES`/`JWL_I_DS` |
| `talismans` | 護石 ID・名前・レア度 | `EQUIP_TALISMAN_NAMES`、`TALISMAN_RARITY`、`talisman-tables.csv` |
| `skills` | スキル ID・名前・説明・最大Lv | `extract/jp_names/skills.csv`、`SKILL_NAMES`、`skill-trees.csv` |
| `hunter-arts` | 狩技 ID・名前・武器種・コスト | `refsrc/data/hunter-arts.csv`、`hunterArtsData_jpn.gmd` |
| `kinsects` | 操虫棍の虫 ID・名前 | `KINSECT_NAMES` |
| `palico-weapons` | オトモ武器 ID・名前 | `PALICO_WEAPON_NAMES`、`extract/jp_names/palico_weapon.csv` |
| `palico-armor` | オトモ防具 ID・名前 | `PALICO_HEAD_NAMES`/`_IDS`、`PALICO_ARMOR_NAMES`/`_IDS` |
| `palico-skills` | オトモスキル ID・名前 | `PALICO_SKILLS` 系 |
| `palico-support` | オトモ支援行動 ID・名前 | `PALICO_SUPPORT_MOVES` 系 |

### analyst-world（世界・進行系）
| id | 内容 | 主な出典 |
|---|---|---|
| `monsters` | モンスター ID・名前（日英）・分類 | `refsrc/data/monster-index.csv`、`MONSTER_HUNT_NAMES`、`HN_MonsterListMsg_jpn.gmd` |
| `stages` | ステージ ID・名前・エリア | `quest-info.csv` の stage、`MapName_jpn.gmd`、各種 Msg |
| `quests` | クエスト ID・名前・ランク・種別 | `refsrc/data/quest-index.csv`、`quest-info.csv` |
| `quest-monsters` | クエスト×モンスター | `refsrc/data/quest-monsters.csv` |
| `quest-rewards` | クエスト報酬 | `refsrc/data/quest-rewards.csv` |
| `npcs` | NPC ID・名前 | `refsrc/data/npc-index.csv`、`NpcName_jpn.gmd` |
| `arena` | 闘技大会 ID・クエスト | `refsrc/data/arena.csv` |
| `awards` | 勲章 ID・名前 | `refsrc/data/awards.csv`、`GC_Medal_jpn.gmd` |
| `canteen` | 食堂メニュー ID | `refsrc/data/canteen.csv` |
| `provisions` | 調合・食材など | `refsrc/data/provisions.csv` |
| `requests` | 村依頼 ID・名前 | `refsrc/data/request-index.csv`、`activityData_jpn.gmd` |
| `monster-carves` | モンスター剥ぎ取り | `refsrc/data/monster-carves.csv` |
| `recipes` | 生産・強化レシピ | `refsrc/data/recipes.csv` |

> テーブルは増減可。ただし **id は manifest と HTML で一貫**させること。増やす場合は Lead に報告。

---

## 6. HTML ビューア仕様（builder）

`web/index.html` は **file:// で直接開いて動く**こと（外部 CDN・fetch 禁止）。

必須機能:
1. 左サイドバー: テーブル一覧（グループ分け・件数表示）、クリックで切替
2. 検索ボックス: 全列横断の部分一致（大文字小文字無視、日本語可）
3. 列フィルタ: 列選択 + 値の絞り込み
4. ソート: ヘッダークリックで昇順/降順
5. 行選択: チェックボックス、全選択/全解除、フィルタ結果のみ選択
6. コピー: 選択行 / 表示中 / 全件 を **TSV** または **CSV** でクリップボードへ
7. ダウンロード: 選択行 / 表示中 / 全件 を **.csv** / **.tsv** で保存（BOM 付き）
8. 列表示切替（チェックボックス）
9. 行クリックで詳細パネル（全列を縦に表示、各値コピー可）
10. テーブル定義パネル（manifest の columns / source / confidence を表示）
11. 件数表示（全件 / フィルタ後 / 選択中）
12. キーボード: `/` で検索フォーカス、`Esc` でクリア
13. 大きいテーブル（1万行超）でも破綻しない（ページング or 仮想スクロール）

見た目: ダークテーマ基調、等幅フォントで ID を揃える、日本語 UI。

---

## 7. 完了条件（Definition of Done）

- [ ] `data/equip/` と `data/world/` に CSV と `_manifest.json` が揃い、row_count が実ファイルと一致
- [ ] `data/index.json` が全テーブルを列挙し、`tools/build.py` で再生成可能
- [ ] `web/index.html` がオフラインで動作し、コピー / CSV / TSV 抽出が動く
- [ ] `README.md` に使い方・ID 範囲早見表・出典・再生成手順
- [ ] `docs/table-definitions.md` に全テーブルの列定義
- [ ] `review/REVIEW.md` に PASS/FAIL と根拠
- [ ] 主キー重複ゼロ、ID 範囲の矛盾ゼロ
- [ ] git 初期コミット済み
