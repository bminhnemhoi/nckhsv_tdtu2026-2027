# -*- coding: utf-8 -*-
"""
Smoke tests that do not require the physiological recordings.

They pin the numbers that the README and the proposal quote, so that a refactor
which silently changes the model cannot pass CI.
"""
import os
import importlib.util

import numpy as np
import pytest
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CKPT_DIR = os.path.join(ROOT, 'model', 'checkpoints')

_spec = importlib.util.spec_from_file_location(
    'fqrs', os.path.join(ROOT, 'model', 'fqrs_model.py'))
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)


# ------------------------------------------------------------------ model
def test_parameter_count_is_pinned():
    """113,481 is quoted in the README, the proposal and the paper draft."""
    assert M.n_params(M.FetalQRSTCN()) == 113_481


def test_receptive_field_is_1516_ms():
    net = M.FetalQRSTCN()
    assert net.receptive_field == 379
    assert net.receptive_field * 1000 // M.CFG['fs'] == 1516


def test_forward_is_sequence_to_sequence():
    """One logit per input sample -- this is what buys the 1.0 ms jitter."""
    net = M.FetalQRSTCN().eval()
    x = torch.randn(2, 2, M.CFG['seg'])
    with torch.no_grad():
        y = net(x)
    assert y.shape == (2, M.CFG['seg'])
    assert torch.isfinite(y).all()


def test_config_constants_match_the_evidence():
    """Every one of these was selected by an experiment; see pilot_evidence/."""
    assert M.CFG['band'] == (10.0, 60.0)          # 8-band ablation
    assert M.CFG['fs'] == 250                     # Behar 2014 / Chen 2025 convention
    assert M.CFG['seg'] / M.CFG['fs'] == 4.0      # 4 s context
    assert M.CFG['dilations'] == (1, 2, 4, 8, 16)  # receptive-field sweep
    assert M.CFG['tolerance_ms'] == 50            # CinC 2013 convention


# ------------------------------------------------------------------ checkpoints
FOLDS = ['r01', 'r04', 'r07', 'r08', 'r10']


@pytest.mark.skipif(not os.path.isdir(CKPT_DIR), reason='checkpoints not present')
@pytest.mark.parametrize('rec', FOLDS)
def test_fold_checkpoint_loads_and_is_leakage_free(rec):
    blob = torch.load(os.path.join(CKPT_DIR, f'fetalqrs_tcn_fold_{rec}.pt'),
                      map_location='cpu', weights_only=False)
    net = M.FetalQRSTCN()
    net.load_state_dict(blob['state_dict'])            # raises if shapes drifted

    assert blob['test_record'] == rec
    # the record under test must appear in neither the training nor the validation split
    assert rec not in blob['train_records']
    assert rec != blob['val_record']
    assert 0.0 < blob['threshold'] < 1.0


@pytest.mark.skipif(not os.path.isdir(CKPT_DIR), reason='checkpoints not present')
def test_production_checkpoint_declares_it_has_no_held_out_score():
    blob = torch.load(os.path.join(CKPT_DIR, 'fetalqrs_tcn_production.pt'),
                      map_location='cpu', weights_only=False)
    assert sorted(blob['trained_on']) == sorted(FOLDS)
    assert 'No held-out score exists' in blob['note']
    assert 'expected_performance' in blob


# ------------------------------------------------------------------ evaluation
def test_event_matching_is_one_to_one():
    """Two detections must never be credited to the same reference beat."""
    fs = M.CFG['fs']
    ref = np.array([100, 200, 300])
    det = np.array([100, 101, 200, 300])          # 101 is a duplicate of 100
    m = M.match_events(det, ref, fs, tolerance_ms=50)
    assert m['TP'] == 3 and m['FP'] == 1 and m['FN'] == 0


def test_perfect_detection_scores_100():
    fs = M.CFG['fs']
    ref = np.arange(100, 2000, 100)
    m = M.match_events(ref.copy(), ref, fs, tolerance_ms=50)
    assert m['F1'] == pytest.approx(100.0)
    assert m['FP'] == 0 and m['FN'] == 0


def test_tolerance_boundary_is_respected():
    fs = M.CFG['fs']                               # 250 Hz -> 50 ms = 12.5 samples
    ref = np.array([1000])
    assert M.match_events(np.array([1012]), ref, fs, 50)['TP'] == 1
    assert M.match_events(np.array([1020]), ref, fs, 50)['TP'] == 0


# ------------------------------------------------------------------ signal front end
def test_preprocess_resamples_to_250_hz():
    x = np.random.randn(4000)                      # 4 s at 1000 Hz
    y = M.preprocess(x, fs_in=1000, cfg=M.CFG)
    assert abs(len(y) - 1000) <= 1
    assert np.isfinite(y).all()


def test_maternal_cancellation_reduces_energy():
    """A synthetic 'maternal' train must lose energy after template subtraction."""
    fs = M.CFG['fs']
    n = fs * 20
    t = np.arange(n) / fs
    x = np.zeros(n)
    for beat in range(0, n, int(0.8 * fs)):        # 75 bpm maternal rhythm
        idx = np.arange(max(0, beat - 10), min(n, beat + 10))
        x[idx] += 10 * np.exp(-0.5 * ((idx - beat) / 3.0) ** 2)
    x += 0.05 * np.random.randn(n)

    res, _ = M.cancel_maternal(x, M.CFG)
    assert len(res) == len(x)
    assert np.std(res) < np.std(x)


def test_heatmap_peaks_at_annotated_beats():
    hm = M.make_heatmap(1000, np.array([100, 500, 900]))
    assert hm.shape == (1000,)
    assert hm.max() == pytest.approx(1.0, abs=1e-6)
    for p in (100, 500, 900):
        assert hm[p] == pytest.approx(1.0, abs=1e-6)
    assert hm[300] < 0.01
