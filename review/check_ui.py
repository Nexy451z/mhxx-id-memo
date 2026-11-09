#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MHXX ID MEMO 独立検証: UI 出力と実セーブの突合 (reviewer).

review/cdp_scan.js が書き出した _ui_scan.json（実ブラウザで UI を操作した結果）を、
review/save_equip.py の独立実装（実セーブから導いた仕様）と比較する。

  - UI が出す hex が実セーブのレコードと一致するか（防具・武器・護石）
  - リトルエンディアンか
  - レイアウト仕様が出典として表示されているか（M1）
  - オフセット計算機が正しいか
  - レスポンシブ / 既存機能の回帰
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import save_equip as SE

REPO = r"C:\anyWorkspace\nx\mhxx\mhxx-id-memo"
issues = []


def add(sev, msg, ev=""):
    issues.append({"severity": sev, "message": msg, "evidence": ev})


def hexs(b):
    return " ".join("%02X" % x for x in b)


def pats_of(case):
    """[{label,text}] を {label: text} に。旧形式（文字列配列）にも耐える。"""
    out = []
    for p in case.get("pats") or []:
        if isinstance(p, dict):
            out.append((p.get("label") or "", (p.get("text") or "").strip().upper()))
        else:
            out.append(("", str(p).strip().upper()))
    return out


def find_pat(case, prefix):
    for label, text in pats_of(case):
        if label.startswith(prefix):
            return text
    return ""


_RARITY = None


def _kind_rarity(kind):
    """talismans.csv の talisman_id -> rarity（護石の種類ごとのレア度）。"""
    global _RARITY
    if _RARITY is None:
        import csv
        import io
        _RARITY = {}
        fp = os.path.join(REPO, "data", "equip", "talismans.csv")
        if os.path.exists(fp):
            raw = open(fp, "rb").read()
            body = raw[3:] if raw[:3] == b"\xef\xbb\xbf" else raw
            for row in csv.DictReader(io.StringIO(body.decode("utf-8"), newline="")):
                try:
                    _RARITY[int(row["talisman_id"])] = int(row["rarity"])
                except (KeyError, ValueError):
                    pass
    return _RARITY.get(kind, 99)


