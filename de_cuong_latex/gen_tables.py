# -*- coding: utf-8 -*-
"""Sinh cac bang LaTeX tu du lieu khao sat 30 paper (khong go tay -> khong sai so)."""
import os, sys, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'tables'); os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(ROOT, 'survey', 'survey_raw.json'), encoding='utf-8'))
PAPERS = {p['id']: p for p in S['papers']}


def esc(t):
    if t is None: return ''
    t = str(t)
    for a, b in [('\\', '\\textbackslash{}'), ('&', '\\&'), ('%', '\\%'), ('$', '\\$'),
                 ('#', '\\#'), ('_', '\\_'), ('{', '\\{'), ('}', '\\}'), ('~', '\\textasciitilde{}'),
                 ('^', '\\textasciicircum{}')]:
        t = t.replace(a, b)
    return t


def clip(t, n):
    t = re.sub(r'\s+', ' ', str(t)).strip()
    return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + '…'


def short_cite(p):
    """rut gon trich dan thanh 'Tac gia nam'"""
    c = p['trich_dan']
    m = re.search(r'\b(19|20)\d{2}\b', c)
    year = m.group(0) if m else ''
    first = re.split(r'[,;.]', c)[0].strip()
    parts = first.replace('"', '').split()
    sur = parts[0] if parts else first
    if len(sur) <= 2 and len(parts) > 1: sur = parts[1]
    return f'{sur} {year}'.strip()


# ---------------------------------------------------------------- bang 1: tong quan 30 bai
GROUP = {
    'Học sâu dò fQRS': ['p01', 'p09', 'p10', 'p12'],
    'Tách nguồn / tái tạo dạng sóng': ['p03', 'p04', 'p05', 'p06', 'p07', 'p11'],
    'Xử lý tín hiệu cổ điển': ['p16', 'p17', 'p19'],
    'Đối chuẩn, dữ liệu, thử thách': ['p13', 'p14', 'p15', 'p20', 'p21'],
    'Lý thuyết TDA': ['p22', 'p23', 'p24', 'p25', 'p26'],
    'Nhúng trễ và chọn tham số': ['p27', 'p28'],
    'TDA cho tín hiệu tim': ['p29', 'p30', 'p31', 'p32', 'p33'],
}
CMP = {'co': '\\tot{có}', 'mot phan': 'một phần', 'khong': '\\xau{không}'}


def bang_tong_quan():
    L = ['\\begin{longtable}{@{}L{1.05cm} L{3.25cm} L{3.9cm} L{4.5cm} C{1.35cm}@{}}',
         '\\caption{Ba mươi công trình nhóm đã đọc toàn văn, xếp theo họ phương pháp. '
         'Cột cuối cho biết giao thức đánh giá của bài đó có đối chiếu trực tiếp được với '
         'giao thức của nhóm hay không.}\\label{tab:tongquan}\\\\',
         '\\toprule',
         '\\textbf{Mã} & \\textbf{Công trình} & \\textbf{Mô hình} & \\textbf{Kết quả và giao thức} & '
         '\\textbf{So được?} \\\\',
         '\\midrule\\endfirsthead',
         '\\multicolumn{5}{@{}l}{\\footnotesize\\itshape Bảng \\thetable{} (tiếp theo)}\\\\',
         '\\toprule',
         '\\textbf{Mã} & \\textbf{Công trình} & \\textbf{Mô hình} & \\textbf{Kết quả và giao thức} & '
         '\\textbf{So được?} \\\\',
         '\\midrule\\endhead',
         '\\midrule\\multicolumn{5}{r@{}}{\\footnotesize\\itshape tiếp trang sau}\\\\\\endfoot',
         '\\bottomrule\\endlastfoot']
    for g, ids in GROUP.items():
        L.append(f'\\multicolumn{{5}}{{@{{}}l}}{{\\cellcolor{{rowbg}}\\textbf{{{esc(g)}}}}}\\\\[1pt]')
        for pid in ids:
            p = PAPERS.get(pid)
            if not p: continue
            kq = clip(p['ket_qua_chinh'], 230)
            gt = clip(p['giao_thuc_danh_gia'], 150)
            L.append(f'{esc(pid)} & {esc(clip(short_cite(p), 40))}\\newline'
                     f'{{\\scriptsize {esc(clip(p["ho_lam_gi"], 120))}}} & '
                     f'{{\\scriptsize {esc(clip(p["mo_hinh"], 210))}}} & '
                     f'{{\\scriptsize {esc(kq)}}}\\newline{{\\scriptsize\\itshape {esc(gt)}}} & '
                     f'{CMP.get(p["co_the_so_sanh_truc_tiep"], "")} \\\\[2pt]')
    L.append('\\end{longtable}')
    open(os.path.join(OUT, 'bang_tongquan.tex'), 'w', encoding='utf-8').write('\n'.join(L))
    print('  -> bang_tongquan.tex')


