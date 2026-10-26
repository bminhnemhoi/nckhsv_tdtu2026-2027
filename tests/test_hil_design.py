"""Offline electrical bounds and connectivity checks, not hardware validation."""

from __future__ import annotations

import csv
import itertools
import json
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/hil_revC"
DESIGN = json.loads((FOLDER / "RF-HIL-001_RevC_netlist.json").read_text())


def test_connections_cover_all_populated_component_pins() -> None:
    """Each wired endpoint must occur once, on the component's declared net."""
    endpoints: dict[str, str] = {}
    for net, members in DESIGN["nets"].items():
        for member in members:
            assert member not in endpoints, f"Endpoint shorts two nets: {member}"
            endpoints[member] = net
            ref, pin = member.split(":")
            assert DESIGN["components"][ref]["pins"][pin] == net
    expected = {
        f"{ref}:{pin}": net
        for ref, component in DESIGN["components"].items()
        for pin, net in component["pins"].items()
    }
    assert endpoints == expected
    with (FOLDER / "RF-HIL-001_RevC_connections.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        wires = list(csv.DictReader(stream))
    # USB ports and probe attachment points are represented separately.
    required = {
        name
        for name in endpoints
        if not name.startswith(("TP", "USB")) and not name.endswith("USB_VBUS")
    }
    touched: set[str] = set()
    for wire in wires:
        assert wire["population"] == "required"
        for side in ("from", "to"):
            endpoint = wire[f"{side}_label"]
            assert endpoints[endpoint] == wire["net"]
            ref, pin = endpoint.split(":")
            header = DESIGN["components"][ref].get("header_map", {}).get(pin, pin)
            assert wire[f"{side}_header"] == header
            touched.add(endpoint)
    assert required <= touched
    # A list of endpoints alone would miss a disconnected branch in the CSV.
    for net, members in DESIGN["nets"].items():
        terminals = required.intersection(members)
        if not terminals:
            continue
        visited = {next(iter(terminals))}
        while True:
            previous = visited.copy()
            for wire in wires:
                pair = {wire["from_label"], wire["to_label"]}
                if wire["net"] == net and pair & visited:
                    visited |= pair
            if visited == previous:
                break
        assert terminals <= visited, f"Disconnected net: {net}"


@pytest.mark.parametrize(
    "r1_tol,r2_tol,rail_tol", list(itertools.product((-0.05, 0.05), repeat=3))
)
def test_adc_voltage_at_all_tolerance_corners(
    r1_tol: float, r2_tol: float, rail_tol: float
) -> None:
    """Test independent resistor/rail corners, including the high-voltage one."""
    r1 = DESIGN["components"]["R1"]["value"] * (1 + r1_tol)
    r2 = DESIGN["components"]["R2"]["value"] * (1 + r2_tol)
    peak = 3.3 * (1 + rail_tol) * r2 / (r1 + r2)
    assert 0 < peak < DESIGN["limits"]["adc_measurement_acceptance_max"]
    # The old 56k variant fails the conservative calibrated-range constraint.
    old_high = 3.465 * (56_000 * 1.05) / (10_000 * 0.95 + 56_000 * 1.05)
    assert old_high > DESIGN["limits"]["adc_guideline_calibrated_upper"]


def test_filter_and_display_limits_expose_original_plan_problems() -> None:
    r1 = DESIGN["components"]["R1"]["value"]
    r2 = DESIGN["components"]["R2"]["value"]
    capacitance = DESIGN["components"]["C1"]["value"]
    tau = r1 * r2 / (r1 + r2) * capacitance
    assert 1 / (2 * math.pi * tau) == pytest.approx(199.964, abs=0.001)
    attenuation_125 = -10 * math.log10(1 + (2 * math.pi * 125 * tau) ** 2)
    assert attenuation_125 > -2  # weak anti-alias rejection at 250 Hz acquisition
    assert 128 * 64 / 8 * 9 / 100_000 > 0.09  # exceeds a 4 ms sample period
    # Five-point moving average at 250 Hz has a zero at 50 Hz.
    response = (
        sum(
            complex(math.cos(n * 2 * math.pi / 5), math.sin(n * 2 * math.pi / 5))
            for n in range(5)
        )
        / 5
    )
    assert abs(response) < 1e-12


def test_power_and_physical_pin_constraints() -> None:
    assert set(DESIGN["nets"]["USB5_A1"]).isdisjoint(DESIGN["nets"]["USB5_A2"])
    assert "A1:3V3" not in DESIGN["nets"]["3V3_A2"]
    assert {"A1:GND", "A2:GND", "A3:GND"} <= set(DESIGN["nets"]["GND"])
    expected = {
        "A1": {"GPIO25": "J2.9", "GND": "J2.14"},
        "A2": {
            "GPIO1": "J3.4",
            "GPIO8": "J1.12",
            "GPIO9": "J1.15",
            "3V3": "J1.1",
            "GND": "J1.22",
        },
        "A3": {"VCC": "P1.4", "GND": "P1.3", "SCL": "P1.2", "SDA": "P1.1"},
    }
    for ref, pins in expected.items():
        assert pins.items() <= DESIGN["components"][ref]["header_map"].items()
    for ref in ("R3", "R4"):
        assert DESIGN["components"][ref]["default_population"] == "FIT"
