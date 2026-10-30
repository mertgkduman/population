/* Run the exact browser science.js in Node against SciPy fixtures. */
const fs=require('fs'); const Science=require('./science.js');
const fixtures=JSON.parse(fs.readFileSync('fixtures.json','utf8'));
const cases=[]; let maxScaled=0,maxAbs=0,maxHalf=0,maxAnalytic=0;
for (const x of fixtures) {
  const coarse=Science.trajectory(x.config,.05,401,true),fine=Science.trajectory(x.config,.025,401,true);
  if (coarse.error||fine.error) throw Error(coarse.error||fine.error);
  let absolute=0,scaled=0,halving=0;
  for(let i=0;i<x.t.length;i++) for(const key of ['F','A']) {
    const a=Math.abs(coarse[key][i]-x[key][i]); absolute=Math.max(absolute,a);scaled=Math.max(scaled,a/Math.max(1,Math.abs(x[key][i])));
    halving=Math.max(halving,Math.abs(coarse[key][i]-fine[key][i])/Math.max(1,Math.abs(x[key][i])));
  }
  const q=x.config,e=x.expected,analytical=[Math.abs(Science.loss(q)-e.loss),Math.abs(Science.muF(q)-e.mu_F),Math.abs(Science.r0(q)-e.r0),Math.abs(Science.star(q)-e.N_star)];if(e.self_invasion!==null)analytical.push(Math.abs(Science.invasion(q,q)-e.self_invasion));const analytic=Math.max(...analytical);maxAnalytic=Math.max(maxAnalytic,analytic);
  cases.push({model:q.model,policy:q.policy,d:q.d,tau:q.tau,max_absolute_error:absolute,max_scaled_error:scaled,max_step_halving_scaled:halving,max_analytic_error:analytic});
  maxAbs=Math.max(maxAbs,absolute);maxScaled=Math.max(maxScaled,scaled);maxHalf=Math.max(maxHalf,halving);
}
fs.writeFileSync('browser_parity.json',JSON.stringify({engine:'Node executing browser science.js',cases,max_absolute_error:maxAbs,max_scaled_error:maxScaled,max_halving_scaled:maxHalf,max_analytic_error:maxAnalytic,step:.05,half_step:.025,relative_denominator:'max(1, |reference state|)'},null,2)+'\n');
console.log(`JS/SciPy scaled error ${maxScaled}; step halving ${maxHalf}`);
