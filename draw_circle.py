#!/usr/bin/env python3
"""Generate an ARIS MarkedFishMeasurements XML containing a circle."""

import argparse
import math


def draw_circle(cx, cy, radius, n_points=36, fish_id=1, frame_index=0, output="circle.xml"):
    # n_points + 1 so the last node closes back to the first
    angles = [2 * math.pi * i / n_points for i in range(n_points + 1)]
    points = [(cx + radius * math.cos(a), cy + radius * math.sin(a)) for a in angles]

    # Cumulative arc length in centimetres (world coords are metres)
    lengths = [0.0]
    for i in range(1, len(points)):
        dx = points[i][0] - points[i - 1][0]
        dy = points[i][1] - points[i - 1][1]
        lengths.append(lengths[-1] + math.hypot(dx, dy) * 100)

    # Build XML as a string to exactly match the compact, single-line format
    nodes = "".join(
        f'<FishMeasureNode WorldPointX="{x}" WorldPointY="{y}" Length="{round(l, 4)}" />'
        for (x, y), l in zip(points, lengths)
    )
    xml = (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<MarkedFishMeasurements>"
        f'<MarkedFishMeasurement FishID="{fish_id}" FrameIndex="{frame_index}">'
        f"{nodes}"
        "</MarkedFishMeasurement>"
        "</MarkedFishMeasurements>"
    )

    with open(output, "w", encoding="utf-8") as f:
        f.write(xml)

    circumference = lengths[-1]
    print(f"Wrote {len(points)} nodes to {output}")
    print(f"Circle: center=({cx}, {cy}) m, radius={radius} m, circumference={circumference:.4f} cm")


def main():
    p = argparse.ArgumentParser(description="Draw a circle in ARIS XML format")
    p.add_argument("--cx", type=float, help="Center X (metres)")
    p.add_argument("--cy", type=float, help="Center Y (metres)")
    p.add_argument("--radius", type=float, help="Radius (metres)")
    p.add_argument("--n-points", type=int, default=36, help="Polygon approximation points (default 36)")
    p.add_argument("--fish-id", type=int, default=1)
    p.add_argument("--frame-index", type=int, default=0)
    p.add_argument("-o", "--output", default="circle.xml")
    args = p.parse_args()

    draw_circle(args.cx, args.cy, args.radius, args.n_points, args.fish_id, args.frame_index, args.output)


if __name__ == "__main__":
    main()
