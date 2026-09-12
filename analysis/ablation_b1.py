# -*- coding: utf-8 -*-
"""
C2 -- HOAN TAT ABLATION BO B1 (pha incorporation bias).

1. Gop cac file train_12_<tag>.json (chay song song) vao model/train_12.json.
2. Doc benchmark_dpss/eval_12.json (mo hinh 12 tren B1 + CinC 75) va benchmark_dpss/eval_22.json
   (m22 fold giu lai, m5 production) -> so sanh muc CHU THE.
3. Xuat analysis/ABLATION_B1.md (tieng Viet co dau) + analysis/ablation_b1_results.json.

Chay: python analysis/ablation_b1.py [--merge-only]
"""
import os, sys
os.environ['OPENBLAS_NUM_THREADS'] = '1'; os.environ['OMP_NUM_THREADS'] = '1'; os.environ['MKL_NUM_THREADS'] = '1'
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json, glob, argparse, datetime
import numpy as np
from scipy.stats import wilcoxon, binomtest, t as tdist

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TRAIN12 = os.path.join(ROOT, 'model', 'train_12.json')
EVAL12 = os.path.join(ROOT, 'benchmark_dpss', 'eval_12.json')
EVAL22 = os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json')
CINC75 = os.path.join(ROOT, 'benchmark_dpss', 'eval_cinc75.json')
OUT_MD = os.path.join(HERE, 'ABLATION_B1.md')
OUT_JSON = os.path.join(HERE, 'ablation_b1_results.json')
N_BOOT = 10000; SEED = 0
B1 = [f'B1_{i:02d}' for i in range(1, 11)]
GOLD12 = ['r01', 'r04', 'r07', 'r08', 'r10', 'B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
BAD_ANN = ('a33', 'a38', 'a47', 'a52', 'a54', 'a71', 'a74')


def vn(x, nd=2):
    """So kieu Viet Nam: dau phay thap phan."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return '--'
    return f'{x:.{nd}f}'.replace('.', ',')


def vns(x, nd=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return '--'
    return f'{x:+.{nd}f}'.replace('.', ',')


def pfmt(p):
    if p is None or not np.isfinite(p):
        return '--'
    return (f'{p:.4f}' if p >= 1e-4 else f'{p:.2e}').replace('.', ',')


def cliffs_delta(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    gt = sum(int(np.sum(xi > y)) for xi in x); lt = sum(int(np.sum(xi < y)) for xi in x)
    d = (gt - lt) / (len(x) * len(y)); ad = abs(d)
    mag = 'khong dang ke' if ad < .147 else ('nho' if ad < .330 else ('trung binh' if ad < .474 else 'lon'))
    return dict(delta=float(d), magnitude=mag)


def ci_t(d, alpha=.05):
    d = np.asarray(d, float); n = len(d)
    if n < 2: return [float('nan'), float('nan')]
    se = d.std(ddof=1) / np.sqrt(n); h = tdist.ppf(1 - alpha / 2, n - 1) * se
    return [float(d.mean() - h), float(d.mean() + h)]


def paired_stats(a, b, name_a='a', name_b='b'):
    a = np.asarray(a, float); b = np.asarray(b, float); d = a - b; n = len(d)
    rng = np.random.default_rng(SEED)
    boots = d[rng.integers(0, n, size=(N_BOOT, n))].mean(1)
    try:
        w = float(wilcoxon(a, b, zero_method='wilcox').pvalue) if np.any(np.abs(d) > 1e-9) else 1.0
    except ValueError:
        w = 1.0
    wins = int(np.sum(d > 1e-9)); losses = int(np.sum(d < -1e-9))
    sp = float(binomtest(wins, wins + losses, .5).pvalue) if (wins + losses) else 1.0
    return dict(a=name_a, b=name_b, n=int(n), mean_a=float(a.mean()), mean_b=float(b.mean()),
                sd_a=float(a.std(ddof=1)) if n > 1 else 0.0, sd_b=float(b.std(ddof=1)) if n > 1 else 0.0,
                mean_diff=float(d.mean()),
                ci95_bootstrap=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
                ci95_t=ci_t(d), wilcoxon_p=w, sign_test_p=sp,
                wins=wins, losses=losses, ties=int(n - wins - losses), cliffs_delta=cliffs_delta(a, b))


def row_stats(c):
    return (f'{vns(c["mean_diff"])} | [{vns(c["ci95_bootstrap"][0])}; {vns(c["ci95_bootstrap"][1])}] | '
            f'[{vns(c["ci95_t"][0])}; {vns(c["ci95_t"][1])}] | {pfmt(c["wilcoxon_p"])} | {pfmt(c["sign_test_p"])} | '
            f'{c["wins"]}/{c["losses"]} | {vns(c["cliffs_delta"]["delta"], 3)} ({c["cliffs_delta"]["magnitude"]})')


# ------------------------------------------------------------------ 1. gop fold
def merge_folds():
    base = json.load(open(TRAIN12, encoding='utf-8')) if os.path.isfile(TRAIN12) else dict(folds={}, subjects={})
    added = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'model', 'train_12_*.json'))):
        if os.path.basename(p) in ('train_12.json',):
            continue
        try:
            o = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print(f'   bo qua {os.path.basename(p)}: {e}'); continue
        for k, v in o.get('folds', {}).items():
            if k not in base['folds']:
                base['folds'][k] = v; added.append(f'{os.path.basename(p)}:fold{k}')
        for k, v in o.get('subjects', {}).items():
            base['subjects'].setdefault(k, v)
    # tong hop lai
    summ = {}
    for g in ('PhysioNet', 'B2'):
        rows = [e for e in base['subjects'].values() if e['group'] == g]
        if not rows: continue
        for key in ('F1_psd', 'F1_mean4'):
            v = np.array([e[key] for e in rows])
            summ[f'{g}_{key}'] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                                      n=int(len(v)), n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()))
    rows = list(base['subjects'].values())
    for key in ('F1_psd', 'F1_mean4'):
        v = np.array([e[key] for e in rows])
        summ[f'ALL12_{key}'] = dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                                    n=int(len(v)), n_ge90=int((v >= 90).sum()), n_lt50=int((v < 50).sum()))
    base['summary'] = summ
    base.setdefault('meta', {})['merged_at'] = str(datetime.datetime.now())
    json.dump(base, open(TRAIN12, 'w'), indent=1, default=float)
    print(f'   gop: {added if added else "khong co gi moi"}; tong {len(base["folds"])} fold, '
          f'{len(base["subjects"])} chu the')
    return base


# ------------------------------------------------------------------ 2. bao cao
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--merge-only', action='store_true')
    a = ap.parse_args()
    print('-- gop ket qua fold --')
    tr = merge_folds()
    if a.merge_only:
        return
    ev12 = json.load(open(EVAL12, encoding='utf-8'))
    e22 = json.load(open(EVAL22, encoding='utf-8'))['subjects']
    res = dict(meta=dict(date=str(datetime.datetime.now()), n_boot=N_BOOT, seed=SEED,
                         eval12_checkpoint=ev12['meta'].get('checkpoint'),
                         eval12_threshold=ev12['meta'].get('threshold'),
                         n_folds_done=len(tr['folds'])))

    # ---- (a) B1
    b1 = ev12.get('B1')
    L = []
    L.append('# Ablation bỏ B1 — cải thiện 5 → 22 chủ thể là do THÊM DỮ LIỆU hay do HỌC PHONG CÁCH NHÃN?\n')
    L.append(f'*Sinh ngày {datetime.datetime.now():%Y-%m-%d %H:%M} bởi `analysis/ablation_b1.py`. '
             f'Nguồn số: `model/train_12.json`, `benchmark_dpss/eval_12.json`, `benchmark_dpss/eval_22.json`, '
             f'`benchmark_dpss/eval_cinc75.json`. Bootstrap cụm {N_BOOT} lần ở mức CHỦ THỂ, seed {SEED}.*\n')
    L.append('## 0. Thiết kế và ba mô hình được so sánh\n')
    L.append('| Mô hình | Huấn luyện trên | Loại nhãn | Đã từng thấy B1? | Checkpoint |')
    L.append('|---|---|---|---|---|')
    L.append('| **m5** | 5 sản phụ ADFECGDB | điện cực da đầu (trực tiếp) | Không | `fetalqrs_tcn_production.pt` |')
    L.append('| **m12** | 12 sản phụ (5 PhysioNet + 7 B2) | điện cực da đầu (trực tiếp) | **Không — đây là biến ablation** | '
             f'`{ev12["meta"].get("checkpoint")}` |')
    L.append('| **m22** | 22 sản phụ (5 + 7 + **10 B1**) | 12 trực tiếp + 10 **gián tiếp** | Có (fold giữ lại chính chủ thể đang đo) | `fetalqrs_tcn_22_fold_XX.pt` |')
    L.append('')
    L.append('Nhãn B1 là nhãn **gián tiếp**: tác giả Silesia khử ECG mẹ trên tín hiệu bụng rồi dò QRS thai và duyệt lại — '
             'không có điện cực da đầu. B1 chiếm 72 % tổng thời lượng huấn luyện của m22, nên nếu m22 hơn m5 chỉ vì nó '
             '*bắt chước phong cách chấm nhãn của B1* thì con số 97,15 trên B1 là thiên lệch do sáp nhập dữ liệu '
             '(incorporation bias), không phải năng lực thật.\n')
    L.append('**Quy tắc quyết định khai báo trước:** nếu m12 (ít dữ liệu hơn, chưa từng thấy B1) vẫn ngang m22 trên B1 '
             'thì phong cách nhãn KHÔNG phải nguyên nhân. Nếu m12 ≈ m5 ≪ m22 trên B1 nhưng m12 ≈ m22 trên CinC thì '
             'phần lớn lợi ích trên B1 là do học phong cách nhãn.\n')

    if b1:
        rec = b1['records']; ref = b1['reference']
        v12 = [rec[t]['F1_psd'] for t in B1]; v22 = [ref[t]['m22_psd'] for t in B1]; v5 = [ref[t]['m5_psd'] for t in B1]
        m12m = [rec[t]['F1_mean4'] for t in B1]; m22m = [ref[t]['m22_mean4'] for t in B1]; m5m = [ref[t]['m5_mean4'] for t in B1]
        L.append('## 1. (a) 10 chủ thể B1 — tập mà m12 CHƯA TỪNG THẤY\n')
        L.append('F1 trên kênh chọn theo quy tắc PSD mù nhãn (%), dung sai ±50 ms.\n')
        L.append('| Chủ thể | m5 | **m12** | m22 | m12 − m5 | m12 − m22 |')
        L.append('|---|---:|---:|---:|---:|---:|')
        for t in B1:
            L.append(f'| {t} | {vn(ref[t]["m5_psd"])} | **{vn(rec[t]["F1_psd"])}** | {vn(ref[t]["m22_psd"])} | '
                     f'{vns(rec[t]["F1_psd"] - ref[t]["m5_psd"])} | {vns(rec[t]["F1_psd"] - ref[t]["m22_psd"])} |')
        L.append(f'| **Trung bình (PSD)** | **{vn(np.mean(v5))}** | **{vn(np.mean(v12))}** | **{vn(np.mean(v22))}** | '
                 f'{vns(np.mean(v12) - np.mean(v5))} | {vns(np.mean(v12) - np.mean(v22))} |')
        L.append(f'| Độ lệch chuẩn | {vn(np.std(v5, ddof=1))} | {vn(np.std(v12, ddof=1))} | {vn(np.std(v22, ddof=1))} | | |')
        L.append(f'| **Trung bình 4 kênh** | {vn(np.mean(m5m))} | **{vn(np.mean(m12m))}** | {vn(np.mean(m22m))} | '
                 f'{vns(np.mean(m12m) - np.mean(m5m))} | {vns(np.mean(m12m) - np.mean(m22m))} |')
        L.append('')
        L.append('**Thống kê ghép cặp ở mức chủ thể (n = 10):**\n')
        L.append('| So sánh | Hiệu số TB | KTC 95 % bootstrap | KTC 95 % t | p Wilcoxon | p sign test | thắng/thua | Cliff δ |')
        L.append('|---|---:|---|---|---:|---:|---:|---|')
        names = {'psd_m12_vs_m5': 'B1 kênh PSD: m12 − m5', 'psd_m12_vs_m22': 'B1 kênh PSD: m12 − m22',
                 'psd_m22_vs_m5': 'B1 kênh PSD: m22 − m5 (mốc cũ)',
                 'mean4_m12_vs_m5': 'B1 TB 4 kênh: m12 − m5', 'mean4_m12_vs_m22': 'B1 TB 4 kênh: m12 − m22'}
        for k, nm in names.items():
            if k in b1['tests']:
                L.append(f'| {nm} | {row_stats(b1["tests"][k])} |')
        L.append('')
        sw = b1.get('threshold_sweep', {})
        if sw:
            L.append('**Quét ngưỡng (m12 trên B1, trung bình 10 chủ thể)** — kiểm tra kết luận có phụ thuộc ngưỡng không:\n')
            L.append('| Ngưỡng | ' + ' | '.join(k.replace('.', ',') for k in sorted(sw)) + ' |')
            L.append('|---|' + '---:|' * len(sw))
            L.append('| F1 kênh PSD | ' + ' | '.join(vn(sw[k]['F1_psd']) for k in sorted(sw)) + ' |')
            L.append('| F1 TB 4 kênh | ' + ' | '.join(vn(sw[k]['F1_mean4']) for k in sorted(sw)) + ' |')
            L.append('')
        res['B1'] = dict(mean_m5=float(np.mean(v5)), mean_m12=float(np.mean(v12)), mean_m22=float(np.mean(v22)),
                         tests=b1['tests'])

    # ---- (b) CinC
    cc = ev12.get('cinc2013')
    if cc:
        L.append('## 2. (b) CinC 2013 set-a — 75 bản ghi, zero-shot ngoài miền\n')
        L.append('Con số chính là **quy tắc PSD mù nhãn**. Kênh 0 cố định là quy tắc chọn HẬU KIỂM, chỉ để tham chiếu.\n')
        for vk in ('75', '68'):
            v = cc.get(f'variant_{vk}')
            if not v: continue
            lab = 'toàn bộ 75 bản ghi' if vk == '75' else '68 bản ghi (loại 7 bản chú thích sai)'
            L.append(f'### {lab} (n = {v["n"]})\n')
            L.append('| Quy tắc chọn kênh | m5 | **m12** | m22 | m12 − m5 [KTC 95 %] | p | m12 − m22 [KTC 95 %] | p |')
            L.append('|---|---:|---:|---:|---|---:|---|---:|')
            for rule, nm in (('psd', '**PSD mù nhãn (SỐ CHÍNH)**'), ('lead0', 'kênh 0 cố định (hậu kiểm)'),
                             ('mean4', 'TB 4 kênh'), ('oracle', 'oracle (chặn trên)')):
                q = v['rules'][rule]; d5 = q['m12_vs_m5']; d22 = q['m12_vs_m22']
                L.append(f'| {nm} | {vn(q["m5"]["mean"])} | **{vn(q["m12"]["mean"])}** | {vn(q["m22"]["mean"])} | '
                         f'{vns(d5["mean_diff"])} [{vns(d5["ci95_bootstrap"][0])}; {vns(d5["ci95_bootstrap"][1])}] | '
                         f'{pfmt(d5["wilcoxon_p"])} | '
                         f'{vns(d22["mean_diff"])} [{vns(d22["ci95_bootstrap"][0])}; {vns(d22["ci95_bootstrap"][1])}] | '
                         f'{pfmt(d22["wilcoxon_p"])} |')
            q = v['rules']['psd']
            L.append('')
            L.append(f'Phân bố theo quy tắc PSD ({lab}): ≥ 90 điểm — m5 {q["dist_m5"]["ge90"]}, '
                     f'**m12 {q["dist_m12"]["ge90"]}**, m22 {q["dist_m22"]["ge90"]}; '
                     f'< 50 điểm — m5 {q["dist_m5"]["lt50"]}, **m12 {q["dist_m12"]["lt50"]}**, m22 {q["dist_m22"]["lt50"]}.\n')
            sw = v.get('threshold_sweep', {})
            if sw:
                L.append('| Ngưỡng | ' + ' | '.join(k.replace('.', ',') for k in sorted(sw)) + ' |')
                L.append('|---|' + '---:|' * len(sw))
                L.append('| m12 F1 kênh PSD | ' + ' | '.join(vn(sw[k]['F1_psd']) for k in sorted(sw)) + ' |')
                L.append('| m12 F1 kênh 0 | ' + ' | '.join(vn(sw[k]['F1_lead0']) for k in sorted(sw)) + ' |')
                L.append('')
        res['cinc'] = {vk: {r: dict(m5=cc[f'variant_{vk}']['rules'][r]['m5']['mean'],
                                    m12=cc[f'variant_{vk}']['rules'][r]['m12']['mean'],
                                    m22=cc[f'variant_{vk}']['rules'][r]['m22']['mean'])
                            for r in ('psd', 'lead0', 'mean4', 'oracle')}
                       for vk in ('75', '68') if f'variant_{vk}' in cc}

    # ---- (a2) dau van nhan: do lech thoi diem va jitter tren B1
    if b1:
        rec = b1['records']
        rows = []
        for t in B1:
            r22 = e22[t]['model_22']; r5 = e22[t]['model_5']
            rows.append(dict(tag=t, f12=rec[t]['F1_psd'], f22=r22['F1_psd'], f5=r5['F1_psd'],
                             b12=rec[t]['bias_psd'], b22=r22['bias_psd'], b5=r5['bias_psd'],
                             j12=rec[t]['jitter_psd'], j22=r22['jitter_psd'], j5=r5['jitter_psd']))
        easy = [r for r in rows if min(r['f12'], r['f22'], r['f5']) >= 95.0]
        L.append('## 3. Dấu vân nhãn — độ lệch thời điểm và jitter trên B1\n')
        L.append('Nếu m22 chỉ *bắt chước phong cách chấm* của B1 thì dấu hiệu rõ nhất không phải F1 mà là **vị trí mốc thời gian**: '
                 'mô hình học theo nhãn B1 sẽ trùng tâm với nhãn B1, còn mô hình học nhãn điện cực da đầu sẽ lệch một khoảng hệ thống.\n')
        L.append('| Nhóm bản ghi | n | độ lệch tuyệt đối TB (ms) m5 | **m12** | m22 | jitter TB (ms) m5 | **m12** | m22 |')
        L.append('|---|---:|---:|---:|---:|---:|---:|---:|')
        for nm, g in (('cả 10 chủ thể B1', rows), ('8 chủ thể mà cả ba mô hình đều đạt F1 ≥ 95 (loại B1_06, B1_07)', easy)):
            if not g: continue
            ab = lambda k: float(np.mean([abs(r[k]) for r in g]))
            jt = lambda k: float(np.mean([r[k] for r in g]))
            L.append(f'| {nm} | {len(g)} | {vn(ab("b5"))} | **{vn(ab("b12"))}** | {vn(ab("b22"))} | '
                     f'{vn(jt("j5"))} | **{vn(jt("j12"))}** | {vn(jt("j22"))} |')
        L.append('')
        res['label_fingerprint'] = dict(
            all10=dict(absbias=[float(np.mean([abs(r[k]) for r in rows])) for k in ('b5', 'b12', 'b22')],
                       jitter=[float(np.mean([r[k] for r in rows])) for k in ('j5', 'j12', 'j22')]),
            easy=dict(n=len(easy),
                      absbias=[float(np.mean([abs(r[k]) for r in easy])) for k in ('b5', 'b12', 'b22')],
                      jitter=[float(np.mean([r[k] for r in easy])) for k in ('j5', 'j12', 'j22')]))

    # ---- (a3) phan ra loi ich
    if b1 and cc:
        L.append('## 4. Bao nhiêu phần của lợi ích 5 → 22 được 7 chủ thể nhãn vàng tái tạo?\n')
        L.append('| Tập kiểm tra | m5 | m12 | m22 | lợi ích 5→22 | phần m12 lấy lại | phần còn cần B1 | giảm sai số tương đối m12→m22 |')
        L.append('|---|---:|---:|---:|---:|---:|---:|---:|')
        items = [('B1 (10 chủ thể, kênh PSD)', b1['summary']['m5_psd']['mean'], b1['summary']['m12_psd']['mean'],
                  b1['summary']['m22_psd']['mean']),
                 ('B1 (10 chủ thể, TB 4 kênh)', b1['summary']['m5_mean4']['mean'], b1['summary']['m12_mean4']['mean'],
                  b1['summary']['m22_mean4']['mean'])]
        for vk in ('75', '68'):
            v = cc.get(f'variant_{vk}')
            if v:
                q = v['rules']['psd']
                items.append((f'CinC 2013 ({vk} bản ghi, kênh PSD)', q['m5']['mean'], q['m12']['mean'], q['m22']['mean']))
        for nm, x5, x12, x22 in items:
            gain = x22 - x5; got = x12 - x5
            share = 100 * got / gain if abs(gain) > 1e-9 else float('nan')
            err = 100 * (x22 - x12) / (100 - x12) if (100 - x12) > 1e-9 else float('nan')
            L.append(f'| {nm} | {vn(x5)} | **{vn(x12)}** | {vn(x22)} | {vns(gain)} | {vns(got)} ({vn(share, 0)} %) | '
                     f'{vns(x22 - x12)} ({vn(100 - share, 0)} %) | {vn(err, 1)} % |')
        L.append('')

    # ---- (c) 12 chu the vang
    subs = tr['subjects']
    done = [t for t in GOLD12 if t in subs]
    L.append(f'## 5. (c) Chính 12 chủ thể nhãn vàng — kiểm định chéo giữ lại nhóm\n')
    L.append(f'{len(tr["folds"])}/6 fold đã chạy → {len(done)}/12 chủ thể có kết quả ngoài mẫu. '
             f'Ở mục này mỗi mô hình m12 chỉ học từ **9** chủ thể (2 test + 1 val bị giữ lại), còn mỗi mô hình '
             f'm22 học từ **19** chủ thể — nghĩa là m22 được lợi hơn gấp đôi dữ liệu. '
             f'Cột m22 lấy từ `eval_22.json` (cũng là fold giữ lại chính chủ thể đó), nên hai cột so sánh được.\n')
    L.append('| Chủ thể | Nhóm | fold | m12 (PSD) | m22 (PSD) | m12 − m22 | m12 (TB4) | m22 (TB4) |')
    L.append('|---|---|---:|---:|---:|---:|---:|---:|')
    a12, a22, b12, b22 = [], [], [], []
    for t in done:
        e = subs[t]; r22 = e22[t]['model_22']
        a12.append(e['F1_psd']); a22.append(r22['F1_psd'])
        b12.append(e['F1_mean4']); b22.append(r22['F1_mean4'])
        L.append(f'| {t} | {e["group"]} | {e.get("fold", "-")} | {vn(e["F1_psd"])} | {vn(r22["F1_psd"])} | '
                 f'{vns(e["F1_psd"] - r22["F1_psd"])} | {vn(e["F1_mean4"])} | {vn(r22["F1_mean4"])} |')
    if done:
        L.append(f'| **Trung bình** | | | **{vn(np.mean(a12))}** | **{vn(np.mean(a22))}** | '
                 f'{vns(np.mean(a12) - np.mean(a22))} | {vn(np.mean(b12))} | {vn(np.mean(b22))} |')
        L.append('')
        if len(done) >= 2:
            cpsd = paired_stats(a12, a22, 'm12', 'm22'); c4 = paired_stats(b12, b22, 'm12', 'm22')
            L.append('| So sánh | Hiệu số TB | KTC 95 % bootstrap | KTC 95 % t | p Wilcoxon | p sign test | thắng/thua | Cliff δ |')
            L.append('|---|---:|---|---|---:|---:|---:|---|')
            L.append(f'| 12 chủ thể vàng, kênh PSD: m12 − m22 | {row_stats(cpsd)} |')
            L.append(f'| 12 chủ thể vàng, TB 4 kênh: m12 − m22 | {row_stats(c4)} |')
            L.append('')
            res['gold12'] = dict(n=len(done), mean_m12=float(np.mean(a12)), mean_m22=float(np.mean(a22)),
                                 psd=cpsd, mean4=c4)
    L.append('*Ghi chú thực thi: fold 01 chạy riêng, các fold 02–06 chạy song song 3 tiến trình (mỗi tiến trình '
             '1 nhân CPU, cờ `--tag`) nên chỉ lưu số đo chứ không lưu checkpoint từng fold; checkpoint được lưu '
             'là `fetalqrs_tcn_12_fold_01.pt` và `fetalqrs_tcn_12_production.pt`. Kết quả từng fold nằm trong '
             '`model/train_12.json` (đã gộp) và `model/train_12_f23.json`, `_f45.json`, `_f6.json`.*\n')
    thr = [v['threshold'] for v in tr['folds'].values()]
    if thr:
        L.append('Ngưỡng chọn trên tập val của từng fold: ' + ', '.join(vn(x) for x in sorted(thr)) +
                 f' (trung vị {vn(float(np.median(thr)))}).\n')
    try:
        sys.path.insert(0, HERE)
        from _ablation_concl import conclusion
        conclusion(L, b1, cc, res, vn, vns, pfmt, np, tr, e22, B1)
    except Exception as e:
        print(f'   (khong sinh duoc phan ket luan: {e})')
    json.dump(res, open(OUT_JSON, 'w'), indent=1, default=float)
    open(OUT_MD, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print(f'-> {OUT_MD}\n-> {OUT_JSON}')


if __name__ == '__main__':
    main()
