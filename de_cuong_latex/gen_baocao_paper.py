# -*- coding: utf-8 -*-
"""Sinh bao cao 30 paper dang de doc: moi bai mot muc, khong phai bang chi chit."""
import os, sys, json, re, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.chdir(HERE)
S = json.load(open(os.path.join(ROOT, 'survey', 'survey_raw.json'), encoding='utf-8'))
P = {p['id']: p for p in S['papers']}

GROUP = [
    ('Học sâu dò QRS thai', ['p01', 'p09', 'p10', 'p12'],
     'Nhóm công trình dùng mạng nơ-ron để dò trực tiếp vị trí nhịp thai. Đây là họ gần nhất với '
     'mô hình của nhóm, nên cũng là nhóm đáng so nhất.'),
    ('Tách nguồn và tái tạo dạng sóng', ['p03', 'p04', 'p05', 'p06', 'p07', 'p11'],
     'Nhóm công trình đặt bài toán khác: thay vì dò vị trí nhịp, họ tái tạo lại toàn bộ dạng sóng '
     'điện tim thai rồi mới dò. Cách này cho thêm thông tin hình thái nhưng khó hơn và tốn hơn.'),
    ('Xử lý tín hiệu cổ điển', ['p16', 'p17', 'p19'],
     'Các phương pháp không dùng học máy. Quan trọng vì Power-MF năm 2024 cho thấy hướng cổ điển '
     'vẫn cạnh tranh được với học sâu.'),
    ('Đối chuẩn, bộ dữ liệu và thử thách', ['p13', 'p14', 'p15', 'p20', 'p21'],
     'Các công trình định nghĩa luật chơi của cả lĩnh vực: bộ dữ liệu nào, chấm điểm thế nào, '
     'dung sai bao nhiêu.'),
    ('Lý thuyết phân tích dữ liệu topo', ['p22', 'p23', 'p24', 'p25', 'p26'],
     'Nền tảng lý thuyết mà bản đề cương đầu tiên của nhóm dựa vào. Nhóm đọc kỹ nhóm này để hiểu '
     'vì sao giả thuyết ban đầu sai.'),
    ('Nhúng trễ và chọn tham số', ['p27', 'p28'],
     'Hai công trình về cách chọn tham số trễ. Quan trọng vì chúng đi trước phần đóng góp mà bản '
     'đề cương đầu tiên định nhận.'),
    ('Topo cho tín hiệu tim', ['p29', 'p30', 'p31', 'p32', 'p33'],
     'Các công trình đã áp dụng topo cho tín hiệu tim người lớn. Đây là chỗ nhóm tìm được tiền lệ '
     'cho đóng góp C3.'),
]

FIELDS = [
    ('ho_lam_gi', 'Họ làm gì'),
    ('phuong_phap', 'Phương pháp'),
    ('mo_hinh', 'Mô hình'),
    ('du_lieu', 'Dữ liệu'),
    ('giao_thuc_danh_gia', 'Giao thức đánh giá'),
    ('ket_qua_chinh', 'Kết quả chính'),
    ('diem_yeu', 'Điểm yếu'),
    ('so_voi_chung_ta', 'So với mô hình của nhóm'),
    ('bai_hoc_ap_dung', 'Nhóm rút ra gì'),
]
CMP = {'co': ('okgreen', 'so sánh trực tiếp được'),
       'mot phan': ('tdtblue', 'so được một phần'),
       'khong': ('warnred', 'không so trực tiếp được')}


def gon_cite(t):
    t = re.sub(r'\s*\(.*', '', str(t or '')).strip()
    return re.sub(r',?\s*(tiền ấn|bản tiền ấn|bài không nêu|không ghi).*', '', t, flags=re.I).strip(' ,')


def clip(t, n):
    t = re.sub(r'\s+', ' ', str(t or '')).strip()
    return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + ' ...'


def esc(t):
    t = str(t or '')
    for a, b in [('\\', '\\textbackslash{}'), ('&', '\\&'), ('%', '\\%'), ('$', '\\$'),
                 ('#', '\\#'), ('_', '\\_'), ('{', '\\{'), ('}', '\\}'),
                 ('~', '\\textasciitilde{}'), ('^', '\\textasciicircum{}')]:
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


