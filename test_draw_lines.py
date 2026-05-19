#!/usr/bin/env python3
"""
Test draw_lines.py by rendering a simple house shape made of three polylines:
  - a square base
  - a triangular roof
  - a door cutout

Local coordinates are in the 0..1 range and are scaled/translated into a
plausible ARIS world-coordinate region (roughly x ∈ [-0.15, 0.15], y ∈ [6.35, 6.8]).
"""

import math
import xml.etree.ElementTree as ET

from draw_lines import transform, write_xml

OUTPUT = "test_house.xml"

# House defined in local [0,1]×[0,1.5] space
LOCAL_LINES = [
    # Square base (closed)
    [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.0, 0.0)],
    # Triangle roof
    [(0.0, 1.0), (0.5, 1.5), (1.0, 1.0)],
    # Door (open bottom)
    [(0.35, 0.0), (0.35, 0.5), (0.65, 0.5), (0.65, 0.0)],
]

# Scale local coords to 0.3 m wide and shift into ARIS-like world coords
SCALE = 0.3
TRANSLATE = (-0.15, 6.35)


def test_structure():
    """Correct number of measurements and nodes."""
    world_lines = transform(LOCAL_LINES, scale=SCALE, translate=TRANSLATE)
    write_xml(world_lines, OUTPUT)

    root = ET.parse(OUTPUT).getroot()
    measurements = root.findall("MarkedFishMeasurement")

    assert len(measurements) == 3, f"expected 3 measurements, got {len(measurements)}"

    expected_node_counts = [5, 3, 4]
    for i, (m, expected) in enumerate(zip(measurements, expected_node_counts)):
        got = len(m.findall("FishMeasureNode"))
        assert got == expected, f"segment {i}: expected {expected} nodes, got {got}"

    print("PASS: correct measurement and node counts")


def test_fish_ids():
    """FishID increments starting from 1."""
    root = ET.parse(OUTPUT).getroot()
    fish_ids = [m.get("FishID") for m in root.findall("MarkedFishMeasurement")]
    assert fish_ids == ["1", "2", "3"], f"wrong FishIDs: {fish_ids}"
    print("PASS: FishID values are 1, 2, 3")


def test_first_length_zero():
    """Every segment's first node has Length=0."""
    root = ET.parse(OUTPUT).getroot()
    for i, m in enumerate(root.findall("MarkedFishMeasurement")):
        first = m.find("FishMeasureNode")
        assert float(first.get("Length")) == 0.0, f"segment {i}: first Length != 0"
    print("PASS: first node of every segment has Length=0")


def test_lengths_monotone():
    """Cumulative lengths are non-decreasing within each segment."""
    root = ET.parse(OUTPUT).getroot()
    for i, m in enumerate(root.findall("MarkedFishMeasurement")):
        lengths = [float(n.get("Length")) for n in m.findall("FishMeasureNode")]
        for j in range(1, len(lengths)):
            assert lengths[j] >= lengths[j - 1], (
                f"segment {i}, node {j}: length decreased ({lengths[j-1]} → {lengths[j]})"
            )
    print("PASS: lengths are monotonically non-decreasing")


def test_transform_correctness():
    """Spot-check that scale+translate lands a known point at the right world coord."""
    lx, ly = 1.0, 1.0  # top-right of square base
    expected = (lx * SCALE + TRANSLATE[0], ly * SCALE + TRANSLATE[1])

    root = ET.parse(OUTPUT).getroot()
    # Third node of the first measurement (index 2) is (1,1) in local space
    nodes = root.findall("MarkedFishMeasurement")[0].findall("FishMeasureNode")
    got = (float(nodes[2].get("WorldPointX")), float(nodes[2].get("WorldPointY")))

    assert math.isclose(got[0], expected[0], abs_tol=1e-9), f"X mismatch: {got[0]} != {expected[0]}"
    assert math.isclose(got[1], expected[1], abs_tol=1e-9), f"Y mismatch: {got[1]} != {expected[1]}"
    print(f"PASS: world coord of local (1,1) = {got} as expected")


def test_square_perimeter():
    """The closed square base should have total length ≈ 4 × 0.3 m = 120 cm."""
    root = ET.parse(OUTPUT).getroot()
    nodes = root.findall("MarkedFishMeasurement")[0].findall("FishMeasureNode")
    total = float(nodes[-1].get("Length"))
    expected = 4 * SCALE * 100  # cm
    assert math.isclose(total, expected, rel_tol=1e-6), (
        f"square perimeter {total:.4f} cm != expected {expected:.4f} cm"
    )
    print(f"PASS: square perimeter = {total:.4f} cm (expected {expected:.4f} cm)")


def print_summary():
    root = ET.parse(OUTPUT).getroot()
    print("\nGenerated segments:")
    for m in root.findall("MarkedFishMeasurement"):
        nodes = m.findall("FishMeasureNode")
        total_len = float(nodes[-1].get("Length"))
        print(f"  FishID={m.get('FishID')}  nodes={len(nodes)}  total_length={total_len:.4f} cm")


if __name__ == "__main__":
    test_structure()
    test_fish_ids()
    test_first_length_zero()
    test_lengths_monotone()
    test_transform_correctness()
    test_square_perimeter()
    print_summary()
    print("\nAll tests passed.")
