<div align="center">

# RelyFetal

**Reliability-aware single-channel fetal QRS detection**

*A leakage-free benchmark, a three-tier contribution decomposition, and a reject-option gate — with a controlled negative result on persistent homology*

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/Docs-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20only-EE4C2C.svg)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/tests-53%20passing-brightgreen.svg)](tests/)

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
> Under a leakage-free protocol, six network architectures land within **1.53 points** of each other,
> and with **n = 5 subjects this study cannot tell them apart in either direction**: an equivalence
> test (TOST) at a pre-declared 1.0-point margin declares **0 of 7 architectures equivalent** to the
> 26 k-parameter dilated CNN and leaves 6 of 7 inconclusive. The architectural variables large enough
> to resolve at this sample size are dilation (+2.95 at equal parameters) and the receptive field
> (+4.49).

The earlier wording of this README — *"eight architectures are indistinguishable"* — was an
equivalence claim drawn from `p > 0.05`, i.e. from absence of evidence. It is withdrawn. So is the
sentence that generalised it to the whole field: this study measures five women, not a decade of
research.

---

## Headline results

Every number below is produced by code in this repository. Protocol throughout: event-level scoring,
**±50 ms** tolerance (CinC 2013 convention — three times stricter than ANSI/AAMI EC57), greedy one-to-one
matching cross-checked against optimal Hungarian assignment, **label-blind** channel selection.

### One model, five data configurations

| Dataset | Subjects | Minutes | Labels | F1, blind PSD lead | 95 % CI (cluster bootstrap) | F1, mean of 4 leads |
|---|---:|---:|---|---:|---|---:|
| ADFECGDB (PhysioNet), leave-one-record-out | 5 | 25 | scalp electrode | **99.21** | [97.87; 99.95] | 97.45 |
| Silesia B2 labour, 12 records | 12 | 60 | scalp electrode | 97.17 | [92.68; 99.75] | 95.26 |
| Silesia B2, only the 7 unseen records, zero-shot | 7 | 35 | scalp electrode | 95.87 | [88.41; 99.84] | 93.73 |
| **Silesia B1 pregnancy, 32–42 weeks, zero-shot** | 10 | 200 | indirect | **93.30** | [84.93; 99.37] | 91.31 |
| CinC 2013 set-a, zero-shot, **all 75 records** | 75 | 75 | crowd-sourced | 71.21 | SD 33.96, median 94.34¹ | 64.78 |

Intervals are 95 % cluster-bootstrap percentile intervals over subjects (10 000 resamples, seed 0;
`analysis/boot_ci_table1.py` → `analysis/boot_ci_table1.json`). They replace the `± SD` of earlier
versions, whose t-intervals ran above 100 % F1.

¹ **Retraction.** Earlier versions of this table gave **59.15 [38.32; 81.01]** for CinC 2013, measured
on a **10-record subsample** of set-a. That number is **withdrawn**: the subsample was biased, and on all
75 records the same model and the same label-blind rule score **71.21**. No cluster-bootstrap interval was
computed for the 75-record mean, so SD and median are quoted instead rather than inventing one
(`benchmark_dpss/eval_cinc75.json`).

The model was trained on 5 labour recordings only and had never seen pregnancy data. Moving from labour
to pregnancy *within the same recording system* costs ~4 points; moving to a *different recording system*
(CinC 2013) costs ~26 and produces a **bimodal** distribution — 15/75 records perfect, 22/75 below 50.
The variable that breaks generalisation is hardware and electrode placement, not gestational age.

A leakage check by cross-correlation showed that **5 of the 12 Silesia B2 records are the 5 PhysioNet
records** (NCC 0.988–0.994). Those five are scored with fold checkpoints that never saw them; the
independent subject count is therefore **22**, not 27.

### Retraining on 22 subjects

