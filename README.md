<div align="center">

# RelyFetal

**Reliability-aware single-channel fetal QRS detection**

*A leakage-free benchmark, a three-tier contribution decomposition, and a reject-option gate — with a controlled negative result on persistent homology*

[![License: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/Docs-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20only-EE4C2C.svg)](https://pytorch.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-brightgreen.svg)](tests/)

Undergraduate research project · Faculty of Information Technology · Ton Duc Thang University · 2026–2027

[Vietnamese README](README.vi.md) · [Full proposal (PDF)](docs/De_cuong_NCKH_RelyFetal.pdf) · [30-paper survey (PDF)](docs/Bao_cao_30_paper.pdf) · [Demo](demo/)

</div>

---

> **Picking this project up? Start with [`HANDOFF.md`](HANDOFF.md)** (Vietnamese) — setup, data download,
> repository map, the single source of truth for every number, integrity rules, known technical traps, and
> the prioritised to-do list. What changed and what was withdrawn, round by round: [`CHANGELOG.md`](CHANGELOG.md).

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

> On a 300 ms-window learner, changing the band-pass filter was worth **+11.00 F1 points**; re-measured on
> the TCN itself over 22 women the same change is worth only **+2.44 [−0.05; +6.30]** (interval contains
> zero, `pilot_evidence/band_tcn.json`), so the **+11.00 headline is withdrawn** as a claim about the model
> shipped here.
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
| CinC 2013 set-a, zero-shot, **60 clean records**¹ | 60 | 60 | crowd-sourced | 64.04 | [55.4; 72.5] | 56.00 |

Intervals are 95 % cluster-bootstrap percentile intervals over subjects (10 000 resamples, seed 0;
`analysis/boot_ci_table1.py` → `analysis/boot_ci_table1.json`). They replace the `± SD` of earlier
versions, whose t-intervals ran above 100 % F1.

¹ **Retraction (twice), and a correction of who found what.** Earlier versions of this table gave
**59.15 [38.32; 81.01]** (a 10-record subsample) and then **71.21** (all 75 records) for CinC 2013. **Both
are withdrawn.** Set-a is not independent of ADFECGDB, and **this was documented by the Challenge organisers
from the start**: Silva et al. (CinC 2013;40:149–152, Table 1: "Abdominal and Direct FECG — 25 records")
and Clifford et al. (Physiol Meas 2014;35:1521, Table 2), who also warned that an entry trained on
ADFECGDB "may have led to a bias in the results as this database was included in set-a, set-b (and possibly
a few records in set-c)". That sentence was already in our own reading notes
(`de_cuong_latex/tables/bang_baihoc.tex`, entry p20) and we failed to act on it; an earlier version of this
README and of `analysis/DULIEU.md` presented the overlap as our finding — **that wording is withdrawn**
(`survey/RO_RI_VANLIEU.md`). What no accessible source states is *which* set-a records are ADFECGDB, and
that part we measured (`analysis/dulieu_audit.py`, independently re-implemented in
`analysis/dulieu_m4b_verify.py`): exactly **15 of the 75 records are verbatim copies of the five training
recordings** (normalised cross-correlation = 1.0000 on all four channels in order, RR offset 0.0 ms; the
known B2↔PhysioNet duplicates, used as positive controls, reach only 0.86–0.98; the 60 other records peak at
0.44 filtered / 0.62 raw). Each ADFECGDB record appears three times, as its 0–60 s, 120–180 s and 240–300 s
windows: r01→a04,a05,a22 · r04→a13,a20,a25 · r07→a19,a23,a24 · r08→a08,a15,a17 · r10→a03,a12,a14. Every
production model was trained on those five women, so the 15 records are not out-of-domain. All headline
CinC numbers are now computed on the **60 clean records** (`benchmark_dpss/eval_cinc60_sach.py` →
`eval_cinc60_sach.json`; 10 000 bootstrap resamples of records, seed 0). The 15 leaked records score 99.87
under the 22-subject model, which is how they inflated the old means by 3.27–7.18 points.

