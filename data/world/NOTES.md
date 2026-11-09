# data/world — 世界・進行系 ID テーブル

Monster Hunter XX (Nintendo Switch) の「世界・進行」系 ID の一覧。
すべて **実データからの抽出** で、値の捏造はしていない。不明は空文字。

- 生成: `python tools/extract_world_tables.py`
- 検証: `python tools/extract_world_verify.py`
- テーブル数 **19**（第 1 バッチ 13 + 第 2 バッチ 6）/ 総行数 **58,277**

---

## 1. テーブル一覧

### 第 1 バッチ（13 テーブル / 42,739 行）

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

### 第 2 バッチ（6 テーブル / 15,538 行）

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

## 2. 主キーについて（SPEC「1 列目 = 主キー」）

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

## 3. 出典

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

### .gmd の読み方（この dump の実測）

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

### .arc（クエスト書庫）の読み方

```
+0x00 'ARC\0'
+0x06 u16 エントリ数
+0x0C エントリ 0x50 バイト: 名前 64 B / u32 圧縮サイズ / u32 展開サイズ / u32 オフセット / u32 未使用
     圧縮サイズ != 展開サイズ (& 0x1FFFFFFF) または先頭 0x78 なら zlib
```

`arc/quest/qNNNNNNN.arc` の NNNNNNN はクエスト ID を 7 桁ゼロ埋めしたもの
（例 `q0100304.arc` → quest 100304）。

---

## 4. 最重要課題だったステージ ID の解決

### 4.1 stage 列の値域

`quest-info.csv` の `stage` 列は **1..27 と 101..104 の 31 種**。

### 4.2 出どころは questData の .mib +0x14

クエスト書庫の `quest\questData\questData_NNNNNNN`（拡張子なし = .mib、249 B）
の **+0x14 が map_id**（mhnx の `arc-mib` も同じ名前で出す）。

**全 1,855 クエストの書庫を解析して突き合わせた結果、quest-info.csv の 1,512 行と
stage 列が 1,512/1,512 で完全一致（不一致 0）**。これで `stage` 列が
ステージ ID であることが確定した。

### 4.3 1..27 は arc/stage の m01d..m27d

`romfs/nativeNX/arc/stage/` に `m01d`..`m27d` の 27 フォルダ、
`arc/stage/map_com/` に `m00.arc`..`m27.arc` がある。
stage 1..27 が m01..m27 に対応する。**101..104 は 1..4 の夜版**（4.4 の日本語名が同一）。

### 4.4 英語名はゲーム自身のクエストボード表記

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

### 4.5 日本語名はクエスト本文から（根拠件数を各行に記載）

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

### 4.6 名前を空にした 2 ステージ（捏造禁止のため）

| stage | name_en | 状況 |
|---:|---|---|
| 10 | Volcano Slayground (V. Slayground) | 依頼文は「闘技場」11/20・「立体闘技場」7/20 のみ。stage 9「闘技場」との区別がこの dump だけでは確定できない |
| 15 | Frozen Slayground (F. Slayground) | 依頼文は「闘技場」4/12 のみ。同上 |

英語名はゲームの message table の値なので確か。日本語名は **空文字**（SPEC 0 章「不明は空文字」）。

### 4.7 英語名と日本語名が 1 対 1 でない例

- stage 17: `name_en` = Forlorn Arena（ゲームの表記そのまま）/
  `name_ja` = 塔（依頼文 20/41 件）。両者は同じ ID でも名前が対応しない。
  `notes_ja` に明記した。
- stage 16: Sanctuary / 禁足地、stage 20: Polar Field / 極圏 も同様に、
  英語名はゲームの表記・日本語名は本文の地名という別ソース。

---

## 5. 日本語名の出どころ（ステージ以外）

