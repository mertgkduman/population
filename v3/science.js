/* Browser/Node v3 model. Q and d are prescribed functions, not ODE states. */
const Science=(()=>{
 const numeric=['sigma_I','sigma_A0','bias_A','rho','mu_F_base','k_error','mu_A','S0','K_S','K_N','beta_const','beta_min','beta_gain','tau_learning','F_initial','A_initial','T','d0','d_floor','tau','lambda_d','Q0','Q_max','lambda_Q'];
 const positive=['K_S','K_N','tau_learning','T','tau'];const nonnegative=['sigma_I','sigma_A0','mu_F_base','k_error','mu_A','S0','beta_const','beta_min','beta_gain','F_initial','A_initial','d0','d_floor','lambda_d','Q0','Q_max','lambda_Q'];
 function validate(p){for(const k of numeric)if(!Number.isFinite(p[k]))return `${k} must be finite`;for(const k of positive)if(p[k]<=0)return `${k} must be positive`;for(const k of nonnegative)if(p[k]<0)return `${k} must be nonnegative`;if(!(0<=p.d_floor&&p.d_floor<=p.d0&&p.d0<=1))return 'require 0≤d_floor≤d0≤1';if(p.Q_max<p.Q0)return 'Qmax must be at least Q0';if(p.rho< -1||p.rho>1)return 'rho out of range';if(!['copy','blend'].includes(p.policy)||!['M0','M1'].includes(p.model))return 'unknown policy/model';return ''}
 function d(t,p,d0=p.d0){return p.d_floor+(d0-p.d_floor)*Math.exp(-p.lambda_d*t)}
 function Q(t,p){return p.Q0+(p.Q_max-p.Q0)*(1-Math.exp(-p.lambda_Q*t))}
 function sigmaA(t,p){return p.sigma_A0*(1+p.Q0)/(1+Q(t,p))}
 function loss(t,p,d0=p.d0){const w=d(t,p,d0),s=sigmaA(t,p),i=p.sigma_I*p.sigma_I,a=s*s+p.bias_A*p.bias_A;return p.policy==='copy'?(1-w)*i+w*a:(1-w)**2*i+w*w*a+2*p.rho*w*(1-w)*p.sigma_I*s}
 function muF(t,p,d0=p.d0){return p.mu_F_base+p.k_error*loss(t,p,d0)}
 function betaMax(p,tau=p.tau){return p.model==='M0'?p.beta_const:p.beta_min+p.beta_gain*tau/(tau+p.tau_learning)}
 function beta(n,p,tau=p.tau){const s=p.S0/(1+n/p.K_N);return betaMax(p,tau)*s/(p.K_S+s)}
 function rInst(t,p){const m=1/p.tau,u=muF(t,p),v=p.mu_A,b=beta(0,p);return .5*(-(m+u+v)+Math.sqrt((m+u-v)**2+4*m*b))}
 function flux(t,F,A,p){const B=beta(F+A,p)*A,D=muF(t,p)*F+p.mu_A*A,M=F/p.tau;return [B,D,M]}
 function deriv(t,F,A,p){const [B,,M]=flux(t,F,A,p);return [B-M-muF(t,p)*F,M-p.mu_A*A]}
 function trajectory(p,step=.05,points=401,full=true){const error=validate(p);if(error)return {error};let F=p.F_initial,A=p.A_initial;const steps=Math.max(1,Math.ceil(p.T/step)),h=p.T/steps,stride=Math.max(1,Math.floor(steps/(points-1)));const out={t:[],F:[],A:[],N:[],B:[],D:[],M:[],net:[],per_capita:[],d:[],Q:[],sigma_A:[],loss:[],mu_F:[],r_inst:[]};function save(t){const [B,D,M]=flux(t,F,A,p),N=F+A;for(const [k,v] of Object.entries({t,F,A,N,B,D,M,net:B-D,per_capita:N>0?(B-D)/N:null,d:d(t,p),Q:Q(t,p),sigma_A:sigmaA(t,p),loss:loss(t,p),mu_F:muF(t,p),r_inst:rInst(t,p)}))out[k].push(v)}if(full)save(0);for(let i=0;i<steps;i++){const t=i*h,k1=deriv(t,F,A,p),k2=deriv(t+h/2,F+h*k1[0]/2,A+h*k1[1]/2,p),k3=deriv(t+h/2,F+h*k2[0]/2,A+h*k2[1]/2,p),k4=deriv(t+h,F+h*k3[0],A+h*k3[1],p);F+=h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6;A+=h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6;if(!Number.isFinite(F+A)||F< -1e-8||A< -1e-8)return {error:'integration failed; result missing'};if(full&&((i+1)%stride===0||i===steps-1))save((i+1)*h)}return full?out:{F,A,N:F+A}}
 return {validate,d,Q,sigmaA,loss,muF,betaMax,beta,rInst,flux,trajectory};
})();if(typeof module!=='undefined')module.exports=Science;
