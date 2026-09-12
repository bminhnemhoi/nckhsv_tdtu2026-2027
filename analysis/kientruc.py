# -*- coding: utf-8 -*-
"""
Phan tich thong ke cho M2 (kien truc) -- doc pilot_evidence/arch22.json, KHONG huan luyen lai gi.

Ap dung dung quy uoc da chot o analysis/STATS.md:
  * don vi phan tich = CHU THE (n = 22), khong phai cap (chu the x kenh)
  * cluster bootstrap lay mau lai chu the + KTC 95% kieu t (bao thu) -- bao cao CA HAI
  * TOST bien 1,0 diem F1 de phat bieu TUONG DUONG
  * Wilcoxon signed-rank + sign test (bao thu nhat) + hieu chinh Holm cho ho so sanh
  * thang LOGIT voi hieu chinh lien tuc eps = 1/(4*n_ref) (nhu analysis/luongcuc.py) de tranh
    tran 100 -- bat buoc vi LUONGCUC da chi ra hieu ung "tap trung o nhom kho" tren thang F1
    chi la he qua toan hoc cua tran 100

Xuat: analysis/kientruc_results.json, analysis/KIENTRUC.md
Chay:  python analysis/kientruc.py
"""
import os, sys, json, math, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'pilot_evidence', 'arch22.json')
CACHE = os.path.join(ROOT, 'pilot_evidence', 'arch22_cache')
MARGIN = 1.0
NBOOT = 20000
SEED = 0

R = json.load(open(SRC, encoding='utf-8'))
SUBJ = R['meta']['subjects']
HARD = R['meta']['hard_subjects']
EASY = [s for s in SUBJ if s not in HARD]
RUNS = R['runs']
BASE = 'tcn'

# n_ref tung chu the (de hieu chinh lien tuc tren thang logit) -- lay tu chinh cache tin hieu
NREF = {}
for t in SUBJ:
    z = np.load(os.path.join(CACHE, t + '.npz'))
    NREF[t] = int(len(z['fq']))


def logit_F1(F, nref):
    p = np.clip(np.asarray(F, float) / 100.0, 0, 1)
    eps = 1.0 / (4.0 * np.maximum(np.asarray(nref, float), 1))
    return np.log(np.clip(p, eps, 1 - eps) / (1 - np.clip(p, eps, 1 - eps)))


def boot_ci(d, n=NBOOT, seed=SEED):
    d = np.asarray(d, float)
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(n, len(d)))].mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def t_ci(d, conf=.95):
    d = np.asarray(d, float); n = len(d)
    if n < 2:
        return float('nan'), float('nan')
    se = d.std(ddof=1) / math.sqrt(n)
    h = st.t.ppf(.5 + conf / 2, n - 1) * se
    return float(d.mean() - h), float(d.mean() + h)


def tost(d, margin=MARGIN):
    d = np.asarray(d, float); n = len(d)
    se = d.std(ddof=1) / math.sqrt(n) if n > 1 else 0.0
    if se == 0:
        return dict(p=0.0 if abs(d.mean()) < margin else 1.0,
                    equivalent=bool(abs(d.mean()) < margin),
                    ci90=[float(d.mean())] * 2)
    p = max(float(st.t.sf((d.mean() + margin) / se, n - 1)),
            float(st.t.cdf((d.mean() - margin) / se, n - 1)))
    h = float(st.t.ppf(.95, n - 1)) * se
    return dict(p=p, equivalent=bool(p < .05), ci90=[float(d.mean() - h), float(d.mean() + h)])


def sign_test(d):
    d = np.asarray(d, float)
    pos = int((d > 0).sum()); neg = int((d < 0).sum())
    if pos + neg == 0:
        return 1.0
    return float(st.binomtest(pos, pos + neg, .5).pvalue)


def holm(pvals, names):
    order = np.argsort(pvals)
    m = len(pvals); adj = np.empty(m); run = 0.0
    for i, j in enumerate(order):
        v = (m - i) * pvals[j]
        run = max(run, v)
        adj[j] = min(1.0, run)
    return {names[j]: float(adj[j]) for j in range(m)}


def pack(arch, tags, key='F1_psd'):
    a = np.array([RUNS[arch]['rows'][t][key] for t in tags], float)
    b = np.array([RUNS[BASE]['rows'][t][key] for t in tags], float)
    d = a - b
    lo, hi = boot_ci(d); tlo, thi = t_ci(d)
    nref = np.array([NREF[t] for t in tags], float)
    dl = logit_F1(a, nref) - logit_F1(b, nref)
    llo, lhi = boot_ci(dl, seed=SEED + 1)
    try:
        w = float(st.wilcoxon(a, b, zero_method='wilcox').pvalue) if np.any(d != 0) else 1.0
    except Exception:
        w = 1.0
    return dict(n=len(tags), mean_a=float(a.mean()), mean_b=float(b.mean()),
                mean_diff=float(d.mean()), boot_ci95=[lo, hi], t_ci95=[tlo, thi],
                wilcoxon_p=w, sign_p=sign_test(d),
                n_win=int((d > 0).sum()), n_tie=int((d == 0).sum()), n_loss=int((d < 0).sum()),
                logit_diff=float(dl.mean()), logit_ci95=[llo, lhi], tost=tost(d),
                per_subject={t: float(x) for t, x in zip(tags, d)})


