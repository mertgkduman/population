/* The v2 browser model: two demographic ODEs, externally prescribed sigma_A(t). */
const Science=(()=>{
  const numeric=['sigma_I','sigma_A','bias_A','rho','mu_F_base','k_error','mu_A','S0','K_S','K_N','beta_const','beta_min','beta_gain','tau_learning','F_initial','A_initial','T','d','tau','drift_rate','sigma_floor','sigma_ceiling'];
  const positive=['K_S','K_N','tau_learning','T','tau','sigma_ceiling'];
  const nonnegative=['sigma_I','sigma_A','mu_F_base','k_error','mu_A','S0','beta_const','beta_min','beta_gain','F_initial','A_initial','sigma_floor'];
  function validate(p){for(const k of numeric)if(!Number.isFinite(p[k]))return `${k} must be finite`;for(const k of positive)if(p[k]<=0)return `${k} must be positive`;for(const k of nonnegative)if(p[k]<0)return `${k} must be nonnegative`;if(p.d<0||p.d>1||p.rho< -1||p.rho>1)return 'd/rho out of range';if(p.sigma_floor>p.sigma_A||p.sigma_A>p.sigma_ceiling)return 'sigma bounds must contain initial adult sigma';if(!['copy','blend'].includes(p.policy)||!['M0','M1'].includes(p.model))return 'unknown policy/model';return ''}
  function sigmaA(t,p){return Math.max(p.sigma_floor,Math.min(p.sigma_ceiling,p.sigma_A*Math.exp(Math.max(-700,Math.min(700,-p.drift_rate*t)))))}
  function loss(t,p,d=p.d){const s=sigmaA(t,p),i=p.sigma_I*p.sigma_I,a=s*s+p.bias_A*p.bias_A;return p.policy==='copy'?(1-d)*i+d*a:(1-d)**2*i+d*d*a+2*p.rho*d*(1-d)*p.sigma_I*s}
  function muF(t,p,d=p.d){return p.mu_F_base+p.k_error*loss(t,p,d)}
  function betaMax(p,tau=p.tau){return p.model==='M0'?p.beta_const:p.beta_min+p.beta_gain*tau/(tau+p.tau_learning)}
  function beta(n,p,tau=p.tau){const s=p.S0/(1+n/p.K_N);return betaMax(p,tau)*s/(p.K_S+s)}
  function rInst(t,p){const m=1/p.tau,u=muF(t,p),v=p.mu_A,b=beta(0,p);return .5*(-(m+u+v)+Math.sqrt((m+u-v)**2+4*m*b))}
  function flux(t,f,a,p){const b=beta(f+a,p)*a,d=muF(t,p)*f+p.mu_A*a,m=f/p.tau;return [b,d,m]}
  function deriv(t,f,a,p){const [b,,m]=flux(t,f,a,p);return [b-m-muF(t,p)*f,m-p.mu_A*a]}
  function trajectory(p,step=.05,points=401,full=true){const error=validate(p);if(error)return {error};let f=p.F_initial,a=p.A_initial;const steps=Math.max(1,Math.ceil(p.T/step)),h=p.T/steps,stride=Math.max(1,Math.floor(steps/(points-1)));const out={t:[],F:[],A:[],N:[],B:[],D:[],M:[],net:[],per_capita:[],sigma_A:[],loss:[],mu_F:[],r_inst:[]};function save(t){const [b,d,m]=flux(t,f,a,p),n=f+a;for(const [k,v] of Object.entries({t,F:f,A:a,N:n,B:b,D:d,M:m,net:b-d,per_capita:n>0?(b-d)/n:null,sigma_A:sigmaA(t,p),loss:loss(t,p),mu_F:muF(t,p),r_inst:rInst(t,p)}))out[k].push(v)}if(full)save(0);for(let i=0;i<steps;i++){const t=i*h,k1=deriv(t,f,a,p),k2=deriv(t+h/2,f+h*k1[0]/2,a+h*k1[1]/2,p),k3=deriv(t+h/2,f+h*k2[0]/2,a+h*k2[1]/2,p),k4=deriv(t+h,f+h*k3[0],a+h*k3[1],p);f+=h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6;a+=h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6;if(!Number.isFinite(f+a)||f< -1e-8||a< -1e-8)return {error:'integration failed; cell missing'};if(full&&((i+1)%stride===0||i===steps-1))save((i+1)*h)}return full?out:{F:f,A:a,N:f+a}}
  return {validate,sigmaA,loss,muF,betaMax,beta,rInst,flux,trajectory};
})();
if(typeof module!=='undefined')module.exports=Science;
