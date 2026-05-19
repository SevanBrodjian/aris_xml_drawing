#!/usr/bin/env python3
"""
Load polylines from svg_polylines.txt and write them as ARIS XML.

Each non-empty line in the file must be a Python-literal list of (x, y) tuples:
    [(x0, y0), (x1, y1), ...]

The SVG coordinate space is scaled and translated into ARIS world coordinates
(metres) before writing.

Usage:
    python3 svg_to_xml.py [input.txt] [options]

    --scale S        multiply every coordinate by S (default: 0.001, i.e. 1 px ≈ 1 mm)
    --tx TX          X translation in metres after scaling (default: 0.0)
    --ty TY          Y translation in metres after scaling (default: 0.0)
    -o OUTPUT        output XML file (default: output.xml)
    --frame-index N  FrameIndex attribute on every measurement (default: 0)
"""

import argparse
import ast

from draw_lines import transform, write_xml


def load_polylines(path):
    """Return a list of polylines from a file where each non-empty line is a tuple-list literal."""
    polylines = []
    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                pts = ast.literal_eval(line)
            except (ValueError, SyntaxError) as e:
                raise ValueError(f"Line {lineno}: could not parse as a list of points: {e}") from e
            if not isinstance(pts, list) or not all(len(p) == 2 for p in pts):
                raise ValueError(f"Line {lineno}: expected a list of (x, y) pairs")
            polylines.append([(float(x), float(y)) for x, y in pts])
    return polylines


def main():
    p = argparse.ArgumentParser(description="Convert svg_polylines.txt to ARIS XML")
    p.add_argument("input", nargs="?", default="svg_polylines.txt")
    p.add_argument("--scale", type=float, default=0.001,
                   help="Scale factor applied to SVG coords (default 0.001: 1 px → 1 mm)")
    p.add_argument("--tx", type=float, default=0.0, help="X translation in metres (default 0)")
    p.add_argument("--ty", type=float, default=0.0, help="Y translation in metres (default 0)")
    p.add_argument("-o", "--output", default="output.xml")
    p.add_argument("--frame-index", type=int, default=0)
    args = p.parse_args()

    polylines = load_polylines(args.input)
    print(f"Loaded {len(polylines)} polyline(s) from {args.input}")

    world_lines = transform(polylines, scale=args.scale, translate=(args.tx, args.ty))
    write_xml(world_lines, args.output, frame_index=args.frame_index)


if __name__ == "__main__":
    main()
