/* Offline Chrome DevTools verification; no remote libraries or page network. */
const fs=require('fs'),path=require('path'),os=require('os'),net=require('net'),{spawn}=require('child_process');
const chrome='/hpc/home/mg551/.agent-browser/browsers/chrome-154.0.8037.92/chrome';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function freePort(){return await new Promise((res,rej)=>{const s=net.createServer();s.listen(0,'127.0.0.1',()=>{const p=s.address().port;s.close(()=>res(p))});s.on('error',rej)})}
async function main(){
 const port=await freePort(),profile=fs.mkdtempSync(path.join(os.tmpdir(),'deference-chrome-'));
 const proc=spawn(chrome,['--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--disable-background-networking','--no-first-run','--disable-extensions','--remote-allow-origins=*',`--remote-debugging-port=${port}`,`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
 let ws,errors=[],remote=[],results=[];
 const record=(name,pass,detail='')=>results.push({name,pass:!!pass,detail});
 try{
  let pages=[];for(let i=0;i<100;i++){try{pages=await (await fetch(`http://127.0.0.1:${port}/json`)).json();if(pages.some(x=>x.type==='page'))break}catch{}await sleep(100)}
  const page=pages.find(x=>x.type==='page');if(!page)throw Error('Chrome DevTools page unavailable');
  ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.addEventListener('open',res,{once:true});ws.addEventListener('error',rej,{once:true})});
  let seq=0;const pending=new Map();ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(Error(m.error.message)):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);else if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errors.push(m.params.entry.text);else if(m.method==='Network.requestWillBeSent'&&/^https?:/.test(m.params.request.url))remote.push(m.params.request.url)});
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(Error(method+' timeout'))}},20000)});
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value};
  async function until(expression,ms=20000){const start=Date.now();while(Date.now()-start<ms){try{if(await evaluate(expression))return true}catch{}await sleep(100)}return false}
  await send('Runtime.enable');await send('Log.enable');await send('Network.enable');await send('Network.setBlockedURLs',{urls:['http://*','https://*']});await send('Page.enable');
  await send('Page.navigate',{url:'file://'+path.join(__dirname,'index.html')});
  record('offline_load',await until("document.readyState==='complete' && typeof Plotly!=='undefined' && document.getElementById('Fview').textContent!=='—'",30000));
  record('analytic_map_render',await until("typeof mapComplete!=='undefined' && mapComplete && document.getElementById('heatmap').data?.length>0",30000));
  record('only_local_requests',remote.length===0,JSON.stringify(remote));
  const initial=await evaluate("({F:document.getElementById('Fview').textContent,A:document.getElementById('Aview').textContent,N:series.N[0],map:document.getElementById('mapStatus').textContent})");record('initial_trajectory',Number(initial.F)>0&&Number(initial.A)>0&&Math.abs(initial.N-100)<1e-12,JSON.stringify(initial));
  const fixtures=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures.json'),'utf8'));let browserAbs=0,browserScaled=0,browserHalf=0;
  for(const x of fixtures){const result=await evaluate(`(()=>{const q=${JSON.stringify(x.config)},coarse=Science.trajectory(q,.05,401,true),fine=Science.trajectory(q,.025,401,true);return {coarse:{F:coarse.F,A:coarse.A},fine:{F:fine.F,A:fine.A}}})()`);for(const key of ['F','A'])for(let i=0;i<x.t.length;i++){const a=Math.abs(result.coarse[key][i]-x[key][i]);browserAbs=Math.max(browserAbs,a);browserScaled=Math.max(browserScaled,a/Math.max(1,Math.abs(x[key][i])));browserHalf=Math.max(browserHalf,Math.abs(result.coarse[key][i]-result.fine[key][i])/Math.max(1,Math.abs(x[key][i])));}}
  record('browser_scipy_trajectory_parity',browserScaled<=2e-5,`12 cases; max absolute=${browserAbs}; max scaled=${browserScaled}; denominator=max(1,|reference state|)`);
  record('browser_rk4_step_halving',browserHalf<=2e-5,`max scaled h=0.05 vs 0.025: ${browserHalf}`);
  await evaluate("document.getElementById('play').click()");await sleep(450);const moving=await evaluate('cursor');record('play_advances',moving>0,`cursor=${moving}`);
  await evaluate("document.getElementById('pause').click()");await sleep(350);record('pause_stops',(await evaluate('cursor'))===moving);
  await evaluate("document.getElementById('scrub').value='200';document.getElementById('scrub').dispatchEvent(new Event('input'))");record('scrub_sync',(await evaluate('cursor'))===200 && (await evaluate("document.getElementById('timeLabel').textContent")).includes('100'));
  await evaluate("document.getElementById('restart').click()");record('reset_time',(await evaluate('cursor'))===0);
  const before=await evaluate('p.d');await evaluate("document.getElementById('heatmap').emit('plotly_click',{points:[{x:1,y:.5}]})");record('heatmap_selection',await until('p.d===1 && Math.abs(p.tau-.5)<1e-12'),`before=${before}`);
  await evaluate("document.getElementById('matched').click()");record('three_pins',(await evaluate("document.querySelectorAll('#pins tbody tr').length"))>=3);
  await evaluate("document.getElementById('pinResident').click();document.getElementById('metric').value='invasion';document.getElementById('metric').dispatchEvent(new Event('change'))");record('invasion_map',await until("mapComplete && document.getElementById('heatmap').data?.length>0"));
  record('resident_self_invasion',Math.abs(await evaluate('Science.invasion(resident,resident)'))<1e-10);
  await evaluate("document.getElementById('metric').value='rT';document.getElementById('metric').dispatchEvent(new Event('change'))");record('numerical_map',await until('mapComplete',30000));
  const preserved=await evaluate("({F:p.F_initial,A:p.A_initial,model:p.model,T:p.T,K:p.K_N})");
  await evaluate("document.getElementById('metric').value='r0';document.getElementById('metric').dispatchEvent(new Event('change'));document.getElementById('scenario').value='noisy';document.getElementById('scenario').dispatchEvent(new Event('change'))");
  record('scenario_preserves_demography',await evaluate(`p.F_initial===${preserved.F} && p.A_initial===${preserved.A} && p.model==='${preserved.model}' && p.T===${preserved.T} && p.K_N===${preserved.K} && p.sigma_A===2`));
  record('resident_invalidated_on_scenario_change',await evaluate('resident===null'));
  record('r0_boundary_visible',await until("mapComplete && document.getElementById('heatmap').data?.[1]?.x?.length>0"));
  await evaluate("document.getElementById('policy').value='blend';document.getElementById('policy').dispatchEvent(new Event('change'));document.getElementById('model').value='M1';document.getElementById('model').dispatchEvent(new Event('change'))");
  record('policy_model_controls',await evaluate("p.policy==='blend' && p.model==='M1' && series.N.length>0"));
  await evaluate("const dt=new DataTransfer();dt.items.add(new File([JSON.stringify({config:{...p,d:.2}})],'import.json',{type:'application/json'}));document.getElementById('importConfig').files=dt.files;document.getElementById('importConfig').dispatchEvent(new Event('change'))");
  record('configuration_import',await until('p.d===.2'));
  await evaluate("document.getElementById('metric').value='rT';document.getElementById('grid').value='51';document.getElementById('metric').dispatchEvent(new Event('change'));document.getElementById('cancel').click();document.getElementById('metric').value='r0';document.getElementById('metric').dispatchEvent(new Event('change'))");
  record('cancel_restart_no_stale_map',await until("mapComplete && document.getElementById('mapStatus').textContent.includes('analytic cells')"));
  await evaluate("document.getElementById('metric').value='r0';document.getElementById('metric').dispatchEvent(new Event('change'))");await until('mapComplete');
  await evaluate("window.__exports=[];download=(name,text,type)=>window.__exports.push({name,text,type});document.getElementById('exportConfig').click();document.getElementById('exportSweep').click();document.getElementById('exportSweepJson').click();document.getElementById('exportSeries').click();document.getElementById('exportSeriesJson').click()");
  const exported=await evaluate("window.__exports.map(x=>({name:x.name,bytes:x.text.length,hasRun:x.text.includes(RUN_ID),hasSimulation:x.text.includes('simulation data')}))");record('exports',exported.length===5&&exported.every(x=>x.bytes>100&&x.hasRun&&x.hasSimulation),JSON.stringify(exported));
  await send('Emulation.setDeviceMetricsOverride',{width:480,height:800,deviceScaleFactor:1,mobile:true});await sleep(250);record('responsive_layout',await evaluate("document.documentElement.scrollWidth<=window.innerWidth+2 && getComputedStyle(document.querySelector('.layout')).gridTemplateColumns.split(' ').length===1"));
  const screenshot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(__dirname,'browser_screenshot.png'),Buffer.from(screenshot.data,'base64'));
  record('browser_console_errors',errors.length===0,JSON.stringify(errors));
 }catch(e){record('harness_error',false,e.stack||String(e))}finally{try{ws?.close()}catch{}proc.kill('SIGTERM');await sleep(300);try{fs.rmSync(profile,{recursive:true,force:true})}catch{}}
 const report={browser:'Chrome for Testing 154.0.8037.92',mode:'file:// with HTTP(S) blocked',checks:results,console_errors:errors,remote_requests:remote,pass:results.every(x=>x.pass)};
 fs.writeFileSync(path.join(__dirname,'browser_verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));if(!report.pass)process.exitCode=1;
}
main();
