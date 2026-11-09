#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO ビルドツール。

    python tools/build.py                 # 全部生成（単一ファイル版も含む）
    python tools/build.py --single-file   # 単一ファイル版を明示的に生成
    python tools/build.py --no-single-file
    python tools/build.py --root <dir>    # テスト用に対象リポジトリを差し替え
    python tools/build.py --stamp         # meta に生成時刻を入れる（既定は入れない = 冪等）

出力:
    data/index.json                 全テーブルカタログ
    data/<area>/<name>.tsv          CSV から生成（タブ・改行は半角スペースに置換）
    web/data.js                     window.MHXX_ID_MEMO = {...}
    web/mhxx-id-memo.html           データ埋め込みの自己完結版
    docs/table-definitions.md       列定義（自動生成）
    docs/sources.md                 出典と抽出方法（自動生成）
    docs/build-report.md            検証レポート（自動生成）
    README.md の <!-- BEGIN:TABLES --> ブロック

再実行しても同じ入力なら同じ出力になる（--stamp を付けた場合を除く）。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- 定数

AREAS = (("equip", "装備・アイテム"), ("world", "世界・進行"))
AREA_JA = dict(AREAS)
BUILD_VERSION = 1
CSV_ENCODING = "utf-8-sig"
DATA_TAG = '<script src="data/index.js" id="mhxx-index"></script>'
README_BEGIN = "<!-- BEGIN:TABLES"
README_END = "<!-- END:TABLES -->"
VALID_TYPES = ("int", "str", "float", "bool")
VALID_CONFIDENCE = ("verified", "derived", "curated")
BT = chr(96)  # バッククォート

_TSV_BAD = re.compile(r"[\t\r\n]+")


# ---------------------------------------------------------------- レポート

class Reporter:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.lines = []

    def error(self, msg):
        self.errors.append(msg)
        self.lines.append("ERROR  " + msg)

    def warn(self, msg):
        self.warnings.append(msg)
        self.lines.append("WARN   " + msg)

    def ok(self, msg):
        self.lines.append("OK     " + msg)


# ---------------------------------------------------------------- 小道具

def rel(path, root):
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def tsv_cell(value):
    if value is None:
        return ""
    return _TSV_BAD.sub(" ", str(value))


def fmt_int(n):
    try:
        return "{:,}".format(int(n))
    except (TypeError, ValueError):
        return str(n)


def fmt_range(rng):
    if not rng or not isinstance(rng, (list, tuple)) or len(rng) != 2:
        return "—"
    return "{0}–{1}".format(rng[0], rng[1])


def code(s):
    return BT + str(s) + BT


def demote_headings(text, levels=2):
    """Markdown の見出しを levels 段下げる。

    NOTES.md を docs/sources.md の "###" セクションに埋め込むとき、
    H1 がそのまま入ると目次構造が壊れるため。コードフェンス内は触らない。
    """
    out = []
    in_fence = False
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("```") or s.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                hashes = len(stripped) - len(stripped.lstrip("#"))
                rest = stripped[hashes:]
                if 1 <= hashes <= 6 and (rest == "" or rest[0] in " \t"):
                    out.append("#" * min(6, hashes + levels) + rest)
                    continue
        out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------- CSV / TSV