L = [r'\documentclass[12pt,a4paper]{article}', r'\input{preamble.tex}',
     r'\fancyhead[L]{\footnotesize\color{tdtgray} Báo cáo đọc 30 công trình}',
     r'\begin{document}', r'\begin{titlepage}\centering\setstretch{1.0}',
     r'\vspace*{1.5cm}',
     r'{\large TRƯỜNG ĐẠI HỌC TÔN ĐỨC THẮNG}\\[1.6cm]',
     r'\rule{\textwidth}{0.8pt}\\[0.7cm]',
     r'{\LARGE\bfseries\color{tdtblue} Báo cáo đọc 30 công trình\\[6pt] về điện tim thai và phân tích '
     r'dữ liệu topo\par}\vspace{0.6cm}',
     r'\rule{\textwidth}{0.8pt}\\[1.2cm]',
     r'{\large Họ làm gì, bằng phương pháp nào,\\ và mô hình của nhóm đứng ở đâu so với họ\par}',
     r'\vspace{2.2cm}',
     r'\begin{tabular}{@{}r@{\hspace{1.2em}}l@{}}',
     r'\textbf{Thuộc đề tài} & RelyFetal --- Đề cương NCKH sinh viên 2026 \\[3pt]',
     r'\textbf{Người thực hiện} & Ngô Bình Minh \\[3pt]',
     r'\textbf{Số công trình} & 30, đọc toàn văn \\[3pt]',
     r'\textbf{Ngày} & 09/09/2026 \\', r'\end{tabular}', r'\vfill',
     r'\begin{ghichu}[title={Cách đọc báo cáo này}]\footnotesize\justifying',
     r'Mỗi công trình được trình bày theo chín mục giống nhau để dễ so sánh chéo. '
     r'Mục quan trọng nhất là \textbf{Giao thức đánh giá} --- đây là chỗ quyết định một con số '
     r'công bố có so sánh được với con số của nhóm hay không. Nhiều công trình có F1 rất cao nhưng '
     r'đạt được bằng cách chia dữ liệu ngẫu nhiên trong cùng một bệnh nhân, nới dung sai, gộp nhiều '
     r'kênh, hoặc tinh chỉnh trên chính tập đích. Những chỗ bài báo \textbf{không nêu} thông tin cũng '
     r'được ghi rõ, vì đó là dấu hiệu công trình không tái lập được.',
     r'\end{ghichu}', r'\end{titlepage}',
     r'\pagenumbering{roman}\tableofcontents\clearpage\pagenumbering{arabic}']

# ------------------------------------------------------- bang tom tat dau bao cao
L += [r'\section{Bảng tóm tắt: ai so được với nhóm}',
      r'Trong 30 công trình, chỉ một số ít có giao thức đối chiếu trực tiếp được. '
      r'Bảng này là bản đồ nhanh trước khi đi vào chi tiết từng bài.', '',
      r'\begin{longtable}{@{}L{1.0cm} L{3.6cm} L{6.6cm} C{3.2cm}@{}}',
      r'\toprule \textbf{Mã} & \textbf{Công trình} & \textbf{Kết quả công bố} & '
      r'\textbf{So với nhóm} \\ \midrule \endfirsthead',
      r'\toprule \textbf{Mã} & \textbf{Công trình} & \textbf{Kết quả công bố} & '
      r'\textbf{So với nhóm} \\ \midrule \endhead',
      r'\bottomrule \endlastfoot']
for g, ids, _ in GROUP:
    L.append(r'\multicolumn{4}{@{}l}{\cellcolor{rowbg}\textbf{%s}}\\[1pt]' % esc(g))
    for pid in ids:
        p = P.get(pid)
        if not p: continue
        col, lab = CMP.get(p['co_the_so_sanh_truc_tiep'], ('black', ''))
        L.append('%s & {\\scriptsize %s} & {\\scriptsize %s} & {\\scriptsize\\color{%s}\\textbf{%s}} \\\\[2pt]'
                 % (pid, esc(clip(gon_cite(p.get('trich_dan_ngan', '')), 46)),
                    esc(clip(p['ket_qua_chinh'], 200)), col, lab))
L += [r'\end{longtable}', r'\clearpage']

# ------------------------------------------------------- tung bai
for g, ids, mota in GROUP:
    L += [r'\section{%s}' % esc(g), esc(mota), '']
    for pid in ids:
        p = P.get(pid)
        if not p: continue
        col, lab = CMP.get(p['co_the_so_sanh_truc_tiep'], ('black', ''))
        L += [r'\subsection{%s \normalfont\small (%s)}' % (esc(gon_cite(p.get('trich_dan_ngan', pid)) or pid), pid),
              r'\noindent{\footnotesize\itshape %s}\par\vspace{2pt}' % esc(clip(p['trich_dan'], 400)),
              r'\noindent{\small\color{%s}\textbf{Kết luận: %s}}\par\vspace{4pt}' % (col, lab)]
        for key, ten in FIELDS:
            hl = r'\textbf{%s.} ' % ten
            if key in ('so_voi_chung_ta', 'bai_hoc_ap_dung'):
                hl = r'\textbf{\color{tdtblue}%s.} ' % ten
            L.append(r'\noindent %s%s\par\vspace{3pt}' % (hl, esc(p[key])))
        L.append(r'\vspace{6pt}')
    L.append(r'\clearpage')

L.append(r'\end{document}')
open('bao_cao_30_paper.tex', 'w', encoding='utf-8').write('\n'.join(L))
print('da tao bao_cao_30_paper.tex')

for i in range(3):
    subprocess.run(['xelatex', '-interaction=nonstopmode', 'bao_cao_30_paper.tex'],
                   capture_output=True)
log = open('bao_cao_30_paper.log', encoding='utf-8', errors='replace').read()
print('loi LaTeX:', log.count('\n! '))
if os.path.exists('bao_cao_30_paper.pdf'):
    import pymupdf
    print('PDF: %d trang, %.2f MB' % (pymupdf.open('bao_cao_30_paper.pdf').page_count,
                                      os.path.getsize('bao_cao_30_paper.pdf') / 1e6))
