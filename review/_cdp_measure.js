
const { spawn } = require('child_process');
const http = require('http');

const CHROME = process.argv[3] || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const URL_ = process.argv[2];
const PORT = 9333;

function get(url) {
  return new Promise((res, rej) => {
    http.get(url, r => { let d=''; r.on('data', c=>d+=c); r.on('end', ()=>res(d)); }).on('error', rej);
  });
}
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }

(async () => {
  const prof = process.env.TEMP + '\\mhxx-cdp-prof-' + Date.now();
  const child = spawn(CHROME, [
    '--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
    '--remote-debugging-port=' + PORT, '--user-data-dir=' + prof, 'about:blank'
  ], { stdio: 'ignore' });

  let ver = null;
  for (let i=0;i<80;i++) {
    try { ver = JSON.parse(await get('http://127.0.0.1:'+PORT+'/json/version')); break; } catch(e) { await sleep(250); }
  }
  if (!ver) { console.log('CHROME_START_FAILED'); child.kill(); process.exit(1); }

  const ws = new WebSocket(ver.webSocketDebuggerUrl);
  let id = 0; const pending = new Map(); const events = [];
  ws.addEventListener('message', ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result); }
    else events.push(m);
  });
  await new Promise(r => ws.addEventListener('open', r));
  const send = (method, params, sessionId) => new Promise((res, rej) => {
    const mid = ++id; pending.set(mid, {res, rej});
    ws.send(JSON.stringify({ id: mid, method, params: params||{}, sessionId }));
  });

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const S = (m,p) => send(m,p,sessionId);

  await S('Page.enable'); await S('Runtime.enable'); await S('Log.enable');
  const t0 = Date.now();
  await S('Page.navigate', { url: URL_ });
  for (let i=0;i<300;i++) {
    if (events.some(e => e.method === 'Page.loadEventFired' && e.sessionId === sessionId)) break;
    await sleep(100);
  }
  const loadMs = Date.now() - t0;
  await sleep(1500);

  const evalJs = async (expr) => {
    const r = await S('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) return { error: r.exceptionDetails.text };
    return r.result.value;
  };

  const info = await evalJs('(function(){ var t = performance.timing; var rows = document.querySelectorAll("#grid tbody tr").length; var sb = document.querySelectorAll("[data-id]").length; return { title: document.title, hasData: !!window.MHXX_ID_MEMO, tables: (window.MHXX_ID_MEMO && window.MHXX_ID_MEMO.tables || []).length, domContentLoaded: Math.round(t.domContentLoadedEventEnd - t.navigationStart), loadEvent: Math.round(t.loadEventEnd - t.navigationStart), firstPaint: (performance.getEntriesByType("paint")[0] || {}).startTime, rows: rows, sidebarItems: sb, bodyBg: getComputedStyle(document.body).backgroundColor, visibleText: (document.body.innerText || "").slice(0, 120) }; })()');

  const errors = events.filter(e => e.method === 'Runtime.exceptionThrown' || e.method === 'Log.entryAdded')
    .map(e => JSON.stringify(e.params).slice(0, 300));

  const clickRes = await evalJs('(function(){ var items = document.querySelectorAll("#sb-list [data-id]"); if (!items.length) return "NO_SIDEBAR_ITEMS"; items[Math.min(1, items.length-1)].click(); return "clicked:" + items.length; })()');
  await sleep(900);
  const after = await evalJs('(function(){ return { rows: document.querySelectorAll("#grid tbody tr").length, name: (document.getElementById("tbl-name")||{}).textContent }; })()');

  const searchRes = await evalJs('(function(){ var q = document.getElementById("q"); if (!q) return "NO_SEARCH"; q.value = "1"; q.dispatchEvent(new Event("input", {bubbles:true})); return "ok"; })()');
  await sleep(900);
  const afterSearch = await evalJs('(function(){ return { rows: document.querySelectorAll("#grid tbody tr").length }; })()');

  console.log(JSON.stringify({ loadMs, info, clickRes, after, searchRes, afterSearch, errors: errors.slice(0,10) }, null, 2));

  child.kill();
  process.exit(0);
})().catch(e => { console.log('ERR ' + e.message); process.exit(1); });
