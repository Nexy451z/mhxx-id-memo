# MHXX ID MEMO — 独立レビュー報告

- **レビュー担当**: reviewer
- **対象**: `C:\anyWorkspace\nx\mhxx\mhxx-id-memo`
- **対象データ版**: `sha256:9f346b940d85d78ba196a13055a17ef9971e9d81d2796ef5d6fdc00cd217ea92`
- **規模**: 42 テーブル / 91,406 行（equip 23 テーブル 33,129 行 / world 19 テーブル 58,277 行）
- **実施日**: 2026-11-09
- **判定**: **PASS**

---

## 0. 総合判定

**PASS。**

42 テーブルすべてで、主キー重複ゼロ・`row_count`/`id_range` の一致・出典との値一致を確認した。
**捏造（推測で埋めた値）は検出されず**、特に**ステージ ID とモンスター ID は全行を一次資料と突合して完全一致**した。
ビルドは冪等で再現可能、HTML は必須機能 1〜13 をすべて実装し、単一ファイル版も完全オフラインで動作する。

レビュー中に検出した指摘はすべて解消済み（§5 参照）。残る作業は **lead の git 初期コミット**のみで、
これは「レビュー確定後に実施する」と lead が明示している工程のため、本レビューの判定には影響しない。

| 区分 | 件数 |
|---|---|
| Critical | 0 |
| Major（未解決） | 0 |
| Major（レビュー中に解決） | 2 |
| Minor（未解決・任意） | 1 |
| Minor（レビュー中に解決） | 1 |

---

## 1. 検証環境と再現方法

| 項目 | 値 |
|---|---|
| Python | `C:\Users\haruk\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe` |
| Node | `C:\Users\haruk\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe` |
| 乱数 seed | `20260101`（出典突合のサンプリングを再現可能にする） |

レビュー用スクリプトは `review/` に置いた。**データは一切変更していない**（CSV / manifest は read のみ）。

```bash
cd C:\anyWorkspace\nx\mhxx\mhxx-id-memo
python review/verify.py                       # 構造 / manifest / TSV / 捏造
python review/provenance.py                   # 出典整合（各表 20 行を無作為抽出）
python review/fullcheck.py                    # 重点項目の全行チェック
python review/check_build.py --twice          # 再現性（build.py を 2 回実行）
python review/check_html.py                   # HTML / JS
```

終了コードは各スクリプトとも `0` = 指摘なし、`1` = 指摘あり。

---

## 2. 検証結果サマリ

| # | 検証項目 | 結果 | 指摘 |
|---|---|---|---|
| 1 | 構造（主キー・重複・snake_case・BOM・LF） | **PASS** | 0 件 |
| 2 | manifest 整合（row_count / id_range / columns） | **PASS** | 0 件 |
| 3 | 出典整合（各表 20 行抽出 × 一次資料） | **PASS** | 不一致 0 件 |
| 4 | 捏造チェック（空値・confidence・ID 範囲） | **PASS** | 0 件 |
| 5 | TSV が CSV と同内容 | **PASS** | 0 件 |
| 6 | HTML（node --check / 必須機能 1〜13） | **PASS** | 0 件 |
| 7 | 再現性（build.py 再実行・冪等） | **PASS** | 差分 0 |
| 8 | README / docs と実データの整合 | **PASS** | 0 件（M1 解決済み） |

### 出典突合の内訳（`review/provenance.py`）

42 テーブルすべてで **不一致 0**。比較は改行を LF に正規化したうえで行った（SPEC §0.6 の LF 規約に合わせる）。

