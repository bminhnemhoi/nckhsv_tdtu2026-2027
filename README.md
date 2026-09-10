<div align="center">

# RelyFetal

**Reliability-aware single-channel fetal QRS detection**

*A leakage-free benchmark, a three-tier contribution decomposition, and a reject-option gate — with a controlled negative result on persistent homology*

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/Docs-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20only-EE4C2C.svg)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/tests-24%20passing-brightgreen.svg)](tests/)

Undergraduate research project · Faculty of Information Technology · Ton Duc Thang University · 2026–2027

[Vietnamese README](README.vi.md) · [Full proposal (PDF)](docs/De_cuong_NCKH_RelyFetal.pdf) · [30-paper survey (PDF)](docs/Bao_cao_30_paper.pdf) · [Demo](demo/)

</div>

---

## What this is

Detecting the fetal heartbeat from **a single abdominal ECG electrode** is the cheapest and most wearable
configuration for at-home pregnancy monitoring, and the hardest one to solve. The maternal QRS complex is
several times larger than the fetal one, the two overlap in frequency, and with one channel there is no
multi-channel blind source separation to fall back on.

This repository contains a complete, reproducible pipeline for that problem, the experimental evidence
behind every design decision, three re-implemented classical baselines, a working demo with a confidence
light, and one carefully controlled negative result.

**The main scientific result is counter-intuitive:**

> Changing the band-pass filter is worth **+11.00 F1 points**.
> Under a leakage-free protocol, **six network architectures land within 1.5 points of each other and none
> differs significantly from a 26 k-parameter dilated CNN** (all paired-Wilcoxon `p ≥ 0.105`). The only
> architectural variable that matters is the receptive field (`p = 0.0001`).

A field that has spent a decade designing ever-larger networks has been optimising the wrong stage.

---

## Headline results

Every number below is produced by code in this repository. Protocol throughout: event-level scoring,
**±50 ms** tolerance (CinC 2013 convention — three times stricter than ANSI/AAMI EC57), greedy one-to-one
matching cross-checked against optimal Hungarian assignment, **label-blind** channel selection.

### One model, five data configurations

| Dataset | Subjects | Minutes | Labels | F1, blind PSD lead | F1, mean of 4 leads |
|---|---:|---:|---|---:|---:|
| ADFECGDB (PhysioNet), leave-one-record-out | 5 | 25 | scalp electrode | **99.21 ± 1.50** | 97.45 ± 2.96 |
| Silesia B2 labour, 12 records | 12 | 60 | scalp electrode | 97.17 ± 7.45 | 95.26 ± 9.59 |
| Silesia B2, only the 7 unseen records, zero-shot | 7 | 35 | scalp electrode | 95.87 ± 9.75 | 93.73 ± 12.48 |
| **Silesia B1 pregnancy, 32–42 weeks, zero-shot** | 10 | 200 | indirect | **93.30 ± 13.46** | 91.31 ± 9.99 |
| CinC 2013 set-a, zero-shot | 10 | 10 | crowd-sourced | 59.15 ± 37.17 | 61.96 ± 34.09 |

The model was trained on 5 labour recordings only and had never seen pregnancy data. Moving from labour
to pregnancy *within the same recording system* costs ~4 points; moving to a *different recording system*
(CinC 2013) costs ~38 and produces a **bimodal** distribution — 4/10 records perfect, 5/10 below 50.
The variable that breaks generalisation is hardware and electrode placement, not gestational age.

A leakage check by cross-correlation showed that **5 of the 12 Silesia B2 records are the 5 PhysioNet
records** (NCC 0.988–0.994). Those five are scored with fold checkpoints that never saw them; the
independent subject count is therefore **22**, not 27.

### Three-tier contribution decomposition

| Stage | Δ Macro F1 | p | Verdict |
|---|---:|---:|---|
| Signal front-end (band-pass choice) | **+11.00** | < 0.001 | significant |
| Temporal context & per-sample output | +4.53 | 0.0000 | significant |
| Architecture family, at fixed context | +0.41 | **0.7012** | **not significant** |

### Re-implemented classical baselines (ADFECGDB, same protocol, hyper-parameters tuned on r01 only)

| Method | Mean of 4 leads (n=20) | Blind PSD lead (n=5) | Δ vs model | p, worse in |
|---|---:|---:|---:|---|
| Template subtraction + Pan–Tompkins | 78.96 ± 23.52 | 87.68 | −18.49 | 5.7×10⁻⁶, 19/20 |
| TS-PCA + Pan–Tompkins | 91.05 ± 10.17 | 96.74 | −6.40 | 1.9×10⁻⁶, 20/20 |
| Peak prominence on the **same front-end** | 86.39 ± 11.14 | 92.03 | −11.06 | 1.9×10⁻⁶, 20/20 |
| **FetalQRS-TCN** | **97.45 ± 4.44** | **99.21** | — | — |

The third baseline isolates the network's contribution: same residual, peak-picking instead of the
network → the network is worth **+11.06 points**. TS-PCA on the best lead reaches 96.74 — classical
methods remain strong, consistent with the front-end finding.

### Reject-option gate and a negative result on persistent homology

