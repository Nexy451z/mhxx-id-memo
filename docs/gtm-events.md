# GTM / GA4 ページ内イベント

このビューアは Google Tag Manager（コンテナ `GTM-T9NHWQW4`）を設置済みで、
ページ内の操作を `dataLayer.push({ event: 'mhxx_xxx', ... })` で送ります。

| 項目 | 値 |
|---|---|
| GTM コンテナ | `GTM-T9NHWQW4` |
| GA4 測定 ID | `G-QPCD4BGBL8` |
| GA4 プロパティ | mhxx-id-memo |
| サイト | <https://nexy451z.github.io/mhxx-id-memo/> |

> サイト側に `gtag.js` を直接貼ると GTM と二重計測になります。**GA4 は GTM 経由で設定**してください。

- 実装: `web/index.html` の `track(name, params)` ヘルパー
- すべての呼び出しは `try/catch` で包んであり、**計測が失敗してもアプリの挙動は変わりません**
- イベント名は `mhxx_` 接頭辞 + snake_case（40 文字以内）

## プライバシー方針

- **検索文字列そのものは送りません**（`query_len` = 文字数のみ）
- **表の行の中身（セルの値）は送りません**。件数・ID・種別だけ送ります
- 入力フォームの値、クリップボードの中身、ダウンロードしたデータは一切送りません
- Cookie / localStorage の値を送ることもありません

## イベント一覧

| # | イベント名 | パラメータ | 発火タイミング |
|---:|---|---|---|
| 1 | `mhxx_ready` | `tables` `rows` `mode` | 最初のテーブルが画面に描画されたとき（1 セッション 1 回） |
| 2 | `mhxx_table_select` | `table_id` `table_title` `rows` | サイドバーでテーブルを切り替えたとき |
| 3 | `mhxx_mode_change` | `mode` | 「一覧 / メモリ配置」を切り替えたとき（`list` / `mem`） |
| 4 | `mhxx_theme_change` | `theme` | 🌙 / ☀ でテーマを切り替えたとき（`light` / `dark`） |
| 5 | `mhxx_search` | `query_len` `results` `table_id` | 検索ボックスの入力が落ち着いたとき（デバウンス 110ms 後） |
| 6 | `mhxx_sort` | `table_id` `column` `dir` | ヘッダーをクリックしてソートしたとき（`asc` / `desc` / `none`） |
| 7 | `mhxx_copy` | `scope` `format` `rows` `table_id` | コピーを実行したとき（`scope` = `sel`/`view`/`all`、`format` = `tsv`/`csv`） |
| 8 | `mhxx_download` | `scope` `format` `rows` `table_id` | ダウンロードを実行したとき |
| 9 | `mhxx_detail_open` | `table_id` `row_index` | 行をクリックして詳細パネルを開いたとき |
| 10 | `mhxx_memory_pick` | `category` `name` `type` `id` | メモリ配置モードで装備を選んだとき |
| 11 | `mhxx_memory_copy` | `bytes` `category` | メモリ配置モードで hex をコピーしたとき |

### パラメータの意味

| パラメータ | 型 | 内容 |
|---|---|---|
| `tables` | number | 収録テーブル数（42） |
| `rows` | number | 総行数、またはコピー/ダウンロードした行数 |
| `mode` | string | `list` / `mem` |
| `theme` | string | `light` / `dark` |
| `table_id` | string | テーブル ID（例: `armor`） |
| `table_title` | string | テーブル名（例: 防具） |
| `query_len` | number | 検索文字列の**文字数**（文字列そのものは送らない） |
| `results` | number | 検索後のヒット件数 |
| `column` | string | ソートした列名（例: `armor_id`） |
| `dir` | string | `asc` / `desc` / `none` |
| `scope` | string | `sel`（選択行）/ `view`（表示中）/ `all`（全件） |
| `format` | string | `tsv` / `csv` |
| `row_index` | number | 元データでの行番号（0 始まり） |
| `category` | string | `armor` / `weapon` / `talisman` |
| `name` | string | 装備名（例: ベルダーターバン） |
| `type` | number | レコードの type（1..5 防具 / 6 護石 / 7..21 武器） |
| `id` | number | series_id / weapon_index / kind |
| `bytes` | number | コピーした hex のバイト数 |

## GA4 側の設定

### 1. カスタムイベントとして受け取る

GTM で **GA4 イベントタグ**を作成し、トリガーを「カスタムイベント」で `mhxx_.*`（正規表現一致）にします。
イベント名は `{{Event}}` をそのまま使えます。

送信パラメータには上表のパラメータを追加してください（値は `{{DLV - table_id}}` のようなデータレイヤー変数で参照）。

### 2. カスタムディメンションの登録（必須）

**GA4 は自動収集していないパラメータをそのままではレポートで見られません。**
管理 → カスタム定義 → カスタムディメンションで、次のパラメータを登録してください。

| パラメータ名 | スコープ | 説明 |
|---|---|---|
| `table_id` | イベント | テーブル ID |
| `table_title` | イベント | テーブル名 |
| `scope` | イベント | コピー/ダウンロードの範囲 |
| `format` | イベント | `tsv` / `csv` |
| `category` | イベント | メモリ配置のカテゴリ |
| `mode` | イベント | `list` / `mem` |
| `bytes` | イベント | コピーした hex のバイト数 |

数値パラメータ（`rows` `tables` `query_len` `results` `row_index` `type` `id`）は
**カスタム指標**（管理 → カスタム定義 → カスタム指標）として登録すると集計・平均が出せます。

### 3. おすすめの探索（Explore）例

- **テーブル別の利用状況**: ディメンション `table_title`、指標 `イベント数` で `mhxx_table_select` を集計
- **コピー vs ダウンロード**: ディメンション `format` `scope` で `mhxx_copy` / `mhxx_download` を比較
- **検索の使われ方**: `mhxx_search` の `query_len` 平均と `results` 平均
- **メモリ配置モードの利用率**: `mhxx_mode_change` の `mode` 別セッション数

## 実装メモ

### track ヘルパー

```js
function track(name, params) {
  try {
    window.dataLayer = window.dataLayer || [];
    var o = { event: name };
    if (params) {
      for (var k in params) {
        if (Object.prototype.hasOwnProperty.call(params, k)) { o[k] = params[k]; }
      }
    }
    window.dataLayer.push(o);
  } catch (e) { /* 計測失敗は無視 */ }
}
```

### gtag 互換シム

GA4 の `gtag()` 形式でも送れるように、GTM スニペットの直後に次を置いています。

```js
window.gtag = window.gtag || function () {
  (window.dataLayer = window.dataLayer || []).push(arguments);
};
```

GTM 公式スニペットが作る `dataLayer` とは共存します（`gtm.start` などの既存エントリはそのまま残ります）。

### 動作確認

ブラウザのコンソールで次を実行すると、送信されたイベントを確認できます。

```js
dataLayer.filter(function (e) { return e && String(e.event).indexOf('mhxx_') === 0; });
```