The model was trained on 5 labour recordings only and had never seen pregnancy data. Moving from labour
to pregnancy *within the same recording system* costs ~4 points; moving to a *different recording system*
(CinC 2013, 60 clean records) costs ~35 and produces a split distribution — 27/60 records at or above 90,
22/60 below 50 (descriptive only: the two modes are a lead-selection artefact, not two populations,
`analysis/LUONGCUC.md`). The variable that breaks generalisation is hardware and electrode placement, not
gestational age.

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

#### Cross-system, zero-shot on CinC 2013 — 60 clean records

> **Retraction.** Every CinC 2013 number this README carried before 12 Sep 2026 — **59.15**, **69.31**,
> **77.34**, **90.34** (10-record subsample) and then **71.21 / 79.40 / 86.87 / +8.18 / +7.47** and every
> other figure computed on **all 75 records** — is **withdrawn**. The first set was a biased subsample; the
> second set is contaminated by the 15 records that are copies of the training data (footnote ¹ above),
> and additionally violates record-level independence because those 15 records come from only 5 women.
> The 75-record figures are kept in `benchmark_dpss/eval_cinc75.json` and in the analysis reports for
> traceability only; nothing below uses them.

The headline number is the **label-blind PSD rule** on the 60 clean records
(`benchmark_dpss/eval_cinc60_sach.json`):

| Lead-selection rule | 5-subject model | **22-subject model** | Blind? |
|---|---:|---:|---|
| **PSD rule (declared, label-blind)** — **headline** | 64.04 | **74.28** [66.6; 81.8] | yes |
| Mean of 4 leads | 56.00 | 67.69 | yes |
| Fixed lead 0 (**chosen post hoc, withdrawn**) | 48.43 | 61.78 | **no** |
| Oracle lead (uses test labels) | 72.76 | 83.60 | **no** |

Going from 5 to 22 training subjects is worth **+10.24 points** on the blind rule
(paired Wilcoxon *p* = 3.5e-10, 52 wins / 3 losses / 5 ties, bootstrap CI
[+7.13; +13.60]) — larger than the +8.18 measured on the contaminated set, because the 15 leaked
records sat at 100 for every model and compressed the difference. Records at F1 ≥ 90: 27 → 33 of 60; records
below 50: 22 → 16. Median F1 of the 22-subject model is 95.07.

The lead-selection rule, not only the detector, loses accuracy across recorders: in domain the PSD rule is
**0.02–1.90 points** below the oracle (ADFECGDB 0.02, Silesia B2 0.66, Silesia B1 1.90); on the 60 clean
CinC records it is **9.32 points** below it (74.28 vs 83.60, CI [+5.10; +14.15]) and picks the
oracle lead in only 17/60 records. The earlier gap of 7.47 (75 records) understated the problem.

**Declared exclusion variant.** Seven set-a records have reference annotations known to be unreliable
(a33, a38, a47, a52, a54, a71, a74 — Behar/Oster/Clifford, CinC 2013;40:297–300); the list was declared
before the first run. On the 53 clean records that remain the blind PSD rule gives
**64.19 → 75.27** (5-subject → 22-subject). Both variants are reported; neither is selected after the fact.

#### A better label-blind lead rule — reported as a hypothesis, not a confirmed result

Seven label-blind lead rules were compared against the PSD rule on the same 60 clean records
(`analysis/CHONKENH.md`, `analysis/dulieu_results.json → chon_kenh_60_sach`). The strongest is
**`peakprob`**: run the detector on all four leads and keep the lead whose mean model probability at its
own detected peaks is highest — no training, no hyper-parameter.

| Rule (22-subject model, 60 clean records) | mean F1 | Δ vs PSD | 95 % CI | Wilcoxon p | Holm p (7 rules) | < 50 |
|---|---:|---:|---|---:|---:|---:|
| PSD (current) | 74.28 | — | — | — | — | 16 |
| `gate` — **the rule the written analysis plan designated** | 80.72 | +6.44 | [+2.49; +11.10] | 0.010 | **0.0505 — fails** | 12 |
| `gate4` | 81.01 | +6.72 | [+2.85; +11.18] | 0.0025 | 0.0150 | 12 |
| `rrcv` | 80.00 | +5.72 | [+1.61; +10.41] | 0.101 | 0.406 | 12 |
| **`peakprob`** — best of the seven, **chosen after seeing the data** | **82.01** | **+7.73** | [+3.82; +12.41] | 5.6e-04 | **0.0039** | **9** |
| Oracle lead (labels) | 83.60 | +9.32 | — | — | — | 8 |

