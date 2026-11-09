'use strict';
/* MHXX ID MEMO — メモリ配置モード / レスポンシブ / 回帰の CDP 実測ハーネス (reviewer).
 *
 *   node review/cdp_scan.js [--port 9334] [--out review/_ui_scan.json]
 *
 * Chrome を headless で起動し、file:// で web/index.html を開いて
 * メモリ配置モードの出力 hex を読み取り、JSON に書き出す。
 * 期待値との比較は review/check_ui.py が行う（独立性のため）。
 */
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const REPO = 'C:\\anyWorkspace\\nx\\mhxx\\mhxx-id-memo';
const PAGE = 'file:///' + REPO.replace(/\\/g, '/') + '/web/index.html';

function arg(name, dflt) {
  const i = process.argv.indexOf('--' + name);
  return i >= 0 ? process.argv[i + 1] : dflt;
}
const PORT = parseInt(arg('port', '9334'), 10);
const OUT = arg('out', path.join(REPO, 'review', '_ui_scan.json'));

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function connect() {
  for (let i = 0; i < 120; i++) {
    try {
      const list = await (await fetch('http://127.0.0.1:' + PORT + '/json/list')).json();
      const page = list.find(t => t.type === 'page');
      if (page && page.webSocketDebuggerUrl) return page.webSocketDebuggerUrl;
    } catch (e) { /* retry */ }
    await sleep(250);
  }
  throw new Error('chrome not reachable on ' + PORT);
}

function makeClient(ws) {
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', ev => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const p = pending.get(msg.id); pending.delete(msg.id);
      msg.error ? p.reject(new Error(JSON.stringify(msg.error))) : p.resolve(msg.result);
    }
  });
  return {
    send(method, params) {
      return new Promise((resolve, reject) => {
        const myId = ++id;
        pending.set(myId, { resolve, reject });
        ws.send(JSON.stringify({ id: myId, method, params: params || {} }));
        setTimeout(() => { if (pending.has(myId)) { pending.delete(myId); reject(new Error('timeout ' + method)); } }, 60000);
      });
    }
  };
}

