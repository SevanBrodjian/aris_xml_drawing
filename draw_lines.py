#!/usr/bin/env python3
"""
Write multiple polylines to ARIS MarkedFishMeasurements XML.

Each polyline becomes one MarkedFishMeasurement element.  Points are supplied
in any convenient local coordinate space; use `transform()` to apply a uniform
scale and translation before calling `write_xml()`.

CLI usage:
    python3 draw_lines.py input.json -o output.xml [--scale S] [--tx TX] [--ty TY]

JSON input formats accepted:
    list of polylines:  [ [[x0,y0],[x1,y1],...], [[x0,y0],...], ... ]
    single polyline:    [ [x0,y0], [x1,y1], ... ]          (e.g. path_unit_width.json)

For JSON input, y values are negated (vertical flip) before any scale/translate.
"""

import argparse
import json
import math


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _cumulative_lengths_cm(polyline):
    lengths = [0.0]
    for i in range(1, len(polyline)):
        dx = polyline[i][0] - polyline[i - 1][0]
        dy = polyline[i][1] - polyline[i - 1][1]
        lengths.append(lengths[-1] + math.hypot(dx, dy) * 100)
    return lengths


def _measurement_xml(polyline, fish_id, frame_index):
    lengths = _cumulative_lengths_cm(polyline)
    nodes = "".join(
        f'<FishMeasureNode WorldPointX="{x:.3f}" WorldPointY="{y:.3f}" Length="{round(l, 4)}" />'
        for (x, y), l in zip(polyline, lengths)
    )
    return (
        f'<MarkedFishMeasurement FishID="{fish_id}" FrameIndex="{frame_index}">'
        f"{nodes}"
        "</MarkedFishMeasurement>"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transform(lines, scale=1.0, translate=(0.0, 0.0)):
    """Return a new list of polylines with uniform scale applied then translate."""
    tx, ty = translate
    return [
        [(x * scale + tx, y * scale + ty) for x, y in line]
        for line in lines
    ]


def write_xml(lines, output, frame_index=0, start_fish_id=1):
    """
    Write a list of polylines to an ARIS MarkedFishMeasurements XML file.

    lines         -- list of polylines; each polyline is a list of (x, y) tuples
                     in world coordinates (metres)
    output        -- path of the XML file to create/overwrite
    frame_index   -- FrameIndex attribute written to every MarkedFishMeasurement
    start_fish_id -- FishID for the first polyline; increments by 1 for each
    """
    measurements = "".join(
        _measurement_xml(line, start_fish_id + i, frame_index)
        for i, line in enumerate(lines)
    )
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<MarkedFishMeasurements>"
        f"{measurements}"
        "</MarkedFishMeasurements>"
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write(xml)

    total_nodes = sum(len(line) for line in lines)
    print(f"Wrote {len(lines)} segment(s), {total_nodes} total nodes → {output}")


# ---------------------------------------------------------------------------
# JSON loader
# ---------------------------------------------------------------------------

def load_json_polylines(path):
    """
    Load polylines from a JSON file.

    Accepts two formats:
      - list of polylines: [ [[x,y],...], [[x,y],...] ]
      - single polyline:   [ [x,y], [x,y], ... ]

    Y values are negated to flip the drawing vertically, matching the
    orientation convention of the txt format.
    """
    with open(path) as f:
        data = json.load(f)

    # Detect format: if first element is a pair of numbers → single polyline
    if isinstance(data[0][0], (int, float)):
        polylines = [data]
    else:
        polylines = data

    return [[(float(x), -float(y)) for x, y in line] for line in polylines]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Write polylines to ARIS XML")
    p.add_argument("input", help="JSON file (single polyline or list of polylines)")
    p.add_argument("-o", "--output", default="lines.xml")
    p.add_argument("--scale", type=float, default=1.0, help="Uniform scale factor (default 1.0)")
    p.add_argument("--tx", type=float, default=0.0, help="X translation in metres (default 0)")
    p.add_argument("--ty", type=float, default=0.0, help="Y translation in metres (default 0)")
    p.add_argument("--frame-index", type=int, default=0)
    p.add_argument("--start-fish-id", type=int, default=1)
    args = p.parse_args()

    lines = load_json_polylines(args.input)
    lines = transform(lines, scale=args.scale, translate=(args.tx, args.ty))
    write_xml(lines, args.output, frame_index=args.frame_index, start_fish_id=args.start_fish_id)


if __name__ == "__main__":
    main()