OUT = dict(meta=dict(date=str(datetime.datetime.now()), source=os.path.relpath(SRC, ROOT),
                     margin_F1=MARGIN, n_boot=NBOOT, seed=SEED,
                     unit='chu the (n=22)', n_ref_per_subject=NREF,
                     run_meta={k: R['meta'][k] for k in
                               ('seed', 'n_folds', 'epochs', 'batch_size', 'stride',
                                'tolerance_ms', 'protocol', 'scale_down', 'ms_per_step',
                                'threads', 'minutes') if k in R['meta']},
                     folds=R['meta']['folds']),
           table={}, comparisons={})

for k, v in RUNS.items():
    psd = np.array([v['rows'][t]['F1_psd'] for t in SUBJ])
    OUT['table'][k] = dict(params=v['params'], params_pct_vs_tcn=100 * (v['params'] / RUNS[BASE]['params'] - 1),
                           rf_ms=v['rf_ms'], sigma_ms=v['sigma_ms'], desc=v['desc'],
                           macro_psd=v['macro_psd'], sd_psd=v['sd_psd'],
                           boot_ci95_macro=list(boot_ci(psd)),
                           macro_mean4=v['macro_mean4'], macro_oracle=v['macro_oracle'],
                           jitter_psd=v['jitter_psd'], n_ge90=v['n_ge90'], n_lt50=v['n_lt50'],
                           minutes=v['minutes'],
                           thresholds=[f['threshold'] for f in v['folds'].values()])

others = [k for k in RUNS if k != BASE]
for k in others:
    OUT['comparisons'][k] = dict(all22=pack(k, SUBJ), easy19=pack(k, EASY), hard3=pack(k, HARD),
                                 mean4=pack(k, SUBJ, 'F1_mean4'), oracle=pack(k, SUBJ, 'F1_oracle'),
                                 jitter=pack(k, SUBJ, 'jitter_psd'))
if others:
    for fam, key in (('wilcoxon', 'wilcoxon_p'), ('tost', None)):
        if key:
            ps = [OUT['comparisons'][k]['all22'][key] for k in others]
            OUT['holm_' + fam] = holm(ps, others)
    ps = [OUT['comparisons'][k]['all22']['tost']['p'] for k in others]
    OUT['holm_tost'] = holm(ps, others)

json.dump(OUT, open(os.path.join(HERE, 'kientruc_results.json'), 'w'), indent=1, default=float)

# ------------------------------------------------------------------ bao cao man hinh
print(f"{'kien truc':<11}{'tham so':>9}{'%':>7}{'RF ms':>7}{'macro PSD':>11}{'SD':>7}{'TB4':>8}"
      f"{'oracle':>8}{'jitter':>8}{'>=90':>6}")
for k in RUNS:
    t = OUT['table'][k]
    print(f"{k:<11}{t['params']:>9,}{t['params_pct_vs_tcn']:>+7.1f}{t['rf_ms']:>7.0f}"
          f"{t['macro_psd']:>11.2f}{t['sd_psd']:>7.2f}{t['macro_mean4']:>8.2f}"
          f"{t['macro_oracle']:>8.2f}{t['jitter_psd']:>8.2f}{t['n_ge90']:>6d}")
print()
for k in others:
    c = OUT['comparisons'][k]['all22']
    print(f"{k:<11}{c['mean_diff']:+7.2f} boot[{c['boot_ci95'][0]:+.2f};{c['boot_ci95'][1]:+.2f}] "
          f"t[{c['t_ci95'][0]:+.2f};{c['t_ci95'][1]:+.2f}] W={c['wilcoxon_p']:.4f} "
          f"(Holm {OUT['holm_wilcoxon'][k]:.4f}) sign={c['sign_p']:.4f} "
          f"T/H/B {c['n_win']}/{c['n_tie']}/{c['n_loss']} "
          f"TOST p={c['tost']['p']:.4f} {'TUONG DUONG' if c['tost']['equivalent'] else 'chua ket luan'} "
          f"logit {c['logit_diff']:+.3f}[{c['logit_ci95'][0]:+.3f};{c['logit_ci95'][1]:+.3f}]")
print(f"\n-> {os.path.join(HERE, 'kientruc_results.json')}")

# ------------------------------------------------------------------ bang markdown (chi BANG, phan dien giai viet tay)
def fmt(x, n=2):
    return ('%.' + str(n) + 'f') % x