(async function main() {
  const userDataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mhxx-cdp-'));
  const chrome = spawn(CHROME, [
    '--headless=new', '--remote-debugging-port=' + PORT, '--user-data-dir=' + userDataDir,
    '--allow-file-access-from-files', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
    '--hide-scrollbars', '--force-device-scale-factor=1', 'about:blank'
  ], { stdio: 'ignore' });

  const result = { page: PAGE, cases: [], calc: {}, responsive: [], regression: {}, errors: [] };
  let c;
  try {
    const wsUrl = await connect();
    const ws = new WebSocket(wsUrl);
    await new Promise((res, rej) => { ws.addEventListener('open', res); ws.addEventListener('error', rej); });
    c = makeClient(ws);
    await c.send('Page.enable');
    await c.send('Runtime.enable');

    async function js(expr) {
      const r = await c.send('Runtime.evaluate', {
        expression: '(function(){' + expr + '})()',
        returnByValue: true, awaitPromise: true
      });
      if (r.exceptionDetails) throw new Error('JS: ' + JSON.stringify(r.exceptionDetails).slice(0, 300));
      return r.result && r.result.value;
    }
    async function waitFor(expr, ms) {
      const t0 = Date.now();
      while (Date.now() - t0 < (ms || 20000)) {
        try { if (await js('return !!(' + expr + ');')) return true; } catch (e) { /* ignore */ }
        await sleep(150);
      }
      return false;
    }

    await c.send('Page.navigate', { url: PAGE });
    await waitFor("document.readyState === 'complete'", 30000);
    const okBoot = await waitFor("window.MHXX_ID_MEMO_TABLES && Object.keys(window.MHXX_ID_MEMO_TABLES).length > 0", 30000);
    result.boot = okBoot;

    await js("var b=document.querySelector('button[data-mode=\"mem\"]'); if(b) b.click(); return 1;");
    const okMem = await waitFor("document.querySelector('#mem-list') && document.querySelector('#mem-list').children.length > 0", 30000);
    result.memReady = okMem;

    const cases = [
      { id: 'armor-head-bherna', cat: 'armor', part: 0, key: 'a3', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'armor-head-leather', cat: 'armor', part: 0, key: 'a1', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'armor-head-lv5', cat: 'armor', part: 0, key: 'a3', level: 5, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'armor-head-tmog', cat: 'armor', part: 0, key: 'a3', level: 1, tl: 2, tm: 1, decos: [0, 0, 0] },
      { id: 'armor-chest-bherna', cat: 'armor', part: 1, key: 'a3', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'weapon-gs-1', cat: 'weapon', wtype: 0, key: 'w1', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'weapon-lbg-1', cat: 'weapon', wtype: 6, key: 'w1', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'weapon-cb-1', cat: 'weapon', wtype: 14, key: 'w1', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'weapon-gs-lv7', cat: 'weapon', wtype: 0, key: 'w1', level: 7, tl: 1, tm: 0, decos: [0, 0, 0] },
      { id: 'talisman-1', cat: 'talisman', key: 'k1', level: 1, tl: 1, tm: 0, decos: [0, 0, 0] }
    ];

    for (const cs of cases) {
      try {
        await js("var cat=document.querySelector('#mem-cat'); cat.value=" + JSON.stringify(cs.cat) +
          "; cat.dispatchEvent(new Event('change',{bubbles:true})); return 1;");
        if (cs.cat === 'armor') {
          await js("var p=document.querySelector('#mem-part'); p.value=" + JSON.stringify(String(cs.part)) +
            "; p.dispatchEvent(new Event('change',{bubbles:true})); return 1;");
        } else if (cs.cat === 'weapon') {
          await js("var w=document.querySelector('#mem-wtype'); w.value=" + JSON.stringify(String(cs.wtype)) +
            "; w.dispatchEvent(new Event('change',{bubbles:true})); return 1;");
        }
        await sleep(200);
        const picked = await js("var b=document.querySelector('#mem-list [data-key=" + JSON.stringify(cs.key) +
          "]'); if(!b) return false; b.click(); return true;");
        if (!picked) { result.cases.push({ id: cs.id, error: 'item not found: ' + cs.key }); continue; }
        await js("function setv(sel,v){var e=document.querySelector(sel); if(!e) return; e.value=String(v);" +
          " e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true}));}" +
          " setv('#mem-level', " + cs.level + "); setv('#mem-tl', " + cs.tl + "); setv('#mem-tm', " + cs.tm + ");" +
          " setv('#mem-deco1', " + cs.decos[0] + "); setv('#mem-deco2', " + cs.decos[1] + "); setv('#mem-deco3', " + cs.decos[2] + ");" +
          " return 1;");
        await sleep(250);
        const out = await js("var pats=[]; document.querySelectorAll('#mem-pats .pat').forEach(function(p){" +
          " var c=p.querySelector('code'); if(!c) return;" +
          " var l=p.querySelector('.lbl'); pats.push({label:(l?l.textContent:''), text:c.textContent});});" +
          " var hex=document.querySelector('#mem-hex').textContent;" +
          " var annot=document.querySelector('#mem-annot').textContent;" +
          " return {pats:pats, hex:hex, annot:annot};");
        result.cases.push(Object.assign({ id: cs.id, input: cs }, out));
      } catch (e) {
        result.cases.push({ id: cs.id, error: String(e).slice(0, 200) });
      }
    }

    // ---- 実セーブの護石レコードとの突合（M2 の検証）
    try {
      await js("var cat=document.querySelector('#mem-cat'); cat.value='talisman'; cat.dispatchEvent(new Event('change',{bubbles:true})); return 1;");
      await sleep(350);
      await js("var b=document.querySelector('#mem-list [data-act=\"mem-pick\"]'); if(b) b.click(); return 1;");
      await sleep(250);
      await js("function setv(sel,v){var e=document.querySelector(sel); if(!e) return;" +
        " e.value=String(v); e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true}));}" +
        " setv('#mem-kind', 10); setv('#mem-skill1', 74); setv('#mem-p1', 6);" +
        " setv('#mem-skill2', 70); setv('#mem-p2', 10); setv('#mem-slots', 3); return 1;");
      await sleep(350);
      result.talismanReal = await js("var pats=[]; document.querySelectorAll('#mem-pats .pat').forEach(function(p){" +
        " var c=p.querySelector('code'); if(!c) return;" +
        " var l=p.querySelector('.lbl'); pats.push({label:(l?l.textContent:''), text:c.textContent});});" +
        " var hex=(document.querySelector('#mem-hex')||{}).textContent||'';" +
        " var talHidden=(document.querySelector('#mem-tal-opts')||{}).hidden;" +
        " return {pats:pats, hex:hex, talOptsHidden:talHidden};");
    } catch (e) { result.errors.push('talisman: ' + String(e).slice(0, 200)); }

    // ---- レイアウト定義が UI に読まれているか
    try {
      result.layout = await js("var L=window.MHXX_EQUIP_LAYOUT||null;" +
        " return {keys: L?Object.keys(L):null, has_record_size: !!(L&&L.record_size)," +
        "   has_save_offset: !!(L&&L.save_offset), has_fields: !!(L&&Array.isArray(L.fields))," +
        "   has_nested_box: !!(L&&L.box), has_nested_record_fields: !!(L&&L.record&&L.record.fields)," +
        "   help: (document.querySelector('#mem-help')||{}).textContent || ''};");
    } catch (e) { result.errors.push('layout: ' + String(e).slice(0, 200)); }

    try {
      await js("var e=document.querySelector('#mem-idx'); e.value='5'; e.dispatchEvent(new Event('input',{bubbles:true})); return 1;");
      await sleep(120);
      result.calc.idx5 = await js("return document.querySelector('#mem-idx-out').textContent;");
      // 実セーブの record 5 の絶対アドレス = 0x12C786 + 5*36 = 0x12C83A
      await js("var e=document.querySelector('#mem-hit'); e.value='0x12C83A'; e.dispatchEvent(new Event('input',{bubbles:true}));" +
        "var i=document.querySelector('#mem-hit-idx'); i.value='5'; i.dispatchEvent(new Event('input',{bubbles:true})); return 1;");
      await sleep(120);
      result.calc.hit = await js("return document.querySelector('#mem-hit-out').textContent;");
      await js("var e=document.querySelector('#mem-page'); e.value='3'; e.dispatchEvent(new Event('input',{bubbles:true})); return 1;");
      await sleep(120);
      result.calc.page3 = await js("return document.querySelector('#mem-page-out').textContent;");
    } catch (e) { result.errors.push('calc: ' + String(e).slice(0, 200)); }

    const widths = [320, 375, 768, 1024, 1440];
    const HIT_HELPER = "function hit(sel){var e=document.querySelector(sel); if(!e) return 'missing';" +
      " if(e.offsetParent===null && getComputedStyle(e).position!=='fixed') return 'hidden';" +
      " e.scrollIntoView({block:'center', inline:'center'});" +
      " var r=e.getBoundingClientRect(); if(r.width<=0||r.height<=0) return 'zero';" +
      " var cx=Math.round(r.x+r.width/2), cy=Math.round(r.y+r.height/2);" +
      " if(cx<0||cy<0||cx>=window.innerWidth||cy>=window.innerHeight) return 'offscreen';" +
      " var t=document.elementFromPoint(cx,cy); if(!t) return 'null';" +
      " return (t===e||e.contains(t)||t.contains(e))?'ok':'covered:'+t.tagName;}" +
      " function overX(){var de=document.documentElement,b=document.body;" +
      "   return Math.max(de.scrollWidth,b.scrollWidth)-window.innerWidth;}";
    for (const w of widths) {
      await c.send('Emulation.setDeviceMetricsOverride', {
        width: w, height: 900, deviceScaleFactor: 1, mobile: w <= 768
      });
      await sleep(350);
      // --- 一覧モード
      await js("var b=document.querySelector('button[data-mode=\"list\"]'); if(b) b.click(); window.scrollTo(0,0); return 1;");
      await sleep(300);
      const listM = await js(HIT_HELPER +
        " var sel=['#q','#fcol','#fval','[data-act=\"sel-all\"]','[data-menu=\"menu-copy\"]','[data-act=\"def\"]'];" +
        " var hits={}; sel.forEach(function(s){hits[s]=hit(s);});" +
        " window.scrollTo(0,0);" +
        " return {overX:overX(), hits:hits, tableRows:document.querySelectorAll('#tbody tr').length};");
      // --- メモリ配置モード
      await js("var b=document.querySelector('button[data-mode=\"mem\"]'); if(b) b.click(); window.scrollTo(0,0); return 1;");
      await sleep(400);
      const memM = await js(HIT_HELPER +
        " var sel=['#mem-cat','#mem-search','#mem-level','#mem-tl','#mem-tm','#mem-deco1','#mem-list'," +
        "   '#mem-idx','#mem-hit','#mem-page'];" +
        " var hits={}; sel.forEach(function(s){hits[s]=hit(s);});" +
        " window.scrollTo(0,0);" +
        " return {overX:overX(), hits:hits, memListW:(document.querySelector('#mem-list')||{getBoundingClientRect:function(){return {width:0};}}).getBoundingClientRect().width};");
      result.responsive.push({ width: w, list: listM, mem: memM });
    }
    await c.send('Emulation.clearDeviceMetricsOverride');

    try {
      await js("var b=document.querySelector('button[data-mode=\"list\"]'); if(b) b.click(); return 1;");
      await sleep(500);
      const reg = await js("var out={};" +
        " out.tables = (window.MHXX_ID_MEMO_TABLES ? Object.keys(window.MHXX_ID_MEMO_TABLES).length : 0);" +
        " out.sidebarItems = document.querySelectorAll('#sb-list .titem').length;" +
        " out.thead = document.querySelectorAll('#thead th').length;" +
        " out.tbodyRows = document.querySelectorAll('#tbody tr').length;" +
        " var q=document.querySelector('#q'); if(q){ q.value='レザー'; q.dispatchEvent(new Event('input',{bubbles:true})); }" +
        " return out;");
      await sleep(500);
      reg.afterSearch = await js("return {rows: document.querySelectorAll('#tbody tr').length, counts: (document.querySelector('#counts')||{}).textContent};");
      // ソートは再描画で th が差し替わるので、毎回クエリし直す
      reg.sort = await js("function st(){var t=document.querySelector('#thead th[data-c]'); if(!t) return 'no th';" +
        " t.click(); return document.querySelector('#thead th.asc')?'asc':(document.querySelector('#thead th.desc')?'desc':'none');}" +
        " var a=st(); var b=st(); var c2=st(); return a+'/'+b+'/'+c2;");
      reg.sortOrder = await js("var rows=document.querySelectorAll('#tbody tr'); if(rows.length<2) return 'few';" +
        " var a=rows[0].children[2].textContent, b=rows[1].children[2].textContent; return a+'|'+b;");
      // 列フィルタ: 実際に存在する値で絞り込む
      reg.filter = await js("var q=document.querySelector('#q'); if(q){q.value=''; q.dispatchEvent(new Event('input',{bubbles:true}));}" +
        " var f=document.querySelector('#fcol'); if(!f) return 'no fcol';" +
        " var col=f.options[1]?f.options[1].value:''; f.value=col; f.dispatchEvent(new Event('change',{bubbles:true}));" +
        " return {col:col};");
      await sleep(500);
      const probe = await js("var r=document.querySelector('#tbody tr'); if(!r) return null;" +
        " var cells=r.children; return cells.length>2 ? cells[2].textContent : null;");
      reg.filterProbe = probe;
      if (probe) {
        await js("var v=document.querySelector('#fval'); if(v){v.value=" + JSON.stringify(probe) +
          "; v.dispatchEvent(new Event('input',{bubbles:true}));} return 1;");
        await sleep(500);
        reg.afterFilter = await js("return {rows: document.querySelectorAll('#tbody tr').length, counts:(document.querySelector('#counts')||{}).textContent};");
        await js("var v=document.querySelector('#fval'); if(v){v.value=''; v.dispatchEvent(new Event('input',{bubbles:true}));} return 1;");
        await sleep(300);
      }
      reg.menus = await js("var out={}; ['menu-copy','menu-dl','menu-cols'].forEach(function(id){" +
        " var m=document.getElementById(id); out[id]= m ? m.children.length : -1;}); return out;");
      reg.modal = await js("var b=document.querySelector('[data-act=\"def\"]'); if(!b) return 'no btn';" +
        " b.click(); var m=document.getElementById('modal');" +
        " var open = m && !m.hidden; var len = m ? m.textContent.length : 0;" +
        " var x=document.querySelector('[data-act=\"close-modal\"]'); if(x) x.click();" +
        " return {open:open, len:len};");
      result.regression = reg;
    } catch (e) { result.errors.push('regression: ' + String(e).slice(0, 300)); }

  } catch (e) {
    result.errors.push('fatal: ' + String(e).slice(0, 400));
  } finally {
    try { chrome.kill(); } catch (e) { /* ignore */ }
    fs.writeFileSync(OUT, JSON.stringify(result, null, 1), 'utf8');
    console.log('wrote ' + OUT);
    console.log('boot=' + result.boot + ' memReady=' + result.memReady + ' cases=' + result.cases.length +
      ' errors=' + result.errors.length);
    if (result.errors.length) console.log(result.errors.join('\n'));
    process.exit(0);
  }
})();
