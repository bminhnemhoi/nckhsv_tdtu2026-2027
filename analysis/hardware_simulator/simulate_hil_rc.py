"""Transient check of the proposed DAC -> divider/RC -> ADC wiring."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "analysis/hardware_simulator/patient_sim_data.h"
FS = 250
VREF = 3.3
SUPPLY_TOLERANCE = 0.05
R1_OHM = 10_000
R2_OHM = 39_000
C1_FARAD = 100e-9


def read_records() -> dict[str, np.ndarray]:
    source = HEADER.read_text(encoding="utf-8")
    records: dict[str, np.ndarray] = {}
    for name in ("R01", "A02"):
        match = re.search(
            rf"ECG_RECORD_{name}\[\d+\]\s*=\s*\{{(.*?)\}}", source, re.DOTALL
        )
        if match is None:
            raise ValueError(f"Missing ECG_RECORD_{name} in {HEADER}")
        values = np.array(
            [int(item) for item in re.findall(r"\d+", match.group(1))], dtype=float
        )
        records[name] = values
    return records


def simulate(
    r1: float, r2: float, c: float, phase: float, values: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return ideal divider samples and RC-node samples at receiver sample times."""
    gain = r2 / (r1 + r2)
    tau = (r1 * r2 / (r1 + r2)) * c
    dt = 1e-5
    steps_per_sample = round((1 / FS) / dt)
    phase_steps = round(phase / dt)
    phase_steps %= steps_per_sample
    target = gain * VREF * values / 255
    node = float(target[0])
    samples = []
    for index, level in enumerate(target):
        for step in range(steps_per_sample):
            node = level + (node - level) * np.exp(-dt / tau)
            if step == phase_steps:
                samples.append(node)
    ideal = target[: len(samples)]
    return ideal, np.asarray(samples)


def moving_average(values: np.ndarray, window: int = 5) -> np.ndarray:
    return np.convolve(values, np.ones(window) / window, mode="same")


def main() -> None:
    records = read_records()
    ratio = R2_OHM / (R1_OHM + R2_OHM)
    tau = (R1_OHM * R2_OHM / (R1_OHM + R2_OHM)) * C1_FARAD
    cutoff = 1 / (2 * np.pi * tau)
    print(f"Nominal divider ratio: {ratio:.6f}")
    print(f"Nominal RC tau: {tau * 1e3:.3f} ms; cutoff: {cutoff:.1f} Hz")
    print(f"Ideal DAC max 3.3 V -> ADC node: {VREF * ratio:.3f} V")
    corner_max = (
        VREF
        * (1 + SUPPLY_TOLERANCE)
        * (R2_OHM * 1.05)
        / (R1_OHM * 0.95 + R2_OHM * 1.05)
    )
    print(f"Rev B: R1={R1_OHM} ohm, R2={R2_OHM} ohm, C1={C1_FARAD:g} F")
    print(f"Worst-case high node (R ±5%, DAC rail +5%): {corner_max:.3f} V")
    print(
        "ADC codes below are ideal 3.3 V/12-bit proxies, not calibrated S3 ADC predictions."
    )
    for name, values in records.items():
        print(
            f"{name}: {len(values)} samples; DAC code {values.min():.0f}..{values.max():.0f}; mean {values.mean():.2f}"
        )
        for phase_ms in (0.1, 1.0, 2.0, 3.9):
            ideal, actual = simulate(R1_OHM, R2_OHM, C1_FARAD, phase_ms / 1000, values)
            adc = np.rint(actual / 3.3 * 4095).astype(int)
            moving = moving_average(adc)
            corr = float(np.corrcoef(ideal[4:-4], actual[4:-4])[0, 1])
            rmse_lsb = float(
                np.sqrt(np.mean((adc[4:-4] - np.rint(ideal[4:-4] / 3.3 * 4095)) ** 2))
            )
            print(
                f"  phase={phase_ms:.1f}ms: node={actual.min():.3f}..{actual.max():.3f}V, "
                f"ADC={adc.min()}..{adc.max()}, corr={corr:.4f}, analog RC RMSE={rmse_lsb:.1f} ADC LSB, "
                f"5-sample mean={moving.mean():.1f}"
            )


if __name__ == "__main__":
    main()
