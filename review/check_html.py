#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: HTML / JS (reviewer).

- node --check による構文検証 (index.html の inline script, data.js)
- data.js を Node で評価して構造を検証
- SPEC §6 必須機能 1〜13 の実装痕跡をコードから抽出
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

NODE = r"C:\Users\haruk\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"
REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"

issues = []


def add(sev, msg, ev=""):
    issues.append({"severity": sev, "message": msg, "evidence": ev})


def node_check(path):
    r = subprocess.run([NODE, "--check", path], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


SCRIPT_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.S | re.I)


def extract_scripts(html):
    out = []
    for m in SCRIPT_RE.finditer(html):
        attrs, body = m.group(1), m.group(2)
        if "src=" in attrs.lower():
            out.append(("external", attrs.strip(), None))
        else:
            out.append(("inline", attrs.strip(), body))
    return out


FEATURES = [
    (1, "左サイドバー: テーブル一覧 (グループ分け・件数表示)",
     [r"sidebar", r"nav", r"table-list|tableList|tables-nav"]),
    (2, "検索ボックス: 全列横断の部分一致 (大小無視・日本語可)",
     [r"toLowerCase\(\)", r"search|query"]),
    (3, "列フィルタ: 列選択 + 値の絞り込み",
     [r"filter", r"column"]),
    (4, "ソート: ヘッダークリックで昇順/降順",
     [r"sort", r"asc|desc"]),
    (5, "行選択: チェックボックス / 全選択 / フィルタ結果のみ",
     [r"checkbox", r"selectAll|select-all|全選択"]),
    (6, "コピー: 選択行/表示中/全件 を TSV/CSV でクリップボードへ",
     [r"clipboard|execCommand\('copy'\)|navigator\.clipboard", r"tsv", r"csv"]),
    (7, "ダウンロード: .csv / .tsv 保存 (BOM 付き)",
     [r"download|Blob", r"\\ufeff|\\\\ufeff|\\uFEFF"]),
    (8, "列表示切替 (チェックボックス)",
     [r"visibleCols|S\.hidden|列の表示切替|hiddenColumns"]),
    (9, "行クリックで詳細パネル (全列縦表示・各値コピー)",
     [r"detail|drawer|panel"]),
    (10, "テーブル定義パネル (manifest の columns/source/confidence)",
     [r"confidence", r"source"]),
    (11, "件数表示 (全件 / フィルタ後 / 選択中)",
     [r"count|件"]),
    (12, "キーボード: / で検索フォーカス, Esc でクリア",
     [r"'/'\s*|\"/\"|key === '/'|keydown"]),
    (13, "大きいテーブル対応 (ページング or 仮想スクロール)",
     [r"page|paging|virtual|slice\("]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    a = ap.parse_args()
    web = os.path.join(a.repo, "web")
    idx = os.path.join(web, "index.html")
    dat = os.path.join(web, "data.js")

    print("=" * 78)
    print("HTML / JS 検証")
    print("=" * 78)

    if not os.path.exists(idx):
        add("Critical", "web/index.html が存在しない", idx)
    else:
        html = open(idx, encoding="utf-8").read()
        print("index.html: %d bytes, %d 行" % (len(html), html.count("\n") + 1))
        # 外部リソース禁止 (file:// で動くこと)
        for pat, label in ((r"<script[^>]+src\s*=\s*[\"']https?:", "外部 script"),
                           (r"<link[^>]+href\s*=\s*[\"']https?:", "外部 stylesheet"),
                           (r"\bfetch\s*\(", "fetch() 呼び出し"),
                           (r"XMLHttpRequest", "XMLHttpRequest")):
            for m in re.finditer(pat, html, re.I):
                add("Critical", "file:// で動かない可能性: %s" % label,
                    html[max(0, m.start() - 40):m.end() + 40].replace("\n", " "))
        scripts = extract_scripts(html)
        print("script タグ: %d (inline=%d)" % (len(scripts), sum(1 for s in scripts if s[0] == "inline")))
        tmpdir = tempfile.mkdtemp(prefix="mhxx_rev_")
        for i, (kind, attrs, body) in enumerate(scripts):
            if kind == "external":
                src = re.search(r"src\s*=\s*[\"']([^\"']+)", attrs)
                tgt = src.group(1) if src else "?"
                if tgt.startswith("http"):
                    add("Critical", "外部 script 参照", tgt)
                else:
                    p = os.path.join(web, tgt)
                    if not os.path.exists(p):
                        add("Critical", "script src の実体が無い", tgt)
                continue
            if not body.strip():
                continue
            tp = os.path.join(tmpdir, "inline_%d.js" % i)
            open(tp, "w", encoding="utf-8").write(body)
            rc, out = node_check(tp)
            if rc != 0:
                add("Critical", "inline script の構文エラー (#%d)" % i, out[:500])
            else:
                print("  inline script #%d: node --check OK (%d bytes)" % (i, len(body)))

    if not os.path.exists(dat):
        add("Critical", "web/data.js が存在しない", dat)
    else:
        rc, out = node_check(dat)
        if rc != 0:
            add("Critical", "data.js の構文エラー", out[:500])
        else:
            print("data.js: node --check OK (%d bytes)" % os.path.getsize(dat))
        # 構造検証
        probe = r'''
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const sandbox = { window: {} };
const fn = new Function('window', src);
fn(sandbox.window);
const d = sandbox.window.MHXX_ID_MEMO;
if (!d) { console.log(JSON.stringify({error: 'window.MHXX_ID_MEMO が未定義'})); process.exit(0); }
const out = { keys: Object.keys(d) };
const tables = d.tables || (Array.isArray(d) ? d : null);
out.shape = Array.isArray(d) ? 'array' : typeof d;
out.tableCount = tables ? tables.length : null;
if (tables && tables.length) {
  out.sample = JSON.parse(JSON.stringify(tables[0])).constructor === Object ? Object.keys(tables[0]) : null;
  out.ids = tables.map(t => t.id).slice(0, 40);
  out.rowCounts = tables.map(t => [t.id, (t.rows||[]).length]).slice(0, 40);
}
console.log(JSON.stringify(out));
'''
        pp = os.path.join(tempfile.mkdtemp(prefix="mhxx_probe_"), "probe.js")
        open(pp, "w", encoding="utf-8").write(probe)
        r = subprocess.run([NODE, pp, dat], capture_output=True, text=True)
        txt = (r.stdout + r.stderr).strip()
        print("data.js 構造: %s" % txt[:1200])
        try:
            info = json.loads(txt.splitlines()[-1])
            if info.get("error"):
                add("Critical", "data.js 構造不正", info["error"])
            elif not info.get("tableCount"):
                add("Major", "data.js にテーブルが入っていない", txt[:300])
            else:
                print("  tables=%d" % info["tableCount"])
        except Exception:
            add("Major", "data.js の構造を判定できなかった", txt[:300])

    # 必須機能の痕跡
    print("-" * 78)
    print("SPEC §6 必須機能の実装痕跡")
    print("-" * 78)
    body = ""
    if os.path.exists(idx):
        body = open(idx, encoding="utf-8").read()
    if not body:
        print("  (index.html 不在のため機能チェックは省略)")
    for no, label, pats in (FEATURES if body else []):
        hits = []
        for p in pats:
            if re.search(p, body, re.I):
                hits.append(p)
        status = "痕跡あり" if hits else "痕跡なし"
        print("  %2d. %-52s %s (%s)" % (no, label, status, ",".join(hits) if hits else "-"))
        if not hits:
            add("Major", "必須機能 %d の実装痕跡が見つからない: %s" % (no, label), idx)

    print("-" * 78)
    for i in issues:
        print("[%s] %s" % (i["severity"], i["message"]))
        if i["evidence"]:
            print("        %s" % i["evidence"][:300])
    print("指摘: %d" % len(issues))
    return 1 if any(i["severity"] in ("Critical", "Major") for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
