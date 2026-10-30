"""Independent solver, invariance, limiting-case and stochastic-path checks."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import importlib.util,json,sys,time
from dataclasses import replace,asdict
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm,eigvals
from model import *
from invasion import run_invasion
ROOT=Path(__file__).resolve().parent
checks=[]
def check(name,ok,detail=None):
    checks.append({'name':name,'pass':bool(ok),'detail':detail});print(name,bool(ok),flush=True)
def reference(c,d,tau,segments):
    x=initial(c);t=0.;calls=0
    for j,(start,theta,pi) in enumerate(segments):
        end=segments[j+1][0] if j+1<len(segments) else c.T
        sol=solve_ivp(lambda t,y:rhs(c,y.reshape(x.shape),[d],[tau],theta,pi).ravel(),(start,end),x.ravel(),method='DOP853',rtol=1e-10,atol=1e-12)
        if not sol.success:raise ValueError(sol.message)
        x=sol.y[:,-1].reshape(x.shape);calls+=sol.nfev
    return x,calls
def main():
    c=Config(T=60);x=initial(c,3);d=np.array([0,.5,1.]);tau=np.array([.5,3,12.]);v=rhs(c,x,d,tau);met=metrics(c,x,d,tau)
    err=np.max(abs(v.sum((1,2,3))-(met['B']-met['D'])))
    check('birth/death accounting excludes maturation and learning',err<1e-12,float(err))
    check('absorbing all-zero population',np.max(abs(rhs(c,np.zeros_like(x),d,tau)))==0)
    neutral=replace(c,nu_private=0,nu_social=0,nu_adult=0,mu_F=0,mu_A=0,error_F=0,error_A=0,beta_base=0,beta_skill=0)
    rng=np.random.default_rng(66331);x0=rng.random(x.shape)
    r=run(neutral,d,tau,points=11,x0=x0)
    ef=x0[:,0]*np.exp(-neutral.T/tau)[:,None,None];ea=x0[:,1]+x0[:,0]-ef
    error=float(np.max(abs(r['final_state']-np.stack([ef,ea],axis=1))))
    check('state-preserving irreversible maturation exact solution',error<1e-9,error)
    check('maturation conserves population',np.max(abs(r['N']-r['N'][:,0,None]))<1e-10)
    check('no adult-to-juvenile flow',np.all(rhs(neutral,np.stack([np.zeros_like(x[:,0]),x[:,1]],axis=1),d,tau)[:,0]==0))
    for eta in [0.,.1,1.]:
        cc=replace(c,plasticity_A=eta)
        seg=stochastic_segments(cc,.2,65002);rr=run(cc,d,tau,seg,points=31)
        check('nonnegative states eta '+str(eta),float(rr['states'].min())>=-1e-12,float(rr['states'].min()))
        check('d=0 private and conviction ledger coincide eta '+str(eta),np.max(abs(rr['states'][0,:,:,~np.eye(2*c.H+1,dtype=bool)]))==0)
    mirrored=initial(c)[:,:,::-1,::-1]
    rp=run(c,[.75],[3],points=2);rm=run(c,[.75],[3],segments=[(0,-1,1-c.p)],points=2,x0=mirrored)
    err=float(np.max(abs(rp['final_state']-rm['final_state'][:,:,::-1,::-1])))
    check('opposite fixed environments are sign-symmetric',err<1e-10,err)
    check('kappa=0 independent of seed',stochastic_segments(c,0,1)==stochastic_segments(c,0,2))
    ss=stochastic_segments(c,.2,65002);same=stochastic_segments(replace(c,plasticity_A=1),.2,65002)
    check('environmental paths shared across plasticity',ss==same)
    first=np.random.default_rng(65002).exponential(5.)
    check('continuous-time first switch matches exponential draw',ss[1][0]==first)
    invalid=0
    for cc,dd,tt,rate in [(replace(c,plasticity_A=-.1),0,1,0),(replace(c,plasticity_F=1.1),0,1,0),(c,-.1,1,0),(c,1,0,0),(c,0,1,-1)]:
        try:validate(cc,np.array([dd]),np.array([tt]));stochastic_segments(cc,rate,1)
        except ValueError:invalid+=1
    check('invalid parameter ranges rejected',invalid==5)
    nc=replace(c,payoff=False,query_cost=0)
    a=run(nc,[0],[3],[(0,1,c.p)],points=16)
    b=run(replace(nc,plasticity_A=0),[1],[3],ss,points=16)
    check('neutral demographic invariance to d/plasticity/environment',np.max(abs(a['N']-b['N']))<1e-8,float(np.max(abs(a['N']-b['N']))))
    # Independent two-stage constant-resource matrix benchmark.
    cc=replace(nc,nu_private=0,nu_adult=0,nu_social=0);env=np.array([.5,.5,1.]);g=np.array([[-1/3-cc.mu_F,.5*cc.beta_base],[1/3,-cc.mu_A]])
    rr=run(cc,[0],[3],fixed_env=env,points=2);exact=expm(g*cc.T)@np.array([80.,20.]);got=np.r_[rr['F'][0,-1],rr['A'][0,-1]]
    check('constant-resource matrix exponential',np.max(abs(got-exact))<1e-6,float(np.max(abs(got-exact))))
    big=generator(cc,0,3,env);check('dominant eigenvalue agrees with two-stage matrix',abs(eigvals(big).real.max()-eigvals(g).real.max())<1e-10)
    # Reuse is audited against unmodified V5 when plasticity is one.
    path=ROOT.parents[1]/'v5/experiments/model.py';spec=importlib.util.spec_from_file_location('v5_reference',path);old=importlib.util.module_from_spec(spec);sys.modules['v5_reference']=old;spec.loader.exec_module(old)
    cc=replace(c,plasticity_A=1);kw=asdict(cc);kw.pop('plasticity_F');kw.pop('plasticity_A');oc=old.Config(**kw)
    check('eta_F=eta_A=1 exactly reproduces V5 RHS',np.max(abs(rhs(cc,x,d,tau)-old.rhs(oc,x,d,tau)))==0)
    errors=[]
    for dd,tt,eta in [(0.,.5,.1),(1.,12.,.1),(.5,3.,0.),(.5,3.,1.)]:
        cc=replace(c,plasticity_A=eta);seg=stochastic_segments(cc,.2,65002);ref,nf=reference(cc,dd,tt,seg)
        coarse=run(cc,[dd],[tt],seg,points=16)['final_state'];fine=run(replace(cc,dt=.05),[dd],[tt],seg,points=16)['final_state']
        scale=max(1.,float(ref.max()));e=float(np.max(abs(coarse-ref)));e2=float(np.max(abs(fine-ref)));ratio=e/e2 if e2 else None
        errors.append({'d':dd,'tau':tt,'eta_A':eta,'max_abs':e,'max_scaled':e/scale,'half_max_abs':e2,'halving_ratio':ratio,'reference_evaluations':nf})
        check('DOP853 and halving d='+str(dd)+' tau='+str(tt)+' eta='+str(eta),e/scale<2e-6 and (e2<e/7 or e<1e-10),errors[-1])
    cc=replace(c,T=200);seg=stochastic_segments(cc,.05,65003);ts=np.linspace(0,200,51)
    lg,rn=run_invasion(cc,np.array([.5,0.,1.]),np.array([3.,3.,3.]),seg,ts)
    err=float(np.max(abs(lg[0]-np.log(rn/100))))
    check('self-mutant relative neutrality in common stochastic environment',err<1e-11,err)
    # Full fixed-equilibrium convergence plus independent cultural sign reversal.
    eq=equilibrium(c,.5,3)
    check('fixed-environment equilibrium full residual',eq['residual']<1e-8,{k:float(eq[k]) for k in ['N','residual','self_rate']})
    check('equilibrium resident self-invasion',abs(eq['self_rate'])<1e-7,float(eq['self_rate']))
    report={'pass':all(x['pass'] for x in checks),'checks':checks,'solver':'DOP853 rtol=1e-10 atol=1e-12, exact segment restarts; RK4 dt=.1 and .05','errors':errors}
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['pass']:raise SystemExit(1)
if __name__=='__main__':main()
