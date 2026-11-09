const { spawn } = require('child_process');
const http = require('http');
const CHROME = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const URL_ = process.argv[2];
const PORT = 9391;
function get(url){return new Promise((res,rej)=>{http.get(url,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',rej);});}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
(async()=>{
  const prof = process.env.TEMP + '\\mhxx-ga2-' + Date.now();
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
  await S('Network.enable'); await S('Page.enable'); await S('Runtime.enable');
  await S('Page.navigate',{url:URL_});
  for(let i=0;i<300;i++){ if(events.some(e=>e.method==='Page.loadEventFired'&&e.sessionId===sessionId)) break; await sleep(100);}
  await sleep(3000);
  const ev = async (expr)=>{ const r=await S('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true}); if(r.exceptionDetails) return {error:r.exceptionDetails.text}; return r.result.value; };
  await ev('document.getElementById("btn-theme").click()'); await sleep(800);
  await ev('(function(){var b=document.querySelector(\'#mode-switch button[data-mode="mem"]\'); if(b) b.click();})()'); await sleep(1500);
  await sleep(3000);
  const urls = events.filter(e=>e.method==='Network.requestWillBeSent').map(e=>e.params.request.url);
  const ga = urls.filter(u=>u.indexOf('google-analytics.com')>=0 || u.indexOf('analytics.google.com')>=0);
  const tids = {}; const ens = {};
  ga.forEach(function(u){ var m=u.match(/[?&]tid=([^&]+)/); if(m){tids[m[1]]=(tids[m[1]]||0)+1;} var e=u.match(/[?&]en=([^&]+)/); if(e){ens[decodeURIComponent(e[1])]=(ens[decodeURIComponent(e[1])]||0)+1;} });
  const gtag = urls.filter(u=>u.indexOf('gtag/js')>=0);
  console.log(JSON.stringify({gaHits: ga.length, tids: tids, events: ens, gtagJs: gtag, gtmReqs: urls.filter(u=>u.indexOf('gtm.js')>=0), errors: events.filter(e=>e.method==='Runtime.exceptionThrown').map(e=>JSON.stringify(e.params).slice(0,160))}, null, 2));
  child.kill(); process.exit(0);
})().catch(e=>{console.log('ERR '+e.message);process.exit(1);});