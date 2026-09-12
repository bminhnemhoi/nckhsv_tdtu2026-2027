# -*- coding: utf-8 -*-
"""Sinh khoi Markdown cho muc 3.3 cua analysis/DULIEU.md tu analysis/dulieu_results.json.
Chay: python analysis/dulieu_exp_md.py   (tu dong chen vao giua <!-- KET_QUA_M4_MINI --> ... <!-- HET -->)
"""
import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'dulieu_results.json'), encoding='utf-8'))
E = R['thuc_nghiem']
NAME = {'base': 'base (tăng cường BẬT)', 'noaug': 'noaug (tăng cường TẮT)',
        'bal': 'bal (cân bằng theo số nhịp)'}


def ci(s):
    return '%+.2f KTC95 bootstrap [%+.2f; %+.2f], KTC95 t [%+.2f; %+.2f], Wilcoxon p = %.3f, thắng %d/%d (hoà %d)' % (
        s['mean_diff'], s['ci95_bootstrap'][0], s['ci95_bootstrap'][1],
        s['ci95_t'][0], s['ci95_t'][1], s['wilcoxon_p'], s['wins'], s['wins'] + s['losses'], s['ties'])


L = []
if E.get('trang_thai') or not E.get('n_chu_the'):
    L.append('**Lần chạy chưa hoàn tất trong ngân sách — không có kết quả để báo cáo.** '
             'Trạng thái: `%s`.' % E.get('trang_thai', 'không rõ'))
else:
    arms = E['meta']['arms']
    subj = E['chu_the']
    L.append('Đã hoàn tất %d fold đủ cả ba nhánh (fold %s), n = **%d chủ thể** kiểm thử: %s.'
             % (len(E['fold_du_ca_ba_nhanh']), ', '.join(str(f) for f in E['fold_du_ca_ba_nhanh']),
                E['n_chu_the'], ', '.join(subj)))
    L.append('')
    L.append('| Chủ thể | ' + ' | '.join(NAME[a] for a in arms) + ' |')
    L.append('|---|' + '---|' * len(arms))
    for t in subj:
        L.append('| %s | ' % t + ' | '.join('%.2f' % E['F1_psd'][a][t] for a in arms) + ' |')
    L.append('| **Trung bình (F1 PSD)** | ' +
             ' | '.join('**%.2f**' % E['trung_binh_F1_psd'][a] for a in arms) + ' |')
    L.append('| Trung bình (F1 trung bình 4 kênh) | ' +
             ' | '.join('%.2f' % E['trung_binh_F1_mean4'][a] for a in arms) + ' |')
    L.append('')
    if 'tang_cuong_base_tru_noaug' in E:
        L.append('**Tăng cường (base − noaug), quy tắc PSD:** ' + ci(E['tang_cuong_base_tru_noaug']))
        L.append('')
        L.append('**Tăng cường (base − noaug), trung bình 4 kênh:** ' +
                 ci(E['tang_cuong_base_tru_noaug_mean4']))
        L.append('')
    if 'can_bang_bal_tru_base' in E:
        L.append('**Cân bằng theo số nhịp (bal − base), quy tắc PSD:** ' + ci(E['can_bang_bal_tru_base']))
        L.append('')
        L.append('**Cân bằng theo số nhịp (bal − base), trung bình 4 kênh:** ' +
                 ci(E['can_bang_bal_tru_base_mean4']))
        L.append('')
    bs = E.get('can_bang_da_ap_dung')
    if bs:
        L.append('Nhánh `bal` lấy mẫu lại chỉ số huấn luyện như sau (fold đầu tiên):')
        L.append('')
        L.append('| Nguồn | đoạn gốc | đoạn sau cân bằng | nhịp gốc | nhịp sau cân bằng | lấy lặp |')
        L.append('|---|---|---|---|---|---|')
        for g in sorted(bs):
            v = bs[g]
            L.append('| %s | %d | %d | %.0f | %.0f | %s |'
                     % (g, v['n_goc'], v['n_moi'], v['nhip_goc'], v['nhip_moi'],
                        'CÓ' if v['replace'] else 'không'))
        L.append('')

block = '\n'.join(L)
p = os.path.join(HERE, 'DULIEU.md')
s = open(p, encoding='utf-8').read()
A, B = '<!-- KET_QUA_M4_MINI -->', '<!-- HET_M4_MINI -->'
new = A + '\n\n' + block + '\n\n' + B
if A in s and B in s:
    s = s[:s.index(A)] + new + s[s.index(B) + len(B):]
elif A in s:
    s = s.replace(A, new)
else:
    raise SystemExit('khong tim thay moc ' + A)
open(p, 'w', encoding='utf-8').write(s)
print(block)
print('\n-> da chen vao', p)
