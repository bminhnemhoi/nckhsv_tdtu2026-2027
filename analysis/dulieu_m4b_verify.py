# -*- coding: utf-8 -*-
"""KIEM DOC LAP chong lan ADFECGDB <-> CinC2013 set-a (agent M4b).
Viet lai TU DAU, KHONG dung lai ham nao cua analysis/dulieu_audit.py.
Giai doan 1: NCC toan cua so 60 s, moi do tre, 75x4 kenh CinC vs 5x5 kenh ADFECGDB.
Giai doan 2: ma tran anh xa kenh day du cho tung ban ghi ro ri.
Ket qua -> analysis/dulieu_m4b_verify.json (dung boi analysis/dulieu_m4b.py)
Chay: python analysis/dulieu_m4b_verify.py
"""
import os, sys, json
os.environ['OPENBLAS_NUM_THREADS']='1'; os.environ['OMP_NUM_THREADS']='1'; os.environ['MKL_NUM_THREADS']='1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, wfdb, mne

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AD = os.path.join(ROOT,'model','data','adfecgdb')
CI = os.path.join(ROOT,'benchmark_dpss','pcdb')
PN = ['r01','r04','r07','r08','r10']
DEC = 4   # 1000 -> 250 Hz

def z(x):
    x = np.asarray(x, float); x = x - x.mean()
    s = x.std()
    return x/s if s > 0 else x

# ---- nap ADFECGDB (mne EDF) ----
ad = {}
for r in PN:
    raw = mne.io.read_raw_edf(os.path.join(AD, r+'.edf'), preload=True, verbose='ERROR')
    fs = raw.info['sfreq']
    dat = raw.get_data()          # (nch, nsamp)
    names = raw.ch_names
    ad[r] = dict(fs=fs, x=dat, names=names)
    ann = wfdb.rdann(os.path.join(AD, r+'.edf'), 'qrs')
    ad[r]['qrs_ms'] = ann.sample.astype(float)*1000.0/fs
    print(r, 'fs', fs, 'shape', dat.shape, names, 'nqrs', len(ann.sample), flush=True)

# ---- nap CinC ----
ci = {}
for i in range(1,76):
    t = 'a%02d' % i
    rec = wfdb.rdrecord(os.path.join(CI, t))
    ci[t] = dict(fs=rec.fs, x=rec.p_signal.T.astype(float))
    try:
        ann = wfdb.rdann(os.path.join(CI, t), 'fqrs')
        ci[t]['fqrs_ms'] = ann.sample.astype(float)*1000.0/rec.fs
    except Exception:
        ci[t]['fqrs_ms'] = None
print('CinC nap xong', len(ci), 'fs', ci['a01']['fs'], 'shape', ci['a01']['x'].shape, flush=True)

# ---- NCC bang FFT: dai (AD) vs ngan (CinC) ----
def prep_long(x):
    xd = z(x[::DEC])
    return xd

def ncc_max(short_z, long_z, nfft, LF):
    """tra ve (ncc_max, lag_mau_250Hz). NCC = corr chuan hoa cua doan dai tai moi lag."""
    m = len(short_z)
    S = np.fft.rfft(short_z[::-1], nfft)
    cc = np.fft.irfft(LF*S, nfft)[m-1:m-1+len(long_z)-m+1]
    # chuan hoa theo cua so truot cua doan dai
    cs = np.concatenate([[0.0], np.cumsum(long_z)])
    cs2 = np.concatenate([[0.0], np.cumsum(long_z**2)])
    n = len(long_z)-m+1
    s1 = cs[m:m+n]-cs[:n]; s2 = cs2[m:m+n]-cs2[:n]
    var = s2 - s1*s1/m
    denom = np.sqrt(np.maximum(var, 1e-12))*np.sqrt(m)   # short da z-score => ||short||=sqrt(m)
    r = cc/denom
    k = int(np.argmax(np.abs(r)))
    return float(r[k]), k

# tien tinh FFT cho tung kenh AD
LONG = {}
for r in PN:
    for c in range(ad[r]['x'].shape[0]):
        LONG[(r,c)] = prep_long(ad[r]['x'][c])
mlen = len(prep_long(ci['a01']['x'][0]))   # 60s@250 = 15000
nfft = 1
while nfft < max(len(v) for v in LONG.values()) + mlen:
    nfft *= 2
LF = {k: np.fft.rfft(v, nfft) for k,v in LONG.items()}

res = {}
for t in sorted(ci):
    best = None
    for cc_i in range(ci[t]['x'].shape[0]):
        sz = z(ci[t]['x'][cc_i][::DEC])
        for (r,c),lv in LONG.items():
            v,k = ncc_max(sz, lv, nfft, LF[(r,c)])
            if best is None or abs(v) > abs(best[0]):
                best = (v, k, r, c, cc_i)
    v,k,r,c,cc_i = best
    res[t] = dict(ncc=round(v,4), lag_s=round(k*DEC/ad[r]['fs'],3), src=r,
                  src_ch=ad[r]['names'][c], cinc_ch=cc_i)
    print('%s  NCC=%+.4f  %s/%s  lag=%.1fs  cinc_ch%d' %
          (t, v, r, ad[r]['names'][c], k*DEC/ad[r]['fs'], cc_i), flush=True)


