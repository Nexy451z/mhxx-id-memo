# MHXX ID MEMO

Monster Hunter XX (Nintendo Switch) の各種 ID を、**CSV / TSV / 単一 HTML ビューア**で引けるようにしたメモです。

- 対象: アイテム / 武器 / 防具 / 装飾品 / 護石 / スキル / 狩技 / モンスター / ステージ / クエスト / NPC など
- データは**ゲーム実データ由来**。出典は各テーブルの `source` と [docs/sources.md](docs/sources.md) に記載
- 不明な値は**空文字**（推測で埋めていない）
- `confidence` で根拠の強さを明示（`verified` / `derived` / `curated`）

> **🌐 オンライン版**: <https://nexy451z.github.io/mhxx-id-memo/>
> （GitHub Pages・インストール不要。ローカルで使う場合は下記の HTML を直接開いてください）

---

## クイックスタート（インストール不要）

### 1. ブラウザで開く

| ファイル | 内容 |
|---|---|
| `web/mhxx-id-memo.html` | **これ 1 ファイルで完結**（データ埋め込み・完全オフライン） |
| `web/index.html` | `web/data.js` を読み込む版（データ更新時は再読み込みするだけ） |

どちらも `file://` で直接開けます。ローカルサーバー・外部 CDN・外部フォントは不要です。

### 2. 表計算ソフトで開く

| ファイル | 形式 |
|---|---|
| `data/equip/*.tsv` / `data/world/*.tsv` | UTF-8 BOM 付き・タブ区切り（Excel でそのまま開ける） |
| `data/equip/*.csv` / `data/world/*.csv` | UTF-8 BOM 付き・RFC4180（引用符付き CSV） |
| `data/index.json` | 全テーブルのカタログ（列定義・出典・件数） |

---

## テーブル一覧・ID 範囲早見表

<!-- BEGIN:TABLES (tools/build.py が自動生成。手編集しないこと) -->
**テーブル数**: 42 / **総行数**: 91,406 / **データ版**: `sha256:9f346b940d85`

