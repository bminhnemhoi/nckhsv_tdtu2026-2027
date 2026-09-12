# -*- coding: utf-8 -*-
"""Ve lai analysis/fig_thichnghi.png sau khi adapt_results.json da co khoa 'peakprob' (bang G)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adapt_analyze as AN

HERE = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(os.path.join(HERE, 'adapt_results.json'), encoding='utf-8'))
diag = json.load(open(os.path.join(HERE, 'diag_results.json'), encoding='utf-8'))
AN.make_fig(res, diag)
print('-> %s (%d bang, co bang G peakprob: %s)' % (AN.FIG, 7 if 'peakprob' in res else 6, 'peakprob' in res))
