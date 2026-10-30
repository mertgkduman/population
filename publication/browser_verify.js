/* Offline Chrome DevTools verification for the V5 single-file dashboard. */
'use strict';
const fs=require('fs'),path=require('path'),os=require('os'),net=require('net'),{spawn}=require('child_process'),crypto=require('crypto');
const CHROME=process.env.CHROME_BIN||'/hpc/home/mg551/.agent-browser/browsers/chrome-154.0.8037.92/chrome';
const INDEX=path.join(__dirname,'../docs/index.html');
const BASE=process.env.PUBLICATION_URL||'http://127.0.0.1:8765/docs/index.html';
const OUTPUT_DIR=process.env.VERIFY_OUTPUT_DIR||__dirname;
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const freePort=()=>new Promise((resolve,reject)=>{const server=net.createServer();server.listen(0,'127.0.0.1',()=>{const port=server.address().port;server.close(()=>resolve(port))});server.on('error',reject)});
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');

async function main(){
  const port=await freePort(),profile=fs.mkdtempSync(path.join(os.tmpdir(),'v5-dashboard-chrome-'));
  const chrome=spawn(CHROME,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--disable-background-networking','--no-first-run','--disable-extensions','--remote-allow-origins=*',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
  let ws;const errors=[],remote=[],checks=[];const record=(name,pass,detail='')=>checks.push({name,pass:!!pass,detail});
  try{
    if(!fs.existsSync(INDEX))throw Error(`${INDEX} missing; run python build_dashboard.py first`);
    let pages=[];for(let i=0;i<200;i++){try{pages=await (await fetch(`http://127.0.0.1:${port}/json`)).json();if(pages.some(x=>x.type==='page'))break}catch{}await sleep(100)}
    const page=pages.find(x=>x.type==='page');if(!page)throw Error('Chrome page unavailable');
    ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.addEventListener('open',resolve,{once:true});ws.addEventListener('error',reject,{once:true})});
    let seq=0;const pending=new Map();ws.addEventListener('message',event=>{const msg=JSON.parse(event.data);if(msg.id){const p=pending.get(msg.id);if(p){pending.delete(msg.id);msg.error?p.reject(Error(msg.error.message)):p.resolve(msg.result)}}else if(msg.method==='Runtime.exceptionThrown')errors.push(msg.params.exceptionDetails.exception?.description||msg.params.exceptionDetails.text);else if(msg.method==='Log.entryAdded'&&msg.params.entry.level==='error')errors.push(msg.params.entry.text);else if(msg.method==='Network.requestWillBeSent'&&/^https?:/.test(msg.params.request.url)&&!msg.params.request.url.startsWith('http://127.0.0.1:8765/'))remote.push(msg.params.request.url)});
    const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(Error(`${method} timeout`))}},120000)});
    const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
    async function until(expression,timeout=120000){const start=Date.now();while(Date.now()-start<timeout){try{if(await evaluate(expression))return true}catch{}await sleep(150)}return false}
    await send('Runtime.enable');await send('Log.enable');await send('Network.enable');await send('Network.setBlockedURLs',{urls:['https://*']});await send('Page.enable');
    await send('Page.navigate',{url:BASE});
    record('portal_loaded',await until("window.PublicationState?.ready===true"));
    record('six_top_tabs',await evaluate("document.querySelectorAll('[data-version]').length===6 && document.querySelector('[data-version=future]').textContent==='Further work'"));
    for(const v of ['v1','v2','v3','v4','v5','future']){
      for(const section of ['model','changes','shortcomings']){
        await evaluate("select('"+v+"','"+section+"')");
        record(v+'_'+section,await evaluate("PublicationState.version==='"+v+"' && PublicationState.section==='"+section+"' && document.getElementById('panel').textContent.length>100 && document.querySelectorAll('[data-section][aria-selected=true]').length===1"));
      }
    }
    await evaluate("select('future','results')");
    record('future_results_explicitly_unrun',await evaluate("document.getElementById('panel').textContent.includes('No new simulation results') && !document.querySelector('iframe')"));
    await evaluate("document.querySelector('[data-version=v1]').focus();document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}))");
    record('keyboard_version_navigation',await evaluate("PublicationState.version==='v2'"));
    for(const v of ['v1','v2','v3','v4','v5']){
      await evaluate("select('"+v+"','results')");
      const ready=await until("document.querySelector('iframe')?.contentWindow.document.querySelectorAll('.js-plotly-plot').length>2 && document.querySelector('iframe').contentWindow.document.querySelectorAll('.publication-download').length>2",180000);
      record(v+'_plots_rendered',ready);
      if(!ready)throw Error(v+' did not load plots');
      record(v+'_every_plot_download',await evaluate("(()=>{const d=document.querySelector('iframe').contentDocument;return [...d.querySelectorAll('.js-plotly-plot')].every(g=>g.nextElementSibling?.classList.contains('publication-download'))})()"));
      const hrefs=await evaluate("[...document.querySelector('iframe').contentDocument.querySelectorAll('.reference-package')].map(a=>a.href)");
      const responses=await Promise.all([...new Set(hrefs)].map(async url=>({url,status:(await fetch(url,{method:'HEAD'})).status})));
      record(v+'_reference_links_resolve',responses.every(x=>x.status===200),JSON.stringify(responses));
      await evaluate("(()=>{const w=document.querySelector('iframe').contentWindow;w.__capturePlotZip=async(name,blob,files)=>{w.__plotTest={name,bytes:Array.from(new Uint8Array(await blob.arrayBuffer())),files:Object.keys(files)}};w.exportPublicationPlot(w.document.querySelector('.js-plotly-plot'))})()");
      await until("document.querySelector('iframe').contentWindow.__plotTest?.bytes.length>0");
      const exported=await evaluate("document.querySelector('iframe').contentWindow.__plotTest");
      fs.writeFileSync(path.join(OUTPUT_DIR,v+'-displayed-plot.zip'),Buffer.from(exported.bytes));
      record(v+'_displayed_zip_export',exported.files.includes('raw-records.csv')&&exported.files.includes('parameters.json')&&exported.bytes.length>100&&exported.bytes.length<10*1024*1024,exported.name);
    }
    await evaluate("select('v5','model')");
    record('deep_link_state',await evaluate("location.hash==='#v5/model'"));
    await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});await sleep(400);
    let shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(OUTPUT_DIR,'desktop.png'),Buffer.from(shot.data,'base64'));
    await send('Emulation.setDeviceMetricsOverride',{width:480,height:820,deviceScaleFactor:1,mobile:true});await evaluate("select('future','model')");await sleep(300);
    record('responsive_portal',await evaluate("document.documentElement.scrollWidth<=window.innerWidth+2"));
    shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(OUTPUT_DIR,'mobile.png'),Buffer.from(shot.data,'base64'));
    record('no_remote_requests',remote.length===0,JSON.stringify(remote));
    record('no_console_errors',errors.length===0,JSON.stringify(errors));
  }catch(error){record('harness_error',false,error.stack||String(error))}
  finally{try{ws?.close()}catch{}chrome.kill('SIGTERM');await sleep(300);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
  const report={mode:'HTTP with a project-site path prefix; HTTPS blocked',checks,console_errors:errors,remote_requests:remote,pass:checks.every(x=>x.pass)};
  fs.writeFileSync(path.join(OUTPUT_DIR,'browser_verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({pass:report.pass,checks:checks.length,failed:checks.filter(x=>!x.pass),console_errors:errors,remote_requests:remote},null,2));process.exit(report.pass?0:1)
}
main();