`peakprob` recovers **82.9 %** of the oracle head-room, wins 19 / ties 35 / loses 6 records, and no record loses more than
3.90 points. A label-shuffle check (`analysis/chonkenh_leakcheck.py`) changed 0 of 776 lead choices, so the
*selection* step is label-blind.

**Mandatory caveats.** (1) The written analysis plan (`analysis/chonkenh_khaibao_truoc.json`) designated
`gate` as the confirmatory rule, and `gate` **does not survive Holm correction** (p_Holm 0.0505 on the
60 clean records, 0.085 on 75). By the plan's own decision rule the confirmatory test **failed**. (2)
`peakprob` was picked **after** the CinC results were seen; the only statistical basis for reporting it is
that its effect survives Holm over the whole declared family of seven rules. (3) The plan file was written
before any rule was scored but **after** the per-lead F1 of CinC was on disk, and it was not committed to
git or time-stamped by a third party, so this study is **not pre-registered** and we do not use that word.
(4) The result has **not been replicated on an independent third dataset, and at present it cannot be**:
of the candidates on disk, NIFEADB distributes no fetal annotations, NInFEA has no beat labels (its
reference is Doppler), the `.qrs` file of nifecgdb marks *maternal* QRS (median RR 0.695 s = 86 bpm), and
CinC 2013 set-b labels are unpublished (`analysis/XACNHAN.md`, `xacnhan_results.json → viec2_bo_thu_ba`).
(5) **On the logit scale the post-hoc problem does not disappear** (`analysis/XACNHAN.md`, pre-declared in
`analysis/xacnhan_khaibao.md`, git `ed819e3`): over the 22 in-domain subjects the leading rule is `gate`
under two of three clamping schemes and `rrcv` under the third, `peakprob` ranks 3rd/4th/6th and its
interval contains zero; on the 60 clean CinC records the leading rule on the logit scale is `gate4`, not
`peakprob`. The statement the data support is "selecting the lead from the model's own output beats the PSD
rule out of domain"; which specific rule is best depends on the scale. We therefore state `peakprob` as
*a strong hypothesis, not a confirmed result*.

Median signed offset against scalp-electrode labels stays at 0.0 ms, so the indirect B1 labels did not
pull the model. The sample-efficiency curve (1 → 2 → 3 training subjects: 91.2 → 93.4 → 97.5) is not
saturated, which is why 22 subjects still help.

**Two-seed stability.** Retraining the 22-subject model with seed 1 changes per-subject F1 by
**0.28 points on average** over the 20 subjects common to both runs, largest single change **2.81**
(B2_03); at subject level the PSD-lead F1 is 97.56 (seed 0) vs 97.59 (seed 1), difference +0.03
[−0.18; +0.34] (`analysis/xacnhan_results.json → viec5_seed`; the fold split differs between seeds, so this
includes fold-assignment variance). The per-fold decision thresholds are less stable: 0.50–0.80 for seed 1
against 0.20–0.80 for seed 0 (seed 0 fold 10 used an extreme 0.20). The seed-1 checkpoints were **not
saved** (`train_22.py` only writes checkpoints for an empty `--tag`), so no out-of-domain seed-1 number
exists.

### Three-tier contribution decomposition

| Stage | Δ Macro F1 (per subject) | 95 % CI | Verdict |
|---|---:|---|---|
| Signal front-end (band-pass choice) | **+11.00** (300 ms GBM; **withdrawn for the TCN**: +2.44 [−0.05; +6.30]) | not recomputable¹ | largest effect on the 300 ms learner only |
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
| CinC 2013 set-a, 60 clean records | 60 | not run | 55.97 | **74.28** (PSD) / 82.01 (`peakprob`, post hoc) |

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