Retrained with grouped 11-fold CV over all 22 independent subjects (19 train / 1 validation / 2 test per
fold, on-the-fly augmentation, threshold chosen on the validation subject). Paired Wilcoxon against the
5-subject model on the same subjects and leads:

| Group | n | 5-subject model | **22-subject model** | p | wins/losses |
|---|---:|---:|---:|---:|---|
| PhysioNet labour | 5 | 99.21 | 99.40 | 1.00 | 2/2 |
| Silesia B2 labour, unseen | 7 | 95.87 | 96.82 | 0.125 | 4/0 |
| **Silesia B1 pregnancy** | 10 | 93.30 | **97.15** | **0.037** | 9/1 |
| All 22 | 22 | 95.46 | **97.56** | **0.007** | 15/3 |

#### Cross-system, zero-shot on CinC 2013 — now on all 75 records

> **Retraction.** Every CinC 2013 number this README carried before 12 Sep 2026 — **59.15**, **69.31**,
> **77.34**, **90.34** — was measured on a **10-record subsample** of set-a. All four are **withdrawn**.
> The subsample was biased **in both directions**, so this is not a rounding correction: it changed which
> lead-selection rule wins. The full set has now been run
> (`benchmark_dpss/eval_cinc75.py` → `eval_cinc75.json`).

The headline number is the **pre-declared, label-blind PSD rule** on all 75 records:

| Lead-selection rule | 5-subject model | **22-subject model** | Blind? |
|---|---:|---:|---|
| **PSD rule (pre-declared, label-blind)** — **headline** | 71.21 | **79.40** | yes |
| Mean of 4 leads | 64.78 | 74.09 | yes |
| Fixed lead 0 (**chosen post hoc**) | 58.72 | 69.33 | **no** |
| Oracle lead (uses test labels) | 78.21 | 86.87 | **no** |

Going from 5 to 22 training subjects is worth **+8.18 points** on the blind rule
(paired Wilcoxon *p* = 3.2 × 10⁻¹⁰, 53 wins / 5 losses / 17 ties, Cliff's δ = 0.23, bootstrap CI
[5.62; 11.09]). Records at F1 ≥ 90 go from 42 to 48; records below 50 go from 22 to 16.

**The post-hoc rule was not just illegitimate — it was also wrong.** On the 10-record subsample, fixed
lead 0 appeared to beat the blind PSD rule by 21 points (90.34 vs 69.31), and that apparent gap was the
reason the fixed lead was ever promoted. On all 75 records fixed lead 0 scores **69.33**, which is
**10.07 points worse** than the blind PSD rule and the **weakest of the four rules**. Selecting a
hyper-parameter after looking at the evaluation set produced a number that was optimistic by ~21 points
and a conclusion that reversed on the full set.

The lead-selection rule, not only the detector, loses accuracy across recorders — but by much less than
previously claimed: in domain the PSD rule is **0.02–1.90 points** below the oracle (ADFECGDB 0.02,
Silesia B2 0.66, Silesia B1 1.90), out of domain it is **7.47 points** below it (79.40 vs 86.87). The
earlier figure of **22.33 points** is **withdrawn** — it too came from the 10-record subsample.

**Pre-declared exclusion variant.** Seven set-a records have reference annotations known to be unreliable
(a33, a38, a47, a52, a54, a71, a74 — Behar/Oster/Clifford, CinC 2013;40:297–300). That exclusion was
declared before the run. On the remaining 68 records the blind PSD rule gives **72.08 → 80.70**
(5-subject → 22-subject). Both variants are reported; neither is selected after the fact.

Median signed offset against scalp-electrode labels stays at 0.0 ms, so the indirect B1 labels did not
pull the model. The sample-efficiency curve (1 → 2 → 3 training subjects: 91.2 → 93.4 → 97.5) is not
saturated, which is why 22 subjects still help.

