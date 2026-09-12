# -*- coding: utf-8 -*-
"""
KIEM TRA RO RI NHAN -- chay duoc, khong phai loi hua suong.

Ba kiem tra tu dong:
 1. Khong ham thich nghi nao (A.m_*, preprocess_adaptive, leads_notch, simulate_windows tren
    duong CinC) nhan doi so ten `gt` / `label` / `ann` / `fqrs`.
 2. Trong adapt_run.py, nhan `gt` chi chay vao cac vo boc CHAM DIEM (eval_record, eval_adapted,
    run_methods) va ket thuc o A.score(...); khong bao gio vao ham thich nghi (m_*, fit).
 3. hp_selected.json khong chua ban ghi nao cua CinC (ten bat dau bang 'a' + 2 chu so).

Chay: python adapt/check_no_leak.py    (ma thoat 0 = dat)
"""
import os, sys, ast, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
BAD_ARG = ('gt', 'label', 'labels', 'ann', 'fqrs', 'y_true')
fails = []

# ---- 1 + 2
for fn in ('adapt_common.py', 'adapt_run.py'):
    src = open(os.path.join(HERE, fn), encoding='utf-8').read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            is_adapt = node.name.startswith('m_') or node.name in (
                'preprocess_adaptive', 'leads_notch', 'mains_present', '_quantize', '_inject_mains')
            if is_adapt and any(a in BAD_ARG for a in args):
                fails.append('%s::%s nhan doi so nhan: %s' % (fn, node.name, args))

src = open(os.path.join(HERE, 'adapt_run.py'), encoding='utf-8').read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        names = [a.id for a in node.args if isinstance(a, ast.Name)]
        if 'gt' in names or 'wgt' in names:
            f = node.func
            tgt = (f.attr if isinstance(f, ast.Attribute) else getattr(f, 'id', '?'))
            OK = ('score', 'simulate_windows', 'len', 'asarray', 'int', 'array', 'mean',
                  'eval_record', 'eval_adapted', 'run_methods')   # vo boc CHAM DIEM, deu ket thuc o score()
            if tgt not in OK:
                fails.append('adapt_run.py dong %d: nhan duoc truyen vao %s()' % (node.lineno, tgt))
            if tgt.startswith('m_') or tgt == 'fit':
                fails.append('adapt_run.py dong %d: nhan duoc truyen vao ham THICH NGHI %s()'
                             % (node.lineno, tgt))

# ---- 3
p = os.path.join(HERE, 'hp_selected.json')
if os.path.isfile(p):
    txt = open(p, encoding='utf-8').read()
    hits = sorted(set(re.findall(r'"(a\d{2})"', txt)))
    if hits:
        fails.append('hp_selected.json co ten ban ghi CinC: %s' % hits)
else:
    fails.append('chua co hp_selected.json')

if fails:
    print('KHONG DAT:')
    for f in fails:
        print('  -', f)
    sys.exit(1)
print('DAT: khong phat hien duong ro ri nhan mien dich trong adapt/.')