Gradio, **eight tabs**: five-tier signal view (raw → filtered → residual → probability → result),
label-blind lead selection across all four leads (`peakprob` or PSD), fetal heart-rate trace with a per-segment
**confidence light**, comparison against annotations, the clean-60 summary, **Our data** (a live table of every
record in the five collections read from the `.hea`/`.edf` headers, plus a raw-signal viewer with annotations
overlaid), **Upload new data** (`.edf`, `.dat`+`.hea`, `.csv`, `.npy`, `.txt`, with an optional annotation file
and Vietnamese error messages for six malformed-input cases), and a JSON log. Selecting an ADFECGDB record
automatically uses the fold checkpoint that never saw it. Requires **Gradio 6.x**. Operating guide:
[`docs/HUONG_DAN_DEMO.md`](docs/HUONG_DAN_DEMO.md).

The light has two modes: *learned* (gradient-boosted classifier on 12 classical SQIs per 4 s segment,
`fsqi/gate.py`, default) and *rule* (hand-set thresholds). Re-run on 12 Sep 2026 (17:07; repeated at 23:11 with an identical summary) over the 82 labelled
records that are neither training duplicates nor leaked CinC copies (5 ADFECGDB with their fold checkpoint,
60 clean CinC 2013, 17 Silesia; `python demo/run_check.py --threads 2` → `demo/results/demo_check_2modes.json`,
`summary_by_mode`):

| Mode | Green (n · mean F1 · min) | Yellow (n · mean F1) | Red (n · mean F1) | Green but F1 < 90 | Red but F1 ≥ 95 |
|---|---|---|---|---|---|
| learned (default) | 46 · 95.70 · 17.02 | 17 · 96.94 | 19 · 54.26 | 3 (a52, a54, a57) | 0 |
| rule | 58 · 97.79 · 78.79 | 19 · 63.82 | 5 · 39.34 | 5 (a06, a11, a16, B1_07, B2_03) | 0 |

The earlier table in this section (8 green / 5 yellow / 2 red, "no record with F1 < 96.5 was ever green") was
computed on 15 sample records, four of them leaked CinC copies, and is superseded. The learned gate is
calibrated on the 5-subject model; the 22-subject gate of `analysis/GATE22.md` has not been exported to the
demo. Tested at three levels: unit tests on the core, HTTP smoke test, and `gradio_client` API call.
Screenshots in [`demo/screenshots/`](demo/screenshots/).

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
HANDOFF.md                Start here: setup, data, repo map, integrity rules, traps, next steps (Vietnamese)
CHANGELOG.md              Round-by-round changes and every retraction
requirements.txt          Core: pipeline, demo, API, tests (tested versions noted inline)
requirements-research.txt Analyses, document rebuild, demo screenshots

model/                    Core library, training, inference, weights
├─ fqrs_model.py            Reference implementation — every constant traced to an experiment
├─ train_final.py           LORO training → 5 fold checkpoints + 1 production model
├─ predict.py               CLI inference: EDF / WFDB / CSV / NPY
├─ download_data.py         PhysioNet sources with SHA-256 data card
├─ download_silesia.py      Resumable figshare download (URL expires in 10 s, needs Range + retry)
├─ silesia_loader.py        Silesia .ecg reader (int16 big-endian, 500 Hz) → 1 kHz
└─ checkpoints/             20 trained models (5-, 12- and 22-subject folds + production), 0.48 MB each

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
├─ core.py                  Pipeline logic, no UI dependency, unit-tested (39 tests)
├─ app.py                   Eight-tab UI: signal, leads, FHR + light, annotations, clean-60 summary, our data, upload, log
├─ run_check.py             Scores the 82 labelled non-leaked records in both gate modes → results/demo_check_2modes.json
├─ screenshot.py            Playwright capture of the showcase screenshots → screenshots/ + screenshots.json
├─ make_vidu_tai_len.py     Regenerates the 30 s upload example from CinC a09 (demo/assets/ is gitignored)
└─ screenshots/             Real captures from the running app (16: five showcase records + the two new tabs)

pilot_evidence/           Every pilot experiment with logs
├─ arch_loro.py             8-candidate architecture sweep (LORO, 10–60 Hz) — the "indistinguishable" claim is withdrawn
├─ band_ablation.py         8 band-pass candidates
├─ seq_search.py            Receptive-field sweep
└─ seq_loro.py              3-seed LORO + paired Wilcoxon