def read_csv_table(path):
    """CSV を読む。返り値 (header, rows)。末尾の完全空行は落とす。"""
    with path.open("r", encoding=CSV_ENCODING, newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    header = [h.strip() for h in rows[0]]
    body = rows[1:]
    while body and not any((c or "").strip() for c in body[-1]):
        body.pop()
    return header, body


def write_tsv(path, header, rows):
    """TSV を書く。

    値内のタブ・改行は tsv_cell() で半角スペースに置換済みなので、単純に join する。
    csv モジュールは QUOTE_NONE でも quotechar を特別扱いするため使わない
    （値に引用符が入っていると escapechar 必須エラーになる）。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="\n") as f:
        f.write("\t".join(tsv_cell(c) for c in header) + "\n")
        for r in rows:
            f.write("\t".join(tsv_cell(c) for c in r) + "\n")


# ---------------------------------------------------------------- manifest

def load_manifest(root, area, report):
    """1 エリア分の manifest を読む。壊れていれば空リストを返して警告。"""
    mpath = root / "data" / area / "_manifest.json"
    if not mpath.is_file():
        report.warn("{0} がありません（{1} はスキップ）".format(rel(mpath, root), area))
        return []
    try:
        raw = read_json(mpath)
    except Exception as exc:
        report.error("{0} を JSON として読めません: {1}".format(rel(mpath, root), exc))
        return []
    if not isinstance(raw, dict):
        report.error("{0}: ルートがオブジェクトではありません".format(rel(mpath, root)))
        return []
    tables = raw.get("tables")
    if not isinstance(tables, list):
        report.error("{0}: tables 配列がありません".format(rel(mpath, root)))
        return []
    out = []
    for i, entry in enumerate(tables):
        if not isinstance(entry, dict):
            report.error("{0}: tables[{1}] がオブジェクトではありません".format(rel(mpath, root), i))
            continue
        if not entry.get("id"):
            report.error("{0}: tables[{1}] に id がありません".format(rel(mpath, root), i))
            continue
        out.append(entry)
    return out


def normalize_columns(entry, header, report, where):
    """manifest の columns を検証し、CSV ヘッダーと突き合わせる。"""
    cols = entry.get("columns")
    if not isinstance(cols, list) or not cols:
        report.warn("{0}: columns が無いので CSV ヘッダーから生成します".format(where))
        return [{"name": h, "type": "str", "desc_ja": "", "desc_en": ""} for h in header]

    out = []
    for c in cols:
        if not isinstance(c, dict) or not c.get("name"):
            report.warn("{0}: columns の要素に name が無いので無視します".format(where))
            continue
        ctype = c.get("type") or "str"
        if ctype not in VALID_TYPES:
            report.warn("{0}: 列 {1} の type '{2}' は未知。str として扱います".format(where, c["name"], ctype))
            ctype = "str"
        out.append({
            "name": str(c["name"]),
            "type": ctype,
            "desc_ja": str(c.get("desc_ja") or ""),
            "desc_en": str(c.get("desc_en") or ""),
        })

    names = [c["name"] for c in out]
    if header and names != header:
        only_manifest = [n for n in names if n not in header]
        only_csv = [h for h in header if h not in names]
        if only_manifest or only_csv:
            report.warn(
                "{0}: manifest の columns と CSV ヘッダーが一致しません (manifest のみ: {1} / CSV のみ: {2})".format(
                    where, only_manifest, only_csv)
            )
        else:
            report.warn("{0}: columns の並び順が CSV と違います（CSV 側の順に合わせます）".format(where))
        by_name = {}
        for c in out:
            by_name[c["name"]] = c
        fixed = []
        for h in header:
            if h in by_name:
                fixed.append(by_name[h])
            else:
                fixed.append({"name": h, "type": "str", "desc_ja": "", "desc_en": ""})
        out = fixed
    return out


# ---------------------------------------------------------------- テーブル構築

def build_table(root, area, entry, report):
    tid = str(entry.get("id", "")).strip()
    where = "{0}/{1}".format(area, tid)
    fname = entry.get("file")
    if not fname:
        report.error("{0}: file がありません".format(where))
        return None

    csv_path = root / "data" / area / str(fname)
    if not csv_path.is_file():
        report.warn("{0}: {1} がまだありません（スキップ）".format(where, rel(csv_path, root)))
        return None

    header, rows = read_csv_table(csv_path)
    if not header:
        report.error("{0}: {1} が空です".format(where, rel(csv_path, root)))
        return None

    columns = normalize_columns(entry, header, report, where)

    ncol = len(header)
    ragged = 0
    fixed_rows = []
    for r in rows:
        if len(r) == ncol:
            fixed_rows.append(["" if c is None else str(c) for c in r])
        else:
            ragged += 1
            if len(r) > ncol:
                fixed_rows.append([str(c) for c in r[:ncol]])
            else:
                fixed_rows.append([str(c) for c in r] + [""] * (ncol - len(r)))
    if ragged:
        report.warn("{0}: 列数がヘッダーと違う行が {1} 行ありました（詰めました）".format(where, ragged))
    rows = fixed_rows

    pk = str(entry.get("primary_key") or header[0])
    if pk not in header:
        report.warn("{0}: primary_key '{1}' がヘッダーに無いので 1 列目を使います".format(where, pk))
        pk = header[0]
    if header and pk != header[0]:
        report.warn("{0}: 主キー '{1}' が 1 列目ではありません".format(where, pk))
    pk_idx = header.index(pk)

    seen = {}
    dups = []
    dup_count = 0
    for i, r in enumerate(rows):
        k = r[pk_idx]
        if k in seen:
            dup_count += 1
            if len(dups) < 8:
                dups.append("{0}(行 {1} と {2})".format(k, seen[k] + 2, i + 2))
        else:
            seen[k] = i
    if dup_count:
        report.error("{0}: 主キー {1} に重複 {2} 件: {3}".format(where, pk, dup_count, ", ".join(dups)))

    empty_pk = 0
    for r in rows:
        if not r[pk_idx].strip():
            empty_pk += 1
    if empty_pk:
        report.error("{0}: 主キー {1} が空の行が {2} 件".format(where, pk, empty_pk))

    declared = entry.get("row_count")
    if declared is None:
        report.warn("{0}: row_count が未設定（実測 {1} 行）".format(where, len(rows)))
    else:
        try:
            if int(declared) != len(rows):
                report.error("{0}: row_count 不一致 manifest={1} 実測={2}".format(where, declared, len(rows)))
        except (TypeError, ValueError):
            report.warn("{0}: row_count が整数ではありません: {1}".format(where, declared))

    types = {}
    for c in columns:
        types[c["name"]] = c["type"]
    computed_range = None
    if types.get(pk) == "int":
        nums = []
        bad = 0
        for r in rows:
            v = r[pk_idx].strip()
            if v == "":
                continue
            try:
                nums.append(int(v))
            except ValueError:
                bad += 1
        if bad:
            report.warn("{0}: 主キー {1} に整数でない値が {2} 件".format(where, pk, bad))
        if nums:
            computed_range = [min(nums), max(nums)]
    declared_range = entry.get("id_range")
    if computed_range is not None:
        if declared_range is None:
            report.warn("{0}: id_range が未設定（実測 {1}）".format(where, computed_range))
        elif list(declared_range) != computed_range:
            report.warn("{0}: id_range 不一致 manifest={1} 実測={2}".format(
                where, list(declared_range), computed_range))

    confidence = entry.get("confidence")
    if confidence not in VALID_CONFIDENCE:
        report.warn("{0}: confidence '{1}' は未知（verified/derived/curated）".format(where, confidence))

    source = entry.get("source")
    if isinstance(source, str):
        source = [source]
    if not isinstance(source, list) or not source:
        report.warn("{0}: source が空です".format(where))
        source = []
    else:
        cleaned = []
        for s in source:
            if isinstance(s, str) and s.strip():
                cleaned.append(s)
            else:
                report.warn("{0}: source に空要素があります".format(where))
        source = cleaned

    report.ok("{0}: {1} 行 / {2} 列 / 主キー {3}".format(where, len(rows), len(columns), pk))

    return {
        "id": tid,
        "area": area,
        "area_ja": AREA_JA.get(area, area),
        "title_ja": str(entry.get("title_ja") or tid),
        "title_en": str(entry.get("title_en") or ""),
        "file": "data/{0}/{1}".format(area, fname),
        "tsv": "data/{0}/{1}".format(area, Path(str(fname)).with_suffix(".tsv").name),
        "primary_key": pk,
        "row_count": len(rows),
        "id_range": computed_range,
        "columns": columns,
        "source": source,
        "confidence": confidence if confidence in VALID_CONFIDENCE else "curated",
        "notes_ja": str(entry.get("notes_ja") or ""),
        "notes_en": str(entry.get("notes_en") or ""),
        "rows": rows,
        "_csv_path": csv_path,
    }


# ---------------------------------------------------------------- 生成物

def compute_data_version(root, files):
    h = hashlib.sha256()
    for p in sorted(files, key=lambda x: rel(x, root)):
        h.update(rel(p, root).encode("utf-8"))
        h.update(b"\0")
        try:
            h.update(p.read_bytes())
        except OSError:
            h.update(b"<missing>")
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


def build_index(tables, meta):
    catalog = []
    for t in tables:
        catalog.append({
            "id": t["id"],
            "area": t["area"],
            "area_ja": t["area_ja"],
            "title_ja": t["title_ja"],
            "title_en": t["title_en"],
            "file": t["file"],
            "tsv": t["tsv"],
            "primary_key": t["primary_key"],
            "row_count": t["row_count"],
            "id_range": t["id_range"],
            "columns": t["columns"],
            "source": t["source"],
            "confidence": t["confidence"],
            "notes_ja": t["notes_ja"],
            "notes_en": t["notes_en"],
        })
    return {
        "version": BUILD_VERSION,
        "generator": "tools/build.py",
        "description": "Monster Hunter XX (Nintendo Switch) ID メモ — 全テーブルカタログ",
        "meta": meta,
        "areas": meta["areas"],
        "tables": catalog,
    }


def _js_literal(obj):
    """JSON を JS リテラルとして安全に埋め込む（</ と U+2028/2029 を退避）。"""
    text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    text = text.replace("</", "<\\/")
    text = text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return text


def build_index_js(tables, meta):
    """web/data/index.js — meta + テーブル一覧 + 列定義のみ。行データは含めない。"""
    catalog = []
    for t in tables:
        catalog.append({
            "id": t["id"],
            "area": t["area"],
            "area_ja": t["area_ja"],
            "title_ja": t["title_ja"],
            "title_en": t["title_en"],
            "file": t["file"],
            "tsv": t["tsv"],
            "primary_key": t["primary_key"],
            "row_count": t["row_count"],
            "id_range": t["id_range"],
            "columns": t["columns"],
            "source": t["source"],
            "confidence": t["confidence"],
            "notes_ja": t["notes_ja"],
            "notes_en": t["notes_en"],
        })
    payload = {"meta": meta, "areas": meta["areas"], "tables": catalog}
    return ("/* 自動生成: tools/build.py — 手で編集しないこと */\n"
            "window.__MHXX_INDEX_AT = (window.performance && performance.now) ? performance.now() : Date.now();\n"
            "window.MHXX_ID_MEMO_INDEX = " + _js_literal(payload) + ";\n")


def build_table_js(t):
    """web/data/<id>.js — 1 テーブル分の行データ。"""
    payload = {
        "id": t["id"],
        "header": [c["name"] for c in t["columns"]],
        "rows": t["rows"],
    }
    return ("/* 自動生成: tools/build.py — 手で編集しないこと */\n"
            "window.MHXX_ID_MEMO_TABLES = window.MHXX_ID_MEMO_TABLES || {};\n"
            "window.MHXX_ID_MEMO_TABLES[" + json.dumps(t["id"], ensure_ascii=False) + "] = "
            + _js_literal(payload) + ";\n")


def render_table_definitions(tables, meta):
    out = []
    out.append("# テーブル定義")
    out.append("")
    out.append("> このファイルは " + code("tools/build.py") + " が " + code("_manifest.json") + " から自動生成します。手で編集しないこと。")
    out.append("")
    out.append("- テーブル数: **{0}**".format(len(tables)))
    out.append("- 総行数: **{0}**".format(fmt_int(meta["row_count"])))
    out.append("- データ版: " + code(meta["data_version"]))
    out.append("")
    out.append("## 目次")
    out.append("")
    for area, area_ja in AREAS:
        group = [t for t in tables if t["area"] == area]
        if not group:
            continue
        out.append("### {0} ({1})".format(area_ja, code(area)))
        out.append("")
        out.append("| id | テーブル | 行数 | 主キー | ID 範囲 | confidence |")
        out.append("|---|---|---:|---|---|---|")
        for t in group:
            out.append("| [{0}](#{1}) | {2} | {3} | {4} | {5} | {6} |".format(
                code(t["id"]), t["id"], t["title_ja"], fmt_int(t["row_count"]),
                code(t["primary_key"]), fmt_range(t["id_range"]), t["confidence"]))
        out.append("")
    if not tables:
        out.append("（テーブルがありません）")
        out.append("")

    for area, area_ja in AREAS:
        group = [t for t in tables if t["area"] == area]
        if not group:
            continue
        out.append("---")
        out.append("")
        out.append("## {0} ({1})".format(area_ja, code(area)))
        out.append("")
        for t in group:
            out.append("### {0} <a id=\"{1}\"></a>".format(t["title_ja"], t["id"]))
            out.append("")
            out.append(code(t["id"]))
            out.append("")
            out.append("| 項目 | 値 |")
            out.append("|---|---|")
            out.append("| ファイル | {0} / {1} |".format(code(t["file"]), code(t["tsv"])))
            out.append("| 主キー | {0} |".format(code(t["primary_key"])))
            out.append("| 行数 | {0} |".format(fmt_int(t["row_count"])))
            out.append("| ID 範囲 | {0} |".format(fmt_range(t["id_range"])))
            out.append("| confidence | {0} |".format(code(t["confidence"])))
            out.append("| 英語名 | {0} |".format(t["title_en"] or "—"))
            if t["source"]:
                out.append("| 出典 | " + "<br>".join(code(s) for s in t["source"]) + " |")
            else:
                out.append("| 出典 | — |")
            if t["notes_ja"]:
                out.append("| 備考 | {0} |".format(t["notes_ja"]))
            out.append("")
            out.append("| # | 列名 | 型 | 説明 (ja) | 説明 (en) |")
            out.append("|---:|---|---|---|---|")
            for i, c in enumerate(t["columns"], 1):
                out.append("| {0} | {1} | {2} | {3} | {4} |".format(
                    i, code(c["name"]), c["type"], c["desc_ja"] or "—", c["desc_en"] or "—"))
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_sources(tables, meta, root):
    out = []
    out.append("# 出典と抽出方法")
    out.append("")
    out.append("> このファイルは " + code("tools/build.py") + " が " + code("_manifest.json")
               + " と各 " + code("NOTES.md") + " から自動生成します。手で編集しないこと。")
    out.append("")
    out.append("- データ版: " + code(meta["data_version"]))
    out.append("- テーブル数: **{0}** / 総行数: **{1}**".format(len(tables), fmt_int(meta["row_count"])))
    out.append("")
    out.append("## confidence の意味")
    out.append("")
    out.append("| 値 | 意味 |")
    out.append("|---|---|")
    out.append("| " + code("verified") + " | ゲーム実データ（romfs / 実行時メモリ / 既存抽出物）から直接取得した |")
    out.append("| " + code("derived") + " | 既存テーブル・既知 ID から計算・突合して求めた |")
    out.append("| " + code("curated") + " | 既知リストを人手で対応付けた（一次証拠が弱い） |")
    out.append("")
    out.append("## プレースホルダ（値なし）の扱い")
    out.append("")
    out.append("出典の「値なし」表記は、テーブルごとに次の方針で扱っている。どちらも**出典に忠実で、値の捏造はない**。")
    out.append("")
    out.append("| 出典の表記 | 扱い | 例 |")
    out.append("|---|---|---|")
    out.append("| " + code("(None)") + " / " + code("None") + " などの文字列 | **空文字に置換**（SPEC 0-1「不明は空文字」） | kinsects / talismans の id 0 |")
    out.append("| " + code("-") + " などの記号 | **出典どおり保持**（改変しない） | npcs の 16 行 |")
    out.append("")
    out.append("> 方針が 2 通りあるのは、前者が「値そのものが存在しない」ことを表すのに対し、")
    out.append("> 後者が「出典側が記号で欠損を表現している」ため。データの意味を変えないことを優先した。")
    out.append("")
    out.append("## テーブル別の出典")
    out.append("")
    out.append("| area | id | テーブル | confidence | 出典 |")
    out.append("|---|---|---|---|---|")
    for t in tables:
        src = "<br>".join(code(s) for s in t["source"]) or "—"
        out.append("| {0} | {1} | {2} | {3} | {4} |".format(
            t["area"], code(t["id"]), t["title_ja"], t["confidence"], src))
    if not tables:
        out.append("| — | — | （テーブルがありません） | — | — |")
    out.append("")
    out.append("## 出典ファイルの全体")
    out.append("")
    seen = []
    seen_set = set()
    for t in tables:
        for s in t["source"]:
            if s not in seen_set:
                seen_set.add(s)
                seen.append(s)
    if seen:
        for s in sorted(seen):
            out.append("- " + code(s))
    else:
        out.append("（なし）")
    out.append("")
    out.append("## 抽出メモ（analyst の NOTES.md）")
    out.append("")
    found_notes = False
    for area, area_ja in AREAS:
        p = root / "data" / area / "NOTES.md"
        if not p.is_file():
            continue
        found_notes = True
        out.append("### {0} ({1})".format(area_ja, code("data/" + area + "/NOTES.md")))
        out.append("")
        # NOTES.md は analyst が書き込み中かもしれないので、失敗してもビルドを止めない
        try:
            body = p.read_text(encoding="utf-8-sig").strip()
        except Exception as exc:
            body = "（読み込みに失敗しました: {0}）".format(exc)
        out.append(demote_headings(body) if body else "（空）")
        out.append("")
    if not found_notes:
        out.append("（" + code("data/equip/NOTES.md") + " / " + code("data/world/NOTES.md") + " はまだありません）")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_build_report(tables, meta, report, outputs, root):
    fence = BT * 3
    out = []
    out.append("# ビルドレポート")
    out.append("")
    out.append("> " + code("tools/build.py") + " が自動生成します。手で編集しないこと。")
    out.append("")
    out.append("- データ版: " + code(meta["data_version"]))
    out.append("- テーブル数: **{0}** / 総行数: **{1}**".format(len(tables), fmt_int(meta["row_count"])))
    out.append("- エラー: **{0}** / 警告: **{1}**".format(len(report.errors), len(report.warnings)))
    out.append("")
    out.append("## 生成物")
    out.append("")
    out.append("| ファイル | サイズ |")
    out.append("|---|---:|")
    for p in outputs:
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        out.append("| {0} | {1} B |".format(code(rel(p, root)), fmt_int(size)))
    out.append("")
    out.append("## テーブル別の検証結果")
    out.append("")
    out.append("| area | id | 行数 | 列数 | 主キー | ID 範囲 | confidence |")
    out.append("|---|---|---:|---:|---|---|---|")
    for t in tables:
        out.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            t["area"], code(t["id"]), fmt_int(t["row_count"]), len(t["columns"]),
            code(t["primary_key"]), fmt_range(t["id_range"]), t["confidence"]))
    if not tables:
        out.append("| — | — | 0 | 0 | — | — | — |")
    out.append("")
    out.append("## ログ")
    out.append("")
    out.append(fence)
    if report.lines:
        out.extend(report.lines)
    else:
        out.append("(なし)")
    out.append(fence)
    out.append("")
    return "\n".join(out) + "\n"


def render_readme_block(tables, meta):
    out = []
    out.append(README_BEGIN + " (tools/build.py が自動生成。手編集しないこと) -->")
    out.append("**テーブル数**: {0} / **総行数**: {1} / **データ版**: {2}".format(
        len(tables), fmt_int(meta["row_count"]), code(meta["data_version"][:19])))
    out.append("")
    out.append("| area | id | テーブル | 行数 | 主キー | ID 範囲 | confidence |")
    out.append("|---|---|---|---:|---|---|---|")
    for t in tables:
        out.append("| {0} | {1} | {2} | {3} | {4} | {5} | {6} |".format(
            t["area"], code(t["id"]), t["title_ja"], fmt_int(t["row_count"]),
            code(t["primary_key"]), fmt_range(t["id_range"]), t["confidence"]))
    if not tables:
        out.append("| — | — | （データ未投入） | 0 | — | — | — |")
    out.append(README_END)
    return "\n".join(out)


def update_readme(root, tables, meta, report):
    path = root / "README.md"
    if not path.is_file():
        report.warn("README.md が無いので自動ブロックは更新しません")
        return False
    text = path.read_text(encoding="utf-8")
    start = text.find(README_BEGIN)
    end = text.find(README_END)
    if start < 0 or end < 0 or end < start:
        report.warn("README.md に <!-- BEGIN:TABLES --> / <!-- END:TABLES --> が無いので更新しません")
        return False
    new = text[:start] + render_readme_block(tables, meta) + text[end + len(README_END):]
    if new == text:
        return False
    write_text(path, new)
    return True


def build_single_file(root, index_js, table_js_list, report):
    """index.js + 全テーブル JS を 1 ファイルに埋め込んだ自己完結版を作る。"""
    src = root / "web" / "index.html"
    if not src.is_file():
        report.error("web/index.html がありません（単一ファイル版を作れません）")
        return None
    html = src.read_text(encoding="utf-8")
    if DATA_TAG not in html:
        report.error("web/index.html に " + DATA_TAG + " が見つかりません")
        return None
    inline = ('<script id="mhxx-index">\n' + index_js + "\n" + "\n".join(table_js_list) + "</script>")
    out = html.replace(DATA_TAG, inline, 1)
    dst = root / "web" / "mhxx-id-memo.html"
    write_text(dst, out)
    return dst


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="MHXX ID MEMO ビルドツール")
    ap.add_argument("--root", default=None, help="リポジトリのルート（既定: tools/ の親）")
    ap.add_argument("--single-file", action="store_true", help="web/mhxx-id-memo.html を生成（既定で生成）")
    ap.add_argument("--no-single-file", action="store_true", help="自己完結 HTML を生成しない")
    ap.add_argument("--stamp", action="store_true", help="meta に生成時刻を含める（冪等でなくなる）")
    ap.add_argument("--quiet", action="store_true", help="ログを出さない")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    report = Reporter()

    if not (root / "SPEC.md").is_file() and not (root / "data").is_dir():
        print("[ERROR] リポジトリのルートに見えません: {0}".format(root), file=sys.stderr)
        return 2

    tables = []
    manifests = []
    for area, _ja in AREAS:
        mpath = root / "data" / area / "_manifest.json"
        if mpath.is_file():
            manifests.append(mpath)
        for entry in load_manifest(root, area, report):
            tid = str(entry.get("id", "")).strip()
            dup = False
            for t in tables:
                if t["id"] == tid:
                    dup = True
                    break
            if dup:
                report.error("テーブル id が重複しています: {0} ({1})".format(tid, area))
                continue
            t = build_table(root, area, entry, report)
            if t is not None:
                tables.append(t)

    for t in tables:
        write_tsv(root / t["tsv"], [c["name"] for c in t["columns"]], t["rows"])

    data_files = list(manifests)
    for t in tables:
        data_files.append(t["_csv_path"])
    meta = {
        "version": BUILD_VERSION,
        "generator": "tools/build.py",
        "data_version": compute_data_version(root, data_files),
        "table_count": len(tables),
        "row_count": sum(t["row_count"] for t in tables),
        "areas": [],
    }
    for area, area_ja in AREAS:
        group = [t for t in tables if t["area"] == area]
        meta["areas"].append({
            "id": area,
            "title_ja": area_ja,
            "table_count": len(group),
            "row_count": sum(t["row_count"] for t in group),
        })
    if args.stamp:
        meta["built_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    outputs = []

    index_path = root / "data" / "index.json"
    write_text(index_path, json.dumps(build_index(tables, meta), ensure_ascii=False, indent=2) + "\n")
    outputs.append(index_path)

    for t in tables:
        outputs.append(root / t["tsv"])

    data_dir = root / "web" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    # 旧形式（web/data.js 単体）が残っていれば削除する
    stale = root / "web" / "data.js"
    if stale.is_file():
        try:
            stale.unlink()
        except OSError:
            report.warn("web/data.js を削除できませんでした（手動で削除してください）")

    index_js = build_index_js(tables, meta)
    index_js_path = data_dir / "index.js"
    write_text(index_js_path, index_js)
    outputs.append(index_js_path)

    table_js_list = []
    for t in tables:
        text = build_table_js(t)
        table_js_list.append(text)
        p = data_dir / (t["id"] + ".js")
        write_text(p, text)
        outputs.append(p)

    if not args.no_single_file:
        single = build_single_file(root, index_js, table_js_list, report)
        if single is not None:
            outputs.append(single)

    defs_path = root / "docs" / "table-definitions.md"
    write_text(defs_path, render_table_definitions(tables, meta))
    outputs.append(defs_path)

    src_path = root / "docs" / "sources.md"
    write_text(src_path, render_sources(tables, meta, root))
    outputs.append(src_path)

    if update_readme(root, tables, meta, report):
        outputs.append(root / "README.md")

    report_path = root / "docs" / "build-report.md"
    write_text(report_path, render_build_report(tables, meta, report, outputs, root))
    outputs.append(report_path)

    if not args.quiet:
        print("")
        print("MHXX ID MEMO build")
        print("  root        : {0}".format(root))
        print("  tables      : {0}".format(len(tables)))
        print("  rows        : {0:,}".format(meta["row_count"]))
        print("  data_version: {0}".format(meta["data_version"]))
        table_js_total = 0
        table_js_count = 0
        for p in outputs:
            if p.parent == data_dir and p.name != "index.js":
                table_js_count += 1
                try:
                    table_js_total += p.stat().st_size
                except OSError:
                    pass
                continue
            try:
                size = p.stat().st_size
            except OSError:
                size = 0
            print("  out         : {0:<34} {1:>12,} B".format(rel(p, root), size))
        if table_js_count:
            print("  out         : {0:<34} {1:>12,} B".format(
                "web/data/<table>.js ({0} files)".format(table_js_count), table_js_total))
        if report.errors:
            print("")
            print("  ERRORS ({0}):".format(len(report.errors)))
            for e in report.errors:
                print("    - " + e)
        if report.warnings:
            print("")
            print("  WARNINGS ({0}):".format(len(report.warnings)))
            for w in report.warnings:
                print("    - " + w)
        if not report.errors and not report.warnings:
            print("  status      : OK")

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