def main():
    p = os.path.join(REPO, "review", "_ui_scan.json")
    if not os.path.exists(p):
        print("[Critical] _ui_scan.json が無い。先に node review/cdp_scan.js を実行する")
        return 1
    d = json.load(open(p, encoding="utf-8"))

    print("=" * 78)
    print("UI 実測（headless Chrome / file://）")
    print("=" * 78)
    print("boot=%s  memReady=%s  cases=%d  errors=%s"
          % (d.get("boot"), d.get("memReady"), len(d.get("cases", [])), d.get("errors")))
    if not d.get("boot"):
        add("Critical", "ページが起動しなかった")
    if not d.get("memReady"):
        add("Critical", "メモリ配置モードが初期化されなかった")
    for e in d.get("errors", []):
        add("Major", "CDP 実行時エラー", e)

    raw = SE.load()
    recs = {i: r for i, r in SE.records(raw)}

    # ---- 1. UI の hex vs 独立実装
    print("\n" + "=" * 78)
    print("1. UI が出す hex と独立実装の期待値")
    print("=" * 78)
    print("%-22s %-20s %-20s %s" % ("case", "UI 6B", "期待 6B", "判定"))
    print("-" * 78)
    for c in d.get("cases", []):
        if c.get("error"):
            add("Major", "UI ケース %s が失敗" % c.get("id"), c["error"])
            continue
        inp = c["input"]
        lv, tl, tm = inp.get("level", 1), inp.get("tl", 1), inp.get("tm", 0)
        decos = inp.get("decos", [0, 0, 0])
        if inp["cat"] == "armor":
            rtype, rid = inp["part"] + 1, int(inp["key"][1:])
            exp = SE.encode(rtype, rid, level=lv, tmog_id=tm, tmog_level=tl, decos=decos)
        elif inp["cat"] == "weapon":
            rtype, rid = SE.WEAPON_TYPE_TO_EQUIP[inp["wtype"]], int(inp["key"][1:])
            exp = SE.encode(rtype, rid, level=lv, tmog_id=tm, tmog_level=tl, decos=decos)
        else:
            # 護石: UI の既定は skill1=0 skill2=0 p1=1 p2=0 slots=3、レア度は kind から引く
            rtype, rid = 6, int(inp["key"][1:])
            exp = SE.encode_talisman(rid, 0, 0, 1, 0, 3, _kind_rarity(rid), decos=decos)

        ui6 = find_pat(c, "6 ")
        ui_rec = find_pat(c, "12 ") or find_pat(c, "20 ")
        ui36 = find_pat(c, "36 ")
        # 護石は 6 バイトパターンを出さない（20 バイト推奨のみ）ので 6B はスキップ
        ok6 = True if inp["cat"] == "talisman" else (ui6 == hexs(exp[:6]))
        okrec = ui_rec == hexs(exp[:len(ui_rec.split())]) if ui_rec else False
        ok36 = ui36 == hexs(exp)
        print("%-22s %-20s %-20s %s" % (c["id"], ui6 or "(なし)", hexs(exp[:6]),
                                        "OK" if (ok6 and okrec and ok36) else
                                        "NG 6B=%s 推奨=%s 36B=%s" % (ok6, okrec, ok36)))
        if not ok6:
            add("Critical", "UI の 6 バイト hex が期待値と不一致: %s" % c["id"],
                "UI=%s / 期待=%s" % (ui6, hexs(exp[:6])))
        if not okrec:
            add("Major", "UI の推奨パターンが期待値と不一致: %s" % c["id"],
                "UI=%s / 期待=%s" % (ui_rec, hexs(exp[:len(ui_rec.split())]) if ui_rec else "-"))
        if not ok36:
            add("Major", "UI の 36 バイト hex が期待値と不一致: %s" % c["id"],
                "UI=%s / 期待=%s" % (ui36, hexs(exp)))

    # ---- 2. 実セーブのレコードと一致するか
    print("\n" + "=" * 78)
    print("2. 実セーブのレコードとの一致（最重要）")
    print("=" * 78)
    bycase = {c["id"]: c for c in d.get("cases", []) if not c.get("error")}
    pairs = [
        ("armor-head-bherna", 14, "実セーブ record 14 (ベルダーターバン)"),
        ("armor-chest-bherna", 15, "実セーブ record 15 (ベルダーメイル)"),
        ("weapon-gs-1", 0, "実セーブ record 0 (ベルダーブレイド)"),
        ("weapon-lbg-1", 11, "実セーブ record 11 (ベルダーバレット)"),
        ("weapon-cb-1", 9, "実セーブ record 9 (ベルダーアームズ)"),
    ]
    for cid, idx, label in pairs:
        c = bycase.get(cid)
        if not c:
            add("Major", "UI ケースが無い: %s" % cid)
            continue
        ui6 = find_pat(c, "6 ")
        real6 = hexs(recs[idx]["raw"][:6])
        ok = ui6 == real6
        print("  %-30s UI=%-20s 実セーブ=%-20s %s" % (label, ui6, real6, "一致" if ok else "不一致"))
        if not ok:
            add("Critical", "UI 出力が実セーブの実バイトと不一致: %s" % label,
                "UI=%s / 実=%s" % (ui6, real6))

    # ---- 2b. 護石: サンプルセーブの実レコードと突合
    print("\n" + "=" * 78)
    print("2b. 護石レコードの実セーブ突合（sample save / 650 件）")
    print("=" * 78)
    tr = d.get("talismanReal") or {}
    if not tr:
        add("Major", "護石の実測データが無い（CDP ハーネス未対応）")
    else:
        if tr.get("talOptsHidden"):
            add("Major", "護石モードで護石オプション（種類/スキル/スロット）が表示されない")
        sraw = SE.load(SE.SAMPLE_SAVE)
        tal = SE.talismans(sraw, 0)
        idx, real = tal[0]
        real_hex = hexs(real["raw"])
        ui20 = find_pat(tr, "20 ")
        ui36 = find_pat(tr, "36 ")
        print("  実セーブ idx=%d: type=6 kind=%d skill1=%d skill2=%d p1=%d p2=%d slots=%d rarity=%d"
              % (idx, real["id"], real["skill1_id"], real["skill2_id"],
                 real["skill1_points"], real["skill2_points"], real["slots"], real["rarity"]))
        print("  実 20B : %s" % real_hex[:59])
        print("  UI 20B : %s" % (ui20 or "(なし)"))
        print("  実 36B : %s" % real_hex)
        print("  UI 36B : %s" % (ui36 or "(なし)"))
        ok20 = ui20 == hexs(real["raw"][:20])
        ok36 = ui36 == real_hex
        print("  20 バイト一致: %s / 36 バイト一致: %s" % (ok20, ok36))
        if not ok20:
            add("Critical", "護石の推奨パターンが実セーブの護石レコードと不一致",
                "UI=%s / 実=%s" % (ui20, hexs(real["raw"][:20])))
        if not ok36:
            add("Major", "護石の 36 バイト hex が実セーブと不一致",
                "UI=%s / 実=%s" % (ui36, real_hex))

    # ---- 3. レイアウト仕様が出典として出ているか（M1）
    print("\n" + "=" * 78)
    print("3. レイアウト仕様の反映（M1）")
    print("=" * 78)
    L = d.get("layout") or {}
    help_txt = L.get("help") or ""
    tail = help_txt[-140:]
    print("  ヘルプ末尾: %s" % tail.replace("\n", " "))
    if "既定値" in tail:
        add("Major", "ヘルプのレイアウト出典が「既定値」のまま（仕様書が読まれていない）", tail)
    elif "verify_equip_record_layout" in tail or "equip-record-layout" in tail or "verified" in tail:
        print("  => 仕様ファイル由来の出典が表示されている OK")
    else:
        add("Minor", "レイアウト出典の表示が不明瞭", tail)

    # ---- 4. オフセット計算機
    print("\n" + "=" * 78)
    print("4. オフセット計算機")
    print("=" * 78)
    b = SE.body(raw)
    box_file = SE.box_offset_file(b)
    calc = d.get("calc") or {}
    exp_idx5 = SE.BOX_REL + 5 * SE.REC_SIZE
    got = (calc.get("idx5") or "")
    ok = ("0x%X" % exp_idx5).upper() in got.upper()
    print("  BOX index 5 -> 0x%X   UI=%r  %s" % (exp_idx5, got, "OK" if ok else "NG"))
    if not ok:
        add("Major", "BOX index -> オフセット計算が不一致", got)
    got_hit = (calc.get("hit") or "")
    ok = ("0x%X" % box_file).upper() in got_hit.upper()
    print("  ヒット 0x%X (index 5) -> BOX 先頭 0x%X   UI=%r  %s"
          % (box_file + 5 * SE.REC_SIZE, box_file, got_hit, "OK" if ok else "NG"))
    if not ok:
        add("Major", "ヒットアドレス -> BOX 先頭の逆算が不一致", got_hit)
    # ページ計算は仕様の page_geometry.slots_per_page（エディタ基準 9 枠）に従う。
    # 9 枠/ページなら page 3 -> index 18..26。
    got_page = (calc.get("page3") or "")
    ok = "18" in got_page and "26" in got_page
    print("  ページ 3 -> index 18..26（9 枠/ページ）   UI=%r  %s" % (got_page, "OK" if ok else "NG"))
    if not ok:
        add("Minor", "ページ -> index 範囲の計算が仕様の 9 枠/ページと不一致", got_page)

    # ---- 5. レスポンシブ
    print("\n" + "=" * 78)
    print("5. レスポンシブ（320 / 375 / 768 / 1024 / 1440）")
    print("=" * 78)
    for r in d.get("responsive", []):
        w = r.get("width")
        for mode in ("list", "mem"):
            m = r.get(mode) or {}
            over = m.get("overX")
            bad = {k: v for k, v in (m.get("hits") or {}).items() if v != "ok"}
            print("  %-5d %-5s 横はみ出し=%-3s 押せない要素=%s"
                  % (w, mode, over, bad if bad else "なし"))
            if over is None:
                add("Major", "レスポンシブ計測が取れない w=%s mode=%s" % (w, mode))
            elif over > 0:
                add("Major", "%spx / %s モードで横スクロール（%dpx はみ出し）" % (w, mode, over))
            if bad:
                add("Major", "%spx / %s モードで操作できない要素" % (w, mode), str(bad))

    # ---- 6. 回帰
    print("\n" + "=" * 78)
    print("6. 既存機能の回帰")
    print("=" * 78)
    reg = d.get("regression") or {}
    print("  サイドバー: %s テーブル" % reg.get("sidebarItems"))
    print("  検索: %s" % json.dumps(reg.get("afterSearch"), ensure_ascii=False))
    print("  ソート: %s" % reg.get("sort"))
    print("  列フィルタ: %s" % json.dumps(reg.get("afterFilter"), ensure_ascii=False))
    print("  メニュー: %s" % json.dumps(reg.get("menus"), ensure_ascii=False))
    print("  定義モーダル: %s" % json.dumps(reg.get("modal"), ensure_ascii=False))
    if reg.get("sidebarItems") != 42:
        add("Major", "サイドバーのテーブル数が 42 でない", str(reg.get("sidebarItems")))
    if not (reg.get("afterSearch") or {}).get("rows"):
        add("Major", "検索で行が絞り込まれていない", json.dumps(reg.get("afterSearch"), ensure_ascii=False))
    if reg.get("sort") != "asc/desc/none":
        add("Major", "ソートの巡回が不正", str(reg.get("sort")))
    if not (reg.get("afterFilter") or {}).get("rows"):
        add("Major", "列フィルタが効いていない", json.dumps(reg.get("afterFilter"), ensure_ascii=False))
    if not (reg.get("modal") or {}).get("open"):
        add("Major", "テーブル定義モーダルが開かない", json.dumps(reg.get("modal"), ensure_ascii=False))

    # ---- 判定
    print("\n" + "=" * 78)
    order = {"Critical": 0, "Major": 1, "Minor": 2}
    if issues:
        for x in sorted(issues, key=lambda y: order[y["severity"]]):
            print("[%s] %s" % (x["severity"], x["message"]))
            if x["evidence"]:
                print("        %s" % x["evidence"])
        print("\n指摘: %d" % len(issues))
    else:
        print("指摘なし")
    return 1 if any(x["severity"] in ("Critical", "Major") for x in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