**Two-seed stability (new).** Retraining the 22-subject model with seed 1 changes per-subject F1 by
**0.28 points on average** over the 20 subjects common to both runs, largest single change **2.81**
(B2_03). The per-fold decision thresholds are less stable: 0.50–0.80 for seed 1 against 0.20–0.80 for
seed 0 (seed 0 fold 10 used an extreme 0.20).

### Three-tier contribution decomposition

| Stage | Δ Macro F1 (per subject) | 95 % CI | Verdict |
|---|---:|---|---|
| Signal front-end (band-pass choice) | **+11.00** | not recomputable¹ | largest effect by far |
| Temporal context & per-sample output | +4.49 | [1.58; 7.43] bootstrap; [−0.29; 9.27] paired-t | positive, interval wide |
| Architecture family, at fixed context | +0.41 | inside the 1.0-point margin | **not resolvable at n = 5** |

¹ `pilot_evidence/band_ablation.json` stored only the aggregate per band, not F1 per
record × lead, so the tier-1 comparison cannot be re-tested at subject level. The `p < 0.001` once
quoted for it is **withdrawn as unverifiable**, not confirmed.

**All p-values on ADFECGDB have been removed.** With n = 5 subjects the smallest two-sided p an exact
Wilcoxon signed-rank test can produce is 2/2⁵ = **0.0625**, so *no* comparison on this database can
reach p < 0.05 at subject level, whatever the effect size. The former `1.9 × 10⁻⁶`, `5.7 × 10⁻⁶` and
`0.0000` were computed on 20–60 (record × lead × seed) rows treated as independent — pseudo-replication.
Full accounting in [`analysis/STATS.md`](analysis/STATS.md).

### Re-implemented classical baselines (ADFECGDB, same protocol, hyper-parameters tuned on r01 only)

| Method | Mean of 4 leads (n=20) | Blind PSD lead (n=5) | Δ vs model (per subject) | 95 % CI bootstrap | 95 % CI paired-t | Firm? |
|---|---:|---:|---:|---|---|---|
| Template subtraction + Pan–Tompkins | 78.96 ± 23.52 | 87.68 | −18.49 | [−30.60; −6.38] | **[−38.80; +1.81]** | **no — contains 0** |
| TS-PCA + Pan–Tompkins | 91.05 ± 10.17 | 96.74 | −6.40 | [−8.09; −4.70] | [−9.10; −3.69] | yes |
| Peak prominence on the **same front-end** | 86.39 ± 11.14 | 92.03 | −11.06 | [−14.51; −7.80] | [−16.38; −5.73] | yes |
| **FetalQRS-TCN** | **97.45 ± 4.44** | **99.21** | — | — | — | — |

**The three baselines are not equally firm and must not be read as one block.** Against TS-PCA and
prominence the interval excludes zero on both scales. Against plain TS it does not: the conservative
paired-t interval is [−38.80; +1.81] and contains zero, so the 18.49-point margin is driven by
between-woman variability (one record where TS collapses), not by a stable advantage.

The third baseline isolates the network's contribution: same residual, peak-picking instead of the
network → the network is worth **+11.06 points**, 95 % CI [7.80; 14.51], better in 5/5 women. TS-PCA
on the best lead reaches 96.74 — classical methods remain strong, consistent with the front-end
finding.

### Power-MF — re-run locally, and the question this repository actually answers

Power-MF (Jaeger et al. 2024) is a **multi-channel** method: it uses 4 abdominal leads and two rounds of
ICA. It has now been **re-run from the authors' own MATLAB source** under GNU Octave, scored with *our*
matcher (±50 ms, greedy one-to-one) on the same 22 subjects
(`baselines/powermf_fair_run.py`, [`baselines/BASELINES.md`](baselines/BASELINES.md)).

