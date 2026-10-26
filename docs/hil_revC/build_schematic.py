"""Rebuild the module-level RF-HIL-001 Rev C drawing from its frozen netlist.

Requires reportlab and PyMuPDF. This drawing is not a native ECAD/ERC model.
"""

from __future__ import annotations

import json
from pathlib import Path

import fitz
from reportlab.pdfgen import canvas

FOLDER = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1190, 842


def build() -> None:
    """Write an A3 landscape PDF and an SVG of the same vector drawing."""
    design = json.loads((FOLDER / "RF-HIL-001_RevC_netlist.json").read_text())
    pdf = FOLDER / "RF-HIL-001_RevC_schematic.pdf"
    doc = canvas.Canvas(str(pdf), pagesize=(WIDTH, HEIGHT))
    doc.setTitle("RF-HIL-001 Rev C - bench HIL module interconnect")
    doc.setAuthor("RelyFetal - technical review; independent approval pending")
    doc.setLineWidth(1)

    def line(x1: float, y1: float, x2: float, y2: float) -> None:
        doc.line(x1, HEIGHT - y1, x2, HEIGHT - y2)

    def label(x: float, y: float, value: str, size: float = 11) -> None:
        doc.setFont("Helvetica", size)
        doc.drawString(x, HEIGHT - y, value)

    def rect(x: float, y: float, w: float, h: float) -> None:
        doc.rect(x, HEIGHT - y - h, w, h)

    def dot(x: float, y: float) -> None:
        doc.circle(x, HEIGHT - y, 2.7, fill=1, stroke=0)

    def ground(x: float, y: float) -> None:
        line(x, y, x, y + 8)
        path = doc.beginPath()
        path.moveTo(x - 7, HEIGHT - y - 8)
        path.lineTo(x + 7, HEIGHT - y - 8)
        path.lineTo(x, HEIGHT - y - 19)
        path.close()
        doc.drawPath(path)
        label(x + 12, y + 19, "GND / 0 V", 9)

    def resistor(x: float, y: float, vertical: bool = False) -> None:
        if vertical:
            line(x, y, x, y + 12)
            rect(x - 6, y + 12, 12, 36)
            line(x, y + 48, x, y + 60)
        else:
            line(x, y, x + 12, y)
            rect(x + 12, y - 6, 56, 12)
            line(x + 68, y, x + 80, y)

    def capacitor(x: float, top: float, bottom: float) -> None:
        mid = (top + bottom) / 2
        line(x, top, x, mid - 4)
        line(x - 12, mid - 4, x + 12, mid - 4)
        line(x - 12, mid + 4, x + 12, mid + 4)
        line(x, mid + 4, x, bottom)

    def testpoint(x: float, y: float, name: str) -> None:
        dot(x, y)
        line(x, y, x, y - 18)
        doc.circle(x, HEIGHT - y + 22, 4)
        label(x + 8, y - 20, name, 10)

    rect(20, 20, WIDTH - 40, HEIGHT - 40)
    label(42, 51, "RF-HIL-001   /   MODULE INTERCONNECT SCHEMATIC", 19)
    label(
        42,
        74,
        "Rev C  |  2026-10-21  |  Bench prototype  |  NOT BENCH VERIFIED  |  Sheet 1 / 1",
        11,
    )
    label(42, 100, "1. ANALOG PATH - all voltages relative to common signal GND", 12)
    rect(45, 125, 255, 230)
    label(60, 149, "A1  Espressif ESP32-DevKitC-32E", 12)
    label(60, 170, "DevKitC V4 / ESP32-WROOM-32E", 11)
    label(60, 213, "J2.9  IO25 / DAC1", 12)
    label(60, 303, "J2.14  GND", 12)
    label(60, 333, "USB-to-UART: Micro-B / USB5_A1", 10)
    rect(875, 125, 270, 230)
    label(890, 149, "A2  Espressif ESP32-S3-DevKitC-1", 12)
    label(890, 170, "N8R8 / v1.1 / WROOM-1-N8R8", 11)
    label(890, 213, "J3.4  GPIO1 / ADC1_CH0", 12)
    label(890, 239, "12-bit; highest attenuation; calibrate", 10)
    label(890, 303, "J1.22  GND", 12)
    label(890, 333, "USB-to-UART: Micro-B / USB5_A2", 10)
    line(300, 210, 400, 210)
    testpoint(345, 210, "TP1")
    resistor(400, 210)
    label(390, 170, "R1  10 kOhm / 1% / 0.25 W", 11)
    line(480, 210, 875, 210)
    label(350, 237, "DAC_OUT", 10)
    label(765, 237, "ADC_IN", 10)
    testpoint(805, 210, "TP2")
    line(555, 210, 555, 265)
    dot(555, 210)
    resistor(555, 265, True)
    label(575, 282, "R2  39 kOhm", 11)
    label(575, 300, "1% / 0.25 W", 10)
    line(555, 325, 555, 370)
    capacitor(730, 210, 370)
    dot(730, 210)
    label(750, 278, "C1  100 nF", 11)
    label(750, 296, "X7R / 10% / 50 V", 10)
    label(750, 314, "At A2 ADC/GND", 10)
    line(555, 370, 730, 370)
    dot(555, 370)
    dot(730, 370)
    ground(645, 370)
    testpoint(555, 370, "TP3")
    line(300, 300, 325, 300)
    ground(325, 300)
    line(875, 300, 855, 300)
    ground(855, 300)
    label(
        45,
        397,
        "TP2 acceptance: 0 to 2.85 V including overshoot/measurement uncertainty. Ideal worst corner: 2.813 V (R 5%, rail +5%).",
        11,
    )
    label(
        45,
        419,
        "2. OLED / I2C - host-side R3/R4 FITTED for DFR0486; verify rise time and low level",
        12,
    )
    rect(45, 445, 255, 205)
    label(60, 468, "A2  auxiliary header terminals", 12)
    rect(875, 445, 270, 205)
    label(890, 468, "A3  DFRobot DFR0486", 12)
    label(890, 487, "SSD1306 128 x 64 / schematic V1.0", 10)
    for y, left, right in [
        (510, "J1.1   3V3", "P1.4   VCC"),
        (550, "J1.12 GPIO8 / SDA", "P1.1   SDA"),
        (590, "J1.15 GPIO9 / SCL", "P1.2   SCL"),
        (630, "J1.22 GND", "P1.3   GND"),
    ]:
        label(60, y + 4, left, 12)
        label(890, y + 4, right, 12)
        line(300, y, 875, y)
    label(310, 503, "3V3_A2", 9)
    for x, y, ref in [(500, 550, "R3"), (660, 590, "R4")]:
        line(x, y, x, 505)
        # Top net label connects to VCC; the lower lead crosses VCC without a dot.
        resistor(x, 445, True)
        label(x + 12, 450, f"{ref} 4k7 / 1%", 10)
        line(x, 445, x, 434)
        label(x - 28, 431, "3V3_A2", 9)
        dot(x, y)
    capacitor(805, 510, 630)
    dot(805, 510)
    dot(805, 630)
    label(825, 572, "C2", 10)
    label(825, 586, "100 nF", 9)
    ground(345, 630)
    label(
        45,
        678,
        "NOTES: dots = junctions; crossings without dots are NOT connected. GND triangles = common signal reference, not protective earth.",
        10,
    )
    label(
        45,
        696,
        "A3 numbering follows manufacturer schematic P1, not wiki table row numbers. Confirm silk and cable continuity before power.",
        10,
    )
    label(
        45,
        714,
        "C1/C2 non-polarized X7R 100 nF / 10% / 50 V. C2 at A3. R3/R4 are external host pull-ups; A3 contains level shifters/pull-ups.",
        10,
    )
    label(
        45,
        732,
        "USB5_A1 and USB5_A2 are separate: do not join 5 V or regulator 3V3 outputs. A3 power only from A2. Check both 3V3 rails +/-5%.",
        10,
    )
    label(
        45,
        750,
        "Wire only with both supplies OFF. Power A2 before A1; turn A1 off before A2. No hot-plug protection. No patient/electrode connection.",
        10,
    )
    line(20, 770, WIDTH - 20, 770)
    label(40, 792, "RF-HIL-001 / Rev C / 2026-10-21", 12)
    label(410, 792, "Source: frozen netlist + build_schematic.py", 11)
    label(840, 792, "Approval: PENDING / NOT FOR PRODUCTION", 11)
    label(
        40,
        810,
        f"Models: {design['components']['A1']['model']} | DFR0486. See review/BOM for full references and acceptance plan.",
        9,
    )
    doc.showPage()
    doc.save()
    with fitz.open(pdf) as rendered:
        page = rendered[0]
        (FOLDER / "RF-HIL-001_RevC_schematic.svg").write_text(
            page.get_svg_image(text_as_path=False), encoding="utf-8"
        )


if __name__ == "__main__":
    build()
