# -*- coding: utf-8 -*-
"""
Chạy lõi demo trên các bản ghi có nhãn, chọn kênh tự động (PSD, mù nhãn), rồi chấm đèn tin cậy
ở một hoặc cả hai chế độ (`--mode hoc | luat | ca_hai`) và ghi:
    demo/results/demo_check_2modes.json / .log   (mặc định, --mode ca_hai)
    demo/results/demo_check_<mode>.json / .log   (chế độ đơn)
Không dùng nhãn để chọn bất cứ thứ gì; nhãn chỉ để chấm F1 sau khi đã phân tích.

Bản ghi (32):
    5  ADFECGDB  r01 r04 r07 r08 r10           checkpoint fold rXX (chưa từng thấy rXX), 300 s, nhãn điện cực da đầu
    10 CinC 2013 set-a a01..a10               production (zero-shot), 60 s
    17 Silesia   B1_01..10 (thai kỳ, 20 phút, nhãn GIÁN TIẾP) + B2_03,04,05,06,08,09,12 (chuyển dạ, 5 phút, nhãn da đầu)
                 production (zero-shot). Loại B2_01,02,07,10,11 vì chính là r01,r10,r04,r07,r08 của ADFECGDB
                 (benchmark_dpss/silesia_eval.json['leak_check']: NCC 0,988–0,994).
    + r01 kênh 4 thủ công (mốc kiểm thử).
JSON được ghi lại sau MỖI bản ghi -> ngắt giữa chừng vẫn giữ được phần đã chạy.

Chạy:  python demo/run_check.py --mode ca_hai --threads 2
       python demo/run_check.py --mode luat --no-silesia        # tái tạo bảng 15 bản ghi cũ
"""
import os, sys, json, time, argparse, importlib.util, traceback


def _args():
    ap = argparse.ArgumentParser(description='Kiểm tra lõi demo RelyFetal trên các bản ghi có nhãn')
    ap.add_argument('--mode', choices=('hoc', 'luat', 'ca_hai'), default='ca_hai',
                    help="chế độ đèn tin cậy: 'hoc' (GBM), 'luat' (quy tắc cứng), 'ca_hai' (mặc định)")
    ap.add_argument('--threads', type=int, default=None,
                    help='số luồng torch (đặt RELYFETAL_THREADS; đồng thời OMP/OPENBLAS/MKL_NUM_THREADS=1). Mặc định: core.py (4)')
    ap.add_argument('--no-silesia', action='store_true', help='bỏ 17 bản ghi Silesia (chỉ 15 bản ghi ADFECGDB + CinC)')
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

SILESIA_RECS = tuple(f'B1_{i:02d}' for i in range(1, 11)) + ('B2_03', 'B2_04', 'B2_05', 'B2_06', 'B2_08', 'B2_09', 'B2_12')
SILESIA_EXCLUDED = {'B2_01': 'r01', 'B2_02': 'r10', 'B2_07': 'r04', 'B2_10': 'r07', 'B2_11': 'r08'}   # silesia_eval.json leak_check
MODES = ('hoc', 'luat') if ARGS.mode == 'ca_hai' else (ARGS.mode,)
OUT = os.path.join(HERE, 'results'); os.makedirs(OUT, exist_ok=True)
BASE = ARGS.out or ('demo_check_2modes' if ARGS.mode == 'ca_hai' else f'demo_check_{ARGS.mode}')
LOG = open(os.path.join(OUT, BASE + '.log'), 'w', encoding='utf-8')
JSON_PATH = os.path.join(OUT, BASE + '.json')


def say(*a):
    s = ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()


