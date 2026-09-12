# -*- coding: utf-8 -*-
"""
stats.py -- Tinh lai TOAN BO ket qua thong ke chinh o DON VI CHU THE (subject level).

Van de duoc sua (nhiem vu S3):
  * Cac kiem dinh cu chay tren cap (ban ghi x kenh) -- 20 / 28 / 40 / 60 / 88 cap tu 5..22 chu the.
    Bon kenh bung cua CUNG MOT phu nu KHONG doc lap (cung tim thai, cung dat dien cuc, cung nhieu me)
    => gia lap (pseudo-replication) => p bi phong dai nhieu bac.
  * KTC 95% kieu t cho F1 gan 100 vuot qua 100% (vi du 99,21 +- 1,50, n=5 => [97,35; 101,08]).

Cach sua:
  (a) Don vi phan tich = CHU THE. Voi moi chu the, lay trung binh F1 cua 4 kenh truoc (F1_mean4),
      hoac dung kenh PSD mu nhan (1 gia tri / chu the). Sau do so sanh ghep cap tren n = so chu the.
  (b) Moi so sanh: Wilcoxon signed-rank muc chu the (exact), sign test (nhi thuc),
      cluster bootstrap (lay mau lai CHU THE, 10000 lan) cho KTC 95% cua hieu so,
      Cliff's delta + rank-biserial ghep cap (effect size).
  (c) KTC cho F1: thang logit (co chan biên theo so nhip tham chieu) + bootstrap percentile.
      KHONG dung t tren thang phan tram.
  (d) TOST tuong duong cho ho kien truc, bien delta = 1,0 diem F1, bao cao KTC 90%.
  (e) Hieu chinh Holm cho ho kiem dinh kien truc.

Chay:  python D:/NCKHSV2026-2027/analysis/stats.py
Xuat:  analysis/stats_results.json, analysis/STATS.md
"""

import csv
import json
import math
import os
from datetime import datetime

import numpy as np
from scipy import stats

try:  # torch chi de tuan thu yeu cau ngan sach CPU; khong dung de tinh
    import torch

    torch.set_num_threads(2)
except Exception:  # pragma: no cover
    torch = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "analysis")
B_BOOT = 10000
SEED = 0
DELTA_TOST = 1.0  # bien tuong duong, diem F1

# ----------------------------------------------------------------------------
# Ham thong ke
# ----------------------------------------------------------------------------