analysis/                 Round-6/7 analyses: data audit, lead rules, architecture, error taxonomy, gate, stats
├─ DULIEU.md                The 15 ADFECGDB copies in set-a: evidence, controls, recomputed clean-60 numbers
├─ CHONKENH.md              Seven label-blind lead rules; declared plan vs post-hoc choice
├─ XACNHAN.md               Round 7: no third labelled dataset; logit-scale ranking; visibility-test FN rate; seeds
├─ KIENTRUC.md              Seven architecture families at fixed parameters (logit scale)
└─ dulieu_results.json      Source JSON for every clean-60 number
adapt/                    Unsupervised domain adaptation — four methods, all negative (`adapt_results.json`)
api/                      FastAPI wrapper (`main.py`), schema in api/README.md
de_cuong_latex/           Research proposal — LaTeX source, data-driven figures and tables
paper/cinc2026/           Four-page Computing in Cardiology draft (pdflatex + bibtex)
survey/                   30-paper survey + verified-facts ledgers; facts_phase4.json is current
├─ RO_RI_VANLIEU.md         Who documented the set-a ↔ ADFECGDB overlap (Silva 2013, Clifford 2014) and who is affected
└─ facts_phase4.json        Every current number with the JSON file it was read from
docs/                     Compiled deliverables (PDF + DOCX), publication strategy, Eureka notes, demo guide, talk scripts
├─ trinh_bay/               Slide deck (26 slides, N = speaker notes, O = overview) and project handbook, as local HTML
└─ nhat_ky/                 Minutes of the seven adversarial review rounds
archive/                  Files removed from the working tree during the round-7 clean-up, kept for the PI's decision
tests/                    Smoke tests pinning every quoted number
```

---

## Installation and quickstart

```bash
git clone https://github.com/bminhnemhoi/nckhsv_tdtu2026-2027.git
cd nckhsv_tdtu2026-2027
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt                       # add requirements-research.txt for analyses and documents

python model/download_data.py --root model/data --only adfecgdb    # ~15 MB from PhysioNet
python model/download_more.py --only cinc75                        # ~35 MB, CinC 2013 set-a -> benchmark_dpss/pcdb/
python model/download_silesia.py                                   # ~195 MB zip -- then UNZIP by hand, see HANDOFF.md §4
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
python model/train_22.py && python benchmark_dpss/eval_22.py                # 22-subject model, grouped 11-fold
python benchmark_dpss/eval_cinc75.py && python benchmark_dpss/eval_cinc60_sach.py   # CinC per record, then the clean-60 statistics
python analysis/dulieu_audit.py && python analysis/dulieu_m4b_verify.py     # the leak audit, two implementations
python analysis/chonkenh_cache.py && python analysis/chonkenh_rules.py      # seven lead rules
python baselines/powermf_setup.py && python baselines/powermf_fair_run.py   # Power-MF under Octave
python fsqi/eval_fsqi.py                                 # reject gate + negative result (~4 min)
python demo/run_check.py && python demo/smoke_app.py     # demo checks
python analysis/xacnhan.py                               # round-7 confirmation checks (no new inference)
python survey/make_facts_phase4.py                       # regenerate the single source of truth
pytest tests/ demo/test_core.py                          # 82 tests (records not downloaded are skipped, not failed)
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
  (CinC 2013, 60 clean records) the 22-subject model reaches **74.28 under the blind PSD rule**
  (82.01 under the post-hoc `peakprob` rule), against 97–99 in-domain; multi-centre data is the
  remaining gap. Four unsupervised domain-adaptation methods were tried and **all four failed** on the 60
  clean records (adaptive notch +0.25, p = 0.70; self-training −0.68; AdaBN −1.58; TENT −2.43;
  `analysis/THICHNGHI.md`): the measured distribution shifts do not explain the gap, which is consistent
  with the fetal signal simply being absent on every lead of the hardest records. The
  22-subject run is four epochs and the augmentation contribution has not been isolated; a second seed
  changes per-subject F1 by 0.28 points on average.
- **Sample size is the binding limitation.** ADFECGDB has five women and the whole training set 22, so no
  comparison on ADFECGDB can be statistically significant at subject level and every interval quoted
  here is wide. The architecture benchmark is underpowered by construction, not inconclusive by
  accident.