| 突合方法 | テーブル数 | 主な一次資料 |
|---|---|---|
| 一次資料と 1:1 突合 | 30 | extract/jp_names, refsrc/data, gamedata.rs, questfields.rs, romfs/*.gmd, quest ARC |
| refsrc と同一順で突合 | 8 | armor-skills, combinations, palico-actions, palico-levels, smithy-lists, talisman-tables, weapon-tree, quest-rewards |
| 出典コーパス照合（汎用） | 4 | rewards, unlock-lists, size-variation, request-offer |

「記録のみ（不一致ではない）」として 4 件を検出した。いずれも**出典に忠実な意図的な正規化**であり欠陥ではない:

| テーブル | 内容 |
|---|---|
| kinsects | id 0 の出典 `"(None)"` を空文字に置換（SPEC §2「無い場合は空文字」に沿う） |
| talismans | 同上 |
| stages | stage 20 の ENUM_MAP_ は `極園`、本表は `極圏`（quest 本文由来の表記を採用） |
| stages | stage 21 の ENUM_MAP_ は `竜の墓場`、本表は `竜ノ墓場`（同上） |

> ENUM_MAP_ はエディタ側の列挙テーブルで、ゲーム内クエスト本文とは表記が揺れる。本表はクエスト本文を根拠に
> しており、**本表の表記が正しい**と判断した（`極圏` = Polar Field、`竜ノ墓場` = Wyvern's End）。

---

## 3. 項目別の詳細

### 3.1 構造 — PASS

`review/verify.py` により 42 CSV を全行検査。

- 1 列目 = `primary_key`: 42/42 一致
- 主キー重複: **0**（全テーブル）
- 主キーの空値: **0**
- 列名 snake_case ASCII: 全列 OK
- 列数とヘッダの不一致行: **0**
- UTF-8 BOM: 42/42 付与、CRLF: **0**（すべて LF）
- int 列の非整数値・ゼロ埋め: **0**
- bool 列（`yes`/`no`）: 違反 0
- 空値に `NULL`/`None`/`nan`/`undefined`/`?` 等の文字列: **0**

### 3.2 manifest 整合 — PASS

- `row_count`: 42/42 が実ファイルのデータ行数と一致
- `id_range`: 整数主キーの全テーブルで実測 min/max と一致
- `columns`: 全テーブルで CSV ヘッダと名前・順序とも一致
- `confidence`: 全件が `verified`/`derived`/`curated` のいずれか（verified 22 / derived 19 / curated 1）
- `source`: 空なし。パスは実在（`(定数名)` 注釈・glob を許容して解決）
- manifest 未収録の孤立 CSV: **0**
- テーブル id の重複（area 間含む）: **0**

### 3.3 出典整合 — PASS（重点）

各テーブルから seed 固定で 20 行を無作為抽出し、一次資料と突き合わせた。主な突合内容:

| テーブル | 突合した一次資料 | 結果 |
|---|---|---|
| items | `itemData_jpn.gmd`（name / desc 全文字一致） | 一致 |
| weapons | `weaponNNMsgData_jpn.gmd`（name / levels） | 一致 |
| armor | `armorSeriesData_jpn.gmd`（name / desc） | 一致 |
| skills | `SKILL_NAMES` + `skillTypeData_jpn.gmd`（name/desc は 2 文字列/件の対） | 一致 |
| skill-effects | `skillData_jpn.gmd` | 一致 |
| decorations | `JWL_NAMES`/`JWL_I_DS` + `itemData` | 一致 |
| talismans | `EQUIP_TALISMAN_NAMES`/`TALISMAN_RARITY` | 一致 |
| hunter-arts | refsrc `hunter-arts.csv` | 一致 |
| kinsects | `KINSECT_NAMES` + `insectData_jpn.gmd` | 一致 |
| weapon-types | `HUNT_WEAPONS`（`hunt_weapon_index` 経由。5 は欠番） | 一致 |
| palico-* | `PALICO_*_NAMES`/`_IDS` + `otWeaponData`/`otArmorData` | 一致 |
| item-categories | `itemCategoryTypeData_jpn.gmd` | 一致 |
| monsters | `monster-index.csv` + `MONSTER_HUNT_NAMES` | 一致 |
| stages | `ENUM_MAP_` + `quest-info.csv` の stage 分布 | 一致（表記差 2 件は記録のみ） |
| quests | refsrc `quest-index.csv` | 一致 |
| npcs | refsrc `npc-index.csv` + `NpcName_jpn.gmd` | 一致 |
| awards | refsrc `awards.csv` + `GC_Medal_jpn.gmd`（名前 0..131 / 説明 132..263） | 一致 |
| canteen | refsrc `canteen.csv` + `Kitchen_jpn.gmd` | 一致 |
| requests | refsrc `request-index.csv` + `activityData_jpn.gmd`（index i の名前 = 5*i 番目） | 一致 |
| provisions / arena / quest-monsters / quest-rewards / monster-carves / recipes | refsrc 各 CSV（複合キー内の順序も含む） | 一致 |

> 注: GMD の読み出しは「テキストブロック = ファイル末尾 `+0x20` バイト」という MHXX Switch の
> レイアウトに従った。`+0x1C` が 0 でないファイル（NpcName / GC_Medal / Kitchen / activityData）は
> key とテキストの間にハッシュ表が挟まるため、末尾基準でないと読めない。この点を自前実装で確認済み。

### 3.4 捏造チェック — PASS

- **ID 範囲外の値**: 0。既知の上限（items 0..2990 / monsters 1..137 / stages 1..104 / skills 0..205 など）と照合。
- **confidence の過大申告**: 検出なし。stages が `curated`（最も弱い）と自己申告しているのは誠実。
  items の `verified` は name/desc が実データ由来であるため妥当（name_en 空・category_id の意味未確定は
  notes_ja に明記されている）。
- **空であるべき値の捏造**: 出典が空の箇所に出典外の値は無い。逆に出典が `不明` の行は空文字化されており、
  SPEC §0.1「不明は空文字」に適合（monsters 106..112 の `不明`、134 の `Unknown[133]`）。
- **ステージ 10/15 の name_ja が空**: 依頼文から「闘技場」との区別が確定できないため**意図的に空**。
  推測で埋めていない点は SPEC §0.1 に忠実で、**正しい判断**。

### 3.5 TSV — PASS

`tools/build.py` の `tsv_cell()` は `[\t\r\n]+` を半角スペース 1 個に置換する。
本レビューも同じ規則で CSV から期待値を作り、42 TSV を全行比較した。

- 行数不一致: 0
- 内容不一致: 0
- BOM: 42/42 付与、CRLF: 0
- TSV 未生成: 0（equip 23 / world 19 すべて存在）

### 3.6 HTML / JS — PASS

| 検査 | 結果 |
|---|---|
| `node --check web/data.js`（7.32 MB） | OK |
| `node --check`（index.html の inline script 31 KB） | OK |
| `window.MHXX_ID_MEMO` の構造 | object / tables 42 件 / rows 取得可 |
| 外部 CDN・`fetch()`・`XMLHttpRequest` | 0（file:// で動作可） |
| 単一ファイル版 `web/mhxx-id-memo.html`（7.36 MB） | 外部参照 0・データ埋め込み確認 |

**SPEC §6 必須機能 1〜13 はすべて実装を確認**（コードレビュー + 実装箇所）:

| # | 機能 | 実装箇所 |
|---|---|---|
| 1 | 左サイドバー（グループ・件数） | `renderSidebar()`（area ごとに見出し + 行数） |
| 2 | 全列横断検索（大小・全半角無視） | `computeView()` + `norm()`（NFKC + toLowerCase、行を `\u0001` 連結キャッシュ） |
| 3 | 列フィルタ | `#fcol` / `#fval` |
| 4 | ソート（昇順→降順→解除） | `#thead` の click ハンドラ + `sortIdx()`（数値列は数値比較） |
| 5 | 行選択（全選択/表示中/解除/ページ一括） | `S.sel` + `selectAllRows()` / `selectViewRows()` / `#chk-page` |
| 6 | コピー（選択/表示中/全件 × TSV/CSV） | `buildMenus()` + `doCopy()`（clipboard API → execCommand フォールバック） |
| 7 | ダウンロード（.csv/.tsv、BOM 付き） | `download()`（`'\uFEFF' + text`） |
| 8 | 列表示切替 | `buildColMenu()` + `S.hidden` + `visibleCols()` |
| 9 | 行クリック詳細パネル（値コピー可） | `openDetail()` |
| 10 | テーブル定義パネル | `openDefinition()`（columns / source / confidence / notes） |
| 11 | 件数表示（全件/表示/選択） | `renderCounts()` |
| 12 | `/` で検索フォーカス / `Esc` でクリア | `keydown` ハンドラ |
| 13 | 大きいテーブル対応 | ページング（100/200/500/1000/2000/全件。既定 200） |

見た目も SPEC §6 準拠（ダークテーマ、ID は等幅、UI は日本語、900px 以下でサイドバー折りたたみ）。

**描画の目視確認**: `review/shot-main.png`（1600x1000）で、左サイドバーのグループ分け（装備・アイテム (23) / 世界・進行 (19)）と
各テーブルの件数、ツールバー（全選択 / 表示中を選択 / 選択解除 / コピー / ダウンロード / 列 / テーブル定義）、
ヘッダーの 2 段表示（列名 + 説明）、ページャ（1–200 / 5,836 行）、フッター（tables 42 / rows 91,406）を確認した。

> 注: このスクリーンショットは最終ビルド**前**のもので、フッターのデータ版が `sha256:0228a41a65e3…` と古い。
> UI 構造の確認用であり、最終データ版の証跡ではない。

**生成物間のデータ版一致**: `data/index.json` / `web/data.js` / `web/mhxx-id-memo.html` の
`meta.data_version` が 3 つとも `sha256:9f346b940d85…` で一致することを確認した（ビルドの取りこぼしなし）。

### 3.7 再現性 — PASS

`review/check_build.py --twice`:

- `python tools/build.py` → exit 0 / `status : OK`
- 生成物の内容変化: **0**（リポジトリ内の生成物が build.py の出力と一致）
- 2 回目実行の差分: **0**（冪等）
- `data/index.json`: 42 テーブル・91,406 行を列挙

### 3.8 README / docs — PASS

- `docs/table-definitions.md` / `docs/sources.md` / `docs/build-report.md`: build.py の自動生成で、
  42 テーブル / 91,406 行と実データに一致。
- `README.md`: 記述内容（使い方・再生成手順・検証内容）は実装と一致。コードフェンスも正常（4 箇所 = 2 ブロック）。
- `data/equip/NOTES.md` / `data/world/NOTES.md`: 存在し、抽出方法を記載。

---

## 4. 重点項目（lead 指定）の結果

### 4.1 ステージ ID（31 行） — PASS

- `name_ja` が空なのは **stage 10 / 15 の 2 行のみ**（依頼文から「闘技場」と区別不能）。
- `notes_ja` は **31/31 行が空でない**。うち 31/31 行が「n/m 件の依頼文に一致」形式の根拠を持つ。
  例: stage 1 `Harvest Tour 201「古代林の採集ツアー」（58/256 件の依頼文に一致）`
- 根拠件数は「その stage のクエストのうち、依頼文に当該地名が出た件数」で、分母（stage のクエスト数）と
  分子（一致件数）が併記されており、**検証可能な形で残っている**。妥当。
- 夜版 101..104 は `night=yes` / `base_stage_id = id-100` で一貫。

### 4.2 モンスター ID（137 行） — PASS

- refsrc `monster-index.csv` と **name_en 全 137 行一致**（不一致 0、欠番 0）。
- `MONSTER_HUNT_NAMES[monster_id - 1]` と **name_ja 全 137 行一致**（不一致 0）。
- `name_ja` が空なのは 106..112（出典が `不明`）と 134（出典が `Unknown[133]`）の 8 行のみで、
  SPEC §0.1 に適合。manifest の `notes_ja` にも明記されている。

### 4.3 クエスト（1,508 行） — PASS

- 主キー `quest_index` は **1..1508 で一意**（重複 0）。
- `quest_id` の重複は **1049 と 1050 が各 2 回**のみで、manifest `notes_ja` に
  「index 313/314 と 315/316 に現れるため一意でない」と明記されている。**扱いは正しい**。
- refsrc `quest-index.csv` と `quest_index` で全 1508 行突合し、**quest_id 不一致 0**。

### 4.4 連番 `row_id` 主キーのテーブル — PASS（8 テーブル）

lead の指定は「10 テーブル」だったが、実データで `primary_key = row_id` なのは **8 テーブル**。
8 テーブルすべてで `notes_ja` に複合キーの説明がある。

| テーブル | notes_ja の複合キー説明 |
|---|---|
| armor-skills | 「1 部位に最大 5 スキルが付くため複合キーになり、SPEC 準拠で連番 row_id を置いた」 |
| combinations | 「(item1, item2) は 183 行で重複なし」 |
| palico-actions | 「(kind, action_id) が複合キーなので連番 row_id を置いた」 |
| quest-monsters | 「自然キーは (quest_id, entry_no)」 |
| quest-rewards | 「自然キーは (quest_id, slot)（4897 行すべて一意）」 |
| smithy-lists | 「元の主キーは list という文字列なので連番 row_id を置き、list_name を残した」 |
| talisman-tables | 「自然キーは (kind, tier, skill_id)」※レビュー中に追記された |
| weapon-tree | 「1 武器が最大 5 本へ派生するため複合キーになり、連番 row_id を置いた」 |

### 4.5 TSV — PASS（§3.5 参照）

### 4.6 HTML 必須機能 1〜13 — PASS（§3.6 参照）

### 4.7 build.py 再現性 — PASS（§3.7 参照）

---

## 5. 指摘一覧

### Critical

なし。

### Major

| ID | 対象 | 内容 | 状態 |
|---|---|---|---|
| **M1** | `README.md` | コードフェンスが正しくない（バッククォート 3 個ではなく `@@` になっていた、4 箇所）。再生成コマンドとディレクトリ構成の 2 ブロックが崩れて表示されていた | **解決済み**（builder が修正。現在 `fence_bad=0` / 正常なフェンス 4） |
| **M2** | リポジトリ全体 | git 初期コミットが未実施（SPEC §7 DoD）。`git log` が「does not have any commits yet」 | **lead 対応待ち**（レビュー確定後に実施する工程。本レビューの判定には影響しない） |

### Minor

| ID | 対象 | 内容 | 状態 |
|---|---|---|---|
| m1 | kinsects / talismans / npcs | プレースホルダの扱いが不統一。kinsects・talismans は出典の `(None)` を空文字化、npcs は出典の `-` をそのまま保持（16 行）。どちらも出典に忠実だが方針が揃っていない | **未解決（任意）**。データ修正は不要、方針の 1 行明記を推奨 |
| m2 | talisman-tables | `notes_ja` に自然キー `(kind, tier, skill_id)` の明示がなかった | **解決済み**（analyst-equip が追記。notes_ja 526 字） |

### 情報（欠陥ではない）

- stages の stage 20 / 21 は `ENUM_MAP_` と表記が異なる（`極園`→`極圏`、`竜の墓場`→`竜ノ墓場`）。
  クエスト本文由来の本表が正しく、ENUM_MAP_ 側の揺れと判断。
- items の `name_en` は全行空（日本語 romfs のみ所持のため）。manifest `notes_ja` に明記されており、
  捏造しない方針として正しい。

---

## 6. 残作業・推奨

1. **M2（lead）**: git 初期コミットを実施（SPEC §4 で git 操作は lead の担当）。
   `.gitignore` は `__pycache__/` 等を除外済み。`review/_*.json` などレビュー中間ファイルの扱いも併せて判断されたい。
2. **m1（任意）**: プレースホルダ方針を `docs/sources.md` か各 `NOTES.md` に 1 行明記する
   （例: 「出典の `(None)` は空文字、`-` は出典どおり保持」）。データ修正は不要。

> データ（CSV / manifest）の値そのものに修正が必要な箇所は **0 件**。

---

## 7. 付録: レビュー用スクリプト

| ファイル | 役割 |
|---|---|
| `review/sources.py` | 一次資料のローダ（jp_names / refsrc / gamedata.rs / questfields.rs / romfs GMD / quest ARC） |
| `review/verify.py` | 構造・manifest 整合・TSV 一致・捏造チェック |
| `review/provenance.py` | 出典整合（seed 固定で各表 20 行を無作為抽出し一次資料と突合） |
| `review/fullcheck.py` | 重点項目の全行チェック（stages / monsters / quests / row_id 表） |
| `review/check_build.py` | 再現性（build.py を実行し生成物の差分と冪等性を確認） |
| `review/check_html.py` | HTML / JS（node --check、必須機能 1〜13 の実装痕跡） |
| `review/summary.py` | テーブル棚卸し（README / docs との突合用） |

### 検証の限界（正直な記載）

- ステージ名の一部（stage 10/15）は、依頼文から「闘技場」との区別が確定できないため空欄。これは仕様どおりの
  判断であり、**値を埋める根拠が存在しない**ことを本レビューでも確認した。
- クエスト名（`quests.name_ja`）は quest ARC 内の `questData_*_jpn` を出典とする。本レビューは同 ARC を
  自前で展開して出典コーパスを作り、値の存在を確認したが、全 1,508 件の逐一対応付けは行っていない
  （`quest_index` と `quest_id` の一致、および refsrc との突合で代替した）。
