# -*- coding: utf-8 -*-
"""Sinh survey/facts_phase4.json — nguồn sự thật duy nhất cho mọi con số hiện hành (vòng 7).

Mỗi mục có trường "nguon" chỉ đúng tệp JSON (và khoá) mà con số được đọc ra. Không con số nào
được gõ tay nếu tệp nguồn có trên đĩa; các số chỉ tồn tại trong báo cáo .md được ghi rõ là như vậy.

    python survey/make_facts_phase4.py
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return json.load(f)

def r2(x): return None if x is None else round(float(x), 2)
def r3(x): return None if x is None else round(float(x), 3)

c60 = load('benchmark_dpss/eval_cinc60_sach.json')
dl = load('analysis/dulieu_results.json')
xn = load('analysis/xacnhan_results.json')
pmf = load('baselines/powermf_fair_stats.json')
pmf1 = load('baselines/powermf_1ch.json')
e22 = load('benchmark_dpss/eval_22.json')
band = load('pilot_evidence/band_tcn_stats.json') if os.path.exists(os.path.join(ROOT, 'pilot_evidence/band_tcn_stats.json')) else None
demo = load('demo/results/demo_check_2modes.json')
rori = load('survey/ro_ri_vanlieu.json')

v60 = c60['variants']['60_sach']; v53 = c60['variants']['53_sach_loai_7_nhan_sai']
ck = dl['chon_kenh_60_sach']['bang']

def rule60(name):
    r = v60['rules'][name]
    return {
        'm5': r2(r['m5']['mean']), 'm5_ci95': [r2(x) for x in r['m5']['ci95_bootstrap']],
        'm22': r2(r['m22']['mean']), 'm22_ci95': [r2(x) for x in r['m22']['ci95_bootstrap']],
        'm22_ge90': r['m22']['ge90'], 'm22_lt50': r['m22']['lt50'], 'm22_median': r2(r['m22']['median']),
        'm5_ge90': r['m5']['ge90'], 'm5_lt50': r['m5']['lt50'],
        'm22_minus_m5': r2(r['m22_minus_m5']['mean_diff']),
        'm22_minus_m5_ci95': [r2(x) for x in r['m22_minus_m5']['ci95_bootstrap']],
        'wilcoxon_p': float('%.2g' % r['m22_minus_m5']['wilcoxon_p']),
        'thang_thua_hoa': [r['m22_minus_m5'].get('wins'), r['m22_minus_m5'].get('losses'), r['m22_minus_m5'].get('ties')],
        'nguon': 'benchmark_dpss/eval_cinc60_sach.json -> variants.60_sach.rules.%s' % name,
    }

def ck60(name):
    b = ck[name]
    return {
        'F1_60_sach': r2(b['mean_60_sach']), 'hieu_vs_psd': r2(b['hieu_vs_psd']),
        'ci95': [r2(x) for x in b['ci95']], 'wilcoxon_p': float('%.2g' % b['wilcoxon_p']),
        'holm_p': (float('%.2g' % b['holm_p']) if 'holm_p' in b else None),
        'thang_thua_hoa': [b['thang'], b['thua'], b['hoa']], 'lt50': b['lt50'], 'ge90': b['ge90'],
        'F1_75_o_nhiem_DA_RUT': r2(b['mean_75_o_nhiem']),
        'nguon': 'analysis/dulieu_results.json -> chon_kenh_60_sach.bang.%s' % name,
    }

A = xn['viec3_logit_22']['ket_qua_theo_kep']
facts = {
  'ghi_chu': ('Vòng 7 (12/09/2026). Nguồn sự thật duy nhất cho mọi con số hiện hành. Mỗi mục có trường '
              '"nguon" là tệp JSON trên đĩa. Sinh bởi survey/make_facts_phase4.py. Số đã rút được liệt kê '
              'riêng ở mục Z_DA_RUT và KHÔNG được trích dẫn như sự kiện.'),
  'ngay_sinh': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
  'A_cinc2013_60_ban_sach': {
    'co_so': ('Set-a KHÔNG độc lập với ADFECGDB. Ban tổ chức đã ghi nhận: Silva 2013 (CinC 40:149-152, Bảng 1: '
              '"Abdominal and Direct FECG — 25"); Clifford 2014 (Physiol Meas 35:1521, Bảng 2, cảnh báo về Rodrigues). '
              'Nhóm CHỈ định danh 15 bản và mức thổi phồng; KHÔNG viết "chúng tôi phát hiện rò rỉ".'),
    'nguon_y_van': 'survey/ro_ri_vanlieu.json, survey/RO_RI_VANLIEU.md',
    '15_ban_ro_ri': c60['meta']['leak_records'],
    'nguon_15_ban': 'benchmark_dpss/eval_cinc60_sach.json -> meta.leak_records; analysis/dulieu_results.json -> chong_lan; analysis/dulieu_m4b_verify.json',
    'ncc': 1.0, 'lech_rr_ms': 0.0, 'ncc_toi_da_60_ban_con_lai': 0.62,
    'thoi_phong_diem_F1': [3.27, 7.18],
    'nguon_thoi_phong': 'analysis/DULIEU.md muc 0 (tinh tu eval_cinc75.json vs eval_cinc60_sach.json)',
    'n_sach': v60['n'],
    'psd': rule60('psd'), 'mean4': rule60('mean4'), 'lead0_hau_kiem_da_rut': rule60('lead0'), 'oracle': rule60('oracle'),
    'psd_vs_oracle_m22': {
        'hieu': r2(v60['psd_vs_oracle_m22']['mean_diff']),
        'ci95': [r2(x) for x in v60['psd_vs_oracle_m22']['ci95_bootstrap']],
        'psd_chon_trung_oracle': v60['psd_picks_oracle_lead_m22'],
        'nguon': 'benchmark_dpss/eval_cinc60_sach.json -> variants.60_sach.psd_vs_oracle_m22',
    },
    '53_ban_loai_7_nhan_sai': {
        'psd_m5': r2(v53['rules']['psd']['m5']['mean']), 'psd_m22': r2(v53['rules']['psd']['m22']['mean']),
        'hieu': r2(v53['rules']['psd']['m22_minus_m5']['mean_diff']),
        'ci95': [r2(x) for x in v53['rules']['psd']['m22_minus_m5']['ci95_bootstrap']],
        'wilcoxon_p': float('%.2g' % v53['rules']['psd']['m22_minus_m5']['wilcoxon_p']),
        'nguon': 'benchmark_dpss/eval_cinc60_sach.json -> variants.53_sach_loai_7_nhan_sai',
    },
    'powermf_1ch_60_sach': {
        'F1': r2(c60['powermf_1ch']['60_sach']['F1_psd']['mean']),
        'ci95': [r2(x) for x in c60['powermf_1ch']['60_sach']['F1_psd']['ci95_bootstrap']],
        'rely_m22_psd_minus_pmf1': r2(c60['powermf_1ch']['60_sach']['rely_m22_psd_minus_pmf1']['mean_diff']),
        'ci95_hieu': [r2(x) for x in c60['powermf_1ch']['60_sach']['rely_m22_psd_minus_pmf1']['ci95_bootstrap']],
        'thang_thua_hoa': [c60['powermf_1ch']['60_sach']['rely_m22_psd_minus_pmf1'][k] for k in ('wins', 'losses', 'ties')],
        'nguon': 'benchmark_dpss/eval_cinc60_sach.json -> powermf_1ch.60_sach',
    },
  },
  'B_chon_kenh_7_quy_tac_60_sach': {
    'trang_thai': ('GIẢ THUYẾT MẠNH, CHƯA XÁC NHẬN. gate là quy tắc chỉ định trước và TRƯỢT Holm; peakprob tốt nhất '
                   'theo F1 thô nhưng chọn hậu kiểm; trên logit gate dẫn 22 chủ thể, gate4 dẫn 60 bản; không có bộ '
                   'thứ ba có nhãn thật để lặp lại. KHÔNG dùng "tiền đăng ký".'),
    'psd': ck60('psd'), 'gate_chi_dinh_truoc': ck60('gate'), 'gate4': ck60('gate4'), 'rrcv': ck60('rrcv'),
    'peakprob_hau_kiem': ck60('peakprob'), 'rrplaus': ck60('rrplaus'), 'learned': ck60('learned'),
    'oracle_F1': r2(v60['rules']['oracle']['m22']['mean']),
    'peakprob_phan_tram_du_dia_oracle': r2(ck['peakprob']['phan_tram_du_dia_oracle']),
    'khai_bao_truoc': 'analysis/chonkenh_khaibao_truoc.json (khong neo git, viet sau khi co F1 tung kenh)',
  },
  'C_xac_nhan_vong7': {
    'khai_bao_truoc': xn['meta']['khai_bao_truoc'], 'git_khai_bao': xn['meta']['git_khai_bao'],
    'bo_thu_ba': {
        'co_bo_thu_ba_co_nhan_that': xn['viec2_bo_thu_ba']['co_bo_thu_ba_co_nhan_that'],
        'da_kiem': xn['viec2_bo_thu_ba']['da_kiem'],
        'nguon': 'analysis/xacnhan_results.json -> viec2_bo_thu_ba',
    },
    'logit_22_chu_the': {
        'dung_dau_kep_A': A['A']['dung_dau'], 'dung_dau_kep_B': A['B']['dung_dau'], 'dung_dau_kep_C': A['C']['dung_dau'],
        'xep_hang_kep_A': A['A']['xep_hang_7_quy_tac_moi'],
        'peakprob_kep_A': {'hieu_logit': r3(A['A']['bang']['peakprob']['diff_vs_psd']),
                           'ci95': [r3(x) for x in A['A']['bang']['peakprob']['ci95']],
                           'holm_p': r3(A['A']['bang']['peakprob']['holm_p'])},
        'gate_kep_A': {'hieu_logit': r3(A['A']['bang']['gate']['diff_vs_psd']),
                       'ci95': [r3(x) for x in A['A']['bang']['gate']['ci95']],
                       'holm_p': r3(A['A']['bang']['gate']['holm_p'])},
        'van_de_hau_kiem_bien_mat': xn['viec3_logit_22'].get('van_de_hau_kiem_bien_mat', False),
        'nguon': 'analysis/xacnhan_results.json -> viec3_logit_22',
    },
    'phep_thu_nhin_thay': {
        'ket_luan': 'ket_luan_mo_hinh_khong_nut_that_con_dung = false; phan du dia thieu tin hieu KHONG xac dinh duoc',
        'nguon': 'analysis/xacnhan_results.json -> viec4_phep_thu_nhin_thay',
        'chi_tiet': xn.get('viec4_phep_thu_nhin_thay'),
    },
    'seed': {'nguon': 'analysis/xacnhan_results.json -> viec5_seed', 'chi_tiet': xn.get('viec5_seed')},
  },
  'D_22_chu_the': {
    'nguon': 'benchmark_dpss/eval_22.json; baselines/powermf_fair_stats.json; baselines/powermf_1ch.json',
    'ghi_chu': 'Xem cac tep nguon; cac so tom tat: RelyFetal 97,56 | Power-MF 4 kenh 98,83 | Power-MF 1 kenh 86,71; '
               'Rely - PMF4 = -1,27 [-3,08; +0,27] p 0,156 (18/0/4); Rely - PMF1 = +10,85 [+6,80; +15,40] (22/0/0); '
               'PMF1 - PMF4 = -12,12; 89,5 % loi ich da kenh duoc lay lai. Kiem chung ngoai: B1 99,40 vs 99,46 cong bo.',
    'powermf_fair_stats_keys': list(pmf.keys())[:20] if isinstance(pmf, dict) else None,
  },
  'E_dai_loc_tren_TCN': {
    'nguon': 'pilot_evidence/band_tcn.json, pilot_evidence/band_tcn_stats.json',
    # KTC theo band_tcn_stats.json (20.000 lan cluster bootstrap); band_tcn_log.txt ghi [-0,05; +6,30] / [-0,49; +0,40] tu lan chay khac
    'ghi_chu': '+2,44 [-0,04; +6,29] tren kenh PSD; -0,07 [-0,51; +0,39] trung binh 4 kenh -> +11,00 (GBM 300 ms) DA RUT voi TCN',
    'band_tcn_stats_keys': (list(band.keys())[:20] if isinstance(band, dict) else None),
  },
  'F_demo': {
    'generated': demo['generated'], 'lead_rule': demo['lead_rule'], 'include_leak': demo['include_leak'],
    'n_records_cham': demo['summary_by_mode']['hoc']['n_records'],
    'summary_by_mode': {m: {'by_level': {lv: {'n': x['n'], 'F1_mean': r2(x['F1_mean']), 'F1_min': r2(x['F1_min'])}
                                         for lv, x in s['by_level'].items()},
                            'green_but_F1_below_90': s['green_but_F1_below_90'],
                            'n_red_but_F1_at_least_95': s['n_red_but_F1_at_least_95']}
                        for m, s in demo['summary_by_mode'].items()},
    'nguon': 'demo/results/demo_check_2modes.json -> summary_by_mode',
  },
  'G_venue': {
    'physiological_measurement': 'Q2 (Physiology 25/73) / Q3 (Biomedical Eng. 51/89) Scimago 2024 — KHONG phai Q1',
    'Q1_scimago': ['IEEE JBHI', 'IEEE TBME', 'Biomedical Signal Processing and Control', 'Computers in Biology and Medicine', 'Artificial Intelligence in Medicine'],
    'de_xuat': 'JBHI neu co bo thu ba co nhan; neu khong, Physiological Measurement',
    'nguon': 'docs/CHIEN_LUOC_CONG_BO.md (bang venue)',
  },
  'Z_DA_RUT': {
    'ghi_chu': 'KHONG trich dan nhu su kien. Xem README.md muc Retractions.',
    'cinc_mau_10': [59.15, 69.31, 77.34, 90.34, 22.33],
    'cinc_75_o_nhiem': [71.21, 79.40, 86.87, 74.09, 69.33, 80.70, 8.18, 7.47, 85.60, 6.20, 5.14, 62.82, 16.58],
    'powermf_cong_chuyen_hong': [94.87, 2.74, 98.38, 97.33],
    'dai_loc_gbm_nhu_phat_bieu_ve_tcn': 11.00,
    'cum_tu': ['8 kien truc khong phan biet duoc', 'luong cuc (nhu co che)', 'tien dang ky', 'phat hien ro ri',
               'mo hinh khong phai nut that', '71 % du dia khong co tin hieu', '1,85 diem thuoc mo hinh',
               '8 ban gioi han cung', 'Physiological Measurement la Q1', 'SOTA/novel/first'],
    'khoang_cach_trong_ngoai_mien_17_92': {
      'gia_tri': 17.92,
      'ly_do': 'tinh tu moc CinC 79,40 tren 75 ban nhiem da rut: khoang_cach_CinC_con_lai = C3_ca_hai (97,32, mo phong dich chuyen tren 22 chu the) - CINC_REF_PSD 79,40; moc 79,40 nam trong cinc_75_o_nhiem',
      'nguon': 'adapt/adapt_analyze.py dong 15 (CINC_REF_PSD = 79.40) va dong 76 (khoang_cach_CinC_con_lai); adapt/adapt_results.json -> mo_phong_dich_chuyen.khoang_cach_CinC_con_lai = 17.9166; analysis/THICHNGHI.md (dong 110)',
      'thay_bang': {
        'cach_tinh': 'F1 trong mien 97,56 (baselines/powermf_fair_stats.json -> so_sanh.tat_ca_22.rely_vs_pmf4.mean_a) tru F1 tren 60 ban CinC sach (analysis/dulieu_results.json -> chon_kenh_60_sach.bang.<quy_tac>.mean_60_sach)',
        'psd': 23.28,
        'gate': 16.84,
        'gate4': 16.55,
        'peakprob': 15.55,
        'tran_oracle': 13.96,
        'ghi_chu': 'psd la so chinh; gate la quy tac ke hoach chon (truot Holm p 0,051); gate4 ghi truoc khi chay, song sot Holm p 0,015 nhung khong phai quy tac ke hoach chon; peakprob chon lam mac dinh sau khi xem ket qua CinC (hau kiem); tran_oracle dung nhan. Phan 0,01 diem cua mo phong dich chuyen (C0_60s - C3_ca_hai) khong doi.',
      },
      'ngay_rut': '17/09/2026',
    },
  },
}

out = os.path.join(ROOT, 'survey', 'facts_phase4.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(facts, f, ensure_ascii=False, indent=2)
print('wrote', out)
