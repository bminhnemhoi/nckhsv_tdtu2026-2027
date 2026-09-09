# -*- coding: utf-8 -*-
"""Xuat bao cao 30 paper sang Word."""
import os, re, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

s = open('bao_cao_30_paper.tex', encoding='utf-8').read()
s = s.replace(r'\input{preamble.tex}', '')
s = re.sub(r'\\fancyhead\[L\]\{[^}]*\}', '', s)

# kieu cot tu dinh nghia -> p{}
s = re.sub(r'\bL\{([0-9.]+cm)\}', r'p{\1}', s)
s = re.sub(r'\bC\{([0-9.]+cm)\}', r'p{\1}', s)
s = s.replace('@{}', '')

# hop ghi chu -> quote
def box(m):
    return ('\\begin{quote}\n\\textbf{[Lưu ý] ' + (m.group(1) or '') + '}\n\n'
            + m.group(2) + '\n\\end{quote}')


s = re.sub(r'\\begin\{ghichu\}(?:\[title=\{(.*?)\}\])?(.*?)\\end\{ghichu\}', box, s, flags=re.S)

# longtable: giu mot dau bang
def lt(m):
    b = re.sub(r'\\endfirsthead.*?\\endhead', r'\\\\', m.group(1), flags=re.S)
    for x in ('\\endfirsthead', '\\endhead', '\\endfoot', '\\endlastfoot'):
        b = b.replace(x, '')
    return '\\begin{longtable}' + b + '\\end{longtable}'


s = re.sub(r'\\begin\{longtable\}(.*?)\\end\{longtable\}', lt, s, flags=re.S)

s = s.replace(r'\begin{titlepage}', r'\begin{center}').replace(r'\end{titlepage}', r'\end{center}')
for pat in [r'\\vspace\*?\{[^}]*\}', r'\\setstretch\{[^}]*\}', r'\\rule\{\\textwidth\}\{[^}]*\}']:
    s = re.sub(pat, '', s)
for tok in [r'\clearpage', r'\vfill', r'\justifying', r'\cellcolor{rowbg}',
            r'\pagenumbering{roman}', r'\pagenumbering{arabic}']:
    s = s.replace(tok, '')

open('_bc_flat.tex', 'w', encoding='utf-8').write(s)
r = subprocess.run(['pandoc', '_bc_flat.tex', '-f', 'latex', '-t', 'docx',
                    '-o', 'Bao_cao_30_paper.docx', '--toc', '--toc-depth=2', '--number-sections'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('pandoc ma thoat:', r.returncode)
if r.stderr.strip():
    print(r.stderr[:800])
if os.path.exists('Bao_cao_30_paper.docx'):
    print('DA TAO Bao_cao_30_paper.docx (%.2f MB)' % (os.path.getsize('Bao_cao_30_paper.docx') / 1e6))
os.remove('_bc_flat.tex')