# ---------------------------------------------------------------- bang 2: bai hoc rut ra
def bang_bai_hoc():
    L = ['\\begin{longtable}{@{}L{1.05cm} L{6.0cm} L{7.2cm}@{}}',
         '\\caption{Điều nhóm rút ra được từ từng công trình và điều đó đổi gì trong thiết kế '
         'của nhóm.}\\label{tab:baihoc}\\\\',
         '\\toprule \\textbf{Mã} & \\textbf{So với mô hình của nhóm} & \\textbf{Bài học áp dụng} \\\\',
         '\\midrule\\endfirsthead',
         '\\multicolumn{3}{@{}l}{\\footnotesize\\itshape Bảng \\thetable{} (tiếp theo)}\\\\',
         '\\toprule \\textbf{Mã} & \\textbf{So với mô hình của nhóm} & \\textbf{Bài học áp dụng} \\\\',
         '\\midrule\\endhead',
         '\\midrule\\multicolumn{3}{r@{}}{\\footnotesize\\itshape tiếp trang sau}\\\\\\endfoot',
         '\\bottomrule\\endlastfoot']
    for g, ids in GROUP.items():
        L.append(f'\\multicolumn{{3}}{{@{{}}l}}{{\\cellcolor{{rowbg}}\\textbf{{{esc(g)}}}}}\\\\[1pt]')
        for pid in ids:
            p = PAPERS.get(pid)
            if not p: continue
            L.append(f'{esc(pid)} & {{\\scriptsize {esc(clip(p["so_voi_chung_ta"], 430))}}} & '
                     f'{{\\scriptsize {esc(clip(p["bai_hoc_ap_dung"], 430))}}} \\\\[2pt]')
    L.append('\\end{longtable}')
    open(os.path.join(OUT, 'bang_baihoc.tex'), 'w', encoding='utf-8').write('\n'.join(L))
    print('  -> bang_baihoc.tex')


# ---------------------------------------------------------------- bang 3: diem yeu
def bang_diem_yeu():
    L = ['\\begin{longtable}{@{}L{1.05cm} L{3.2cm} L{10.1cm}@{}}',
         '\\caption{Điểm yếu phương pháp luận nhóm phát hiện khi đọc toàn văn. Đây là cơ sở '
         'để nhóm khẳng định các con số công bố trong y văn không so sánh trực tiếp được với '
         'nhau.}\\label{tab:diemyeu}\\\\',
         '\\toprule \\textbf{Mã} & \\textbf{Công trình} & \\textbf{Hạn chế} \\\\',
         '\\midrule\\endfirsthead',
         '\\multicolumn{3}{@{}l}{\\footnotesize\\itshape Bảng \\thetable{} (tiếp theo)}\\\\',
         '\\toprule \\textbf{Mã} & \\textbf{Công trình} & \\textbf{Hạn chế} \\\\',
         '\\midrule\\endhead',
         '\\midrule\\multicolumn{3}{r@{}}{\\footnotesize\\itshape tiếp trang sau}\\\\\\endfoot',
         '\\bottomrule\\endlastfoot']
    for pid, p in sorted(PAPERS.items()):
        L.append(f'{esc(pid)} & {{\\scriptsize {esc(clip(short_cite(p), 38))}}} & '
                 f'{{\\scriptsize {esc(clip(p["diem_yeu"], 560))}}} \\\\[2pt]')
    L.append('\\end{longtable}')
    open(os.path.join(OUT, 'bang_diemyeu.tex'), 'w', encoding='utf-8').write('\n'.join(L))
    print('  -> bang_diemyeu.tex')


# ---------------------------------------------------------------- danh muc tham khao
def danh_muc():
    L = ['\\begin{enumerate}[leftmargin=1.6em,itemsep=2pt,label={[\\arabic*]}]']
    for pid, p in sorted(PAPERS.items()):
        L.append(f'\\item {{\\small {esc(clip(p["trich_dan"], 340))}}} '
                 f'\\hfill{{\\scriptsize\\itshape ({esc(pid)})}}')
    L.append('\\end{enumerate}')
    open(os.path.join(OUT, 'danhmuc.tex'), 'w', encoding='utf-8').write('\n'.join(L))
    print('  -> danhmuc.tex')


if __name__ == '__main__':
    print('Sinh bang LaTeX:')
    bang_tong_quan(); bang_bai_hoc(); bang_diem_yeu(); danh_muc()
    print(f'XONG -- {len(PAPERS)} cong trinh')