lines = []
lines.append('<!-- BANG TU DONG SINH boi analysis/kientruc.py tu pilot_evidence/arch22.json -- KHONG sua tay -->')
lines.append('')
lines.append('### B1. Bang doi dau (22 chu the, 3 fold theo chu the, kenh PSD mu nhan, +/-50 ms)')
lines.append('')
lines.append('| kien truc | tham so | lech so tham so | RF | macro F1 (PSD) | SD | KTC95 bootstrap | TB 4 kenh | oracle | jitter | >=90 | <50 | phut |')
lines.append('|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|')
for k in sorted(RUNS, key=lambda z: -OUT['table'][z]['macro_psd']):
    t = OUT['table'][k]
    lines.append(f"| `{k}` | {t['params']:,} | {t['params_pct_vs_tcn']:+.1f}% | {t['rf_ms']:.0f} ms | "
                 f"**{fmt(t['macro_psd'])}** | {fmt(t['sd_psd'])} | "
                 f"[{fmt(t['boot_ci95_macro'][0])}; {fmt(t['boot_ci95_macro'][1])}] | {fmt(t['macro_mean4'])} | "
                 f"{fmt(t['macro_oracle'])} | {fmt(t['jitter_psd'])} ms | {t['n_ge90']}/22 | {t['n_lt50']}/22 | "
                 f"{fmt(t['minutes'], 1)} |")
lines.append('')
lines.append('### B2. Hieu so so voi `tcn` o muc CHU THE (n = 22, quy uoc hieu = kien_truc - tcn)')
lines.append('')
lines.append('| so sanh | hieu TB | KTC95 bootstrap | KTC95 kieu t | Wilcoxon p | Holm | sign p | T/H/B | TOST +-1,0 | ket luan TOST | hieu logit | KTC95 logit |')
lines.append('|---|---:|---|---|---:|---:|---:|---:|---:|---|---:|---|')
for k in others:
    c = OUT['comparisons'][k]['all22']
    lines.append(f"| `{k}` - `tcn` | {c['mean_diff']:+.2f} | [{fmt(c['boot_ci95'][0])}; {fmt(c['boot_ci95'][1])}] | "
                 f"[{fmt(c['t_ci95'][0])}; {fmt(c['t_ci95'][1])}] | {c['wilcoxon_p']:.4f} | "
                 f"{OUT['holm_wilcoxon'][k]:.4f} | {c['sign_p']:.4f} | "
                 f"{c['n_win']}/{c['n_tie']}/{c['n_loss']} | {c['tost']['p']:.4f} | "
                 f"{'**TUONG DUONG**' if c['tost']['equivalent'] else 'chua ket luan duoc'} | "
                 f"{c['logit_diff']:+.3f} | [{fmt(c['logit_ci95'][0], 3)}; {fmt(c['logit_ci95'][1], 3)}] |")
lines.append('')
lines.append('### B3. Tach nhom DE (19 chu the) / KHO (B2_03, B1_07, B1_06)')
lines.append('')
lines.append('| so sanh | de19 hieu | KTC95 de19 | kho3 hieu | KTC95 kho3 | TB 4 kenh hieu | KTC95 TB4 | oracle hieu |')
lines.append('|---|---:|---|---:|---|---:|---|---:|')
for k in others:
    e = OUT['comparisons'][k]['easy19']; h = OUT['comparisons'][k]['hard3']
    m = OUT['comparisons'][k]['mean4']; o = OUT['comparisons'][k]['oracle']
    lines.append(f"| `{k}` - `tcn` | {e['mean_diff']:+.2f} | [{fmt(e['boot_ci95'][0])}; {fmt(e['boot_ci95'][1])}] | "
                 f"{h['mean_diff']:+.2f} | [{fmt(h['boot_ci95'][0])}; {fmt(h['boot_ci95'][1])}] | "
                 f"{m['mean_diff']:+.2f} | [{fmt(m['boot_ci95'][0])}; {fmt(m['boot_ci95'][1])}] | "
                 f"{o['mean_diff']:+.2f} |")
lines.append('')
lines.append('### B4. F1 tung chu the (kenh PSD mu nhan)')
lines.append('')
order = [k for k in RUNS]
lines.append('| chu the | nhom | n_ref | ' + ' | '.join(f'`{k}`' for k in order) + ' |')
lines.append('|---|---|---:|' + '---:|' * len(order))
for t in SUBJ:
    g = RUNS[BASE]['rows'][t]['group']
    mark = ' **(kho)**' if t in HARD else ''
    lines.append(f"| {t}{mark} | {g} | {NREF[t]} | " +
                 ' | '.join(fmt(RUNS[k]['rows'][t]['F1_psd']) for k in order) + ' |')
lines.append('')
lines.append('### B5. Nguong da chon tren chu the validation (khong bao gio quet tren test)')
lines.append('')
lines.append('| kien truc | ' + ' | '.join(f"fold {f['fold']} (val {f['val']})" for f in R['meta']['folds']) + ' |')
lines.append('|---|' + '---:|' * len(R['meta']['folds']))
for k in RUNS:
    lines.append(f"| `{k}` | " + ' | '.join(fmt(v['threshold']) for v in RUNS[k]['folds'].values()) + ' |')
lines.append('')
open(os.path.join(HERE, '_kientruc_tables.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('-> analysis/_kientruc_tables.md')
