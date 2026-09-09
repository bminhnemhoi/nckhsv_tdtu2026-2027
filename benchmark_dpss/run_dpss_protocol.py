"""
Chay FetalQRS-TCN dung giao thuc doi chuan cua goi 'goi-danh-gia-doi-chuan-dpss'.
Sinh file JSON dinh vi dinh R thai o 1000 Hz de nap vao benchmark_evaluator.py cua Khanh.

Hai che do:
  loro  - moi ban ghi dung checkpoint fold cua chinh no (mo hinh CHUA TUNG thay ban ghi do).
          Day la con so trung thuc, tuong duong LOSO ma tai lieu cua Khanh tuyen bo.
  prod  - checkpoint production (da train tren ca 5 ban ghi) -> CO RO RI, chi de tham chieu
          nhu 'within-subject upper bound'.
"""
import os, sys, json, argparse, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import numpy as np, torch, mne, wfdb

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(os.path.dirname(HERE), 'model')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _paths import adfecgdb_dir, cinc2013_dir
spec = importlib.util.spec_from_file_location('fqrs', os.path.join(MODEL, 'fqrs_model.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
CFG = M.CFG

# giao thuc dao trinh do goi cua Khanh quy dinh (chi so kenh trong file EDF)
LEAD = {'r01': 4, 'r04': 4, 'r07': 4, 'r08': 4, 'r10': 1}
RECS = ['r01', 'r04', 'r07', 'r08', 'r10']


def refine_1000(peaks_1000, x1000, fs=1000, win_ms=20):
    """dich moi dinh ve cuc tri bien do lon nhat trong +/- win_ms tren tin hieu 1000 Hz"""
    w = int(win_ms * fs / 1000); out = []
    for p in peaks_1000:
        s, t = max(0, p - w), min(len(x1000), p + w)
        if t > s:
            out.append(s + int(np.argmax(np.abs(x1000[s:t]))))
    return np.unique(np.asarray(out, int))


def main(mode, raw_dir, out_json):
    preds, meta = {}, {}
    for rec in RECS:
        ck = os.path.join(MODEL, 'checkpoints',
                          f'fetalqrs_tcn_fold_{rec}.pt' if mode == 'loro'
                          else 'fetalqrs_tcn_production.pt')
        blob = torch.load(ck, map_location='cpu', weights_only=False)
        net = M.FetalQRSTCN(); net.load_state_dict(blob['state_dict']); net.eval()
        thr = float(blob['threshold'])

        raw = mne.io.read_raw_edf(os.path.join(raw_dir, rec + '.edf'), preload=True, verbose=False)
        sig = raw.get_data()[LEAD[rec]]

        x250 = M.preprocess(sig, CFG['fs_in'], CFG)
        res, _ = M.cancel_maternal(x250, CFG)
        prob = M.probability_series(net, M.robust_scale(res).astype(np.float32),
                                    M.robust_scale(x250).astype(np.float32), CFG)
        pk250 = M.pick_peaks(prob, thr, CFG)
        pk1000 = (pk250.astype(np.int64) * (CFG['fs_in'] // CFG['fs']))

        # tin hieu du o 1000 Hz de tinh chinh vi tri dinh
        band = M.bandpass(np.asarray(sig, float), CFG['fs_in'], *CFG['band'])
        pk1000_ref = refine_1000(pk1000, band, CFG['fs_in'], 20)

        preds[rec] = [int(v) for v in (pk1000_ref if os.environ.get('REFINE') == '1' else pk1000)]
        meta[rec] = dict(checkpoint=os.path.basename(ck), threshold=thr,
                         lead_idx=LEAD[rec], lead_name=raw.ch_names[LEAD[rec]],
                         n_detected=len(preds[rec]),
                         train_records=blob.get('train_records', blob.get('trained_on')))
        print(f'{rec}  kenh {raw.ch_names[LEAD[rec]]:<10} ckpt {os.path.basename(ck):<28} '
              f'thr {thr:.2f}  phat hien {len(preds[rec])} dinh')

    json.dump(preds, open(out_json, 'w'), indent=1)
    json.dump(meta, open(out_json.replace('.json', '_meta.json'), 'w'), indent=1)
    print('\nda ghi', out_json)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['loro', 'prod'], default='loro')
    ap.add_argument('--raw-dir', default=None)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    main(a.mode, a.raw_dir or adfecgdb_dir(), a.out or os.path.join(HERE, f'predictions_minh_{a.mode}.json'))
