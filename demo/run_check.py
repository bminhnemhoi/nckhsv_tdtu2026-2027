# -*- coding: utf-8 -*-
"""
Chạy lõi demo trên các bản ghi mẫu có nhãn (core.sample_records), chọn kênh tự động mù nhãn
(`--lead peakprob | psd`, mặc định peakprob), rồi chấm đèn tin cậy ở một hoặc cả hai chế độ
(`--mode hoc | luat | ca_hai`) và ghi:
    demo/results/demo_check_2modes.json / .log   (mặc định, --mode ca_hai)
    demo/results/<--out>.json / .log
Không dùng nhãn để chọn bất cứ thứ gì; nhãn chỉ để chấm F1 sau khi đã phân tích.

Bản ghi (mô hình 22 chủ thể, checkpoint theo core.checkpoint_for):
    5  ADFECGDB  r01 r04 r07 r08 r10           fold 22 ca không chứa chủ thể, 300 s, nhãn điện cực da đầu
    60 CinC 2013 set-a SẠCH                    22_production (zero-shot), 60 s. 15 bản RÒ RỈ (bản sao ADFECGDB)
                                              bị loại mặc định (--include-leak để chạy cả, chỉ để đối chiếu)
    17 Silesia   B1_01..10 (thai kỳ, 20 phút, nhãn GIÁN TIẾP) + B2_03,04,05,06,08,09,12 (chuyển dạ, 5 phút)
                 fold 22 ca không chứa chủ thể. Loại B2_01,02,07,10,11 vì trùng ADFECGDB.
    + r01 kênh 4 thủ công (mốc kiểm thử).
JSON được ghi lại sau MỖI bản ghi -> ngắt giữa chừng vẫn giữ được phần đã chạy.

Chạy:  python demo/run_check.py --mode ca_hai --threads 2
       python demo/run_check.py --only r01,a09,B2_03,a02,a27 --out demo_check_showcase   # 5 bản minh hoạ
"""
import os, sys, json, time, argparse, traceback


def _args():
    ap = argparse.ArgumentParser(description='Kiểm tra lõi demo RelyFetal trên các bản ghi có nhãn')
    ap.add_argument('--mode', choices=('hoc', 'luat', 'ca_hai'), default='ca_hai',
                    help="chế độ đèn tin cậy: 'hoc' (GBM), 'luat' (quy tắc cứng), 'ca_hai' (mặc định)")
    ap.add_argument('--threads', type=int, default=None,
                    help='số luồng torch (đặt RELYFETAL_THREADS; đồng thời OMP/OPENBLAS/MKL_NUM_THREADS=1). Mặc định: core.py (4)')
    ap.add_argument('--no-silesia', action='store_true', help='bỏ 17 bản ghi Silesia')
    ap.add_argument('--lead', choices=('peakprob', 'psd'), default='peakprob', help='quy tắc chọn kênh mù nhãn (mặc định peakprob)')
    ap.add_argument('--only', default='', help='chỉ chạy các bản ghi này (phẩy), ví dụ r01,a09,B2_03,a02,a27')
    ap.add_argument('--include-leak', action='store_true', help='chạy cả 15 bản CinC rò rỉ (mặc định loại)')
    ap.add_argument('--out', default=None, help='tên gốc tệp kết quả trong demo/results (không đuôi)')
    return ap.parse_args()


ARGS = _args()
if ARGS.threads:
    os.environ['RELYFETAL_THREADS'] = str(ARGS.threads)
    for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[k] = '1'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import numpy as np                      # noqa: E402  (sau khi đặt biến môi trường luồng)
import core                             # noqa: E402

MODES = ('hoc', 'luat') if ARGS.mode == 'ca_hai' else (ARGS.mode,)
OUT = os.path.join(HERE, 'results'); os.makedirs(OUT, exist_ok=True)
BASE = ARGS.out or ('demo_check_2modes' if ARGS.mode == 'ca_hai' else f'demo_check_{ARGS.mode}')
LOG = open(os.path.join(OUT, BASE + '.log'), 'w', encoding='utf-8')
JSON_PATH = os.path.join(OUT, BASE + '.json')