> **Retraction.** The Power-MF comparison published on the morning of 12 Sep 2026 — *"94.87 vs 97.61,
> Δ +2.74"* and *"98.38 vs 97.33, Δ −1.06"* — is **withdrawn in full**. Both rested on a **broken port**,
> not on Power-MF. Octave's `signal` package implements `findpeaks`' `MinPeakDistance` with an O(k²)
> pairwise distance matrix, which exhausts memory on the 6 long Silesia B1 records (2 395 600 samples
> after 4× interpolation); MATLAB — the authors' platform — uses a greedy O(k log k) algorithm and never
> hits this. **The fault was ours, not the method's.** The earlier hypothesis that
> `ms_minpeakdistance = 340 ms` was too tight is **also withdrawn**: measured against the reference
> annotations, **0.00 %** of B1_01's RR intervals fall below 340 ms
> (`baselines/powermf_rr_diag.json`), and the parameter was left at the authors' default throughout.
> `baselines/octave/findpeaks_mpd.m` reimplements MATLAB's semantics with a doubly-linked list in O(k),
> verified on 48/48 cases.

**External validation of the fix.** After the patch, Power-MF scores **99.40 ± 0.51** on Silesia B1. The
authors' **own published** figure on that set is **99.46** (`baselines/powermf_published.json`, extracted
from the upstream `Results/*.mat`). A 0.06-point gap says the port is now correct — which is exactly why
the pre-patch numbers had to go.

| Dataset | n | Power-MF, **4 leads** | Power-MF, **1 lead** | **RelyFetal, 1 lead** |
|---|---:|---:|---:|---:|
| ADFECGDB | 5 | 99.01 | 92.37 | **99.40** |
| Silesia B2 (labour) | 7 | 97.90 | 87.28 | 96.82 |
| Silesia B1 (pregnancy) | 10 | **99.40** | 83.48 | 97.15 |
| **All 22 subjects** | 22 | **98.83** | 86.71 | 97.56 |
| CinC 2013 set-a | 75 | not run | 62.82 | **79.40** |

