# -*- coding: utf-8 -*-
"""
Chạy lõi demo trên MỌI bản ghi mẫu có trên đĩa (ADFECGDB 5 bản ghi + CinC 2013 set-a 10 bản ghi),
chế độ chọn kênh tự động (PSD) và thêm r01 kênh 4, rồi ghi:
    demo/results/demo_check.json   -- mọi con số dùng trong README
    demo/results/demo_check.log    -- bảng đọc được
Không dùng nhãn để chọn bất cứ thứ gì; nhãn chỉ để chấm F1 sau khi đã phân tích.

Chạy:  python demo/run_check.py
"""
import os, sys, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
import core

OUT = os.path.join(HERE, 'results'); os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, 'demo_check.log'), 'w', encoding='utf-8')


def say(*a):
    s = ' '.join(str(x) for x in a); print(s); LOG.write(s + '\n'); LOG.flush()


def main():
    recs = core.sample_records()
    say(f'RelyFetal demo -- kiểm tra lõi trên {len(recs)} bản ghi mẫu  ({time.strftime("%Y-%m-%d %H:%M:%S")})')
    say(f'torch threads = {core.torch.get_num_threads()}')
    say('=' * 118)
    say(f'{"bản ghi":<8}{"bộ dữ liệu":<17}{"checkpoint":<26}{"kênh":>5}{"nhịp":>6}{"fHR":>7}'
        f'{"F1":>8}{"Se":>8}{"PPV":>8}{"jit ms":>8}{"đèn":>11}{"điểm":>7}{"bám mẹ":>8}{"ms":>7}')
    say('-' * 118)
    rows = {}
    jobs = [(n, 'auto') for n in recs] + ([('r01', 4)] if 'r01' in recs else [])
    for name, lead in jobs:
        rec = core.load_record(recs[name]['path'])
        out = core.analyze_record(rec, lead=lead)
        s = core.summary(out); s['dataset'] = recs[name]['dataset']; s['lead_requested'] = str(lead)
        rows[f'{name}_lead{lead}'] = s
        m = s.get('metrics') or {}
        c = s['confidence']
        say(f'{name:<8}{recs[name]["dataset"]:<17}{s["checkpoint"]:<26}{s["lead"]:>5}{s["n_beats"]:>6}'
            f'{(s["fhr_mean"] or float("nan")):>7.1f}{m.get("F1", float("nan")):>8.2f}{m.get("Se", float("nan")):>8.2f}'
            f'{m.get("PPV", float("nan")):>8.2f}{(m.get("jitter_ms") or float("nan")):>8.2f}'
            f'{c["level"]:>11}{c["score"]:>7.3f}{(c["components"].get("maternal_lock") or float("nan")):>8.2f}'
            f'{s["latency_ms"]:>7.0f}')
    say('-' * 118)
    # tổng hợp: đèn tin cậy có tách được bản ghi tốt / xấu không?
    lv = {}
    for k, s in rows.items():
        if 'metrics' in s and s['lead_requested'] == 'auto':
            lv.setdefault(s['confidence']['level'], []).append(s['metrics']['F1'])
    agg = {l: dict(n=len(v), F1_mean=float(np.mean(v)), F1_min=float(np.min(v)), F1_max=float(np.max(v)))
           for l, v in lv.items()}
    for l in ('cao', 'trung_binh', 'thap'):
        if l in agg:
            a = agg[l]
            say(f'đèn {l:<11}: {a["n"]:>2} bản ghi, F1 trung bình {a["F1_mean"]:.2f}  (min {a["F1_min"]:.2f}, max {a["F1_max"]:.2f})')
    json.dump(dict(generated=time.strftime('%Y-%m-%d %H:%M:%S'), rule=core.CONF_RULE, rows=rows, by_level=agg),
              open(os.path.join(OUT, 'demo_check.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    say(f'đã ghi {os.path.join(OUT, "demo_check.json")}')


if __name__ == '__main__':
    main()