def _silesia_loader():
    p = os.path.join(ROOT, 'model', 'silesia_loader.py')
    spec = importlib.util.spec_from_file_location('silesia_loader', p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def silesia_record(SL, rid):
    """model/silesia_loader.load(id) -> dict giống core.load_record (4 kênh bụng A1..A4 @1000 Hz, nhãn @1000 Hz)."""
    abd, fq, meta = SL.load(rid)
    return dict(name=rid, signals=np.asarray(abd, float), lead_names=['A1', 'A2', 'A3', 'A4'], fs=1000,
                fs_orig=float(meta['fs_native']), labels=np.asarray(fq, int), source='Silesia',
                duration_s=abd.shape[1] / 1000.0,
                extra=dict(stage=meta['stage'], reference_source=meta['reference_source'],
                           n_fqrs=int(meta['n_fqrs']), n_fqrs_flag0=int(meta['n_fqrs_flag0']),
                           fhr_median_label_bpm=float(meta['fhr_median_bpm'])))


def jobs():
    recs = core.sample_records()
    out = []
    for n in recs:
        out.append(dict(name=n, dataset=recs[n]['dataset'], lead='auto', kind='sample', path=recs[n]['path']))
    if not ARGS.no_silesia:
        try:
            SL = _silesia_loader(); SL.silesia_dir()
            for rid in SILESIA_RECS:
                out.append(dict(name=rid, dataset='Silesia ' + rid[:2] + (' thai kỳ' if rid.startswith('B1') else ' chuyển dạ'),
                                lead='auto', kind='silesia', loader=SL))
        except SystemExit as e:
            say(f'!! bỏ qua Silesia: {e}')
    if 'r01' in recs:
        out.append(dict(name='r01', dataset=recs['r01']['dataset'], lead=4, kind='sample', path=recs['r01']['path']))
    return out


def load(job):
    if job['kind'] == 'silesia':
        return silesia_record(job['loader'], job['name'])
    return core.load_record(job['path'])


def fmt_row(name, dataset, s):
    m = s.get('metrics') or {}
    bm = s['confidence_by_mode']
    cells = ''
    for md in MODES:
        c = bm[md]
        cells += f'{c["level"]:>11}{c["score"]:>7.3f}'
    lock = s['confidence']['components'].get('maternal_lock')
    gate_ms = bm['hoc']['components'].get('gate_ms') if 'hoc' in bm else None
    return (f'{name:<8}{dataset:<20}{s["checkpoint"].replace("fetalqrs_tcn_", "").replace(".pt", ""):<12}'
            f'{s["lead"]:>3}{s["duration_s"]:>6.0f}{s["n_beats"]:>6}{(s["fhr_mean"] or float("nan")):>7.1f}'
            f'{m.get("F1", float("nan")):>8.2f}{m.get("Se", float("nan")):>7.2f}{m.get("PPV", float("nan")):>7.2f}'
            f'{cells}{(lock if lock is not None else float("nan")):>7.2f}{s["latency_ms"]:>7.0f}'
            f'{(gate_ms if gate_ms is not None else float("nan")):>7.0f}')


def header():
    cells = ''.join(f'{"đèn(" + md + ")":>11}{"điểm":>7}' for md in MODES)
    return (f'{"bản ghi":<8}{"bộ dữ liệu":<20}{"checkpoint":<12}{"k":>3}{"s":>6}{"nhịp":>6}{"fHR":>7}'
            f'{"F1":>8}{"Se":>7}{"PPV":>7}{cells}{"bám mẹ":>7}{"ms":>7}{"gate":>7}')


def aggregate(rows):
    """Cho từng chế độ: bảng đèn x {n, F1 TB/min/max}, lỗi nguy hiểm, lỗi thận trọng, macro F1 và độ phủ."""
    auto = {k: s for k, s in rows.items() if 'metrics' in s and s['lead_requested'] == 'auto'}
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
                   torch_threads=core.torch.get_num_threads(), runtime_s=time.time() - t0,
                   records_done=done, records_total=total, complete=done == total,
                   rule=core.CONF_RULE, gate=gate,
                   silesia_records=list(SILESIA_RECS), silesia_excluded_duplicates_of_adfecgdb=SILESIA_EXCLUDED,
                   rows=rows, summary_by_mode=summ, suggested_default=suggested),
              open(JSON_PATH, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def main():
    t0 = time.time()
    J = jobs()
    say(f'RelyFetal demo -- kiểm tra lõi, chế độ đèn = {ARGS.mode}, {len(J)} lần phân tích  ({time.strftime("%Y-%m-%d %H:%M:%S")})')
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