- **CinC 2013 set-a is evaluated on 60 clean records (53 under the declared exclusion), not 75.**
  Fifteen records are copies of the training data and are excluded; whether the remaining 60 records
  come from 60 distinct women has *not* been checked (NCC ≤ 0.62 rules out verbatim copies only).
  Scoring uses our own ±50 ms matcher rather than the original challenge scorer, so these are *not*
  official challenge entries.
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
- **The +11.00-point band-pass result is measured on a 300 ms-window GBM, not on the TCN, and is
  withdrawn as a claim about the TCN.** On the TCN over 22 women (`pilot_evidence/band_tcn.json`,
  three folds, one seed) 10–60 Hz vs 1–45 Hz is worth +2.44 [−0.05; +6.30] on the PSD lead and
  −0.07 [−0.49; +0.40] averaged over four leads: the band does not matter to the detector.
- **The 22-subject in-domain branch is at the F1 ceiling** (14/22 subjects at the oracle lead, 1.08
  points of head-room), so rule and architecture comparisons there must be read on the logit scale;
  on that scale `cnn_wide` is significantly worse than the TCN (`analysis/KIENTRUC.md`).
- **The claim "the model is not the bottleneck" (`analysis/CHANDOAN_MOHINH.md`) is withdrawn**, and so is
  the figure "71 % of the head-room lies on records with no measurable fetal signal". The capacity ceiling
  was measured in-sample on 4 records with one seed, the jitter only on correctly detected beats, and the
  visibility test that defines the "no fetal signal" error class has a **false-negative rate of 18.0 %
  [12.1; 25.0] on the 60 clean CinC records** (above the 10 % threshold declared in advance), rising to
  55–70 % on the records with F1 < 90 — exactly where it is needed. After correcting for that rate the
  "no signal" share of the head-room falls from 86.0 % to 26.0 % at the 0.5 threshold, but the correction
  divides by a sensitivity close to its floor and is not identifiable; the honest statement is that the
  split between "no signal" and "model miss" **cannot be determined with this test**
  (`analysis/XACNHAN.md → viec4`). The correct wording is now "we have neither shown nor excluded that the
  model is the bottleneck".
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
| CinC 2013 = 74.28 (PSD) on 60 clean records | **Reproducible in-repo** | `benchmark_dpss/eval_cinc60_sach.json` (from `eval_cinc75.json` per-record F1) |
| Set-a contains ADFECGDB recordings | **Documented by the organisers, not by us** | Silva et al. 2013 Table 1; Clifford et al. 2014 Table 2 and the Rodrigues caveat; echoed by Su & Wu 2017 and Matonia et al. 2020 (`survey/RO_RI_VANLIEU.md`) |
| *Which* 15/75 set-a records are verbatim copies, and by how much they inflate our numbers | **Measured by us, checked twice** | NCC = 1.0000 on 4/4 channels, RR offset 0.0 ms; two independent implementations (`analysis/dulieu_audit.py`, `analysis/dulieu_m4b_verify.py`); inflation 3.27–7.18 points (`benchmark_dpss/eval_cinc60_sach.json`) |
| `peakprob` lead rule +7.73 over PSD | **Hypothesis — post hoc, not replicated** | survives Holm over 7 declared rules (p 0.0039); the designated rule `gate` fails Holm (0.0505); plan file not git-anchored (`analysis/CHONKENH.md`); on the logit scale `gate` leads the 22 subjects and `gate4` leads the 60 clean records (`analysis/XACNHAN.md`) |
| "The model is not the bottleneck" | **NOT determinable** | visibility test has 18.0 % false negatives on the 60 clean records; corrected share 26 % vs raw 86 % — not identifiable (`analysis/XACNHAN.md`) |
| Unsupervised domain adaptation helps on CinC | **NO — four methods, all negative** | `analysis/THICHNGHI.md`, `adapt/adapt_results.json` |
| Architecture family matters at fixed parameters | **NO (in domain, reduced protocol)** | 7 families within ±2.7 % parameters; `rf_wide`, `tcn_ms` equivalent to TCN by TOST; report on logit scale (`analysis/KIENTRUC.md`) |
| Our Power-MF port is correct | **EXTERNALLY verified** | we measure 99.40 on B1; the authors publish 99.46 (`baselines/powermf_published.json`) — 0.06 apart |
| Power-MF 4-lead / 1-lead / RelyFetal table | **Reproducible in-repo** | `baselines/powermf_fair_stats.json`, `powermf_1ch.json` |
| More data helps for real, rather than learning an annotation style | **Independent evidence** | m12 (never saw B1) 67.93 vs m22 74.28 on the 60 clean CinC records, whose labels were produced by different annotators (`analysis/ABLATION_B1.md`, `analysis/dulieu_results.json`) |
| +11.00 points for the band-pass choice | **WITHDRAWN for the TCN** | measured on a 300 ms-window GBM; on the TCN +2.44 [−0.05; +6.30], zero inside (`pilot_evidence/band_tcn.json`) |
| Timing accuracy (jitter, STV) on Silesia B1 | **NOT usable** | B1 labels are indirect and carry a model-dependent offset (m5 6.50 / m12 6.50 / m22 3.25 ms) |
| Use as a standalone STV meter | **NO** | STV bias +0.33 ms on ADFECGDB but +20.50 ms on CinC (`analysis/CLINICAL.md`) |
| "Eight architectures are indistinguishable" | **WITHDRAWN** | TOST at a 1.0-point margin rejects it: cnn_m is worse, cnn_l is better (`analysis/STATS.md`) |
| Topological feature contribution (C3) | **WITHDRAWN — negative result** | AUROC 0.566 vs 0.929 for classical SQIs (`fsqi/README.md`) |
| Challenge-comparable CinC 2013 score | **NO** | scored with our own ±50 ms matcher, not the official scorer |
| Seed stability | **Only 2 seeds, in domain** | subject-level PSD F1 97.56 vs 97.59, +0.03 [−0.18; +0.34]; per-subject mean absolute change 0.28; seed-1 checkpoints not saved, so nothing out of domain (`analysis/xacnhan_results.json`) |
| Replication of `peakprob` on a third dataset | **NOT possible with the data at hand** | no public set with real fQRS labels: NIFEADB none, NInFEA none (Doppler reference), nifecgdb `.qrs` is maternal, set-b unpublished (`analysis/XACNHAN.md`) |
| Low-SNR training subjects | **NOT available** | the hardest CinC records have no measurable fetal signal on any lead; the training set contains almost none of that regime |
| A second centre with real fQRS labels | **NOT available** | NInFEA does not distribute labels |

