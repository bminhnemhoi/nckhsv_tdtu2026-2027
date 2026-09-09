# -*- coding: utf-8 -*-
"""
Xuat de cuong sang Word (.docx).

Pandoc khong theo \\input va khong hieu tcolorbox / cac lenh tat rieng, nen script nay:
  1. Gop cac tep .tex thanh mot tep phang
  2. Thay cac lenh tat rieng bang LaTeX chuan
  3. Doi hop tcolorbox thanh quote co tieu de in dam
  4. Doi duong dan hinh tu .pdf sang .png (Word khong nhung duoc PDF)
  5. Goi pandoc
"""
import os, re, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)


def doc(path):
    return open(path, encoding='utf-8').read()


# ---------------------------------------------------------------- 1. gop tep
main = doc('de_cuong.tex')
for f in ['sec_1_3.tex', 'sec_4_6.tex', 'sec_7_12.tex']:
    main = main.replace('\\input{%s}' % f, doc(f))
for f in ['bang_tongquan', 'bang_baihoc', 'bang_diemyeu', 'danhmuc']:
    main = main.replace('\\input{tables/%s.tex}' % f, doc('tables/%s.tex' % f))
main = main.replace('\\input{preamble.tex}', '')

# ---------------------------------------------------------------- 2. lenh tat
SUB = [
    (r'\\tot\{', r'\\textbf{'),
    (r'\\xau\{', r'\\textbf{'),
    (r'\\mh\{\}', 'FetalQRS-TCN'),
    (r'\\hethong\{\}', 'RelyFetal'),
    (r'\\mh\b', 'FetalQRS-TCN'),
    (r'\\hethong\b', 'RelyFetal'),
    (r'\\textsc\{([^}]*)\}', r'\1'),
    (r'\\S\\ref', 'mục \\\\ref'),
    (r'\\clearpage', ''),
    (r'\\vfill', ''),
    (r'\\justifying', ''),
    (r'\\setstretch\{[^}]*\}', ''),
    (r'\\cellcolor\{rowbg\}', ''),
    (r'\\rule\{\\textwidth\}\{0\.8pt\}', ''),
    (r'\\newline', r'\\\\ '),
    (r'\\addcontentsline\{[^}]*\}\{[^}]*\}\{[^}]*\}', ''),
]
for a, b in SUB:
    main = re.sub(a, b, main)

# hinh: pdf -> png
main = re.sub(r'(figs/[A-Za-z0-9_]+)\.pdf', r'\1.png', main)

# ---------------------------------------------------------------- 2b. kieu cot tu dinh nghia
# pandoc khong biet L{..} C{..} R{..} nen bo qua ca bang -> doi ve p{..}
main = re.sub(r'\bL\{([0-9.]+cm)\}', r'p{\1}', main)
main = re.sub(r'\bC\{([0-9.]+cm)\}', r'p{\1}', main)
main = re.sub(r'\bR\{([0-9.]+cm)\}', r'p{\1}', main)
main = main.replace('@{}', '')

# longtable nhieu dau bang lam pandoc roi -> giu mot dau bang duy nhat
def gon_longtable(m):
    body = m.group(1)
    # bo phan lap lai giua \endfirsthead va \endhead, va cac chan trang
    body = re.sub(r'\\endfirsthead.*?\\endhead', r'\\\\', body, flags=re.S)
    body = re.sub(r'\\midrule\\multicolumn.*?\\endfoot', '', body, flags=re.S)
    body = body.replace('\\bottomrule\\endlastfoot', '')
    body = body.replace('\\endfirsthead', '').replace('\\endhead', '')
    body = body.replace('\\endfoot', '').replace('\\endlastfoot', '')
    return '\\begin{longtable}' + body + '\\end{longtable}'


main = re.sub(r'\\begin\{longtable\}(.*?)\\end\{longtable\}', gon_longtable, main, flags=re.S)

# ---------------------------------------------------------------- 3. hop tcolorbox -> quote
def box(m):
    kind, title, body = m.group(1), m.group(2) or '', m.group(3)
    tag = 'Lưu ý' if kind == 'ghichu' else 'Cảnh báo'
    head = f'\\textbf{{[{tag}] {title}}}\n\n' if title else f'\\textbf{{[{tag}]}}\n\n'
    return '\\begin{quote}\n' + head + body + '\n\\end{quote}'


main = re.sub(r'\\begin\{(ghichu|canhbao)\}(?:\[title=\{(.*?)\}\])?(.*?)\\end\{\1\}',
              box, main, flags=re.S)

# ---------------------------------------------------------------- 4. don dep con lai
main = main.replace('\\listoftables', '').replace('\\listoffigures', '')
main = main.replace('\\pagenumbering{roman}', '').replace('\\pagenumbering{arabic}', '')
main = re.sub(r'\\begin\{titlepage\}', r'\\begin{center}', main)
main = re.sub(r'\\end\{titlepage\}', r'\\end{center}', main)
main = re.sub(r'\\vspace\*?\{[^}]*\}', '', main)
main = re.sub(r'\\makecell\[l\]\{(.*?)\}', r'\1', main, flags=re.S)

open('_flat.tex', 'w', encoding='utf-8').write(main)
print('da gop -> _flat.tex (%d ky tu)' % len(main))

# ---------------------------------------------------------------- 5. pandoc
cmd = ['pandoc', '_flat.tex', '-f', 'latex', '-t', 'docx',
       '-o', 'De_cuong_NCKH_RelyFetal.docx',
       '--toc', '--toc-depth=2', '--number-sections',
       '--resource-path=.:figs']
if os.path.exists('reference.docx'):
    cmd.append('--reference-doc=reference.docx')
r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
print('pandoc ma thoat:', r.returncode)
if r.stderr.strip():
    print('canh bao pandoc:'); print(r.stderr[:2500])
if os.path.exists('De_cuong_NCKH_RelyFetal.docx'):
    print('DA TAO De_cuong_NCKH_RelyFetal.docx (%.2f MB)'
          % (os.path.getsize('De_cuong_NCKH_RelyFetal.docx') / 1e6))
