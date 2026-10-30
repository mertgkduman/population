"""Export any v3 sweep slice from compressed NPZ to CSV."""
import argparse,csv,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent

def index(values,want):
    i=int(np.argmin(abs(values-want)))
    if abs(float(values[i])-want)>1e-12:raise ValueError(f'{want} is not on the saved grid: {values.tolist()}')
    return i

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scenario',default='helpful');p.add_argument('--policy',choices=['copy','blend'],default='copy');p.add_argument('--model',choices=['M0','M1'],default='M0')
    p.add_argument('--lambda-d',type=float,default=.005);p.add_argument('--lambda-q',type=float,default=.005);p.add_argument('--horizon',type=float,default=200);p.add_argument('--out',default='slice.csv',help='CSV path or - for stdout')
    a=p.parse_args();data=np.load(ROOT/'sweep.npz');sc=list(data['scenarios']);pol=list(data['policies']);models=list(data['models'])
    si=sc.index(a.scenario);pi=pol.index(a.policy);mi=models.index(a.model);di=index(data['lambda_d'],a.lambda_d);qi=index(data['lambda_Q'],a.lambda_q);hi=index(data['horizons'],a.horizon)
    # Read each compressed member once; repeated data['F'] access decompresses the whole array.
    F=data['F'][si,pi,mi,di,qi,:,:,hi];A=data['A'][si,pi,mi,di,qi,:,:,hi];N=data['N'][si,pi,mi,di,qi,:,:,hi];rT=data['r_T'][si,pi,mi,di,qi,:,:,hi]
    f=sys.stdout if a.out=='-' else open(a.out,'w',newline='')
    try:
        f.write('# simulation data; '+json.dumps({'run_id':str(data['run_id']),'scenario':a.scenario,'policy':a.policy,'model':a.model,'lambda_d':a.lambda_d,'lambda_Q':a.lambda_q,'horizon':a.horizon,'units':{'time':'model time','population':'population density','rate':'1/model time'}})+'\n')
        w=csv.writer(f);w.writerow(['d0','tau_model_time','F_T_density','A_T_density','N_T_density','r_T_per_time'])
        for i,d0 in enumerate(data['d0']):
            for j,tau in enumerate(data['tau']):
                w.writerow([float(d0),float(tau),float(F[i,j]),float(A[i,j]),float(N[i,j]),float(rT[i,j])])
    finally:
        if f is not sys.stdout:f.close()

if __name__=='__main__':main()
