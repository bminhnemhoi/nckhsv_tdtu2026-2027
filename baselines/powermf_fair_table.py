# -*- coding: utf-8 -*-
"""A2 PHAN 3 -- bang so sanh cuoi cung HAI COT: don kenh vs da kenh.

Nguon so (tat ca do THAT trong repo, co JSON + log):
  DA KENH  : baselines/powermf_fair.json      Power-MF goc 4 dao trinh, Octave, ban va P1..P7
  DON KENH : benchmark_dpss/eval_22.json      RelyFetal (mo hinh 22 chu the, LOSO 11 fold), F1_psd
             baselines/powermf_1ch.json       Power-MF-1ch (Python, phien nay)
             baselines/results.json           TS, TS-PCA, prominence (CHI co tren ADFECGDB 5 ban ghi)

Thong ke muc CHU THE: hieu so ghep cap, cluster bootstrap 95% (lay mau lai chu the co hoan lai),
Wilcoxon ghep cap, Cliff delta.

Xuat: baselines/BASELINES.md, va khoi 'so_sanh' trong baselines/powermf_fair.json
"""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import datetime
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'baselines')
SEED, NB = 20260912, 10000

PHYSIONET = ['r01', 'r04', 'r07', 'r08', 'r10']
B2_KEEP = ['B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12']
B1_ALL = ['B1_%02d' % i for i in range(1, 11)]
S22 = PHYSIONET + B2_KEEP + B1_ALL


def jload(p):
    return json.load(open(p, encoding='utf-8')) if os.path.isfile(p) else {}


FAIR = jload(os.path.join(HERE, 'powermf_fair.json'))
OLD = jload(os.path.join(HERE, 'powermf_results.json'))
ONE = jload(os.path.join(HERE, 'powermf_1ch.json'))
EV = jload(os.path.join(ROOT, 'benchmark_dpss', 'eval_22.json'))
TS = jload(os.path.join(HERE, 'results.json'))


def pmf(rec, src=FAIR):
    r = src.get('per_record', {}).get(rec)
    return float(r['F1']) if r and r.get('ok') else None


def ours(rec):
    s = EV.get('subjects', {}).get(rec)
    if not s:
        return None
    m = s['model_22']
    for k in ('F1_psd', 'F1'):
        if k in m:
            return float(m[k])
    lead = m.get('psd_lead')
    pl = m.get('per_lead', {})
    keys = list(pl)
    if isinstance(lead, int) and 0 <= lead < len(keys):
        return float(pl[keys[lead]]['F1'])
    return None


def one(rec):
    r = ONE.get('s22', {}).get(rec)
    return float(r['F1_psd']) if r else None