Every number in this README traces back to a JSON file on disk. Retractions are recorded in place, where
the old number used to stand, rather than being quietly deleted.

---

## Retractions — complete list

Recorded here so no earlier number can be quoted as current. Each line gives the withdrawn figure, where it
stood, and the replacement.

| Withdrawn | Was | Why | Replacement |
|---|---|---|---|
| 59.15 / 69.31 / 77.34 / 90.34 / 22.33 | CinC 2013, 10-record subsample | biased subsample, post-hoc fixed lead; 4 of those 10 records are training data | 60 clean records (below) |
| 71.21 / 79.40 / 86.87 / 74.09 / 69.33 / +8.18 / +7.47 / 80.70 | CinC 2013, all 75 records | 15 records are verbatim copies of ADFECGDB training data; 15 records from 5 women violate record-level independence | m5 64.04 / m22 **74.28** / oracle 83.60 / mean-4 67.69 / +10.24 / +9.32 / 53-record 75.27 — `benchmark_dpss/eval_cinc60_sach.json` |
| 85.60 / +6.20 / +5.14 (`peakprob`, `gate` on 75 records) | `analysis/CHONKENH.md` | same contamination | 82.01 / +7.73 / +6.44 on 60 clean records — `analysis/dulieu_results.json` |
| 62.82 (Power-MF one lead on CinC) | Power-MF table | same contamination | 55.97 on 60 clean records |
| 94.87 / +2.74 / 98.38 / 97.33 | Power-MF comparison, morning of 12 Sep 2026 | broken Octave port (`findpeaks` O(k²)) | 98.83 / −1.27 [−3.08; +0.27] on 22 subjects — `baselines/powermf_fair_stats.json` |
| "+11.00 F1 from the band-pass filter" as a claim about the model | headline of earlier READMEs | measured on a 300 ms GBM; on the TCN +2.44, interval contains zero | reported only as a 300 ms-learner result |
| "eight architectures are indistinguishable" | earlier READMEs | equivalence inferred from p > 0.05 | TOST at 1.0 point; on logit scale `cnn_wide` is worse (`analysis/KIENTRUC.md`) |
| "the problem is bimodal" as a mechanism | earlier READMEs | the two modes are a lead-selection artefact, not two populations (`analysis/LUONGCUC.md`) | — |
| "pre-registered" for the lead-rule study | `analysis/CHONKENH.md` | plan file not git-anchored, written after per-lead F1 existed | "analysis plan written before any rule was scored" |
| "the model is not the bottleneck"; "71 % of the head-room lies on records without measurable fetal signal"; "only 1.85 points belong to the model" | `analysis/CHANDOAN_MOHINH.md`, `analysis/THICHNGHI.md` | in-sample n = 4 capacity test, jitter on easy beats; visibility test has 18.0 % false negatives on the 60 clean records (threshold 10 %) and 55–70 % on hard records | "neither shown nor excluded"; the no-signal share is not determinable (26–86 % are two bounds of an unmeasured quantity) — `analysis/XACNHAN.md` |
| "we found / discovered that CinC set-a contains ADFECGDB" — the overlap presented as our finding | earlier READMEs, `analysis/DULIEU.md` §12, `docs/*` | the organisers documented it in 2013 and 2014 and the caveat was in our own reading notes (p20) | "as the organisers noted [Silva 2013; Clifford 2014] … we identified by measurement which 15 records and the inflation" — `survey/RO_RI_VANLIEU.md` |
| "replicate `peakprob` on CinC set-b / NInFEA / NIFEADB" as a plan | earlier READMEs, `docs/CHIEN_LUOC_CONG_BO.md` | none of them has real fQRS labels | no third dataset available; the rule stays a hypothesis |
| "the two-seed run shows stability" beyond the in-domain mean | earlier READMEs | seed-1 checkpoints were never saved | in-domain only: +0.03 [−0.18; +0.34] |
| *Physiological Measurement* is a Q1 journal | proposal v3.4 title page, `docs/` | Scimago 2024 ranks it Q2 (Physiology) / Q3 (Biomedical Eng.) | Q1 (Scimago): JBHI, TBME, BSPC, CBM, AI in Medicine — `docs/CHIEN_LUOC_CONG_BO.md` |
| "AUROC 0.980 / 66.7 % coverage / 15 of 16 failures rejected" as the headline gate result | `analysis/GATE22.md`, `docs/*` | computed on all 75 CinC records, 15 of them ADFECGDB copies; not recomputed on the 60 clean records | in-record AUROC 0.934 [0.872; 0.981] on 22 subjects (LOSO), 3 hardest records ranked 1-2-3 — `analysis/gate22_results.json`; the 75-record figure may only be quoted with that caveat |
| CinC 2026 as the submission target | `paper/cinc2026/`, earlier `docs/` | CinC 2026 (Madrid, 20–23 Sep 2026) is past; the directory name is kept for history | CinC 2027 (abstract expected Apr 2027) — `docs/CHIEN_LUOC_CONG_BO.md` |
| "8 hard-limit records" as a finding | `analysis/CHANDOAN_MOHINH.md` | group defined by the label it predicts (circular); a54 is a label error (37 labels / 144 detections) | descriptive only |
| p < 0.001 for the band-pass tier; all ADFECGDB p-values | earlier READMEs | pseudo-replication over record × lead × seed | intervals only (`analysis/STATS.md`) |
| topological SQI contribution | proposal v1 | AUROC 0.566 vs 0.929 classical | negative result (`fsqi/README.md`) |

The single source of truth for current numbers is [`survey/facts_phase4.json`](survey/facts_phase4.json);
every entry there names the JSON file it was read from.

---

## Citation

```bibtex
@misc{ngo2026relyfetal,
  author = {Ngo, Binh Minh},
  title  = {RelyFetal: Reliability-aware single-channel fetal QRS detection},
  year   = {2026},
  school = {Ton Duc Thang University},
  note   = {Undergraduate research project, v3.5},
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