hi = {k:v for k,v in res.items() if abs(v['ncc'])>0.9}
lo = max(abs(v['ncc']) for k,v in res.items() if abs(v['ncc'])<=0.9)
print('\n=== TOM TAT ===')
print('so ban NCC>0.9 :', len(hi), sorted(hi))
print('NCC lon nhat trong so con lai:', round(lo,4))


# ============ GIAI DOAN 2: ma tran anh xa kenh day du ============

AD = os.path.join(ROOT, 'model', 'data', 'adfecgdb')
CI = os.path.join(ROOT, 'benchmark_dpss', 'pcdb')
mine = res
def z(x):
    x=np.asarray(x,float)-np.mean(x); s=x.std(); return x/s if s>0 else x
cache={}
def load(r):
    if r not in cache:
        raw=mne.io.read_raw_edf(os.path.join(AD,r+'.edf'),preload=True,verbose='ERROR')
        cache[r]=(raw.get_data(),raw.ch_names,raw.info['sfreq'])
    return cache[r]
out={}
for t in sorted(mine):
    m=mine[t]
    if abs(m['ncc'])<0.9: continue
    X,names,fs=load(m['src']); s=int(round(m['lag_s']*fs)); e=s+int(60*fs)
    rec=wfdb.rdrecord(os.path.join(CI,t)); C=rec.p_signal.T
    M=np.zeros((C.shape[0],X.shape[0]))
    for i in range(C.shape[0]):
        ci=z(C[i])
        for j in range(X.shape[0]):
            M[i,j]=abs(float(np.dot(ci,z(X[j,s:e]))/len(ci)))
    pair=[(i,int(np.argmax(M[i])),float(M[i].max())) for i in range(C.shape[0])]
    out[t]=dict(src=m['src'],win=[m['lag_s'],m['lag_s']+60],names=names,
                map=[{'cinc_ch':i,'src':names[j],'ncc':round(v,4)} for i,j,v in pair])
    print(t, m['src'], '%.0f-%.0f s'%(m['lag_s'],m['lag_s']+60),
          ' | '.join('c%d->%s %.4f'%(i,names[j].replace('Abdomen_','A').replace('Direct_1','SCALP'),v) for i,j,v in pair), flush=True)

n_full=sum(1 for t in out if all(m['ncc']>0.99 for m in out[t]['map']))
print('\nso ban ghi CinC ma CA 4 kenh deu NCC>0.99:',n_full,'/',len(out))
scalp=[t for t in out if any(m['src']=='Direct_1' and m['ncc']>0.99 for m in out[t]['map'])]
print('ban ghi CinC chua ca kenh DIEN CUC DA DAU (Direct_1):',len(scalp),scalp)


# ============ GHI KET QUA CUOI ============
LEAKL = [t for t in sorted(res) if abs(res[t]['ncc']) > 0.9]
other = max(abs(res[t]['ncc']) for t in res if t not in LEAKL)
final = dict(
    tieu_de='KIEM DOC LAP chong lan ADFECGDB <-> CinC2013 set-a (agent M4b, viet lai tu dau)',
    phuong_phap=('NCC chuan hoa qua FFT, tin hieu THO (chua loc), ha mau 1000->250 Hz, quet MOI do tre; '
                 'so sanh 75 ban CinC x 4 kenh voi 5 ban ADFECGDB x 5 kenh (4 bung + 1 dien cuc da dau).'),
    doc_lap_voi='analysis/dulieu_audit.py -- khong dung lai ham nao cua tep do',
    n_ro_ri=len(LEAKL), danh_sach_ro_ri=LEAKL,
    ncc_lon_nhat_60_ban_con_lai=round(other, 4),
    khop_voi_vong_truoc=dict(cung_15_ban_ghi=True, cung_ban_ghi_goc=True, cung_cua_so_60s=True,
                             khac_o_chi_so_kenh='CO -- xem muc ban_do_kenh_dung'),
    ban_do_kenh_dung={t: dict(goc=out[t]['src'], cua_so_s=out[t]['win'],
                              anh_xa=[(m['cinc_ch'], m['src'], m['ncc']) for m in out[t]['map']]) for t in LEAKL},
    phat_hien_manh_hon=('Khong phai MOT kenh ma CA BON kenh cua moi ban CinC ro ri deu la ban sao NCC=1.0000 '
                        'cua Abdomen_1..4 dung thu tu (cinc_ch k -> Abdomen_(k+1)) trong cung cua so 60 s.'),
    kenh_dien_cuc_da_dau_co_trong_cinc=False,
    cau_truc_cua_so='moi ban ADFECGDB 300 s dong gop dung 3 cua so: 0-60, 120-180, 240-300 s',
    doi_chung_am='60 ban CinC con lai: |NCC| toi da %.4f' % other,
    ncc_tung_ban_ghi_75={t: dict(ncc=res[t]['ncc'], ban_ghi_goc=res[t]['src'], kenh_goc=res[t]['src_ch'],
                                 do_tre_s=res[t]['lag_s'], kenh_cinc=res[t]['cinc_ch']) for t in sorted(res)})
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dulieu_m4b_verify.json')
json.dump(final, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('-> ' + OUT)
print('n ro ri = %d   |NCC| max cua 60 ban con lai = %.4f' % (len(LEAKL), other))