| area | id | テーブル | 行数 | 主キー | ID 範囲 | confidence |
|---|---|---|---:|---|---|---|
| equip | `armor` | 防具 | 5,836 | `armor_id` | 0–6431 | verified |
| equip | `armor-parts` | 防具部位 | 5 | `part_id` | 0–4 | verified |
| equip | `armor-skills` | 防具スキルポイント | 14,639 | `row_id` | 1–14639 | derived |
| equip | `combinations` | 調合 | 183 | `row_id` | 1–183 | derived |
| equip | `decorations` | 装飾品（珠） | 262 | `decoration_id` | 1–262 | verified |
| equip | `hunter-arts` | 狩技 | 178 | `art_id` | 1–190 | derived |
| equip | `item-categories` | アイテムカテゴリ（素材分類） | 338 | `category_id` | 0–337 | verified |
| equip | `items` | アイテム | 2,991 | `item_id` | 0–2990 | verified |
| equip | `kinsects` | 猟虫 | 32 | `kinsect_id` | 0–31 | verified |
| equip | `palico-actions` | オトモ行動（支援行動・スキル） | 154 | `row_id` | 1–154 | derived |
| equip | `palico-armor` | オトモ防具 | 1,026 | `palico_armor_id` | 0–1053 | verified |
| equip | `palico-levels` | オトモレベル | 99 | `level` | 1–99 | derived |
| equip | `palico-skills` | オトモスキル（術） | 96 | `palico_skill_id` | 0–95 | verified |
| equip | `palico-support` | オトモ支援行動 | 57 | `support_move_id` | 0–56 | derived |
| equip | `palico-weapons` | オトモ武器 | 509 | `palico_weapon_id` | 0–508 | verified |
| equip | `skill-effects` | スキル効果（発動後のスキル名） | 328 | `effect_id` | 0–327 | verified |
| equip | `skills` | スキル | 206 | `skill_id` | 0–205 | derived |
| equip | `smithy-lists` | 鍛冶屋リスト | 23 | `row_id` | 1–23 | derived |
| equip | `talisman-tables` | 護石スキル抽選範囲 | 525 | `row_id` | 1–525 | derived |
| equip | `talismans` | 護石 | 11 | `talisman_id` | 0–10 | verified |
| equip | `weapon-tree` | 武器派生 | 798 | `row_id` | 1–798 | derived |
| equip | `weapon-types` | 武器種 | 15 | `weapon_type_id` | 0–14 | verified |
| equip | `weapons` | 武器 | 4,818 | `weapon_id` | 0–140802 | verified |
| world | `monsters` | モンスター | 137 | `monster_id` | 1–137 | derived |
| world | `stages` | ステージ | 31 | `stage_id` | 1–104 | curated |
| world | `quests` | クエスト | 1,508 | `quest_index` | 1–1508 | derived |
| world | `quest-monsters` | クエスト出現モンスター | 2,449 | `row_id` | 1–2449 | verified |
| world | `quest-rewards` | クエスト報酬枠 | 4,897 | `row_id` | 1–4897 | verified |
| world | `npcs` | NPC | 188 | `npc_id` | 1–999 | derived |
| world | `arena` | 闘技大会 | 17 | `arena_index` | 0–16 | verified |
| world | `awards` | 勲章 | 132 | `award_id` | 0–131 | derived |
| world | `canteen` | 食堂 | 144 | `canteen_id` | 1–144 | derived |
| world | `provisions` | 調合・素材の供出値 | 1,878 | `item_id` | 318–2501 | verified |
| world | `requests` | 村依頼 | 184 | `request_index` | 0–183 | derived |
| world | `monster-carves` | モンスター剥ぎ取り | 2,551 | `carve_id` | 1–2551 | verified |
| world | `recipes` | 生産・強化レシピ | 28,623 | `recipe_id` | 1–28623 | verified |
| world | `rewards` | クエスト報酬テーブル | 10,992 | `reward_id` | 1–10992 | verified |
| world | `quest-unlock` | クエスト出現条件 | 1,506 | `quest_id` | 101–1120013 | derived |
| world | `unlock-lists` | 解放ビット一覧 | 1,418 | `unlock_id` | 1–1418 | verified |
| world | `size-variation` | サイズ変動テーブル | 1,385 | `variation_id` | 1–1385 | verified |
| world | `rotating-quests` | 日替わりクエスト | 51 | `rotating_bit` | 0–50 | derived |
| world | `request-offer` | 村依頼の提示条件 | 186 | `offer_id` | 1–186 | derived |
<!-- END:TABLES -->

---

## ビューアの使い方

### 基本操作

| 操作 | 内容 |
|---|---|
| 左サイドバー | テーブル切替（グループ別・件数付き） |
| `/` キー | 検索ボックスへフォーカス |
| 検索ボックス | **全列横断**の部分一致。日本語・英語・ID すべてにヒット（大文字小文字・全角半角を無視） |
| 列フィルタ | 列を選んで、その列の値で絞り込み |
| `Esc` | モーダル / 詳細パネルを閉じる → 検索・フィルタをクリア |
| ヘッダークリック | 昇順 → 降順 → ソート解除 の順に切替 |
| 行クリック | 右に**詳細パネル**（全列を縦表示・値ごとにコピー可） |
| `テーブル定義` ボタン | manifest の列定義・出典・confidence・備考を表示 |

### 行選択

- 各行のチェックボックス、またはヘッダーのチェックボックス（そのページを全選択）
- `全選択` … テーブル全行
- `表示中を選択` … フィルタ後の行だけを選択に追加
- `選択解除` … 選択をクリア

### コピー / ダウンロード

`コピー ▾` / `ダウンロード ▾` から、**範囲 × 形式**の 6 通りを選べます。

| 範囲 | 内容 |
|---|---|
| 選択行 | チェックした行（表示順 → 表示外の選択行の順） |
| 表示中 | 検索・列フィルタ後・ソート後の全行（ページに収まっていない行も含む） |
| 全件 | テーブルの全行 |

| 形式 | 内容 |
|---|---|
| TSV | タブ区切り。値内のタブ・改行は半角スペースに置換（表計算ソフトでの破損防止） |
| CSV | RFC4180。必要時のみダブルクォート、`""` でエスケープ |

