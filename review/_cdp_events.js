const { spawn } = require('child_process');
const http = require('http');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const URL_ = process.argv[2];
const PORT = 9371;
function get(url){return new Promise((res,rej)=>{http.get(url,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',rej);});}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
(async()=>{
  const prof = process.env.TEMP + '\\mhxx-ev-' + Date.now();
  const child = spawn(CHROME, ['--headless=new','--disable-gpu','--no-first-run','--remote-debugging-port='+PORT,'--user-data-dir='+prof,'about:blank'], {stdio:'ignore'});
  let ver=null; for(let i=0;i<80;i++){ try{ ver=JSON.parse(await get('http://127.0.0.1:'+PORT+'/json/version')); break;}catch(e){await sleep(250);} }
  const ws = new WebSocket(ver.webSocketDebuggerUrl);
  let id=0; const pending=new Map(); const events=[];
  ws.addEventListener('message', ev=>{ const m=JSON.parse(ev.data); if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);} else events.push(m); });
  await new Promise(r=>ws.addEventListener('open',r));
  const send=(method,params,sessionId)=>new Promise((res,rej)=>{const mid=++id;pending.set(mid,{res,rej});ws.send(JSON.stringify({id:mid,method,params:params||{},sessionId}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const S=(m,p)=>send(m,p,sessionId);
  await S('Page.enable'); await S('Runtime.enable');
  await S('Page.navigate',{url:URL_});
  for(let i=0;i<300;i++){ if(events.some(e=>e.method==='Page.loadEventFired'&&e.sessionId===sessionId)) break; await sleep(100);}
  await sleep(2500);
  const ev = async (expr)=>{ const r=await S('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true}); if(r.exceptionDetails) return {error:r.exceptionDetails.text}; return r.result.value; };
  const names = async ()=> await ev('(function(){return (window.dataLayer||[]).filter(function(x){return x&&x.event;}).map(function(x){return x.event;});})()');
  const out={initial: await names()};
  await ev('document.getElementById("btn-theme").click()'); await sleep(500);
  out.afterTheme = await names();
  await ev('(function(){var it=document.querySelectorAll("#sb-list [data-id]"); if(it.length>3){it[3].click();} return it.length;})()'); await sleep(900);
  out.afterTable = await names();
  await ev('(function(){var b=document.querySelector(\'#mode-switch button[data-mode="mem"]\'); if(b) b.click();})()'); await sleep(600);
  out.afterMode = await names();
  out.full = await ev('(function(){return (window.dataLayer||[]).filter(function(x){return x&&x.event&&x.event.indexOf("mhxx_")===0;}).map(function(x){var o={e:x.event}; for(var k in x){if(k!=="event"&&typeof x[k]!=="object") o[k]=x[k];} return o;});})()');
  out.gtagShim = await ev('typeof window.gtag');
  out.gtmInit = await ev('!!(window.google_tag_manager&&window.google_tag_manager["GTM-T9NHWQW4"])');
  out.errors = events.filter(e=>e.method==='Runtime.exceptionThrown').map(e=>JSON.stringify(e.params).slice(0,160));
  console.log(JSON.stringify(out,null,2));
  child.kill(); process.exit(0);
})().catch(e=>{console.log('ERR '+e.message);process.exit(1);});