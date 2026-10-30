/* Real Chrome interactions and exports, with external HTTP(S) blocked. */
'use strict';
const fs=require('fs'),os=require('os'),path=require('path'),{spawn}=require('child_process'),net=require('net');
const URL=process.env.V6_URL||'file://'+path.join(__dirname,'index.html'),CHROME=process.env.CHROME_BIN||'/hpc/home/mg551/.agent-browser/browsers/chrome-154.0.8037.92/chrome';
const sleep=t=>new Promise(r=>setTimeout(r,t));
async function main(){
 const port=await new Promise(r=>{const s=net.createServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>r(p))})}),profile=fs.mkdtempSync(path.join(os.tmpdir(),'v6-browser-'));
 const chrome=spawn(CHROME,['--headless=new','--no-sandbox','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
 const checks=[],errors=[],remote=[];let ws;
 const record=(name,pass,detail=null)=>checks.push({name,pass:!!pass,detail});
 try{
  let pages;for(let i=0;i<200;i++){try{pages=await(await fetch(`http://127.0.0.1:${port}/json`)).json();if(pages.length)break}catch{}await sleep(100)}
  ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);await new Promise(r=>ws.addEventListener('open',r,{once:true}));let seq=0;const pending=new Map();
  ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);else if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errors.push(m.params.entry.text);else if(m.method==='Network.requestWillBeSent'&&/^https?:/.test(m.params.request.url)&&!m.params.request.url.startsWith('http://127.0.0.1:'))remote.push(m.params.request.url)});
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
  const ev=async expression=>{const v=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(v.exceptionDetails)throw Error(v.exceptionDetails.exception?.description||v.exceptionDetails.text);return v.result.value};
  async function until(s){for(let i=0;i<1200;i++){if(await ev(s))return true;await sleep(100)}return false}
  await send('Runtime.enable');await send('Log.enable');await send('Network.enable');await send('Network.setBlockedURLs',{urls:['https://*','http://*']});await send('Page.enable');await send('Page.navigate',{url:URL});
  record('offline_embedded_data_and_plots',await until("window.AppState?.ready&&document.querySelectorAll('.js-plotly-plot').length===9&&document.getElementById('heldoutPlot').data?.length===1"));
  record('all_contexts_and_grid',await ev("V6Data.contexts.length===12&&V6Data.ds.length===9&&V6Data.taus.length===11"));
  await ev("document.getElementById('traitMap').emit('plotly_click',{points:[{x:1,y:12}]})");
  record('heatmap_click_loads_correct_pair',await ev("AppState.di===8&&AppState.ti===10&&JSON.parse(document.getElementById('configView').textContent).d===1"));
  record('logarithmic_tau_axis',await ev("document.getElementById('traitMap').layout.yaxis.type==='log'"));
  await ev("document.getElementById('metric').value='invasion_relative';document.getElementById('metric').dispatchEvent(new Event('change'))");
  record('signed_invasion_map_centered_at_zero',await ev("document.getElementById('traitMap').data[0].zmin===-document.getElementById('traitMap').data[0].zmax&&document.getElementById('traitMap').data[0].zmid===0"));
  await ev("document.getElementById('plasticity').value='0.55';document.getElementById('kappa').value='0.01';document.getElementById('plasticity').dispatchEvent(new Event('change'))");
  record('scenario_controls_select_saved_context',await ev("JSON.parse(document.getElementById('configView').textContent).parameters.context_A===.55&&JSON.parse(document.getElementById('configView').textContent).kappa===.01"));
  await ev("document.getElementById('scrub').value=37;document.getElementById('scrub').dispatchEvent(new Event('input'))");
  record('scrub_synchronizes_population_and_cursor',await ev("AppState.cursor===37&&document.getElementById('timeOut').textContent==='296'&&document.getElementById('populationPlot').layout.shapes[0].x0===296"));
  await ev("document.getElementById('resetTime').click();document.getElementById('play').click()");await sleep(650);
  record('play_advances_time',await ev('AppState.cursor>0&&AppState.playing'));
  await ev("document.getElementById('pause').click();window.pausedCursor=AppState.cursor");await sleep(400);
  record('pause_stops_time',await ev('AppState.cursor===pausedCursor&&!AppState.playing'));
  await ev("document.getElementById('matched').click()");record('three_matched_tau_comparisons',await ev("document.getElementById('comparisonPlot').data.length===3"));
  await ev("document.getElementById('pin').click()");record('pin_adds_fourth_population',await ev("document.getElementById('comparisonPlot').data.length===4"));
  record('map_and_dense_curve_uncertainty_are_visible',await ev("document.getElementById('heldoutPlot').data[0].error_y.visible&&document.getElementById('heldoutPlot').data[0].x.length===33"));
  await ev("window.captured=[];window.__captureDownload=(name,text)=>captured.push({name,text});document.getElementById('exportConfig').click();document.getElementById('exportSweep').click();document.getElementById('exportSeries').click()");
  const exports=await ev('captured');for(const e of exports)fs.writeFileSync(path.join(__dirname,e.name),e.text);
  record('configuration_and_data_exports',exports.length===3&&JSON.parse(exports[0].text).units.time==='model_time'&&exports[1].text.split('\n').length===100&&exports[2].text.split('\n').length===77);
  record('every_plot_has_raw_data_download',await until("[...document.querySelectorAll('.js-plotly-plot')].every(g=>g.nextElementSibling?.classList.contains('publication-download'))"));
  await ev("window.__capturePlotZip=async(name,blob,files)=>{window.zipTest={name,bytes:blob.size,files:Object.keys(files)}};exportPublicationPlot(document.getElementById('traitMap'))");
  record('displayed_plot_zip_export',await until("window.zipTest?.bytes>100&&zipTest.files.includes('raw-records.csv')"));
  await ev("document.getElementById('resetConfig').click()");record('reset_restores_defaults',await ev("AppState.di===4&&JSON.parse(document.getElementById('configView').textContent).parameters.context_A===.7&&JSON.parse(document.getElementById('configView').textContent).parameters.context_F===.9"));
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});await sleep(300);let shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(__dirname,'desktop.png'),Buffer.from(shot.data,'base64'));
  await send('Emulation.setDeviceMetricsOverride',{width:480,height:820,deviceScaleFactor:1,mobile:true});await sleep(350);
  record('mobile_layout_no_horizontal_overflow',await ev('document.documentElement.scrollWidth<=window.innerWidth+2'));
  shot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(__dirname,'mobile.png'),Buffer.from(shot.data,'base64'));
  record('no_console_errors',errors.length===0,errors);record('no_external_requests',remote.length===0,remote);
 }catch(e){record('harness',false,e.stack)}finally{try{ws?.close()}catch{}chrome.kill('SIGTERM');await sleep(200);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
 const report={url:URL,mode:'all HTTP(S) blocked; actual file:// offline dashboard',checked_at:new Date().toISOString(),pass:checks.every(c=>c.pass),checks,console_errors:errors,remote_requests:remote};fs.writeFileSync(path.join(__dirname,'browser_verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({pass:report.pass,checks:checks.length,failed:checks.filter(c=>!c.pass)},null,2));process.exit(report.pass?0:1)
}
main();