def wilcoxon_paired(a, b, alt="two-sided"):
    """Wilcoxon signed-rank ghep cap, loai cap bang nhau, dung exact khi n nho."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    nz = d[np.abs(d) > 1e-12]
    out = {
        "n_pairs": int(len(d)),
        "n_nonzero": int(len(nz)),
        "n_pos": int(np.sum(nz > 0)),
        "n_neg": int(np.sum(nz < 0)),
        "n_tie": int(len(d) - len(nz)),
        "mean_diff": float(np.mean(d)),
        "median_diff": float(np.median(d)),
    }
    if len(nz) < 1:
        out.update({"stat": None, "p": 1.0, "method": "tat ca cap bang nhau"})
        return out
    method = "exact" if len(nz) <= 25 else "approx"
    try:
        res = stats.wilcoxon(nz, alternative=alt, method=method)
    except Exception:
        res = stats.wilcoxon(nz, alternative=alt)
        method = "auto"
    out.update({"stat": float(res.statistic), "p": float(res.pvalue), "method": method})
    # p nho nhat co the dat duoc voi n cap khac 0 (exact, hai phia)
    out["p_min_possible_two_sided"] = float(min(1.0, 2.0 / (2 ** len(nz))))
    return out


def sign_test(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    npos = int(np.sum(d > 1e-12))
    nneg = int(np.sum(d < -1e-12))
    n = npos + nneg
    if n == 0:
        return {"n_eff": 0, "n_pos": 0, "n_neg": 0, "p": 1.0}
    p = float(stats.binomtest(npos, n, 0.5, alternative="two-sided").pvalue)
    return {"n_eff": n, "n_pos": npos, "n_neg": nneg, "p": p}


def cluster_bootstrap_paired(a, b, n_boot=B_BOOT, seed=SEED, alpha=0.05):
    """Lay mau lai CHU THE (cluster = chu the) -> KTC percentile cho trung binh hieu so."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = a - b
    n = len(d)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = d[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    lo90, hi90 = np.percentile(boots, [5.0, 95.0])
    # KTC t tren hieu so -- bao thu hon bootstrap khi so cum nho
    m = float(np.mean(d))
    if n > 1:
        se = float(np.std(d, ddof=1)) / math.sqrt(n)
        h = stats.t.ppf(1 - alpha / 2, n - 1) * se
        ci_t = [m - h, m + h]
    else:
        ci_t = [m, m]
    return {
        "mean_diff": m,
        "ci95": [float(lo), float(hi)],
        "ci90": [float(lo90), float(hi90)],
        "ci95_t_paired": [float(ci_t[0]), float(ci_t[1])],
        "frac_boot_le_0": float(np.mean(boots <= 0)),
        "loai_tru_0_bootstrap": bool(lo > 0 or hi < 0),
        "loai_tru_0_t": bool(ci_t[0] > 0 or ci_t[1] < 0),
        "n_boot": int(n_boot),
        "canh_bao": (
            "n < 8 cum: KTC percentile bootstrap co xu huong HEP hon thuc te; uu tien KTC t."
            if n < 8
            else ""
        ),
    }


def cliffs_delta(x, y):
    """Cliff's delta (do troi) giua hai mau; duong = x troi hon y."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    gt = 0
    lt = 0
    for xi in x:
        gt += int(np.sum(xi > y))
        lt += int(np.sum(xi < y))
    d = (gt - lt) / (len(x) * len(y))
    ad = abs(d)
    if ad < 0.147:
        mag = "khong dang ke"
    elif ad < 0.330:
        mag = "nho"
    elif ad < 0.474:
        mag = "trung binh"
    else:
        mag = "lon"
    return {"delta": float(d), "magnitude": mag}


def rank_biserial_paired(a, b):
    """r ghep cap tu Wilcoxon: (R+ - R-) / tong hang."""
    d = np.asarray(a, float) - np.asarray(b, float)
    nz = d[np.abs(d) > 1e-12]
    if len(nz) == 0:
        return 0.0
    r = stats.rankdata(np.abs(nz))
    rp = float(np.sum(r[nz > 0]))
    rm = float(np.sum(r[nz < 0]))
    return float((rp - rm) / (rp + rm))


def t_ci_pct(values, alpha=0.05):
    """KTC t ngay tren thang phan tram -- CHI de minh hoa loi (co the vuot 100)."""
    v = np.asarray(values, float)
    n = len(v)
    m = float(np.mean(v))
    sd = float(np.std(v, ddof=1)) if n > 1 else 0.0
    if n < 2:
        return {"mean": m, "sd": sd, "ci95": [m, m], "vuot_100": False}
    h = stats.t.ppf(0.975, n - 1) * sd / math.sqrt(n)
    return {
        "mean": m,
        "sd": sd,
        "ci95": [m - h, m + h],
        "vuot_100": bool(m + h > 100.0),
    }


def logit_ci_pct(values, n_ref=None, alpha=0.05):
    """KTC tren thang logit roi doi nguoc. n_ref: so nhip tham chieu moi chu the (de chan bien)."""
    v = np.asarray(values, float) / 100.0
    n = len(v)
    if n_ref is None:
        n_ref = np.full(n, 500.0)
    n_ref = np.asarray(n_ref, float)
    eps = 0.5 / np.maximum(n_ref, 2.0)
    p = np.clip(v, eps, 1.0 - eps)
    z = np.log(p / (1.0 - p))
    m = float(np.mean(z))
    if n < 2:
        back = 100.0 / (1.0 + math.exp(-m))
        return {"mean_backtransformed": back, "ci95": [back, back], "n": n}
    sd = float(np.std(z, ddof=1))
    h = stats.t.ppf(1 - alpha / 2, n - 1) * sd / math.sqrt(n)
    lo, hi = m - h, m + h
    f = lambda t: 100.0 / (1.0 + math.exp(-t))
    return {
        "mean_backtransformed": f(m),
        "ci95": [f(lo), f(hi)],
        "n": int(n),
        "note": (
            "Uoc luong diem la TRUNG BINH TREN THANG LOGIT doi nguoc -- day KHONG phai trung binh "
            "so hoc cua F1; no keo ve phia cac gia tri cao va luon nam trong (0;100). "
            "KTC nay danh cho 'F1 dien hinh cua mot chu the moi'. Muon KTC cho TRUNG BINH SO HOC "
            "thi dung bootstrap percentile."
        ),
    }


def boot_ci_mean(values, n_boot=B_BOOT, seed=SEED, alpha=0.05):
    v = np.asarray(values, float)
    n = len(v)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    boots = v[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"mean": float(np.mean(v)), "ci95_percentile": [float(lo), float(hi)], "n": int(n)}


def tost_paired(a, b, delta=DELTA_TOST, alpha=0.05, seed=SEED):
    """TOST ghep cap (t) + KTC 90% (t va bootstrap). Ket luan tuong duong neu KTC 90% nam trong +-delta."""
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d)
    m = float(np.mean(d))
    sd = float(np.std(d, ddof=1)) if n > 1 else 0.0
    se = sd / math.sqrt(n) if n > 1 else 0.0
    out = {"mean_diff": m, "sd_diff": sd, "n": int(n), "delta": delta}
    if n < 2 or se == 0:
        out.update({"p_tost": None, "ci90_t": [m, m], "ket_luan": "khong du du lieu"})
        return out
    df = n - 1
    t1 = (m + delta) / se          # H01: diff <= -delta
    t2 = (m - delta) / se          # H02: diff >= +delta
    p1 = float(1 - stats.t.cdf(t1, df))
    p2 = float(stats.t.cdf(t2, df))
    p_tost = max(p1, p2)
    h90 = stats.t.ppf(0.95, df) * se
    ci90 = [m - h90, m + h90]
    bb = cluster_bootstrap_paired(a, b, seed=seed)
    ci90_boot = bb["ci90"]
    equiv_t = bool(ci90[0] > -delta and ci90[1] < delta)
    equiv_boot = bool(ci90_boot[0] > -delta and ci90_boot[1] < delta)
    if equiv_t and equiv_boot:
        kl = "TUONG DUONG trong bien 1,0 diem"
    elif (ci90[0] > delta) or (ci90[1] < -delta):
        kl = "KHAC BIET vuot bien 1,0 diem"
    else:
        kl = "KHONG KET LUAN DUOC (KTC 90% rong hon bien tuong duong)"
    out.update(
        {
            "p_tost": float(p_tost),
            "p_lower": p1,
            "p_upper": p2,
            "ci90_t": [float(ci90[0]), float(ci90[1])],
            "ci90_bootstrap": [float(ci90_boot[0]), float(ci90_boot[1])],
            "ket_luan": kl,
        }
    )
    return out


def holm(pvals, alpha=0.05):
    """Hieu chinh Holm-Bonferroni. Tra ve p da hieu chinh + bac bo hay khong."""
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.zeros(m)
    running = 0.0
    for i, idx in enumerate(order):
        val = (m - i) * pvals[idx]
        running = max(running, val)
        adj[idx] = min(1.0, running)
    return [float(x) for x in adj], [bool(x < alpha) for x in adj]


def compare_subject_level(a, b, label, name_a, name_b, seed=SEED, note=""):
    """Bo kiem dinh day du cho mot so sanh ghep cap o muc chu the."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    w = wilcoxon_paired(a, b)
    s = sign_test(a, b)
    cb = cluster_bootstrap_paired(a, b, seed=seed)
    cd = cliffs_delta(a, b)
    rb = rank_biserial_paired(a, b)
    return {
        "label": label,
        "A": name_a,
        "B": name_b,
        "n_subjects": int(len(a)),
        "mean_A": float(np.mean(a)),
        "mean_B": float(np.mean(b)),
        "wilcoxon_subject": w,
        "sign_test": s,
        "cluster_bootstrap": cb,
        "cliffs_delta": cd,
        "rank_biserial_paired": rb,
        "significant_005": bool(w["p"] < 0.05),
        "note": note,
    }


def auroc(scores, labels):
    """AUROC qua thong ke hang (Mann-Whitney), xu ly hang bang."""
    scores = np.asarray(scores, float)
    labels = np.asarray(labels, int)
    pos = labels == 1
    n1 = int(pos.sum())
    n0 = int((~pos).sum())
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = stats.rankdata(scores)
    return float((r[pos].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


# ----------------------------------------------------------------------------
# Doc du lieu
# ----------------------------------------------------------------------------

def J(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    t0 = datetime.now()
    R = {
        "meta": {
            "date": t0.isoformat(timespec="seconds"),
            "muc_dich": "Tinh lai ket qua chinh o DON VI CHU THE; sua gia lap (pseudo-replication)",
            "n_boot": B_BOOT,
            "seed": SEED,
            "delta_tost_F1": DELTA_TOST,
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
        "comparisons": {},
        "confidence_intervals": {},
        "equivalence": {},
        "reversals": [],
        "not_recomputable": [],
    }

    base = J("baselines/results.json")
    blind = J("benchmark_dpss/blind_lead.json")
    allleads = J("benchmark_dpss/all_leads.json")
    sil = J("benchmark_dpss/silesia_eval.json")
    ev22 = J("benchmark_dpss/eval_22.json")
    arch = J("pilot_evidence/arch_loro_merged.json")
    seq = J("pilot_evidence/seq_loro.json")
    fsqi = J("fsqi/results.json")

    RECS5 = ["r01", "r04", "r07", "r08", "r10"]

    # =====================================================================
    # 1. ADFECGDB: mo hinh vs 3 baseline co dien, muc chu the (n = 5)
    # =====================================================================
    # n_ref (so nhip thai tham chieu) tu baseline TS -- dung de chan bien logit
    n_ref_rec = {}
    for rec in RECS5:
        vals = [base["baselines"]["TS"]["per_eval"][rec][str(l)]["n_ref"] for l in [1, 2, 3, 4]]
        n_ref_rec[rec] = float(np.mean(vals))

    model_mean4 = np.array([float(np.mean(allleads[r])) for r in RECS5])
    model_psd = np.array([blind["adfecgdb"][r]["F1_psd"] for r in RECS5])

    bl_mean4 = {}
    bl_psd = {}
    for bname in ["TS", "TS-PCA", "Prominence"]:
        pe = base["baselines"][bname]["per_eval"]
        bl_mean4[bname] = np.array(
            [float(np.mean([pe[r][str(l)]["F1"] for l in [1, 2, 3, 4]])) for r in RECS5]
        )
        pb = base["baselines"][bname].get("psd_blind", {})
        vals = []
        for r in RECS5:
            lead = blind["adfecgdb"][r]["psd_lead"]  # kenh PSD mu nhan cua mo hinh
            vals.append(pe[r][str(lead)]["F1"])
        bl_psd[bname] = np.array(vals)

    old_p_map = {
        "TS": base["baselines"]["TS"]["wilcoxon_vs_model_20"]["p_two_sided"],
        "TS-PCA": base["baselines"]["TS-PCA"]["wilcoxon_vs_model_20"]["p_two_sided"],
        "Prominence": base["baselines"]["Prominence"]["wilcoxon_vs_model_20"]["p_two_sided"],
    }

    for bname in ["TS", "TS-PCA", "Prominence"]:
        key = f"adfecgdb_model_vs_{bname}_mean4"
        c = compare_subject_level(
            model_mean4,
            bl_mean4[bname],
            label=f"ADFECGDB: FetalQRS-TCN vs {bname} (TB 4 kenh)",
            name_a="FetalQRS-TCN",
            name_b=bname,
            note="Don vi cu: 20 cap (ban ghi x kenh) tu 5 phu nu -> gia lap 4x",
        )
        c["old_unit"] = "20 cap (ban ghi x kenh)"
        c["old_p"] = float(old_p_map[bname])
        c["old_n"] = 20
        R["comparisons"][key] = c

        key2 = f"adfecgdb_model_vs_{bname}_psdlead"
        c2 = compare_subject_level(
            model_psd,
            bl_psd[bname],
            label=f"ADFECGDB: FetalQRS-TCN vs {bname} (kenh PSD mu nhan)",
            name_a="FetalQRS-TCN",
            name_b=bname,
            note="1 kenh / chu the -> khong gia lap, nhung n = 5",
        )
        c2["old_unit"] = "5 cap (kenh PSD)"
        c2["old_p"] = float(
            base["baselines"][bname]["wilcoxon_psd_vs_model_5"]["p_two_sided"]
        )
        c2["old_n"] = 5
        R["comparisons"][key2] = c2

    # =====================================================================
    # 2. KTC cho cac con so F1 chinh
    # =====================================================================
    def ci_block(values, n_ref=None, name="", old_claim=None):
        return {
            "ten": name,
            "n_subjects": int(len(values)),
            "mean": float(np.mean(values)),
            "sd": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
            "t_ci_pct_SAI": t_ci_pct(values),
            "logit_ci": logit_ci_pct(values, n_ref=n_ref),
            "bootstrap_ci": boot_ci_mean(values),
            "gia_tri_bao_cao_cu": old_claim,
        }

    nref5 = [n_ref_rec[r] for r in RECS5]
    R["confidence_intervals"]["adfecgdb_psd_5"] = ci_block(
        model_psd, nref5, "ADFECGDB kenh PSD, mo hinh 5 chu the", 99.21
    )
    R["confidence_intervals"]["adfecgdb_mean4_5"] = ci_block(
        model_mean4, nref5, "ADFECGDB TB 4 kenh, mo hinh 5 chu the", 97.45
    )

    # Silesia B1 (model_5, zero-shot) va B1 (model_22)
    b1_recs = [k for k in sil["records"] if sil["records"][k]["group"] == "B1"]
    b1_recs.sort()
    b1_m5_psd = np.array([sil["records"][k]["F1_psd"] for k in b1_recs])
    b1_m5_mean4 = np.array([sil["records"][k]["F1_mean4"] for k in b1_recs])
    b1_nref = [sil["records"][k]["n_ref"] for k in b1_recs]
    R["confidence_intervals"]["silesia_B1_model5_psd"] = ci_block(
        b1_m5_psd, b1_nref, "Silesia B1 thai ky, mo hinh 5 chu the (kenh PSD)", 93.30
    )

    subj = ev22["subjects"]
    b1_subj = [k for k in subj if subj[k]["group"] == "B1"]
    b1_subj.sort()
    b1_m22_psd = np.array([subj[k]["model_22"]["F1_psd"] for k in b1_subj])
    b1_m22_mean4 = np.array([subj[k]["model_22"]["F1_mean4"] for k in b1_subj])
    b1_m5b_psd = np.array([subj[k]["model_5"]["F1_psd"] for k in b1_subj])
    b1_m5b_mean4 = np.array([subj[k]["model_5"]["F1_mean4"] for k in b1_subj])
    b1_nref22 = [subj[k]["n_ref"] for k in b1_subj]
    R["confidence_intervals"]["silesia_B1_model22_psd"] = ci_block(
        b1_m22_psd, b1_nref22, "Silesia B1 thai ky, mo hinh 22 chu the (kenh PSD)", 97.15
    )

    # CinC 2013
    cinc_recs = sorted(ev22["cinc2013"]["records"].keys())
    cinc_m22_l0 = np.array(
        [ev22["cinc2013"]["records"][r]["F1_lead0"] for r in cinc_recs]
    )
    cinc_m5_l0 = np.array(
        [ev22["cinc2013"]["records"][r]["model_5"]["F1_lead0"] for r in cinc_recs]
    )
    cinc_m22_mean4 = np.array(
        [ev22["cinc2013"]["records"][r]["F1_mean4"] for r in cinc_recs]
    )
    cinc_m5_mean4 = np.array(
        [ev22["cinc2013"]["records"][r]["model_5"]["F1_mean4"] for r in cinc_recs]
    )
    cinc_nref = [ev22["cinc2013"]["records"][r]["n_ref"] for r in cinc_recs]
    R["confidence_intervals"]["cinc_model22_lead0"] = ci_block(
        cinc_m22_l0, cinc_nref, "CinC 2013 zero-shot, mo hinh 22 (kenh 0)", 90.34
    )
    R["confidence_intervals"]["cinc_model5_lead0"] = ci_block(
        cinc_m5_l0, cinc_nref, "CinC 2013 zero-shot, mo hinh 5 (kenh 0)", 77.34
    )

    # =====================================================================
    # 3. model_22 vs model_5, muc chu the
    # =====================================================================
    groups = {
        "PhysioNet": [k for k in subj if subj[k]["group"] == "PhysioNet"],
        "B2": [k for k in subj if subj[k]["group"] == "B2"],
        "B1": b1_subj,
        "ALL": sorted(subj.keys()),
    }
    if not groups["PhysioNet"]:
        # nhom PhysioNet co the mang nhan khac
        groups["PhysioNet"] = sorted([k for k in subj if k.startswith("r")])
        groups["B2"] = sorted([k for k in subj if k.startswith("B2")])
    for g in groups:
        groups[g] = sorted(groups[g])

    old_wil = ev22["comparison"]
    for g, keys in groups.items():
        if not keys:
            continue
        a22 = np.array([subj[k]["model_22"]["F1_mean4"] for k in keys])
        a5 = np.array([subj[k]["model_5"]["F1_mean4"] for k in keys])
        c = compare_subject_level(
            a22,
            a5,
            label=f"{g}: mo hinh 22 chu the vs mo hinh 5 chu the (TB 4 kenh)",
            name_a="model_22",
            name_b="model_5",
            note="Don vi cu: (chu the x kenh)",
        )
        ow = old_wil.get(g, {}).get("wilcoxon_subject_x_lead")
        if ow:
            c["old_unit"] = f"{ow['n']} cap (chu the x kenh)"
            c["old_p"] = float(ow["p"])
            c["old_n"] = int(ow["n"])
        R["comparisons"][f"m22_vs_m5_{g}_mean4"] = c

        p22 = np.array([subj[k]["model_22"]["F1_psd"] for k in keys])
        p5 = np.array([subj[k]["model_5"]["F1_psd"] for k in keys])
        c2 = compare_subject_level(
            p22,
            p5,
            label=f"{g}: mo hinh 22 vs mo hinh 5 (kenh PSD mu nhan)",
            name_a="model_22",
            name_b="model_5",
            note="1 kenh / chu the",
        )
        ow2 = old_wil.get(g, {}).get("wilcoxon_psd")
        if ow2:
            c2["old_unit"] = f"{ow2['n']} chu the (kenh PSD)"
            c2["old_p"] = float(ow2["p"])
            c2["old_n"] = int(ow2["n"])
        R["comparisons"][f"m22_vs_m5_{g}_psd"] = c2

    # CinC zero-shot
    c = compare_subject_level(
        cinc_m22_l0,
        cinc_m5_l0,
        label="CinC 2013 zero-shot: mo hinh 22 vs mo hinh 5 (kenh 0 co dinh)",
        name_a="model_22",
        name_b="model_5",
        note="10 ban ghi = 10 chu the",
    )
    c["old_unit"] = "40 cap (ban ghi x kenh)"
    c["old_p"] = float(ev22["cinc2013"]["wilcoxon_record_x_lead"]["p"])
    c["old_n"] = 40
    R["comparisons"]["cinc_m22_vs_m5_lead0"] = c

    c = compare_subject_level(
        cinc_m22_mean4,
        cinc_m5_mean4,
        label="CinC 2013 zero-shot: mo hinh 22 vs mo hinh 5 (TB 4 kenh)",
        name_a="model_22",
        name_b="model_5",
        note="10 ban ghi = 10 chu the",
    )
    c["old_unit"] = "40 cap (ban ghi x kenh)"
    c["old_p"] = float(ev22["cinc2013"]["wilcoxon_record_x_lead"]["p"])
    c["old_n"] = 40
    R["comparisons"]["cinc_m22_vs_m5_mean4"] = c

    # =====================================================================
    # 4. Ho kien truc: 7 kien truc vs cnn_dil, muc ban ghi (n = 5) + Holm + TOST
    # =====================================================================
    arch_res = arch["results"]
    arch_names = list(arch_res.keys())
    per_rec = {}
    for a in arch_names:
        pr = arch_res[a]["summary"]["per_record_F1"]
        per_rec[a] = np.array([pr[r] for r in RECS5])

    ref = "cnn_dil"
    arch_cmp = {}
    pvals = []
    keys_order = []
    for a in arch_names:
        if a == ref:
            continue
        c = compare_subject_level(
            per_rec[a],
            per_rec[ref],
            label=f"Kien truc {a} vs {ref} (TB 4 kenh moi ban ghi)",
            name_a=a,
            name_b=ref,
            note="Don vi cu: 20 cap (ban ghi x kenh)",
        )
        c["old_unit"] = "20 cap (ban ghi x kenh)"
        c["old_n"] = 20
        c["tost"] = tost_paired(per_rec[a], per_rec[ref], delta=DELTA_TOST)
        arch_cmp[a] = c
        pvals.append(c["wilcoxon_subject"]["p"])
        keys_order.append(a)

    adj, rej = holm(pvals)
    for i, a in enumerate(keys_order):
        arch_cmp[a]["p_holm"] = adj[i]
        arch_cmp[a]["significant_after_holm"] = rej[i]
    R["comparisons"]["architectures_vs_cnn_dil"] = arch_cmp

    # so sanh "tot nhat vs cnn_dil" (nguon cua tuyen bo +0,41 / +0,73)
    nonlinear = [a for a in arch_names if a != "linear"]
    macro = {a: arch_res[a]["summary"]["macro_F1"] for a in nonlinear}
    best = max(macro, key=macro.get)
    R["equivalence"]["arch_family"] = {
        "kien_truc": {a: float(macro[a]) for a in sorted(macro, key=macro.get, reverse=True)},
        "tot_nhat": best,
        "delta_tot_nhat_vs_cnn_dil": float(macro[best] - macro[ref]),
        "bien_do_7_kien_truc_phi_tuyen": float(max(macro.values()) - min(macro.values())),
        "tost_tot_nhat_vs_cnn_dil": tost_paired(per_rec[best], per_rec[ref], delta=DELTA_TOST),
        "so_kien_truc_TUONG_DUONG_trong_bien_1_0": int(
            sum(
                1
                for a in arch_cmp
                if arch_cmp[a]["tost"]["ket_luan"].startswith("TUONG DUONG")
            )
        ),
        "so_kien_truc_KHONG_KET_LUAN": int(
            sum(1 for a in arch_cmp if arch_cmp[a]["tost"]["ket_luan"].startswith("KHONG"))
        ),
        "chu_thich": (
            "Tuyen bo '8 kien truc khong phan biet duoc' dua tren p > 0,05 -- day la VANG MAT BANG CHUNG, "
            "khong phai bang chung tuong duong. TOST o bien 1,0 diem moi la kiem dinh dung."
        ),
    }

    # =====================================================================
    # 5. Tang ngu canh (+4,53): tcn_rf2s vs short_cnn, muc ban ghi
    # =====================================================================
    def seq_per_record(rows):
        out = {}
        for r in RECS5:
            vals = [x["F1"] for x in rows if x["rec"] == r]
            out[r] = float(np.mean(vals))
        return np.array([out[r] for r in RECS5])

    long_rf = seq_per_record(seq["tcn_rf2s"]["rows"])
    short = seq_per_record(seq["short_cnn"]["rows"])
    c = compare_subject_level(
        long_rf,
        short,
        label="Tang 2 (ngu canh): TCN truong thu nhan 2 s vs CNN cua so ngan",
        name_a="tcn_rf2s",
        name_b="short_cnn",
        note="Don vi cu: 60 hang = 5 ban ghi x 4 kenh x 3 seed -> gia lap 12x",
    )
    c["old_unit"] = "60 hang (ban ghi x kenh x seed)"
    c["old_n"] = 60
    c["old_p_bao_cao"] = "0,0000 (README)"
    c["tost"] = tost_paired(long_rf, short, delta=DELTA_TOST)
    R["comparisons"]["context_tier_tcn_vs_shortcnn"] = c

    # =====================================================================
    # 6. Cong tu choi (gate): AUROC va loi ich o do phu 80%, cluster bootstrap theo BAN GHI
    # =====================================================================
    gate_rows = []
    gpath = os.path.join(ROOT, "fsqi", "gate_segments.csv")
    if os.path.exists(gpath):
        with open(gpath, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["dataset"] == "cinc":
                    gate_rows.append(
                        {
                            "rec": row["rec"],
                            "p_bad": float(row["p_bad"]),
                            "F1": float(row["F1"]),
                            "bad": 1 if float(row["F1"]) < 80.0 else 0,
                        }
                    )
    if gate_rows:
        recs = sorted({r["rec"] for r in gate_rows})
        by_rec = {r: [x for x in gate_rows if x["rec"] == r] for r in recs}
        sc = np.array([x["p_bad"] for x in gate_rows])
        lb = np.array([x["bad"] for x in gate_rows])
        au_point = auroc(sc, lb)

        rng = np.random.default_rng(SEED)
        boots = []
        gains = []
        n_rec = len(recs)

        def cov80_gain(rows):
            f1 = np.array([x["F1"] for x in rows])
            p = np.array([x["p_bad"] for x in rows])
            k = int(round(0.8 * len(rows)))
            keep = np.argsort(p, kind="stable")[:k]
            return float(f1[keep].mean() - f1.mean())

        gain_point = cov80_gain(gate_rows)
        for _ in range(B_BOOT // 2):  # 5000 lan, du on dinh cho 10 cum
            pick = rng.integers(0, n_rec, size=n_rec)
            rows = []
            for i in pick:
                rows.extend(by_rec[recs[i]])
            s = np.array([x["p_bad"] for x in rows])
            l = np.array([x["bad"] for x in rows])
            if l.sum() == 0 or l.sum() == len(l):
                continue
            boots.append(auroc(s, l))
            gains.append(cov80_gain(rows))
        boots = np.array(boots)
        gains = np.array(gains)
        per_rec_au = {}
        for r in recs:
            rows = by_rec[r]
            l = np.array([x["bad"] for x in rows])
            s = np.array([x["p_bad"] for x in rows])
            per_rec_au[r] = auroc(s, l) if 0 < l.sum() < len(l) else None
        within = [v for v in per_rec_au.values() if v is not None]
        n_both = len(within)
        within_mean = float(np.mean(within)) if within else float("nan")
        # bootstrap cho AUROC TRONG ban ghi (lay mau lai cac ban ghi co du 2 lop)
        rng2 = np.random.default_rng(SEED + 1)
        wb = []
        if n_both > 1:
            arr = np.array(within)
            ii = rng2.integers(0, n_both, size=(5000, n_both))
            wb = arr[ii].mean(axis=1)
        within_ci = (
            [float(np.percentile(wb, 2.5)), float(np.percentile(wb, 97.5))] if len(wb) else None
        )

        R["comparisons"]["gate_auroc_cinc"] = {
            "label": "Cong tu choi (12 SQI co dien) tren CinC 2013: AUROC du doan doan xau (F1 < 80)",
            "don_vi_cu": "600 doan tu 10 ban ghi, coi nhu doc lap",
            "auroc_diem_tinh_lai": float(au_point),
            "auroc_bao_cao_cu": float(fsqi["classifier"]["classical"]["auroc_cinc"]),
            "cluster_bootstrap_ci95_theo_ban_ghi": [
                float(np.percentile(boots, 2.5)),
                float(np.percentile(boots, 97.5)),
            ],
            "n_clusters": int(n_rec),
            "auroc_tung_ban_ghi": {k: (float(v) if v is not None else None) for k, v in per_rec_au.items()},
            "auroc_TRONG_ban_ghi": {
                "n_ban_ghi_co_ca_2_lop": int(n_both),
                "n_ban_ghi_khong_co_doan_xau": int(len(recs) - n_both),
                "trung_binh": within_mean,
                "ci95_bootstrap": within_ci,
                "chu_thich": (
                    "AUROC gop 0,93 phan lon la hieu ung GIUA ban ghi (tach ban ghi tot khoi ban ghi xau), "
                    "khong phai kha nang xep hang doan BEN TRONG mot ban ghi. Trong ung dung thuc te "
                    "(mot thai phu, mot phien do) chi co AUROC TRONG ban ghi moi co y nghia."
                ),
            },
            "loi_ich_F1_o_do_phu_80": {
                "diem": gain_point,
                "ci95_cluster_bootstrap": [
                    float(np.percentile(gains, 2.5)),
                    float(np.percentile(gains, 97.5)),
                ],
                "bao_cao_cu": 7.37,
                "chu_thich": "Tai lap tu p_bad da luu (gate_segments.csv); loi ich = TB F1 cua 80% doan p_bad thap nhat - TB F1 toan bo",
            },
            "topo_auroc_bao_cao_cu": float(fsqi["classifier"]["topo"]["auroc_cinc"]),
            "chu_thich": (
                "600 doan 4 s den tu 10 ban ghi: doan trong cung mot ban ghi tuong quan manh. "
                "KTC dung phai lay mau lai BAN GHI, khong phai doan."
            ),
        }

    # =====================================================================
    # 7. Nhung gi KHONG tinh lai duoc
    # =====================================================================
    R["not_recomputable"] = [
        {
            "muc": "Tang 1 -- front-end dai thong (+11,00 diem, README ghi p < 0,001)",
            "ly_do": (
                "pilot_evidence/band_ablation.json chi luu tong hop (macro_F1 +- sd cho moi dai), "
                "KHONG luu F1 tung ban ghi x kenh. Khong the ghep cap lai o muc chu the, "
                "va khong the kiem chung p da cong bo."
            ),
            "he_qua": "p < 0,001 cho tang 1 hien KHONG KIEM CHUNG DUOC. Phai chay lai co luu per-record.",
        },
        {
            "muc": "AUROC cua nhom dac trung to-po (0,566) va nhom ket hop",
            "ly_do": "fsqi/gate_segments.csv chi luu p_bad cua bo phan loai SQI co dien; muon bootstrap theo cum phai huan luyen lai.",
            "he_qua": "0,566 van dung lam ket luan phu dinh, nhung chua co KTC theo cum.",
        },
        {
            "muc": "Bien thien theo seed",
            "ly_do": "Tat ca ket qua chinh chay 1 seed (tru seq_loro co 3 seed).",
            "he_qua": "Moi KTC o day chi bao phu bien thien GIUA CHU THE, khong bao phu bien thien huan luyen.",
        },
    ]

    # =====================================================================
    # 8. Phat hien DAO CHIEU
    # =====================================================================
    rev = []
    for key, c in R["comparisons"].items():
        if key == "architectures_vs_cnn_dil" or key == "gate_auroc_cinc":
            continue
        if not isinstance(c, dict) or "wilcoxon_subject" not in c:
            continue
        oldp = c.get("old_p")
        newp = c["wilcoxon_subject"]["p"]
        if oldp is None:
            continue
        if oldp < 0.05 <= newp:
            rev.append(
                {
                    "so_sanh": c["label"],
                    "p_cu": oldp,
                    "don_vi_cu": c.get("old_unit"),
                    "p_moi_muc_chu_the": newp,
                    "n_chu_the": c["n_subjects"],
                    "ket_luan": "DAO CHIEU: tu 'co y nghia' thanh 'KHONG co y nghia'",
                }
            )
    for a, c in R["comparisons"]["architectures_vs_cnn_dil"].items():
        if c["wilcoxon_subject"]["p"] < 0.05 and not c["significant_after_holm"]:
            rev.append(
                {
                    "so_sanh": c["label"],
                    "p_cu": None,
                    "p_moi_muc_chu_the": c["wilcoxon_subject"]["p"],
                    "p_holm": c["p_holm"],
                    "ket_luan": "Mat y nghia sau hieu chinh Holm",
                }
            )
    ef0 = R["equivalence"]["arch_family"]
    if ef0["so_kien_truc_TUONG_DUONG_trong_bien_1_0"] == 0:
        rev.append(
            {
                "so_sanh": "TUYEN BO TIEU DE: '8 kien truc khong phan biet duoc / khong cai nao khac cnn_dil'",
                "p_cu": "p > 0,05 (vang mat bang chung)",
                "don_vi_cu": "20 cap (ban ghi x kenh), khong hieu chinh da so sanh",
                "p_moi_muc_chu_the": 1.0,
                "n_chu_the": 5,
                "ket_luan": (
                    "DAO CHIEU: TOST bien 1,0 diem cho 0/7 kien truc tuong duong. "
                    "'Khong khac biet' thuc chat la 'khong du cong suat'. Ngoai ra cnn_m KEM HON "
                    "vuot bien (KTC 90% bootstrap [-4,55; -1,47])."
                ),
            }
        )
    R["reversals"] = rev

    # Ghi chu ve gioi han cua n = 5
    R["meta"]["gioi_han_n5"] = (
        "Voi n = 5 chu the, Wilcoxon signed-rank hai phia co p NHO NHAT co the dat = 2/2^5 = 0,0625. "
        "Do do KHONG mot so sanh nao tren ADFECGDB (5 phu nu) co the dat p < 0,05 o muc chu the, "
        "bat ke hieu so lon den dau. Moi p < 0,05 tung bao cao tren tap nay deu la san pham cua gia lap."
    )

    # =====================================================================
    # Xuat
    # =====================================================================
    os.makedirs(OUT_DIR, exist_ok=True)
    outj = os.path.join(OUT_DIR, "stats_results.json")
    with open(outj, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False)

    write_markdown(R)
    dt = (datetime.now() - t0).total_seconds()
    print(f"Xong trong {dt:.1f} s -> {outj}")
    print(f"So ket luan DAO CHIEU: {len(R['reversals'])}")
    for r in R["reversals"]:
        print("  -", r["so_sanh"], "| p cu", r.get("p_cu"), "-> p moi", round(r["p_moi_muc_chu_the"], 4))


# ----------------------------------------------------------------------------
# Bao cao markdown
# ----------------------------------------------------------------------------

def fp(x, nd=4):
    if x is None:
        return "--"
    if isinstance(x, str):
        return x
    if isinstance(x, float) and (x != x):
        return "--"
    if abs(x) < 1e-4 and x != 0:
        s = f"{x:.2e}"
    else:
        s = f"{x:.{nd}f}"
    return s.replace(".", ",")


def fci(ci, nd=2):
    if ci is None:
        return "--"
    return f"[{fp(ci[0], nd)}; {fp(ci[1], nd)}]"


def write_markdown(R):
    L = []
    A = L.append
    A("# Phan tich thong ke o DON VI CHU THE -- ban sua loi gia lap (pseudo-replication)")
    A("")
    A(f"*Tao ngay {R['meta']['date']} boi `analysis/stats.py`. "
      f"Bootstrap {R['meta']['n_boot']} lan, seed {R['meta']['seed']}, bien tuong duong "
      f"delta = {fp(R['meta']['delta_tost_F1'],1)} diem F1.*")
    A("")
    A("## 0. Loi da sua")
    A("")
    A("| | Cach cu | Cach moi |")
    A("|---|---|---|")
    A("| Don vi phan tich | Cap (ban ghi x kenh), 20-88 cap | **Chu the** (TB 4 kenh truoc), n = 5-22 |")
    A("| Gia dinh doc lap | 4 kenh bung cua cung 1 phu nu coi la 4 quan sat doc lap | Kenh la do lap lai trong cum; chu the la don vi |")
    A("| KTC | t tren thang phan tram | Thang logit + bootstrap percentile |")
    A("| Bien thien | SD tren cap | Cluster bootstrap lay mau lai chu the |")
    A("| Da so sanh | khong hieu chinh | Holm cho ho 7 kien truc |")
    A("| Ket luan 'khong khac' | p > 0,05 | **TOST** bien 1,0 diem |")
    A("")
    A("> **Gioi han cung cua n = 5.** " + R["meta"]["gioi_han_n5"])
    A("")

    # --- Bang 1: bang tong hop chinh
    A("## 1. Bang tong hop: moi so sanh chinh")
    A("")
    A("| So sanh | n chu the | p cu (gia lap) | Don vi cu | p moi (muc chu the) | p sign test | Hieu so TB | KTC 95% bootstrap | KTC 95% t (bao thu) | Cliff delta | Doi ket luan? |")
    A("|---|---:|---:|---|---:|---:|---:|---|---|---:|---|")

    def row(c):
        w = c["wilcoxon_subject"]
        cb = c["cluster_bootstrap"]
        oldp = c.get("old_p")
        newp = w["p"]
        changed = "--"
        if oldp is not None:
            if oldp < 0.05 <= newp:
                changed = "**CO -- mat y nghia**"
            elif oldp >= 0.05 > newp:
                changed = "**CO -- co them y nghia**"
            else:
                changed = "khong"
        return (
            f"| {c['label']} | {c['n_subjects']} | {fp(oldp)} | {c.get('old_unit','--')} | "
            f"**{fp(newp)}** | {fp(c['sign_test']['p'])} | {fp(cb['mean_diff'],2)} | "
            f"{fci(cb['ci95'])} | {fci(cb['ci95_t_paired'])} | "
            f"{fp(c['cliffs_delta']['delta'],3)} ({c['cliffs_delta']['magnitude']}) | {changed} |"
        )

    order = [
        "adfecgdb_model_vs_TS_mean4",
        "adfecgdb_model_vs_TS-PCA_mean4",
        "adfecgdb_model_vs_Prominence_mean4",
        "adfecgdb_model_vs_TS_psdlead",
        "adfecgdb_model_vs_TS-PCA_psdlead",
        "adfecgdb_model_vs_Prominence_psdlead",
        "m22_vs_m5_PhysioNet_mean4",
        "m22_vs_m5_B2_mean4",
        "m22_vs_m5_B1_mean4",
        "m22_vs_m5_ALL_mean4",
        "m22_vs_m5_B1_psd",
        "m22_vs_m5_ALL_psd",
        "cinc_m22_vs_m5_lead0",
        "cinc_m22_vs_m5_mean4",
        "context_tier_tcn_vs_shortcnn",
    ]
    for k in order:
        if k in R["comparisons"]:
            A(row(R["comparisons"][k]))
    A("")
    A("Quy uoc hieu so: **A - B** voi A la cot dau trong ten so sanh (mo hinh, model_22, kien truc moi).")
    A("")
    A("**Doc bang nay cho dung -- ba luu y quan trong:**")
    A("")
    A("1. **Mat y nghia KHONG tu dong co nghia la mat hieu ung -- nhung voi TS thi mat that.** Voi TS-PCA va "
      "Prominence, p tang tu ~1e-6 len 0,0625 chi vi n = 5 lam san kiem dinh hang, con KTC 95% cua hieu so "
      "van **loai tru 0** ca o bootstrap lan o thang t (TS-PCA: [3,69; 9,10] diem theo t). Voi hai baseline nay, "
      "*huong* cua ket qua giu nguyen, chi la **khong duoc tuyen bo y nghia thong ke** tu 5 phu nu. "
      "Nhung voi **TS thi khac**: KTC 95% kieu t la **[-1,81; 38,80] -- chua ca 0**. Hieu so 18,49 diem "
      "hoan toan do bien thien giua 5 ban ghi, khong phai mot loi the on dinh. Bang baseline trong bai "
      "dang trinh bay ca ba nhu nhau; thuc te chung khong cung do chac.")
    A("2. **KTC bootstrap voi n = 5 cum la hep hon thuc te.** Cot 'KTC 95% t' bao thu hon; khi hai cot mau thuan "
      "thi tin cot t. Voi n = 5-7 nen bao cao ca hai.")
    A("3. **Sign test la kiem dinh bao thu nhat** va cho thay do manh that su: vi du 'ALL 22 chu the' co "
      "Wilcoxon p = 0,0029 nhung sign test p = 0,0525 -- tuc ket qua phu thuoc vao DO LON cua vai chu the, "
      "khong phai vao viec da so chu the deu cai thien.")
    A("")

    # --- Bang 2: KTC
    A("## 2. Khoang tin cay cho cac con so dat tren tieu de")
    A("")
    A("| Con so | n chu the | TB so hoc | KTC 95% kieu t tren % (SAI) | Vuot 100%? | **KTC 95% bootstrap (cho TB so hoc)** | Diem logit | KTC 95% logit |")
    A("|---|---:|---:|---|---|---|---:|---|")
    for k, v in R["confidence_intervals"].items():
        A(
            f"| {v['ten']} ({fp(v['gia_tri_bao_cao_cu'],2)} da cong bo) | {v['n_subjects']} | "
            f"{fp(v['mean'],2)} | {fci(v['t_ci_pct_SAI']['ci95'])} | "
            f"{'**CO**' if v['t_ci_pct_SAI']['vuot_100'] else 'khong'} | "
            f"**{fci(v['bootstrap_ci']['ci95_percentile'])}** | "
            f"{fp(v['logit_ci']['mean_backtransformed'],2)} | {fci(v['logit_ci']['ci95'])} |"
        )
    A("")
    A("**Hai uoc luong diem khac nhau, dung nham la sai.**")
    A("")
    A("- Cot *KTC bootstrap* la khoang cho **trung binh so hoc** cua F1 tren cac chu the -- day la dai luong "
      "ma bai bao dang bao cao (99,21 / 93,30 / 90,34). Dung cot nay trong bang ket qua chinh. "
      "No khong bao gio vuot 100% vi chi lay lai mau tu cac gia tri quan sat.")
    _b1 = R["confidence_intervals"].get("silesia_B1_model5_psd")
    if _b1:
        A(f"- Cot *logit* la trung binh tren thang logit roi doi nguoc -- day la **F1 dien hinh cua mot chu the moi**, "
          f"keo ve phia cac gia tri cao. Vi vay no CO THE cao hon trung binh so hoc (vi du Silesia B1: TB so hoc "
          f"{fp(_b1['mean'],2)} nhung diem logit {fp(_b1['logit_ci']['mean_backtransformed'],2)}, vi phan bo lech "
          f"trai co ban ghi thap keo trung binh so hoc xuong). Dung cot nay khi noi ve **mot ca lam sang moi**, "
          f"va phai noi ro la dai luong KHAC voi trung binh so hoc -- neu bao cao nham, con so se bi thoi phong.")
    A("- KTC t tren thang phan tram la cot duy nhat **vuot 100%** -- day chinh la loi dang co trong bai.")
    A("")
    A("Chu y do rong that su: ADFECGDB n = 5 cho KTC rong vai diem F1 (khong phai +-1,5 nhu SD goi y); "
      "Silesia B1 va CinC 2013 rong hon 10-30 diem.")
    A("")

    # --- Bang 3: kien truc
    A("## 3. Ho kien truc: kiem dinh tuong duong (TOST), bien 1,0 diem F1")
    A("")
    A("| Kien truc | Macro F1 | Hieu so vs cnn_dil | p Wilcoxon (n=5) | p sau Holm | KTC 90% (t) | KTC 90% bootstrap | p TOST | Ket luan |")
    A("|---|---:|---:|---:|---:|---|---|---:|---|")
    ac = R["comparisons"]["architectures_vs_cnn_dil"]
    fam = R["equivalence"]["arch_family"]["kien_truc"]
    for a in sorted(ac, key=lambda x: -ac[x]["mean_A"]):
        c = ac[a]
        t = c["tost"]
        A(
            f"| {a} | {fp(c['mean_A'],2)} | {fp(t['mean_diff'],2)} | {fp(c['wilcoxon_subject']['p'])} | "
            f"{fp(c['p_holm'])} | {fci(t['ci90_t'])} | {fci(t['ci90_bootstrap'])} | {fp(t['p_tost'])} | {t['ket_luan']} |"
        )
    A("")
    ef = R["equivalence"]["arch_family"]
    A(f"- Kien truc tot nhat: **{ef['tot_nhat']}**, hon cnn_dil **{fp(ef['delta_tot_nhat_vs_cnn_dil'],2)}** diem "
      f"(tuyen bo cu trong README: +0,41).")
    A(f"- Bien do giua 7 kien truc phi tuyen: {fp(ef['bien_do_7_kien_truc_phi_tuyen'],2)} diem F1.")
    A(f"- So kien truc **chung minh duoc tuong duong** trong bien 1,0 diem: **{ef['so_kien_truc_TUONG_DUONG_trong_bien_1_0']}/{len(ac)}**.")
    A(f"- So kien truc **khong ket luan duoc**: **{ef['so_kien_truc_KHONG_KET_LUAN']}/{len(ac)}**.")
    A("")
    A(f"> {ef['chu_thich']}")
    A("")
    A("### 3.1 Day la DAO CHIEU lon nhat cua toan bo nhiem vu")
    A("")
    A("Tuyen bo trong README va trong tieu de bai -- *'8 kien truc khong phan biet duoc, khong cai nao khac "
      "cnn_dil 26k tham so'* -- **khong song sot qua kiem dinh tuong duong**:")
    A("")
    A("- **0/7** kien truc chung minh duoc tuong duong trong bien +-1,0 diem F1. Sau khi sua don vi phan tich, "
      "du lieu 5 ban ghi **khong du** de ket luan bat ky hai kien truc nao la nhu nhau.")
    A("- Ket luan cu duoc rut ra tu 'p > 0,05'. Voi n = 5 chu the, p > 0,05 la ket qua **gan nhu duong nhien** "
      "(nguong kha thi nho nhat la 0,0625) -- no do do cong suat thap, khong do cac kien truc giong nhau.")
    A("- Nguoc lai, **cnn_m KEM HON ro**: hieu so -2,95 diem, KTC 90% bootstrap [-4,55; -1,47] nam **hoan toan "
      "ngoai** bien +-1,0. Tuyen bo 'sau kien truc nam trong 1,5 diem cua nhau' khong dung voi cnn_m.")
    A("- **cnn_l tot hon** cnn_dil 0,73 diem voi KTC 90% bootstrap [0,18; 1,22] -- khong loai tru duoc kha nang "
      "vuot bien 1,0. Neu cham sat, cnn_l co the thuc su tot hon, chi la chua du bang chung.")
    A("")
    A("**Cach viet lai an toan:** thay 'khong kien truc nao khac biet' bang *'voi n = 5 chu the, nghien cuu nay "
      "khong du cong suat de phan biet cac kien truc trong bien 1,0 diem F1; hieu so quan sat duoc nam trong "
      "khoang -2,95 den +0,73 diem, nho hon nhieu so voi +11,0 diem cua tang front-end'*. Cau nay VAN giu duoc "
      "thong diep chinh (front-end quan trong hon kien truc) ma khong tuyen bo dieu chua chung minh.")
    A("")

    # --- Bang 4: gate
    if "gate_auroc_cinc" in R["comparisons"]:
        g = R["comparisons"]["gate_auroc_cinc"]
        A("## 4. Cong tu choi: AUROC voi cluster bootstrap theo BAN GHI")
        A("")
        A("| Dai luong | Gia tri | KTC 95% (bootstrap theo ban ghi, n = 10 cum) | Bao cao cu |")
        A("|---|---:|---|---:|")
        A(f"| AUROC (12 SQI co dien, CinC 2013) | {fp(g['auroc_diem_tinh_lai'],3)} | "
          f"{fci(g['cluster_bootstrap_ci95_theo_ban_ghi'],3)} | {fp(g['auroc_bao_cao_cu'],3)} |")
        gg = g["loi_ich_F1_o_do_phu_80"]
        A(f"| Loi ich F1 o do phu 80% | {fp(gg['diem'],2)} | {fci(gg['ci95_cluster_bootstrap'])} | {fp(gg['bao_cao_cu'],2)} |")
        A(f"| AUROC nhom to-po (TDA) | {fp(g['topo_auroc_bao_cao_cu'],3)} | chua tinh duoc (can huan luyen lai) | {fp(g['topo_auroc_bao_cao_cu'],3)} |")
        w = g["auroc_TRONG_ban_ghi"]
        A(f"| **AUROC TRONG ban ghi** (TB tren {w['n_ban_ghi_co_ca_2_lop']} ban ghi co ca doan tot lan xau) | "
          f"**{fp(w['trung_binh'],3)}** | {fci(w['ci95_bootstrap'],3)} | chua tung bao cao |")
        A("")
        A("AUROC tung ban ghi: " + ", ".join(
            f"{k} = {fp(v,3) if v is not None else 'n/a (khong co doan xau)'}"
            for k, v in g["auroc_tung_ban_ghi"].items()
        ))
        A("")
        A(f"> {g['chu_thich']}")
        A("")
        A("**Phat hien moi, quan trong:** " + w["chu_thich"])
        A("")
        A(f"{w['n_ban_ghi_khong_co_doan_xau']}/{len(g['auroc_tung_ban_ghi'])} ban ghi CinC khong co doan xau nao "
          "(mo hinh chay hoan hao suot ban ghi), nen chung khong dong gop gi vao AUROC gop. "
          "Con so 0,929 tren thuc te chu yeu tra loi cau hoi *'ban ghi nay co phai ban ghi xau khong'*, "
          "chu khong phai *'doan 4 giay nay trong ban ghi cua benh nhan nay co dang tin khong'* -- "
          "trong khi cong tu choi duoc ban nhu la thu hai. Day la mot gioi han phai neu ro, va la ly do "
          "ket qua nay chua the tuyen bo la dung duoc tai giuong benh.")
        A("")

    # --- Bang 5: dao chieu
    A("## 5. CAC KET LUAN DOI CHIEU")
    A("")
    if not R["reversals"]:
        A("Khong co ket luan nao doi chieu.")
    else:
        A("| So sanh | p cu | Don vi cu | p moi (chu the) | n | Ket luan |")
        A("|---|---:|---|---:|---:|---|")
        for r in R["reversals"]:
            A(f"| {r['so_sanh']} | {fp(r.get('p_cu'))} | {r.get('don_vi_cu','--')} | "
              f"{fp(r['p_moi_muc_chu_the'])} | {r.get('n_chu_the','--')} | {r['ket_luan']} |")
    A("")

    # --- Bang 6: khong tinh lai duoc
    A("## 6. Nhung gi KHONG kiem chung lai duoc tu artefact hien co")
    A("")
    A("| Muc | Ly do | He qua |")
    A("|---|---|---|")
    for n in R["not_recomputable"]:
        A(f"| {n['muc']} | {n['ly_do']} | {n['he_qua']} |")
    A("")

    A("## 7. Viec phai sua trong bai, theo thu tu uu tien")
    A("")
    A("| # | Phai sua | Sua thanh |")
    A("|---:|---|---|")
    A("| 1 | Tuyen bo tieu de '8 kien truc khong phan biet duoc' | 'Nghien cuu nay khong du cong suat (n = 5 chu the) "
      "de phan biet cac kien truc trong bien 1,0 diem F1; hieu so quan sat nam trong -2,95 den +0,73 diem.' "
      "**Day la thay doi bat buoc** -- tuyen bo hien tai la ket luan tuong duong rut ra tu p > 0,05. |")
    A("| 2 | Moi p tren ADFECGDB (1,9e-6, 5,7e-6, ...) | Bo han. Thay bang hieu so + KTC 95% o muc chu the, kem cau "
      "'n = 5 chu the: p < 0,05 la bat kha thi voi kiem dinh hang hai phia'. |")
    A("| 3 | Bang baseline trinh bay ca 3 nhu nhau | Tach ro: TS-PCA va Prominence co KTC loai tru 0; **TS thi khong** "
      "(KTC t [-1,81; 38,80]). |")
    A("| 4 | '99,21 +- 1,50' va cac '+- SD' khac | Trung binh + KTC 95% cluster bootstrap cho TRUNG BINH SO HOC "
      "(cot dam trong Muc 2). Neu muon noi ve 'mot ca moi' thi dung KTC logit va **noi ro do la dai luong khac**. |")
    A("| 5 | 'B2: cai thien co y nghia, p = 0,016' | Bo. O muc chu the p = 0,47, Cliff delta 0,10 (khong dang ke). |")
    A("| 6 | 'Tang 2 (ngu canh) +4,53, p = 0,0000' | p tinh tren 60 hang gom ca 3 seed -- gia lap 12 lan. "
      "O muc ban ghi: +4,49 diem, p = 0,0625, KTC t [-0,29; 9,27]. Bao cao hieu so, bo p. |")
    A("| 7 | 'AUROC cong tu choi 0,929' | Them KTC cluster bootstrap [0,830; 0,982] VA con so AUROC trong ban ghi "
      "0,721 -- vi ung dung lam sang chi dung duoc con so thu hai. |")
    A("| 8 | 'Tang 1 front-end +11,00, p < 0,001' | Chay lai co luu F1 tung ban ghi x kenh roi kiem dinh o muc "
      "chu the. Hien khong kiem chung duoc, va (theo P1) lai do tren GBM chu khong tren TCN. |")
    A("")
    A("**Nguyen tac chung cho ban sua:** bao cao **uoc luong hieu so kem KTC** lam ket qua chinh; p-value la phu "
      "va phai luon di kem n chu the. Voi n = 5-10, khong tuyen bo y nghia thong ke o bat ky dau; "
      "voi ket luan 'khong khac nhau', bat buoc dung TOST kem bien duoc dinh truoc.")
    A("")

    with open(os.path.join(OUT_DIR, "STATS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