| テーブル | 列 | 出どころ | 対応の確認方法 |
|---|---|---|---|
| monsters | name_ja | `gamedata.rs` の `MONSTER_HUNT_NAMES`（137 件・セーブ順） | 件数一致。106..112 は「不明」、134 は "Unknown[133]" なので空にした |
| npcs | name_ja | `NpcName_jpn.gmd` | bit 0 = ベルナ村の村長 = Bherna Chief、188 件すべて意味が一致 |
| awards | name_ja / desc_ja | `GC_Medal_jpn.gmd` | 264 件 = 132 名 + 132 説明。bit 0 の説明が「村の★１と★２の全クエストをクリアした証」で一致 |
| requests | name_ja | `activityData_jpn.gmd` | 920 件 = 184 レコード × 5。index i の名前は 5*i 番目 |
| requests / quest-unlock / rotating-quests / request-offer | quest_name_ja | `questData_*_jpn` | 対象クエストのタイトル（0 番目） |
| canteen | name_ja | `Kitchen_jpn.gmd` | 下記の並び |

### Kitchen_jpn.gmd の並び（144 件の対応）

```
食材: 各カテゴリ先頭 7 件が 103..133（肉 103-109 / 穀物 110-116 / 野菜 117-123 /
      魚 124-130 / 飲み物 131-133）、XX で追加された 14 件が 251..264
料理: 0..76 が 134..210、77..98 が 265..286
```

全 144 件を名前の意味で確認した（例 dish 0 Dauntless Pasta = 屋台の根性まかない飯 /
dish 98 Ultimate Rice = 屋台の究極まかない飯 / 食材 44 Chat-eau de Nya = ニャトーロマーネ）。

---

## 6. 第 2 バッチの補足

### 6.1 `rewards` — `quest-rewards.rem_id` の解決先

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

### 6.2 `quest-unlock`

`quest_id` は **1,506 件で、`quests.csv` の quest_id 集合と完全一致**。
`rule` は `flag:396` / `cleared:11404` / `hr:7` /
`village_star:6 AND ...` の形。空欄 204 件は条件なし（最初から出る）。

### 6.3 `unlock-lists`

自然キー `(map, bit)` は 1,418 行すべて一意。map は 38 種:

`lab`(研究施設) / `song`(ジュークボックス) / `armory:1..21`(武具屋) /
`shop:0,1` / `trader:costumes,delivery,items0,items1,scenes,words` /
`coin` / `combos` / `costume` / `events` / `gallery` /
`milestones` / `notes2` / `supply` / `tips`

`need` は `start`(最初から) / `dlc`(配信) / `never`(未使用) /
`v2|h2`(村★2 または集会所★2) / `q806&q10768`(両方クリア) の形。
`target_id` は解放される装備・アイテム ID（1,074 行が持つ）。

### 6.4 `size-variation`

ゲームの `em_size_yure_data`（52 テーブル）。クエストの boss 枠が
`size_table` を指し、サイズ = クエストの size% × rate。
自然キー `(size_table, rate)` は 1,385 行すべて一意。rate は 88..130。

### 6.5 `rotating-quests`

セーブの `base + 0x504B` のビット（次に 1 クエストクリアするまで有効）。
ビット 0..50 の 51 件、quest_id はすべて quests.csv に存在する。

### 6.6 `request-offer`

NPC の会話データから読んだ「この依頼を出す条件」。自然キー
`(request_index, npc_file, npc_bit, talk_line)` は 186 行すべて一意。

`request_index` は 4 組 (28, 135, 149, 150) が 2 行ずつある:
28 / 149 / 150 は赤鬼・黒鬼の 2 人が同じ依頼を出す、135 は同じ NPC が別の会話行で出す。
`quest_id` が空の行は納品依頼（kind 1）でクエストを持たない。

---

## 7. 自己検証

### 7.1 実行

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

### 7.2 検証項目（222 チェック）

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

### 7.3 WARN 3 件について（失敗ではない）

1. **`rewards` の rem 230073 が 104%** — ゲーム側の実データが 104。
   検証側の仮定（常に 100）の方が外れている。refsrc の `quest.rs` にも
   既知の例外として書かれている。
2. **`quest-monsters` 18 件 / `quest-rewards` 9 件が
   「quests に無い quest_id」** — この 2 表は **全 1,855 クエストファイル**由来、
   `quests.csv` は **セーブのクエストリスト 1,508 行**（SPEC の出典どおり）
   なので母集合が違う。クエストファイルはあるがリストに載っていない
   イベント／ダミークエストが該当する。データの誤りではない。

---

## 8. 未解決点・残課題

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