A segment-level "will the model fail here?" classifier was trained on ADFECGDB and tested **cross-domain**
on CinC 2013:

| Feature set | AUROC | F1 at 80 % coverage | F1 at 50 % coverage |
|---|---:|---:|---:|
| Random rejection | 0.500 | 62.03 | 62.14 |
| 16 topological features (Takens + ripser, sublevel H0) | **0.566** | 63.40 | 64.44 |
| 12 classical SQIs | **0.929** | **69.40** | **84.51** |
| All 28 | 0.905 | 69.41 | 82.44 |
| Oracle | — | 74.55 | 97.81 |

Persistent-homology features barely beat random, add nothing to classical features, and flip correlation
sign between datasets. The strongest single predictors of failure are the model's own confidence
(`prob_max`, AUROC 0.970), RR regularity (0.915) and the 10–60 Hz band-energy ratio (0.904). The reject
gate itself works: +7.4 F1 at 80 % coverage. **The topological contribution originally proposed was
tested with proper controls and withdrawn.**

---

## Model

`FetalQRS-TCN` — dilated residual temporal convolutional network, sequence-to-sequence.

| Property | Value |
|---|---|
| Trainable parameters | **113 481** |
| Checkpoint size | 0.48 MB |
| Receptive field | 379 samples = **1 516 ms** |
| Latency, one 4 s window | **4.35 ms** on CPU (920× real time) |
| Input | 2 × 1000 — maternal-cancelled residual + original, 4 s at 250 Hz |
| Output | one logit **per sample**; Gaussian heat-map target, σ = 12 ms |

```
1-channel aECG @ 1000 Hz
   ↓  Butterworth 10–60 Hz zero-phase + 50 Hz notch → 250 Hz
   ↓  maternal QRS detection (8–25 Hz, RR ≥ 350 ms)
   ↓  median-template cancellation, per-beat least-squares scaling
   ↓  4-second segments, 2 × 1000
   ↓  FetalQRS-TCN — stem Conv1d(k=7) + 5 residual blocks, dilations 1,2,4,8,16
   ↓  per-sample heat-map → peak picking, threshold τ + 250 ms refractory
   ↓  confidence gate (model confidence, RR plausibility, band ratio, maternal-lock check)
fetal beat positions + fetal heart rate + confidence level
```

Under the corrected protocol (10–60 Hz, 5-fold LORO, threshold chosen on an inner validation record),
eight 300 ms-window architectures score 37.5–92.4; the full 4 s sequence-to-sequence model scores 97.43.
The dilated CNN was kept for **parameter efficiency**, not because its family is superior.

---

## Demo

```bash
python demo/app.py        # → http://127.0.0.1:7860
```

Gradio, one page: upload EDF/WFDB/CSV or pick a sample record, automatic label-blind channel selection,
five-tier signal view (raw → filtered → residual → probability → result), fetal heart-rate trace, and a
**confidence light**. Selecting an ADFECGDB record automatically uses the fold checkpoint that never saw it.

| Light | Records | Mean F1 | Min F1 |
|---|---:|---:|---:|
| Green | 8 | 99.54 | 96.54 |
| Yellow | 5 | 50.51 | 21.05 |
| Red | 2 | 19.36 | 16.96 |

No record with F1 < 96.5 was ever marked green. The two worst CinC records are caught by a maternal-lock
rule (≥ 60 % of "fetal" beats coincide with maternal R-peaks). Tested at three levels: unit tests on the
core, HTTP smoke test, and `gradio_client` API call. Screenshots in [`demo/screenshots/`](demo/screenshots/).

> Research prototype. Not a medical device. Not for diagnostic use.

---

## Repository layout

```
model/                    Core library, training, inference, weights
├─ fqrs_model.py            Reference implementation — every constant traced to an experiment
├─ train_final.py           LORO training → 5 fold checkpoints + 1 production model
├─ predict.py               CLI inference: EDF / WFDB / CSV / NPY
├─ download_data.py         PhysioNet sources with SHA-256 data card
├─ download_silesia.py      Resumable figshare download (URL expires in 10 s, needs Range + retry)
├─ silesia_loader.py        Silesia .ecg reader (int16 big-endian, 500 Hz) → 1 kHz
└─ checkpoints/             6 trained models, 0.48 MB each

benchmark_dpss/           Benchmark harness
├─ _paths.py                Data-path resolution (repo is self-contained)
├─ full_measure.py          Full metric suite + measured compute cost
├─ blind_lead.py            Label-blind PSD channel selection, in- and cross-domain
├─ silesia_eval.py          Silesia B1/B2 evaluation + cross-correlation leakage check
└─ all_leads.py             Per-lead breakdown

baselines/                Re-implemented classical methods
├─ ts_baseline.py           TS, TS-PCA, prominence; Pan–Tompkins detector; Wilcoxon vs model
└─ powermf_status.json      Why Power-MF could not be re-run locally

fsqi/                     Signal-quality index experiment (contribution C3)
├─ fsqi.py                  28 features: Takens+ripser H0/H1, sublevel H0, classical SQIs
├─ eval_fsqi.py             Cross-domain failure prediction, risk–coverage curves
└─ README.md                Full negative-result report

demo/                     Gradio application
├─ core.py                  Pipeline logic, no UI dependency, unit-tested
├─ app.py                   One-page UI with confidence light
└─ screenshots/             Real captures from the running app

pilot_evidence/           Every pilot experiment with logs
├─ arch_loro.py             Corrected 8-architecture comparison (LORO, 10–60 Hz)
├─ band_ablation.py         8 band-pass candidates
├─ seq_search.py            Receptive-field sweep
└─ seq_loro.py              3-seed LORO + paired Wilcoxon

de_cuong_latex/           Research proposal — LaTeX source, data-driven figures and tables
survey/                   30-paper survey + verified-facts ledgers
docs/                     Compiled deliverables (PDF + DOCX)
tests/                    Smoke tests pinning every quoted number
```

