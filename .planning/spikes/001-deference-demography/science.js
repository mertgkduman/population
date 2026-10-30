/* Browser/Node implementation. Same schema and equations as model.py. */
const Science = (() => {
  const numeric = ['sigma_I','sigma_A','bias_A','rho','mu_F_base','k_error','mu_A','S0','K_S','K_N','beta_const','beta_min','beta_gain','tau_learning','F_initial','A_initial','T','d','tau'];
  const positive = ['K_S','K_N','tau_learning','T','tau'];
  const nonnegative = ['sigma_I','sigma_A','mu_F_base','k_error','mu_A','S0','beta_const','beta_min','beta_gain','F_initial','A_initial'];
  function validate(p) {
    for (const k of numeric) if (!Number.isFinite(p[k])) return `${k} must be finite`;
    for (const k of positive) if (p[k] <= 0) return `${k} must be positive`;
    for (const k of nonnegative) if (p[k] < 0) return `${k} must be nonnegative`;
    if (p.d < 0 || p.d > 1 || p.rho < -1 || p.rho > 1) return 'd/rho out of range';
    if (!['copy','blend'].includes(p.policy) || !['M0','M1'].includes(p.model)) return 'unknown policy/model';
    return '';
  }
  function loss(p) {
    const d=p.d, i=p.sigma_I**2, a=p.sigma_A**2+p.bias_A**2;
    return p.policy==='copy' ? (1-d)*i+d*a : (1-d)**2*i+d*d*a+2*p.rho*d*(1-d)*p.sigma_I*p.sigma_A;
  }
  function muF(p) { return p.mu_F_base+p.k_error*loss(p); }
  function betaMax(p) { return p.model==='M0' ? p.beta_const : p.beta_min+p.beta_gain*p.tau/(p.tau+p.tau_learning); }
  function beta(p,n) { const s=p.S0/(1+n/p.K_N); return betaMax(p)*s/(p.K_S+s); }
  function dominant(m,u,v,b) { return .5*(-(m+u+v)+Math.sqrt((m+u-v)**2+4*m*b)); }
  function r0(p) { return dominant(1/p.tau,muF(p),p.mu_A,beta(p,0)); }
  function star(p) { if (r0(p)<=0) return 0; const need=p.mu_A*(1+muF(p)*p.tau); if (need===0) return null; return p.K_N*((p.S0/p.K_S)*(betaMax(p)/need-1)-1); }
  function invasion(mutant,resident) { const n=star(resident); return n>0 ? dominant(1/mutant.tau,muF(mutant),mutant.mu_A,beta(mutant,n)) : null; }
  function flux(p,f,a) { const b=beta(p,f+a)*a,d=muF(p)*f+p.mu_A*a,m=f/p.tau; return [b,d,m]; }
  function derivative(p,f,a) { const [b,,m]=flux(p,f,a); return [b-m-muF(p)*f,m-p.mu_A*a]; }
  function trajectory(p,step=.05,points=401,full=true) {
    const error=validate(p); if (error) return {error};
    let f=p.F_initial,a=p.A_initial; const steps=Math.max(1,Math.ceil(p.T/step)),h=p.T/steps;
    const out={t:[],F:[],A:[],N:[],follower_fraction:[],adult_fraction:[],B:[],D:[],M:[],net:[],per_capita:[]};
    const stride=Math.max(1,Math.floor(steps/(points-1)));
    function save(t) { const [b,d,m]=flux(p,f,a),n=f+a; out.t.push(t);out.F.push(f);out.A.push(a);out.N.push(n);out.follower_fraction.push(n>0?f/n:null);out.adult_fraction.push(n>0?a/n:null);out.B.push(b);out.D.push(d);out.M.push(m);out.net.push(b-d);out.per_capita.push(n>0?(b-d)/n:null); }
    if (full) save(0);
    for (let i=0;i<steps;i++) {
      const k1=derivative(p,f,a),k2=derivative(p,f+h*k1[0]/2,a+h*k1[1]/2),k3=derivative(p,f+h*k2[0]/2,a+h*k2[1]/2),k4=derivative(p,f+h*k3[0],a+h*k3[1]);
      f+=h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6;
      a+=h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6;
      if (!Number.isFinite(f+a)||f < -1e-8||a < -1e-8) return {error:'integration failed; result missing'};
      if (full && ((i+1)%stride===0 || i===steps-1)) save((i+1)*h);
    }
    return full ? out : {F:f,A:a,N:f+a};
  }
  return {validate,loss,muF,betaMax,beta,dominant,r0,star,invasion,flux,trajectory};
})();
if (typeof module !== 'undefined') module.exports=Science;
