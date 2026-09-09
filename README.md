<div align="center">

# RelyFetal

**Reliability-aware single-channel fetal QRS detection**

*A leakage-free representation benchmark and a persistent-homology signal-quality index*

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/Docs-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20only-EE4C2C.svg)](https://pytorch.org/)
[![Data: PhysioNet](https://img.shields.io/badge/Data-PhysioNet%20ADFECGDB-006699.svg)](https://physionet.org/content/adfecgdb/)

Undergraduate research project · Faculty of Information Technology · Ton Duc Thang University · 2026–2027

[Vietnamese README](README.vi.md) · [Full proposal (PDF)](docs/De_cuong_NCKH_RelyFetal.pdf) · [30-paper survey (PDF)](docs/Bao_cao_30_paper.pdf)

</div>

---

## What this is

Detecting the fetal heartbeat from **a single abdominal ECG electrode** is the cheapest and most wearable
configuration for at-home pregnancy monitoring, and the hardest one to solve. The maternal QRS complex is
several times larger than the fetal one, the two overlap in frequency, and with one channel you cannot
fall back on multi-channel blind source separation.

This repository contains a complete, reproducible pipeline for that problem, plus the experimental
evidence behind every design decision.

**The main scientific result is counter-intuitive and is the point of the project:**

> Changing the band-pass filter is worth **+11.00 F1 points**.
> Changing the entire network architecture family, at fixed temporal context, is worth **+0.41 points**
> and is *not statistically distinguishable from noise* (Wilcoxon paired, `p = 0.7012`).

A field that has spent a decade designing ever-larger networks has been optimising the wrong stage.

---

## Headline results

All numbers below were produced by the code in this repository and can be regenerated end-to-end.
Protocol: PhysioNet ADFECGDB, **leave-one-record-out**, event-level scoring, **±50 ms** tolerance
(the CinC 2013 convention — three times stricter than the 150 ms of ANSI/AAMI EC57).

### In-domain, ADFECGDB (5 subjects)

| Channel-selection rule | Macro F1 | Se | PPV | Jitter |
|---|---:|---:|---:|---:|
| **Blind, power-spectral-density (reported)** | **99.21** | 99.59 | 98.79 | 3.05 ms |
| Fixed lead map prescribed by an external protocol | 99.18 | 99.59 | 98.79 | 3.05 ms |
| Oracle — uses ground-truth labels, *not reportable* | *99.21* | — | — | — |
| Mean over all four abdominal leads | 97.45 | 97.69 | 97.18 | 3.62 ms |

Micro-averaged over 3 191 annotated beats: **TP 3 178 · FP 40 · FN 13**.

### Cross-dataset, PhysioNet/CinC 2013 set-a — no fine-tuning

| Channel-selection rule | Macro F1 |
|---|---:|
| Fixed lead | **77.34 ± 28.54** |
| Blind PSD rule | 59.15 ± 37.17 |
| Oracle | 77.59 ± 28.14 |

The mean hides the real problem. The distribution is **bimodal**: 4 of 10 records score a perfect 100.0,
three collapse below 50. **The system does not know when it is wrong** — and that observation is what the
project's main novel contribution is built to fix.

### Three-tier contribution decomposition

| Stage | Δ Macro F1 | p | Verdict |
|---|---:|---:|---|
| Signal front-end (band-pass choice) | **+11.00** | < 0.001 | significant |
| Temporal context & output resolution | +4.53 | 0.0000 | significant |
| Architecture family, at fixed context | +0.41 | **0.7012** | **not significant** |

---

## Model

`FetalQRS-TCN` — a dilated residual temporal convolutional network, sequence-to-sequence.

| Property | Value |
|---|---|
| Trainable parameters | **113 481** |
| Checkpoint size | 0.48 MB |
| Receptive field | 379 samples = **1 516 ms** |
| Latency, one 4 s window | **4.35 ms** on CPU (920× real time) |
| Input | 2 × 1000 — maternal-cancelled residual + original signal, 4 s at 250 Hz |
| Output | one logit **per sample**; target is a Gaussian heat-map, σ = 12 ms |

```
1-channel aECG @ 1000 Hz
   ↓  Butterworth 10–60 Hz zero-phase + 50 Hz notch → resample to 250 Hz
   ↓  maternal QRS detection (8–25 Hz, RR ≥ 350 ms)
   ↓  median-template cancellation with per-beat least-squares scaling
   ↓  4-second segments, 2 × 1000
   ↓  FetalQRS-TCN — stem Conv1d(k=7) + 5 residual blocks, dilations 1,2,4,8,16
   ↓  per-sample heat-map → peak picking, threshold τ + 250 ms refractory
fetal beat positions + fetal heart rate
```

The architecture was **not** chosen because dilated TCNs are inherently superior. Across 16 architectures
at matched parameter budget, 13 reasonable ones span only 2.55 F1 points. What actually matters is the
**receptive field** (172 ms → 98.73; 748 ms → 99.25; 1 516 ms → 99.50; saturating thereafter,
`p = 0.0000` against the short-context baseline) and **per-sample output resolution** (localisation jitter
drops from 5.6–6.0 ms to 1.0 ms). A dilated TCN is simply the cheapest way to buy both: at comparable
receptive field a 1-D U-Net costs 678 257 parameters for a *lower* F1, and a Transformer is 21.7× slower
for +0.25 points.

---

## Evaluation protocol

Three rules are enforced throughout, because each is a common source of inflated numbers in this
literature:

1. **No training on the test subject.** Each record is scored by a checkpoint trained only on other
   records. Decision thresholds are selected on a *separate* inner validation record, never on the
   test record.
2. **±50 ms matching tolerance**, with greedy one-to-one event matching cross-checked against optimal
   Hungarian assignment (identical on all our data).
3. **Label-blind channel selection.** Picking the best of four leads by comparing against ground truth is
   oracle selection and is not reportable. We use a power-spectral-density rule
   (after Jaeger et al., *Physiol. Meas.* 2024) that never touches the labels.

---

## Repository layout

```
model/                    Core library, training, inference, trained weights
├─ fqrs_model.py            Reference implementation — every constant traced to an experiment
├─ train_final.py           LORO training, writes 5 fold checkpoints + 1 production model
├─ predict.py               CLI inference: EDF / WFDB / CSV / NPY
├─ download_data.py         Fetches PhysioNet sources, writes SHA-256 data card
└─ checkpoints/             6 trained models (0.48 MB each)

benchmark_dpss/           Benchmark harness
├─ _paths.py                Data-path resolution, keeps the repo self-contained
├─ run_dpss_protocol.py     Runs the model under an external benchmark protocol
├─ full_measure.py          Full metric suite + measured compute cost
├─ blind_lead.py            Label-blind PSD channel selection (in- and cross-domain)
└─ all_leads.py             Per-lead breakdown

pilot_evidence/           Every pilot experiment, with logs
├─ band_ablation.py         8 band-pass candidates
├─ arch_search.py           16 architectures at matched parameter budget
├─ seq_search.py            Receptive-field sweep
├─ seq_loro.py              3-seed LORO + paired Wilcoxon
└─ final_loro.py            Final leave-one-record-out run

de_cuong_latex/           Research proposal — LaTeX source
├─ make_figs.py             8 vector figures, data-driven
├─ gen_tables.py            LaTeX tables generated from the survey JSON
└─ make_docx.py             PDF → DOCX export via pandoc

survey/                   30-paper survey data + verified-facts ledger
docs/                     Compiled deliverables (PDF + DOCX)
tests/                    Smoke tests
```

---

## Installation

```bash
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

CPU is sufficient. The model trains in roughly 30 minutes on a laptop CPU; no GPU is required.

## Quickstart

```bash
# 1. Fetch ADFECGDB from PhysioNet (~15 MB) and write a SHA-256 data card
python model/download_data.py --root model/data --only adfecgdb

# 2. Run inference with a checkpoint that never saw this record
python model/predict.py \
    --input model/data/adfecgdb/r01.edf --lead 1 --annot qrs \
    --checkpoint model/checkpoints/fetalqrs_tcn_fold_r01.pt
```

```
fetal beats  645     fetal HR 127.7 bpm     maternal HR 82.0 bpm
Se 100.00   PPV 99.84   F1 99.92   jitter 1.58 ms   (TP 644, FP 1, FN 0)
```

## Reproducing every number

```bash
python model/train_final.py --epochs 6 --seed 0   # retrain all 6 checkpoints (~30 min CPU)

python benchmark_dpss/full_measure.py             # full metric suite + compute cost
python benchmark_dpss/blind_lead.py               # label-blind channel selection
python benchmark_dpss/all_leads.py                # per-lead breakdown

python pilot_evidence/band_ablation.py            # 8-band ablation
python pilot_evidence/seq_loro.py                 # 3-seed LORO + Wilcoxon
```

Rebuilding the proposal documents:

```bash
cd de_cuong_latex
python make_figs.py && python gen_tables.py
xelatex de_cuong.tex && xelatex de_cuong.tex && xelatex de_cuong.tex
python make_docx.py
```

---

## Data

No physiological recordings are redistributed here. `model/download_data.py` fetches them from the
original sources and records a SHA-256 for every file.

| Dataset | Source | Licence |
|---|---|---|
| ADFECGDB | [physionet.org/content/adfecgdb](https://physionet.org/content/adfecgdb/) · DOI 10.13026/C2RP4B | ODC-BY 1.0 |
| CinC 2013 set-a | [physionet.org/content/challenge-2013](https://physionet.org/content/challenge-2013/) | ODC-BY 1.0 |
| NSTDB | [physionet.org/content/nstdb](https://physionet.org/content/nstdb/) | ODC-BY 1.0 |
| NIFEADB | [physionet.org/content/nifeadb](https://physionet.org/content/nifeadb/) · DOI 10.13026/C2CT0S | ODC-BY 1.0 |
| Silesia (Matonia 2020) | figshare DOI 10.6084/m9.figshare.c.4740794 | manual download |
| FECGSYNDB | [physionet.org/content/fecgsyndb](https://physionet.org/content/fecgsyndb/) | ODC-BY 1.0 |

ADFECGDB is the primary set: 5 women in labour, weeks 38–41, four abdominal channels at 1 kHz, with
ground-truth fetal R-peaks taken from a **direct fetal scalp electrode** and verified by a cardiologist.

---

## Known limitations

Stated plainly, because a reviewer will find them anyway.

- **n = 5 subjects, all in labour at weeks 38–41.** No data below 38 weeks, whereas the clinical value of
  at-home monitoring lies in weeks 24–37. Extending to the Silesia set is the first planned task.
- **The 95 % confidence interval on 99.21 at n = 5 exceeds 100 %**, so the normal approximation is
  violated. Bootstrap or logit-scale intervals are required.
- **The 16-architecture table is optimistic in absolute terms.** It was run at 3–90 Hz rather than the
  optimal 10–60 Hz, on one validation record, one seed, with F1 taken as the maximum over an
  18-point threshold sweep *on the evaluation record itself*. It supports only *relative* comparison,
  because every architecture carries the same bias. Under it, `cnn_dil` ranks 5th, not 1st — the
  defensible claim is **parameter efficiency**, not architectural superiority.
- **No baseline has been re-implemented yet.** All comparisons with the literature are against
  *published* numbers, not against our own re-runs.
- **The persistent-homology signal-quality index is designed but not yet implemented.**

---

## Related work note

[Power-MF](https://doi.org/10.1088/1361-6579/ad4952) (Jaeger et al., *Physiol. Meas.* 45(5):055009, 2024;
code at [mad-lab-fau/fecg-benchmarking](https://github.com/mad-lab-fau/fecg-benchmarking)) reports
98.0 ± 3.0 % F1 on ADFECG B2 at the same 50 ms tolerance using **classical** signal processing. It is not
directly comparable — it uses four channels on the 500 Hz Silesia subsets whereas this work is
single-channel on the public 1 kHz records — but it is the strongest competing result and its
PSD-based channel-selection rule is the one adopted here.

---

## Citation

```bibtex
@misc{ngo2026relyfetal,
  author = {Ngo, Binh Minh},
  title  = {RelyFetal: Reliability-aware single-channel fetal QRS detection},
  year   = {2026},
  school = {Ton Duc Thang University},
  note   = {Undergraduate research project},
  url    = {https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027}
}
```

See [`CITATION.cff`](CITATION.cff) for machine-readable metadata.

---

## Licence

Source code is **MIT**. Documentation, figures and trained weights are **CC BY 4.0**. Physiological data
and third-party publications are **not** redistributed — see [`LICENSE`](LICENSE) for the full scope note.

> **Not a medical device.** This is a research prototype with no clinical validation and no regulatory
> clearance. It must not be used to inform any diagnostic or treatment decision.

## Acknowledgements

PhysioNet and the authors of the ADFECGDB, CinC 2013, NIFEADB and FECGSYNDB databases for making this
work possible. The MaD Lab at FAU Erlangen-Nürnberg for releasing the Power-MF benchmark code.