def say(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()


def jobs():
    recs = core.sample_records()
    only = set(x.strip() for x in ARGS.only.split(',') if x.strip())
    out = []
    for n, info in recs.items():
        if only and n not in only:
            continue
        if info.get('leak') and not ARGS.include_leak:
            continue
        if info['kind'] == 'silesia' and ARGS.no_silesia:
            continue
        out.append(dict(name=n, dataset=info['dataset'], lead=ARGS.lead, kind=info['kind'], note=info.get('note', '')))
    if 'r01' in recs and (not only or 'r01' in only):
        out.append(dict(name='r01', dataset=recs['r01']['dataset'], lead=4, kind='edf', note='mốc kiểm thử'))
    return out


def load(job):
    return core.load_sample(job['name'])


def fmt_row(name, dataset, s):
    m = s.get('metrics') or {}
    bm = s['confidence_by_mode']
    cells = ''
    for md in MODES:
        c = bm[md]
        cells += f'{c["level"]:>11}{c["score"]:>7.3f}'
    lock = s['confidence']['components'].get('maternal_lock')
    gate_ms = bm['hoc']['components'].get('gate_ms') if 'hoc' in bm else None
    return (f'{name:<8}{dataset:<20}{s["checkpoint"].replace("fetalqrs_tcn_", "").replace(".pt", ""):<14}'
            f'{s["lead"]:>3}{s["duration_s"]:>6.0f}{s["n_beats"]:>6}{(s["fhr_mean"] or float("nan")):>7.1f}'
            f'{m.get("F1", float("nan")):>8.2f}{m.get("Se", float("nan")):>7.2f}{m.get("PPV", float("nan")):>7.2f}'
            f'{cells}{(lock if lock is not None else float("nan")):>7.2f}{s["latency_ms"]:>7.0f}'
            f'{(gate_ms if gate_ms is not None else float("nan")):>7.0f}')


def header():
    cells = ''.join(f'{"đèn(" + md + ")":>11}{"điểm":>7}' for md in MODES)
    return (f'{"bản ghi":<8}{"bộ dữ liệu":<20}{"checkpoint":<14}{"k":>3}{"s":>6}{"nhịp":>6}{"fHR":>7}'
            f'{"F1":>8}{"Se":>7}{"PPV":>7}{cells}{"bám mẹ":>7}{"ms":>7}{"gate":>7}')


def aggregate(rows):
    """Cho từng chế độ: bảng đèn x {n, F1 TB/min/max}, lỗi nguy hiểm, lỗi thận trọng, macro F1 và độ phủ."""
    auto = {k: s for k, s in rows.items() if 'metrics' in s and s['lead_requested'] in ('auto', 'peakprob', 'psd')}
    summ = {}
    for md in MODES:
        lv = {}; ds = {}
        f1_all = []
        for k, s in auto.items():
            level = s['confidence_by_mode'][md]['level']; f1 = s['metrics']['F1']
            lv.setdefault(level, []).append((s['record'], f1)); f1_all.append(f1)
            ds.setdefault(s['dataset_group'], {}).setdefault(level, []).append(s['record'])
        by_level = {l: dict(n=len(v), F1_mean=float(np.mean([f for _, f in v])), F1_min=float(min(f for _, f in v)),
                            F1_max=float(max(f for _, f in v)), records={r: round(f, 2) for r, f in v})
                    for l, v in lv.items()}
        green = lv.get('cao', []); red = lv.get('thap', []); yellow = lv.get('trung_binh', [])
        green_low = [(r, round(f, 2)) for r, f in green if f < 90.0]
        red_high = [(r, round(f, 2)) for r, f in red if f >= 95.0]
        non_red = green + yellow
        n = len(auto)
        scores = [s['confidence_by_mode'][md]['score'] for s in auto.values()]
        f1s = [s['metrics']['F1'] for s in auto.values()]
        try:
            from scipy.stats import spearmanr
            rho = float(spearmanr(scores, f1s).statistic)
        except Exception:
            rho = None
        summ[md] = dict(
            n_records=n, by_level=by_level,
            n_green_but_F1_below_90=len(green_low), green_but_F1_below_90=green_low,
            n_red_but_F1_at_least_95=len(red_high), red_but_F1_at_least_95=red_high,
            green_macro_F1=float(np.mean([f for _, f in green])) if green else None,
            green_coverage_pct=100.0 * len(green) / n if n else None,
            non_red_macro_F1=float(np.mean([f for _, f in non_red])) if non_red else None,
            non_red_coverage_pct=100.0 * len(non_red) / n if n else None,
            all_macro_F1=float(np.mean(f1_all)) if f1_all else None,
            spearman_score_vs_F1=rho,
            by_dataset=ds)
    return summ


def suggest_default(summ):
    """ít lỗi nguy hiểm hơn thắng; hoà -> macro F1 nhóm xanh cao hơn; hoà -> độ phủ xanh cao hơn; hoà -> giữ 'luat'."""
    if len(MODES) < 2:
        return None
    key = lambda md: (-summ[md]['n_green_but_F1_below_90'], summ[md]['green_macro_F1'] or 0.0,
                      summ[md]['green_coverage_pct'] or 0.0, 1 if md == 'luat' else 0)
    return max(MODES, key=key)


def dump(rows, summ, t0, done, total, suggested=None):
    gate = None
    if 'hoc' in MODES:
        try:
            import gate as fgate
            gate = fgate.gate_info()
        except Exception as e:
            gate = dict(error=str(e))
    json.dump(dict(generated=time.strftime('%Y-%m-%d %H:%M:%S'), mode=ARGS.mode, modes=list(MODES),
                   lead_rule=ARGS.lead, only=ARGS.only, include_leak=ARGS.include_leak, gate_note=core.GATE_NOTE,
                   torch_threads=core.torch.get_num_threads(), runtime_s=time.time() - t0,
                   records_done=done, records_total=total, complete=done == total,
                   rule=core.CONF_RULE, gate=gate,
                   silesia_records=list(core.SILESIA_RECS), silesia_excluded_duplicates_of_adfecgdb=core.SILESIA_DUP,
                   cinc_leak=core.CINC_LEAK, cinc_bad_annotation=list(core.CINC_BAD_ANN),
                   rows=rows, summary_by_mode=summ, suggested_default=suggested),
              open(JSON_PATH, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def main():
    t0 = time.time()
    J = jobs()
    say(f'RelyFetal demo -- kiểm tra lõi, chế độ đèn = {ARGS.mode}, chọn kênh = {ARGS.lead}, {len(J)} lần phân tích  ({time.strftime("%Y-%m-%d %H:%M:%S")})')
    say(core.GATE_NOTE)
    say(f'torch threads = {core.torch.get_num_threads()}  OMP_NUM_THREADS={os.environ.get("OMP_NUM_THREADS")}')
    say('=' * 140); say(header()); say('-' * 140)
    rows = {}; summ = {}
    for i, job in enumerate(J):
        name, lead = job['name'], job['lead']
        try:
            rec = load(job)
            out = core.analyze_record(rec, lead=lead, confidence_mode=ARGS.mode)
            s = core.summary(out)
            s['dataset'] = job['dataset']; s['lead_requested'] = str(lead)
            s['dataset_group'] = ('ADFECGDB' if job['dataset'].startswith('ADFECGDB') else
                                  'CinC' if job['dataset'].startswith('CinC') else job['dataset'].split()[1])
            s['note'] = job.get('note', ''); s['leak'] = name in core.CINC_LEAK; s['bad_annotation'] = name in core.CINC_BAD_ANN
            s['n_labels'] = int(len(rec['labels'])) if rec.get('labels') is not None else None
            if rec.get('extra'):
                s['silesia'] = rec['extra']
            rows[f'{name}_lead{lead}'] = s
            say(fmt_row(name, job['dataset'], s))
            del out, rec
        except Exception as e:                       # một bản ghi hỏng không được làm hỏng cả lần chạy
            say(f'!! {name} lead {lead}: {type(e).__name__}: {e}'); LOG.write(traceback.format_exc())
        summ = aggregate(rows); dump(rows, summ, t0, i + 1, len(J))
    say('-' * 140)
    suggested = suggest_default(summ)
    for md in MODES:
        S = summ[md]
        say(f'[{md}] {S["n_records"]} bản ghi (chọn kênh tự động):')
        for l in ('cao', 'trung_binh', 'thap'):
            if l in S['by_level']:
                a = S['by_level'][l]
                say(f'   đèn {l:<11}: {a["n"]:>2} bản ghi, F1 trung bình {a["F1_mean"]:6.2f}  (min {a["F1_min"]:6.2f}, max {a["F1_max"]:6.2f})')
        say(f'   XANH nhưng F1 < 90 (LỖI NGUY HIỂM): {S["n_green_but_F1_below_90"]}  {S["green_but_F1_below_90"]}')
        say(f'   ĐỎ nhưng F1 >= 95 (lỗi thận trọng):  {S["n_red_but_F1_at_least_95"]}  {S["red_but_F1_at_least_95"]}')
        gm = S['green_macro_F1']; nm = S['non_red_macro_F1']
        say(f'   macro F1 nhóm xanh = {gm if gm is None else round(gm, 2)} @ độ phủ {S["green_coverage_pct"]:.1f}%'
            f'  |  xanh+vàng = {nm if nm is None else round(nm, 2)} @ {S["non_red_coverage_pct"]:.1f}%'
            f'  |  mọi bản ghi = {S["all_macro_F1"]:.2f}  |  Spearman(điểm, F1) = {S["spearman_score_vs_F1"]}')
    if suggested:
        say(f'=> gợi ý chế độ mặc định theo quy tắc (ít lỗi nguy hiểm > macro F1 xanh > độ phủ > giữ luật): {suggested}')
    dump(rows, summ, t0, len(J), len(J), suggested)
    say(f'đã ghi {JSON_PATH}  ({(time.time() - t0) / 60:.1f} phút)')


if __name__ == '__main__':
    main()