---

## Installation and quickstart

```bash
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python model/download_data.py --root model/data --only adfecgdb    # ~15 MB from PhysioNet
python model/predict.py --input model/data/adfecgdb/r01.edf --lead 1 --annot qrs \
                        --checkpoint model/checkpoints/fetalqrs_tcn_fold_r01.pt
```

```
fetal beats  645     fetal HR 127.7 bpm     maternal HR 82.0 bpm
Se 100.00   PPV 99.84   F1 99.92   jitter 1.58 ms   (TP 644, FP 1, FN 0)
```

CPU only. Retraining all six checkpoints takes ~30 minutes on a laptop.

## Reproducing every number

```bash
python model/train_final.py --epochs 6 --seed 0          # 6 checkpoints
python benchmark_dpss/full_measure.py                    # metrics + compute cost
python benchmark_dpss/blind_lead.py                      # channel-selection rules
python baselines/ts_baseline.py                          # classical baselines (~2 min)
python pilot_evidence/arch_loro.py                       # corrected architecture table (~20 min)
python model/download_silesia.py && python benchmark_dpss/silesia_eval.py   # Silesia (~4 min after download)
python fsqi/eval_fsqi.py                                 # reject gate + negative result (~4 min)
python demo/run_check.py && python demo/smoke_app.py     # demo checks
pytest tests/ demo/test_core.py                          # 24 tests
```

---

## Data

No physiological recordings are redistributed. Download scripts record a SHA-256 for every file.

| Dataset | Source | Licence | Used for |
|---|---|---|---|
| ADFECGDB | physionet.org/content/adfecgdb · DOI 10.13026/C2RP4B | ODC-BY 1.0 | training, LORO evaluation |
| Silesia B1/B2 (Matonia 2020) | figshare DOI 10.6084/m9.figshare.c.4740794 · *Sci Data* 7:200 | CC0 | zero-shot generalisation |
| CinC 2013 set-a | physionet.org/content/challenge-2013 | ODC-BY 1.0 | cross-system generalisation |

Silesia B1 (pregnancy) has **no scalp electrode**; its labels are indirect (author's maternal cancellation
+ automatic detection + expert correction) and sit 8–12 ms after the abdominal R-peak in 5/10 records.
F1 on B1 measures agreement with that pipeline, not physiological ground truth.

---

## Known limitations

- **Training set is still 5 subjects, all in labour.** Evaluation now spans 22 independent subjects
  including 10 in pregnancy, but retraining on all 22 (Phase P3) has not been done.
- **Cross-system generalisation is unsolved.** 59–77 F1 on CinC 2013 with a bimodal distribution. The
  reject gate mitigates it (+7.4 points at 80 % coverage); pre-training on FECGSYNDB (Phase P7) is the
  planned fix.
- **Architecture table is one seed, three epochs**, and omits the Transformer and both 2-D variants for
  cost. Rankings are unchanged in direction but absolute numbers are under-trained.
- **Confidence light in the demo is a hand-set rule.** The maternal-lock threshold (60 %) was set after
  looking at one evaluation record. The learned classical-SQI classifier from `fsqi/` should replace it.
- **Power-MF was not re-run** (MATLAB, missing multi-channel dependencies); its 98.0 % remains a
  published number.
- **The proposed topological signal-quality index does not work** (AUROC 0.566 vs 0.929). This is
  reported as a negative result, not hidden.

---

## Citation

```bibtex
@misc{ngo2026relyfetal,
  author = {Ngo, Binh Minh},
  title  = {RelyFetal: Reliability-aware single-channel fetal QRS detection},
  year   = {2026},
  school = {Ton Duc Thang University},
  note   = {Undergraduate research project, v3.1},
  url    = {https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027}
}
```

See [`CITATION.cff`](CITATION.cff).

## Licence

Source code **MIT**. Documentation, figures and trained weights **CC BY 4.0**. Physiological data and
third-party publications are **not** redistributed — see [`LICENSE`](LICENSE).

> **Not a medical device.** Research prototype with no clinical validation and no regulatory clearance.

## Acknowledgements

PhysioNet; the Silesian Institute of Technology group (Matonia, Jezewski et al.) for the Silesia dataset;
the MaD Lab at FAU Erlangen-Nürnberg for the Power-MF benchmark code.
