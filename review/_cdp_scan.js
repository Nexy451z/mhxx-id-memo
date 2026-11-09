const { spawn } = require('child_process');
const http = require('http');
const CHROME = process.argv[3] || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const URL_ = process.argv[2];
const PORT = 9345;
function get(url){return new Promise((res,rej)=>{http.get(url,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',rej);});}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
(async()=>{
  const prof = process.env.TEMP + '\\mhxx-cdp2-' + Date.now();
  const child = spawn(CHROME, ['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port='+PORT,'--user-data-dir='+prof,'about:blank'], {stdio:'ignore'});
  let ver=null; for(let i=0;i<80;i++){ try{ ver=JSON.parse(await get('http://127.0.0.1:'+PORT+'/json/version')); break;}catch(e){await sleep(250);} }
  if(!ver){ console.log('CHROME_START_FAILED'); child.kill(); process.exit(1);}
  const ws = new WebSocket(ver.webSocketDebuggerUrl);
  let id=0; const pending=new Map(); const events=[];
  ws.addEventListener('message', ev=>{ const m=JSON.parse(ev.data); if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);} else events.push(m); });
  await new Promise(r=>ws.addEventListener('open',r));
  const send=(method,params,sessionId)=>new Promise((res,rej)=>{const mid=++id;pending.set(mid,{res,rej});ws.send(JSON.stringify({id:mid,method,params:params||{},sessionId}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const S=(m,p)=>send(m,p,sessionId);
  await S('Page.enable'); await S('Runtime.enable'); await S('Log.enable');
  await S('Page.navigate',{url:URL_});
  for(let i=0;i<300;i++){ if(events.some(e=>e.method==='Page.loadEventFired'&&e.sessionId===sessionId)) break; await sleep(100);}
  await sleep(1200);
  const ev = async (expr)=>{ const r=await S('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true}); if(r.exceptionDetails) return {error:r.exceptionDetails.text}; return r.result.value; };
  const out = {};
  out.clickMode = await ev('(function(){var b=document.querySelector(\'#mode-switch button[data-mode="mem"]\'); if(!b) return "NO_BTN"; b.click(); return "ok";})()');
  await sleep(700);
  out.setCat = await ev('(function(){var s=document.getElementById("mem-cat"); if(!s) return "NO_CAT"; s.value="armor"; s.dispatchEvent(new Event("change",{bubbles:true})); return s.value;})()');
  await sleep(500);
  out.setPart = await ev('(function(){var s=document.getElementById("mem-part"); if(!s) return "NO_PART"; s.value="0"; s.dispatchEvent(new Event("change",{bubbles:true})); return s.value;})()');
  await sleep(700);
  out.pick = await ev('(function(){var items=[].slice.call(document.querySelectorAll("#mem-list .mem-item")); var t=items.filter(function(x){return x.textContent.indexOf("ベルダーターバン")>=0;}); if(!t.length) return "NOT_FOUND:"+items.length; t[0].click(); return "clicked:"+t[0].getAttribute("data-key");})()');
  await sleep(700);
  out.hex = await ev('(function(){var e=document.getElementById("mem-hex"); return e?e.textContent.trim():"NO_HEX";})()');
  out.annot = await ev('(function(){var e=document.getElementById("mem-annot"); return e?e.textContent.replace(/\\s+/g," ").slice(0,400):"NO_ANNOT";})()');
  out.pats = await ev('(function(){var e=document.getElementById("mem-pats"); return e?e.textContent.replace(/\\s+/g," ").slice(0,600):"NO_PATS";})()');
  out.help = await ev('(function(){var e=document.getElementById("mem-help"); return e?e.textContent.replace(/\\s+/g," ").slice(0,300):"NO_HELP";})()');
  out.errors = events.filter(e=>e.method==='Runtime.exceptionThrown').map(e=>JSON.stringify(e.params).slice(0,200));
  console.log(JSON.stringify(out,null,2));
  child.kill(); process.exit(0);
})().catch(e=>{console.log('ERR '+e.message);process.exit(1);});