Subject-level statistics (cluster bootstrap, 10 000 resamples of **subjects**, seed 0; paired Wilcoxon;
Cliff's δ), all 22 subjects:

| Comparison | Δ F1 | 95 % CI | p | Cliff's δ | win/tie/loss |
|---|---:|---|---:|---:|---|
| RelyFetal − Power-MF (4 leads) | −1.27 | [−3.08; +0.27] | 0.156 | 0.260 | 18/0/4 |
| RelyFetal − Power-MF (1 lead) | **+10.85** | [+6.80; +15.40] | 4.8 × 10⁻⁷ | 0.698 | **22/0/0** |
| Power-MF (1 lead) − Power-MF (4 leads) | −12.12 | [−18.27; −6.90] | 1.4 × 10⁻⁶ | — | 1/0/21 |

Per dataset, RelyFetal − Power-MF (4 leads): ADFECGDB **+0.39** [+0.22; +0.60], 5/0/0 — interval excludes
zero, so **we are ahead there**; Silesia B2 −1.08 [−4.04; +0.54], 6/0/1; Silesia B1 −2.25
[−5.55; +0.32], 7/0/3.

**The mean hides the shape of the result.** The **median** per-subject difference is **+0.23** and
RelyFetal wins **18 of 22** subjects. The negative mean is produced by exactly three records — B1_07
(86.56 vs 99.44, −12.88), B1_06 (89.45 vs 99.97, −10.51) and B2_03 (79.72 vs 89.49, −9.77), with a
fourth, mild one at B1_10 (−1.86). Any summary that quotes only the mean misrepresents the distribution.

**What this measures.** The question is not "who wins". It is: *how much of the benefit that multi-channel
source separation provides can a single-channel 113 481-parameter network recover?* The benefit is now
measurable, because Power-MF has been run in both configurations: dropping multi-channel separation costs
**Power-MF itself 12.12 F1 points** (98.83 → 86.71). The single-channel network recovers **10.85 of those
points — 89.5 % — from one lead**. The outcome is that it is **not distinguishable from multi-channel
Power-MF** (−1.27, CI [−3.08; +0.27], p = 0.156) and is **clearly ahead of Power-MF restricted to the
same single lead** (+10.85, 22/22 subjects).

This is deliberately *not* a claim of beating the state of the art, and the word is not used here.
Power-MF with 4 leads remains ahead on the raw mean.

### Reject-option gate and a negative result on persistent homology

A segment-level "will the model fail here?" classifier was trained on ADFECGDB and tested **cross-domain**
on CinC 2013:

| Feature set | AUROC | 95 % CI (bootstrap over the 10 records) | F1 at 80 % coverage | F1 at 50 % coverage |
|---|---:|---|---:|---:|
| Random rejection | 0.500 | — | 62.03 | 62.14 |
| 16 topological features (Takens + ripser, sublevel H0) | **0.566** | — | 63.40 | 64.44 |
| 12 classical SQIs | **0.929** | [0.830; 0.982] | **69.40** | **84.51** |
| All 28 | 0.905 | — | 69.41 | 82.44 |
| Oracle | — | — | 74.55 | 97.81 |

**The 0.929 is mostly a between-record effect.** Five of the ten CinC records contain no bad segment
at all, so the pooled AUROC largely answers *"is this a bad record?"*. Averaged over the five records
that contain both classes, the **within-record AUROC is 0.721** [0.517; 0.898] — and only that number
describes what a gate would do inside one monitoring session, which is the clinical use case.

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

## API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000          # or: docker compose up --build
curl http://127.0.0.1:8000/health
curl -F "file=@signal.npy" -F "lead=auto" -F "fs=1000" http://127.0.0.1:8000/analyze
```

FastAPI wrapper around `demo/core.py`, three endpoints: `GET /health` (is the production checkpoint present),
`GET /model` (parameter count, receptive field, threshold, config) and `POST /analyze` (EDF/CSV/TXT/NPY in;
`n_beats`, `fhr_mean`, `beats_ms`, `confidence{level,score,reasons}`, `latency_ms` out, plus `metrics` when a
label file is supplied). Input errors come back as `4xx` JSON, never a traceback. Request/response schema in
[`api/README.md`](api/README.md); tests in `tests/test_api.py` (no network, `fastapi.testclient`).

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
├─ powermf_fair_run.py      Power-MF (4 leads) re-run under Octave, incl. the P7 findpeaks patch
├─ powermf_1ch.py           Power-MF restricted to a single lead (Python port)
├─ octave/findpeaks_mpd.m   O(k) MinPeakDistance with MATLAB semantics (48/48 verified)
└─ BASELINES.md             Full baseline report, port-bug diagnosis and retraction

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
pytest tests/ demo/test_core.py                          # 53 tests
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

- **All 22 subjects come from one hospital and one recording system.** On a different system
  (CinC 2013, all 75 records) the 22-subject model reaches **79.4 under the blind lead rule**, against
  97–99 in-domain; multi-centre data is the remaining gap. The
  22-subject run is four epochs and the augmentation contribution has not been isolated; a second seed
  changes per-subject F1 by 0.28 points on average.
- **Sample size is the binding limitation.** ADFECGDB has five women and CinC 2013 ten records, so no
  comparison on ADFECGDB can be statistically significant at subject level and every interval quoted
  here is wide. The architecture benchmark is underpowered by construction, not inconclusive by
  accident.
- **CinC 2013 set-a is now evaluated in full (75 records, and 68 under the pre-declared exclusion).**
  Scoring still uses our own ±50 ms matcher rather than the original challenge scorer, so these are
  *not* official challenge entries even though the record set now matches.
- **The learned confidence gate is calibrated for the 5-subject model** and is over-conservative on
  pregnancy recordings (35 % green on Silesia vs 82 % for the rule). It has not been re-calibrated for
  the 22-subject model.
- **Architecture table is one seed, three epochs**, and omits the Transformer and both 2-D variants for
  cost. Rankings are unchanged in direction but absolute numbers are under-trained.
- **Confidence light in the demo is a hand-set rule.** The maternal-lock threshold (60 %) was set after
  looking at one evaluation record. The learned classical-SQI classifier from `fsqi/` should replace it.
- **Power-MF is now re-run locally, but only on the 22 in-house subjects** — not on CinC 2013, where
  only the single-lead port has been measured. The single-lead port is our reimplementation from the
  published description, not the authors' code, so it carries our reading of the method.
- **The +11.00-point band-pass result is measured on a 300 ms-window GBM, not on the TCN.** The
  band sweep on the TCN itself is still running (`pilot_evidence/band_tcn.py`; 10–60 Hz = 98.07 ± 4.05
  so far, 3 bands to go). Until it finishes, the tier-1 number describes a different model from the one
  this repository ships.
- **The proposed topological signal-quality index does not work** (AUROC 0.566 vs 0.929). This is
  reported as a negative result, not hidden.

---

## What is verified, and what is not

This table exists so a reader does not have to guess how much weight each number carries.
*Externally verified* means it can be checked against a source outside this repository.

| Claim | Status | Evidence |
|---|---|---|
| In-domain F1 (ADFECGDB 99.40; B2 96.82; B1 97.15) | **Reproducible in-repo** | `benchmark_dpss/eval_22.json`, grouped-fold protocol |
| No leakage between the 5 PhysioNet and Silesia B2 records | **Checked** | cross-correlation NCC 0.988–0.994; scored with fold checkpoints that never saw them |
| CinC 2013 = 79.40 on all 75 records | **Reproducible in-repo** | `benchmark_dpss/eval_cinc75.json` |
| Our Power-MF port is correct | **EXTERNALLY verified** | we measure 99.40 on B1; the authors publish 99.46 (`baselines/powermf_published.json`) — 0.06 apart |
| Power-MF 4-lead / 1-lead / RelyFetal table | **Reproducible in-repo** | `baselines/powermf_fair_stats.json`, `powermf_1ch.json` |
| More data helps for real, rather than learning an annotation style | **Independent evidence** | m12 (never saw B1) 74.34 vs m22 79.40 on CinC, whose labels were produced by different annotators (`analysis/ABLATION_B1.md`) |
| +11.00 points for the band-pass choice | **NOT verified on the TCN** | measured on a 300 ms-window GBM; the TCN sweep is still running (`pilot_evidence/band_tcn.py`) |
| Timing accuracy (jitter, STV) on Silesia B1 | **NOT usable** | B1 labels are indirect and carry a model-dependent offset (m5 6.50 / m12 6.50 / m22 3.25 ms) |
| Use as a standalone STV meter | **NO** | STV bias +0.33 ms on ADFECGDB but +20.50 ms on CinC (`analysis/CLINICAL.md`) |
| "Eight architectures are indistinguishable" | **WITHDRAWN** | TOST at a 1.0-point margin rejects it: cnn_m is worse, cnn_l is better (`analysis/STATS.md`) |
| Topological feature contribution (C3) | **WITHDRAWN — negative result** | AUROC 0.566 vs 0.929 for classical SQIs (`fsqi/README.md`) |
| Challenge-comparable CinC 2013 score | **NO** | scored with our own ±50 ms matcher, not the official scorer |
| Seed stability | **Only 2 seeds** | mean absolute change 0.28 points over 20 subjects |
| A second centre with real fQRS labels | **NOT available** | NInFEA does not distribute labels |

Every number in this README traces back to a JSON file on disk. Retractions are recorded in place, where
the old number used to stand, rather than being quietly deleted.

---

## Citation

```bibtex
@misc{ngo2026relyfetal,
  author = {Ngo, Binh Minh},
  title  = {RelyFetal: Reliability-aware single-channel fetal QRS detection},
  year   = {2026},
  school = {Ton Duc Thang University},
  note   = {Undergraduate research project, v3.3},
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
