"""Do tren CA 4 KENH bung de doi chieu voi giao thuc 'chi kenh tot nhat' cua DPSS."""
import os, sys, json, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import adfecgdb_dir, cinc2013_dir
import numpy as np, torch, mne, wfdb
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
spec=importlib.util.spec_from_file_location('fqrs',os.path.join(ROOT,'model','fqrs_model.py'))
M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M); CFG=M.CFG
RAW = adfecgdb_dir()
RECS=['r01','r04','r07','r08','r10']; DPSS={'r01':4,'r04':4,'r07':4,'r08':4,'r10':1}
def mt(det,gt,tol=50):
    gm=np.zeros(len(gt),bool); dm=np.zeros(len(det),bool); e=[]
    for i,x in enumerate(det):
        d=np.abs(gt-x); w=np.where((d<=tol)&(~gm))[0]
        if len(w): j=w[np.argmin(d[w])]; gm[j]=True; dm[i]=True; e.append(d[j])
    tp=int(dm.sum()); return tp,len(det)-tp,len(gt)-tp,(np.mean(e) if e else np.nan)
tab={}
print(f'{"rec":<6}{"lead1":>9}{"lead2":>9}{"lead3":>9}{"lead4":>9}{"":>4}{"DPSS":>8}{"TB 4 kenh":>11}{"TOI NHAT":>10}')
print('-'*76)
for rec in RECS:
    b=torch.load(os.path.join(ROOT,'model','checkpoints',f'fetalqrs_tcn_fold_{rec}.pt'),map_location='cpu',weights_only=False)
    net=M.FetalQRSTCN(); net.load_state_dict(b['state_dict']); net.eval(); thr=float(b['threshold'])
    raw=mne.io.read_raw_edf(os.path.join(RAW,rec+'.edf'),preload=True,verbose=False); sig=raw.get_data()
    gt=np.array(wfdb.rdann(os.path.join(RAW,rec),'edf.qrs').sample)
    f1s=[]
    for lead in (1,2,3,4):
        x=M.preprocess(sig[lead],1000,CFG); r,_=M.cancel_maternal(x,CFG)
        p=M.probability_series(net,M.robust_scale(r).astype(np.float32),M.robust_scale(x).astype(np.float32),CFG)
        det=M.pick_peaks(p,thr,CFG).astype(np.int64)*4
        tp,fp,fn,_=mt(det,gt); f1s.append(200*tp/(2*tp+fp+fn))
    tab[rec]=f1s
    print(f'{rec:<6}'+''.join(f'{v:>9.2f}' for v in f1s)+f'{"":>4}{f1s[DPSS[rec]-1]:>8.2f}{np.mean(f1s):>11.2f}{min(f1s):>10.2f}')
A=np.array([tab[r] for r in RECS])
print('-'*76)
print(f'{"MACRO":<6}'+''.join(f'{A[:,i].mean():>9.2f}' for i in range(4))+
      f'{"":>4}{np.mean([tab[r][DPSS[r]-1] for r in RECS]):>8.2f}{A.mean():>11.2f}{A.min(axis=1).mean():>10.2f}')
json.dump(tab,open(os.path.join(HERE,'all_leads.json'),'w'),indent=1)
print()
print('Y NGHIA: giao thuc DPSS chi lay 1 kenh lam sang tot nhat -> 99,18.')
print('         Con so 97,43 cua nhom la trung binh tren CA 4 kenh, tuc la kho hon han.')
print('         Ca hai deu trung thuc, nhung tra loi hai cau hoi khac nhau.')