- ダウンロードは **BOM 付き UTF-8**（Excel で文字化けしない）
- ファイル名は `mhxx-<table>-<scope>-<yyyymmdd-hhmmss>.<csv|tsv>`
- メニューの「表示中の列のみ」で、非表示列を含めるかどうかを切替できます

### 大きいテーブル

1 万行超のテーブルでも破綻しないよう、**ページング**（100 / 200 / 500 / 1000 / 2000 / 全件）で描画しています。
検索・フィルタ・ソートは全行に対して行い、描画だけをページ単位にしています。

---

## 再生成手順

`data/` 配下の CSV と `_manifest.json` を更新したら、リポジトリのルートで:

```bash
python tools/build.py
```

これで以下がすべて再生成されます（冪等・何度実行しても同じ結果）。

| 生成物 | 内容 |
|---|---|
| `data/index.json` | 全テーブルカタログ（manifest のマージ結果） |
| `data/<area>/*.tsv` | CSV から生成した TSV |
| `web/data.js` | `window.MHXX_ID_MEMO`（ビューア用データ） |
| `web/mhxx-id-memo.html` | データ埋め込みの自己完結版 |
| `docs/table-definitions.md` | 全テーブルの列定義（自動生成） |
| `docs/sources.md` | 出典と抽出方法（自動生成・NOTES.md を統合） |
| `docs/build-report.md` | 検証レポート（件数・主キー重複・row_count 不一致） |
| `README.md` のテーブル一覧ブロック | 自動更新 |

### オプション

| オプション | 内容 |
|---|---|
| `--no-single-file` | 自己完結 HTML を作らない |
| `--root <dir>` | 対象リポジトリを差し替える（テスト用） |
| `--stamp` | `meta.built_at` に生成時刻を入れる（既定は入れない = 冪等） |
| `--quiet` | ログを出さない |

終了コードは **エラーがあれば 1**、警告のみなら 0 です。警告・エラーは `docs/build-report.md` にも残ります。

### 検証内容

`tools/build.py` は次を検証します。

1. manifest の `row_count` と CSV の実データ行数が一致するか
2. 主キーの重複・空値がないか
3. manifest の `columns` と CSV ヘッダーが一致するか
4. `id_range` が実データの min/max と一致するか
5. `confidence` / `type` が既定の値か
6. `source` が空でないか

manifest が無い・壊れている場合はそのエリアをスキップして警告を出します（ビルドは落ちません）。

---

## ディレクトリ構成

```
mhxx-id-memo/
├── SPEC.md                  制作契約
├── README.md                本ファイル
├── data/
│   ├── index.json           全テーブルカタログ（自動生成）
│   ├── equip/               装備・アイテム系 CSV + _manifest.json + NOTES.md
│   └── world/               世界・進行系 CSV + _manifest.json + NOTES.md
├── docs/
│   ├── table-definitions.md 列定義（自動生成）
│   ├── sources.md           出典と抽出方法（自動生成）
│   └── build-report.md      検証レポート（自動生成）
├── tools/
│   ├── build.py             ビルドツール
│   └── extract_*.py         抽出スクリプト
└── web/
    ├── index.html           ビューア本体（オフライン動作）
    ├── data.js              ビューア用データ（自動生成）
    └── mhxx-id-memo.html    自己完結版（自動生成）
```

---

## データ仕様（要約）

- CSV は UTF-8 BOM 付き・RFC4180・LF 改行
- 1 列目が主キー（例: `item_id`）
- 列名は snake_case の ASCII
- ID 列は整数（ゼロ埋めしない）
- 名前は `name_ja` / `name_en`、説明は `desc_ja` / `desc_en`
- 真偽値は `yes` / `no`、空値は空文字

詳細は [SPEC.md](SPEC.md) を参照。

---

## 出典

各テーブルの出典は [docs/sources.md](docs/sources.md) と `data/index.json` の `source` に記載しています。
出典は romfs 内のゲームデータ（`romfs/nativeNX/table/*.gmd` など）、実行時メモリ、既存の抽出物です。

**注意**: 本リポジトリはゲームデータから抽出した ID のメモです。ゲーム本体・ROM は含みません。