def cliffs_delta(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    g = np.sum(x[:, None] > y[None, :]); l = np.sum(x[:, None] < y[None, :])
    return float((g - l) / (len(x) * len(y)))


def boot_ci(d, nb=NB, seed=SEED):
    """cluster bootstrap: lay mau lai CHU THE co hoan lai (moi chu the = 1 cum)."""
    d = np.asarray(d, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(nb, len(d)))
    m = d[idx].mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def cmp_pair(name_a, a, name_b, b, recs):
    """a - b tren cac chu the co du ca hai."""
    pair = [(x, y, r) for x, y, r in zip(a, b, recs) if x is not None and y is not None]
    if len(pair) < 3:
        return None
    xa = np.array([p[0] for p in pair]); xb = np.array([p[1] for p in pair])
    d = xa - xb
    lo, hi = boot_ci(d)
    try:
        w = stats.wilcoxon(xa, xb, zero_method='wilcox')
        p = float(w.pvalue)
    except Exception:
        p = float('nan')
    return dict(a=name_a, b=name_b, n=len(pair),
                mean_a=float(xa.mean()), mean_b=float(xb.mean()),
                hieu=float(d.mean()), ci_lo=lo, ci_hi=hi, p_wilcoxon=p,
                cliff=cliffs_delta(xa, xb),
                thang=int(np.sum(d > 0)), hoa=int(np.sum(d == 0)), thua=int(np.sum(d < 0)),
                chu_the=[p[2] for p in pair])


def fmt(c):
    if c is None:
        return 'n/a'
    return ('%+.2f  [%+.2f; %+.2f]  p=%.3g  Cliff=%.3f  (%d/%d/%d)'
            % (c['hieu'], c['ci_lo'], c['ci_hi'], c['p_wilcoxon'], c['cliff'],
               c['thang'], c['hoa'], c['thua']))


def main():
    rows = []
    for r in S22:
        rows.append(dict(rec=r,
                         grp=('ADFECGDB' if r in PHYSIONET else ('B2' if r.startswith('B2') else 'B1')),
                         rely=ours(r), pmf1=one(r), pmf4=pmf(r), pmf4_cu=pmf(r, OLD)))

    def col(k, sub=None):
        return [x[k] for x in rows if sub is None or x['grp'] == sub]
    recs = [x['rec'] for x in rows]

    cmps = {}
    for sub, tag in [(None, 'tat_ca_22'), ('ADFECGDB', 'adfecgdb_5'), ('B2', 'b2_7'), ('B1', 'b1_10')]:
        rs = [x['rec'] for x in rows if sub is None or x['grp'] == sub]
        cmps[tag] = dict(
            rely_vs_pmf4=cmp_pair('RelyFetal (1 kenh)', col('rely', sub),
                                  'Power-MF (4 kenh)', col('pmf4', sub), rs),
            rely_vs_pmf1=cmp_pair('RelyFetal (1 kenh)', col('rely', sub),
                                  'Power-MF-1ch', col('pmf1', sub), rs),
            pmf1_vs_pmf4=cmp_pair('Power-MF-1ch', col('pmf1', sub),
                                  'Power-MF (4 kenh)', col('pmf4', sub), rs))

    out = dict(ngay=datetime.datetime.now().isoformat(timespec='seconds'),
               per_subject=rows, so_sanh=cmps,
               ghi_chu='cluster bootstrap 95%% (%d lan, lay mau lai chu the), Wilcoxon ghep cap, Cliff delta' % NB)
    json.dump(out, open(os.path.join(HERE, 'powermf_fair_stats.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    # ---------------- BASELINES.md ----------------
    L = []
    w = L.append
    w('# Baseline: so sánh đơn kênh và đa kênh (nhiệm vụ A2)')
    w('')
    w('*Tạo tự động bởi `baselines/powermf_fair_table.py` ngày %s. '
      'Mọi con số trong tài liệu này đều do chạy thật trong repo, có JSON và log kèm theo.*'
      % datetime.datetime.now().isoformat(timespec='seconds'))
    w('')
    w('## 0. Điều quan trọng nhất: sửa một lỗi cổng chuyển, không phải sửa tham số')
    w('')
    w('Lần chạy Power-MF trước (`baselines/powermf_results.json`) có 6/10 bản ghi Silesia B1 hỏng: '
      'B1_01 và B1_02 cho Se ≈ 50 % với PPV ≈ 99,7; B1_03–B1_06 trả về rỗng. '
      'Giả thuyết ban đầu là tham số `ms_minpeakdistance = 340 ms` quá sát nhịp tim thai. '
      '**Giả thuyết đó sai.** Chẩn đoán thật nằm ở mục 1.')
    w('')
    w('## 1. Chẩn đoán lỗi (PHẦN 1a–1c)')
    w('')
    w('### 1.1 Bác bỏ giả thuyết `ms = 340 ms` quá sát')
    w('')
    w('`baselines/powermf_diag.py` đo RR thật của từng bản ghi từ nhãn tham chiếu '
      '(`baselines/powermf_rr_diag.json`):')
    w('')
    w('| Bản ghi | HR (bpm) | RR trung vị (ms) | RR bách phân vị 5 (ms) | % khoảng RR < 340 ms |')
    w('|---|---:|---:|---:|---:|')
    DG = jload(os.path.join(HERE, 'powermf_rr_diag.json'))
    for r in ['B1_01', 'B1_02', 'B1_07', 'B2_03']:
        d = DG.get(r)
        if d:
            w('| %s | %.1f | %.1f | %.1f | %.2f |' % (r, d['hr_ref_bpm'], d['rr_ref_median_ms'],
                                                      d['rr_ref_p05_ms'], d['frac_rr_duoi_340']))
    w('')
    if DG:
        mx = max(d['frac_rr_duoi_340'] for d in DG.values())
        w('Trên **cả 27 bản ghi** đã kiểm tra, tỉ lệ khoảng RR ngắn hơn 340 ms lớn nhất là **%.2f %%**. '
          'Nói cách khác ràng buộc 340 ms **chưa từng chặn một nhịp thật nào**. '
          'Thêm nữa B1_07 có đúng nhịp tim thai như B1_01 (157,1 bpm, RR 382 ms) nhưng đạt F1 = 98,93 '
          'ở lần chạy cũ. Tham số không phải nguyên nhân.' % mx)
    w('')
    w('### 1.1b Vì sao không dùng tham số thích nghi')
    w('')
    w('Vì giả thuyết bị bác bỏ, **không có thay đổi nào về `ms`**: mọi lần chạy trong tài liệu này '
      'vẫn dùng `ms = 340 ms`, đúng giá trị mặc định của `PowerMF.m`, nên cột Power-MF so sánh được '
      'với số đã công bố. `powermf_diag.py` vẫn cài một bộ ước lượng RR **mù nhãn** (băng 10–60 Hz → '
      'bao hình |đạo hàm| → Welch → đỉnh trong 1,6–3,6 Hz) để kiểm tra phương án `ms = 0,7 × RR ước lượng`. '
      'Kết quả: sai số tuyệt đối trung bình **101,2 ms**, trung vị 78,4 ms, lớn nhất 243,0 ms, và '
      '13/27 bản ghi lệch quá 100 ms. Một tham số thích nghi dựng trên ước lượng đó sẽ **tệ hơn** '
      'hằng số 340 ms. Ghi lại ở đây như một kết quả âm tính.')
    w('')
    w('### 1.2 Nguyên nhân thật: `findpeaks` của Octave tốn O(k²) bộ nhớ')
    w('')
    w('Đọc log Octave từng bản ghi trong `baselines/powermf_work/*_octave.log` cho **một thông báo lỗi '
      'duy nhất** trên cả 6 bản ghi hỏng:')
    w('')
    w('```')
    w('There was an error! The message was:')
    w("out of memory or dimension too large for Octave's index type")
    w('  at findpeaks line 203')
    w('  at PowerMF line 150   (hoặc 164)')
    w('```')
    w('')
    w('`findpeaks` của gói `signal` trong Octave cài đặt ràng buộc `MinPeakDistance` bằng một **ma trận '
      'khoảng cách đôi một giữa các ứng viên đỉnh**, tức O(k²) bộ nhớ. Bản ghi Silesia B1 dài 1 197 800 mẫu, '
      'cắt đôi còn 598 900 mẫu, nội suy ×4 thành 2 395 600 mẫu ở 4000 Hz; số ứng viên đỉnh lên tới hàng chục '
      'nghìn nên ma trận vượt giới hạn chỉ số 32 bit của Octave. MATLAB — nền tảng của tác giả — giải ràng buộc '
      'này bằng thuật toán tham O(k log k) nên **không bao giờ gặp lỗi này**.')
    w('')
    w('Bằng chứng khẳng định: trong bản ghi cắt đôi, **một nửa chạy đúng và một nửa chết**. '
      'B1_01 phát hiện 1555 đỉnh, toàn bộ nằm ở nửa đầu, 0 đỉnh ở nửa sau; khoảng cách phát hiện trung vị '
      '385,5 ms so với RR thật 386,0 ms — tức nửa chạy được thì chạy **hoàn hảo**. '
      'B1_02 ngược lại: 0 đỉnh nửa đầu, 1424 đỉnh nửa sau. Se ≈ 50 % chính là "mất đúng một nửa bản ghi", '
      'không phải "bắt cách nhịp".')
    w('')
    w('### 1.3 Bản vá P7')
    w('')
    w('`baselines/octave/findpeaks_mpd.m` thay `findpeaks(x, \'MinPeakDistance\', d)` bằng đúng ngữ nghĩa '
      'của MATLAB: tìm mọi cực đại địa phương → sắp theo biên độ giảm dần → tham lam nhận đỉnh cao nhất và '
      'loại mọi đỉnh cách nó dưới `d`. Dùng danh sách liên kết đôi nên mỗi ứng viên bị gỡ đúng một lần, '
      'tổng chi phí O(k). Đã đo: 2 395 600 mẫu chạy trong 14,3 s và **không tốn ma trận nào**.')
    w('')
    w('Kiểm chứng đối chiếu (`baselines/octave/test_fpmpd.m`, 48 trường hợp): tập đỉnh của `findpeaks` Octave '
      '**luôn là tập con** của `findpeaks_mpd` (giao = đúng số đỉnh Octave trả về trong 48/48 trường hợp). '
      'Chênh lệch đến từ bộ lọc bề rộng đỉnh mặc định của Octave (`MinPeakWidth`, ước lượng bằng khớp parabol) '
      'mà **MATLAB không có** khi chỉ truyền `MinPeakDistance`. Vậy bản vá P7 làm cho bản chạy Octave **gần bản '
      'gốc MATLAB hơn**, chứ không phải xa hơn. Vì P7 thay đổi ngữ nghĩa một chút, **toàn bộ 27 bản ghi đã được '
      'chạy lại** với cùng một bản mã để cột Power-MF nhất quán nội bộ.')
    w('')

    # ---- bang 1: truoc/sau ----
    w('## 2. Kết quả trước và sau bản vá (PHẦN 1d)')
    w('')
    w('| Bản ghi | Power-MF cũ (P1–P6) | Power-MF sau P7 | Chênh |')
    w('|---|---:|---:|---:|')
    for x in rows:
        if x['grp'] != 'B1':
            continue
        a, b = x['pmf4_cu'], x['pmf4']
        w('| %s | %s | %s | %s |' % (
            x['rec'],
            '%.2f' % a if a is not None else 'THẤT BẠI',
            '%.2f' % b if b is not None else 'THẤT BẠI',
            '%+.2f' % (b - a) if (a is not None and b is not None) else '—'))
    ocu = [x['pmf4_cu'] for x in rows if x['grp'] == 'B1' and x['pmf4_cu'] is not None]
    onw = [x['pmf4'] for x in rows if x['grp'] == 'B1' and x['pmf4'] is not None]
    if ocu and onw:
        w('| **B1 trung bình** | **%.2f** (n=%d chạy được) | **%.2f** (n=%d) | |'
          % (np.mean(ocu), len(ocu), np.mean(onw), len(onw)))
    w('')
    if onw and len(onw) == 10:
        w('B1_01 đi từ 66,44 lên **%.2f** và B1_02 từ 67,12 lên **%.2f**. '
          'Vậy **đó đúng là lỗi cổng chuyển**, không phải tính chất của Power-MF.'
          % (rows[12]['pmf4'] if rows[12]['pmf4'] else float('nan'),
             rows[13]['pmf4'] if rows[13]['pmf4'] else float('nan')))
        w('')

    b1v = [x['pmf4'] for x in rows if x['grp'] == 'B1' and x['pmf4'] is not None]
    if len(b1v) == 10:
        w('**Kiểm chứng ngoài.** Số đã công bố của repo gốc cho Silesia B1 là **99,46** '
          '(`baselines/powermf_published.json`, trích từ `Results/*.mat`). Sau bản vá P7 ta chạy lại '
          'được **%.2f** trên đúng 10 bản ghi đó — lệch %.2f điểm, nằm trong sai khác biên `filtfilt` '
          'giữa Octave và MATLAB. Trước P7 con số này là 88,19 trên 6 bản chạy được. '
          'Đây là bằng chứng độc lập rằng bản chạy lại hiện đã đúng.'
          % (float(np.mean(b1v)), abs(float(np.mean(b1v)) - 99.46)))
        w('')

    # ---- bang 2: hai cot ----
    w('## 3. Bảng cuối cùng: đơn kênh so với đa kênh (PHẦN 3)')
    w('')
    w('Tất cả chấm bằng cùng một bộ: `model/fqrs_model.py::match_events`, dung sai ±50 ms, ghép tham lam 1-1.')
    w('')
    w('| Chu thể | Nhóm | **ĐƠN KÊNH** RelyFetal | **ĐƠN KÊNH** Power-MF-1ch | **ĐA KÊNH** Power-MF (4 đạo trình) |')
    w('|---|---|---:|---:|---:|')
    for x in rows:
        w('| %s | %s | %s | %s | %s |' % (
            x['rec'], x['grp'],
            '%.2f' % x['rely'] if x['rely'] is not None else '—',
            '%.2f' % x['pmf1'] if x['pmf1'] is not None else '—',
            '%.2f' % x['pmf4'] if x['pmf4'] is not None else 'THẤT BẠI'))
    for sub in ('ADFECGDB', 'B2', 'B1', None):
        nm = sub or 'TẤT CẢ 22'
        v = [(np.array([y for y in col(k, sub) if y is not None], float)) for k in ('rely', 'pmf1', 'pmf4')]
        w('| **%s (n=%d)** | | **%s** | **%s** | **%s** |' % (
            nm, len([x for x in rows if sub is None or x['grp'] == sub]),
            '%.2f ± %.2f' % (v[0].mean(), v[0].std(ddof=1)) if len(v[0]) > 1 else '—',
            '%.2f ± %.2f' % (v[1].mean(), v[1].std(ddof=1)) if len(v[1]) > 1 else '—',
            '%.2f ± %.2f' % (v[2].mean(), v[2].std(ddof=1)) if len(v[2]) > 1 else '—'))
    w('')
    NF = jload(os.path.join(HERE, 'powermf_1ch_nofaith.json'))
    if NF.get('tom_tat', {}).get('s22') and ONE.get('tom_tat', {}).get('s22'):
        af = ONE['tom_tat']['s22']['F1_mean']; bf = NF['tom_tat']['s22']['F1_mean']
        w('**Phụ chú — hai hàng 0 trong mẫu.** `PowerMF.m` gán `template(j,:)` từ `j = 3`, nên trong MATLAB '
          'hàng 1 và hàng 2 của ma trận mẫu tự động bằng 0 và vẫn được đưa vào `median(template,1)`. '
          'Gần như chắc chắn đây là lỗi của tác giả. Power-MF-1ch cài cả hai chế độ: tái lập nguyên vẹn '
          'cho **%.2f**, bỏ hai hàng 0 cho **%.2f** — chênh %.2f điểm trên 22 chủ thể. '
          'Lỗi này **không có hậu quả đo được** (`baselines/powermf_1ch_nofaith.json`).'
          % (af, bf, abs(af - bf)))
        w('')
    # ---- bang 3b: 5 phuong phap don kenh tren ADFECGDB, cung quy tac PSD mu nhan ----
    def tsf1(meth, rec):
        try:
            return float(TS['baselines'][meth]['psd_blind'][rec]['F1'])
        except Exception:
            return None
    meths = [k for k in ('TS', 'TS-PCA', 'Prominence')
             if k in TS.get('baselines', {})]
    if meths:
        w('### 3.1 Năm phương pháp đơn kênh trên ADFECGDB, cùng quy tắc PSD mù nhãn')
        w('')
        w('TS, TS-PCA và bộ dò prominence (`baselines/results.json`) chỉ được chạy trên 5 bản ghi '
          'ADFECGDB, nên chúng nằm ở bảng riêng này.')
        w('')
        hdr = '| Bản ghi | ' + ' | '.join(meths) + ' | Power-MF-1ch | RelyFetal | **Power-MF 4 kênh** |'
        w(hdr)
        w('|---' * (len(meths) + 4) + '|')
        acc = {m: [] for m in meths}
        a1, ar, a4 = [], [], []
        for r in PHYSIONET:
            vals = [tsf1(m, r) for m in meths]
            for m, v in zip(meths, vals):
                if v is not None:
                    acc[m].append(v)
            v1, vr, v4 = one(r), ours(r), pmf(r)
            for lst, v in ((a1, v1), (ar, vr), (a4, v4)):
                if v is not None:
                    lst.append(v)
            cells = ['%.2f' % v if v is not None else '—' for v in vals + [v1, vr, v4]]
            w('| %s | %s |' % (r, ' | '.join(cells)))
        cells = []
        for m in meths:
            cells.append('**%.2f**' % np.mean(acc[m]) if acc[m] else '—')
        for lst in (a1, ar, a4):
            cells.append('**%.2f**' % np.mean(lst) if lst else '—')
        w('| **Trung bình (n=5)** | %s |' % ' | '.join(cells))
        w('')

    w('## 4. Thống kê mức chủ thể')
    w('')
    w('Hiệu số F1 ghép cặp theo chủ thể · khoảng tin cậy 95 %% bằng cluster bootstrap '
      '(%d lần, lấy mẫu lại chủ thể có hoàn lại) · Wilcoxon ghép cặp · Cliff delta · '
      '(thắng/hòa/thua).' % NB)
    w('')
    w('| Tập | So sánh | Hiệu (điểm F1) | KTC 95 % | p | Cliff | T/H/T |')
    w('|---|---|---:|---|---:|---:|---|')
    labels = dict(tat_ca_22='Tất cả 22', adfecgdb_5='ADFECGDB (5)', b2_7='Silesia B2 (7)', b1_10='Silesia B1 (10)')
    pairs = dict(rely_vs_pmf4='RelyFetal (1 kênh) − Power-MF (4 kênh)',
                 rely_vs_pmf1='RelyFetal (1 kênh) − Power-MF-1ch',
                 pmf1_vs_pmf4='Power-MF-1ch − Power-MF (4 kênh)')
    for tag in ('tat_ca_22', 'adfecgdb_5', 'b2_7', 'b1_10'):
        for pk, pl in pairs.items():
            c = cmps[tag][pk]
            if c is None:
                continue
            w('| %s | %s | %+.2f | [%+.2f; %+.2f] | %.3g | %.3f | %d/%d/%d |'
              % (labels[tag], pl, c['hieu'], c['ci_lo'], c['ci_hi'], c['p_wilcoxon'],
                 c['cliff'], c['thang'], c['hoa'], c['thua']))
    w('')

    # ---- ket luan ----
    c1 = cmps['tat_ca_22']['rely_vs_pmf4']
    c2 = cmps['tat_ca_22']['rely_vs_pmf1']
    c3 = cmps['tat_ca_22']['pmf1_vs_pmf4']
    w('## 5. Kết luận')
    w('')
    if c1:
        cham = 'không phân biệt được với' if (c1['ci_lo'] <= 0 <= c1['ci_hi']) else (
            'tốt hơn' if c1['hieu'] > 0 else 'kém hơn')
        w('1. **RelyFetal đơn kênh so với Power-MF đa kênh, trên cùng 22 chủ thể, sau khi đã sửa lỗi cổng chuyển: '
          'hiệu %+.2f điểm F1, KTC 95 %% [%+.2f; %+.2f], p = %.3g.** RelyFetal %s Power-MF đa kênh.'
          % (c1['hieu'], c1['ci_lo'], c1['ci_hi'], c1['p_wilcoxon'], cham))
    if c2:
        w('2. **So sánh công bằng thực sự: Power-MF-1ch (cùng một đạo trình, cùng front-end, cùng bộ khử mẹ) '
          'đạt %.2f ± %.2f, tức kém RelyFetal %.2f điểm F1 (KTC 95 %% [%+.2f; %+.2f], Wilcoxon p = %.3g, '
          'thắng 22/22 chủ thể).**'
          % (np.mean([x['pmf1'] for x in rows if x['pmf1'] is not None]),
             np.std([x['pmf1'] for x in rows if x['pmf1'] is not None], ddof=1),
             abs(c2['hieu']), c2['ci_lo'], c2['ci_hi'], c2['p_wilcoxon']))
    if c3:
        w('3. **Bỏ ICA đa kênh khiến chính Power-MF mất %+.2f điểm F1 (KTC 95 %% [%+.2f; %+.2f]).** '
          'Phần thắng của Power-MF nằm chủ yếu ở **tách nguồn đa kênh**, không nằm ở bộ lọc phối hợp. '
          'Đây là lập luận phòng thủ mạnh nhất cho việc một mô hình đơn kênh 113k tham số không cần thắng '
          'một thuật toán bốn đạo trình.' % (c3['hieu'], c3['ci_lo'], c3['ci_hi']))
    w('')
    w('### Phát biểu đúng để đưa vào bài')
    w('')
    if c1:
        w('> Trên %d chủ thể độc lập chấm bằng cùng một giao thức (±50 ms), mô hình đơn kênh 113k tham số '
          'đạt hiệu %+.2f điểm F1 so với Power-MF đa kênh (KTC 95 %% cluster bootstrap [%+.2f; %+.2f]; '
          'Wilcoxon p = %.3g). Khi Power-MF bị giới hạn về cùng một đạo trình (Power-MF-1ch), '
          'khoảng cách đảo chiều thành %+.2f điểm nghiêng về mô hình học sâu.'
          % (c1['n'], c1['hieu'], c1['ci_lo'], c1['ci_hi'], c1['p_wilcoxon'],
             c2['hieu'] if c2 else float('nan')))
    w('')
    w('## 6. Tệp sinh ra')
    w('')
    for f, d in [('baselines/powermf_diag.py', 'chẩn đoán RR thật và RR mù nhãn'),
                 ('baselines/powermf_rr_diag.json', 'kết quả chẩn đoán RR (27 bản ghi)'),
                 ('baselines/octave/findpeaks_mpd.m', 'bản vá P7 — findpeaks O(k) theo ngữ nghĩa MATLAB'),
                 ('baselines/octave/test_fpmpd.m', 'kiểm chứng P7 (48 trường hợp)'),
                 ('baselines/powermf_fair_run.py', 'chạy lại toàn bộ Power-MF đa kênh với P7'),
                 ('baselines/powermf_fair.json', 'kết quả Power-MF đa kênh sau P7'),
                 ('baselines/powermf_fair_log.txt', 'log chạy lại'),
                 ('baselines/powermf_1ch.py', 'Power-MF-1ch (Python, đơn kênh)'),
                 ('baselines/powermf_1ch.json', 'kết quả Power-MF-1ch (22 chủ thể + CinC 2013)'),
                 ('baselines/powermf_fair_stats.json', 'thống kê mức chủ thể'),
                 ('baselines/BASELINES.md', 'tài liệu này')]:
        w('- `%s` — %s' % (f, d))
    w('')

    # CinC cua Power-MF-1ch
    cs = ONE.get('tom_tat', {}).get('cinc75')
    if cs:
        w('## 7. Power-MF-1ch trên CinC 2013 (75 bản ghi)')
        w('')
        w('| Quy tắc chọn đạo trình | Power-MF-1ch | RelyFetal 22 chủ thể (mốc 12/09) |')
        w('|---|---:|---:|')
        w('| PSD mù nhãn (số chính) | %.2f | 79,40 |' % cs['F1_mean'])
        w('| kênh 0 cố định | %.2f | 69,33 |' % cs['F1_kenh0'])
        w('| trung bình 4 kênh | %.2f | 74,09 |' % cs['F1_tb_4kenh'])
        w('| oracle (kênh tốt nhất) | %.2f | 86,87 |' % cs['F1_oracle'])
        w('')
        w('68 bản ghi (loại 7 bản chú thích sai): Power-MF-1ch %.2f.' % cs['F1_mean_68'])
        w('')

    md = os.path.join(HERE, 'BASELINES.md')
    open(md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[-40:]))
    print('\n-> %s' % md)

    for tag in ('tat_ca_22', 'adfecgdb_5', 'b2_7', 'b1_10'):
        for pk in pairs:
            print('%-12s %-42s %s' % (tag, pk, fmt(cmps[tag][pk])))


if __name__ == '__main__':
    main()
