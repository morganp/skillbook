#!/usr/bin/env python3
"""openGrid fit calculator for bins and containers.

Answers "what width do I need so this sits exactly on the grid, and what
fits next to it". All sizes in mm. Grid pitch is the openGrid standard 28 mm.

Two bin generators are modelled:
  library  - opengrid_bin() in the openscad-opengrid library (v1.1.0+).
             Snaps land on cell centres for any column count.
  legacy   - resources/opengrid-bin.scad. Snaps are centred on the bin
             midline, 56 mm apart, so only ODD column counts align with grid
             lines. Even counts sit half a cell (14 mm) off.

Usage:
  grid_fit.py table [--max 10]            column count -> outer / inner width
  grid_fit.py cols N                      detail for an N column bin
  grid_fit.py inner MM                    columns needed for an inner width
  grid_fit.py outer MM                    most columns that fit a space
  grid_fit.py split BOARD_COLS COUNT      split a board row into COUNT bins
  grid_fit.py height MM                   snap rows and stack-friendly heights
Options:
  --clearance G   gap left between neighbouring bins, default 0.5
  --wall T        bin wall thickness, default 2
"""

import argparse
import math

PITCH = 28.0
SNAP = 25.0


def outer_width(cols, clearance):
    return cols * PITCH - clearance


def inner_width(cols, clearance, wall):
    return outer_width(cols, clearance) - 2 * wall


def legacy_snaps(cols, clearance, wall, preferred=-1):
    """Snap centres for resources/opengrid-bin.scad, measured from the left
    grid line of the footprint (bin centred in its cols * 28 footprint)."""
    w = outer_width(cols, clearance)
    chamfer = wall * 1.5
    cells = math.floor((w - 2 * chamfer) / PITCH)
    max_count = math.ceil(cells / 2) if cells > 0 else 0
    count = max_count if preferred == -1 else min(max_count, preferred)
    mid = cols * PITCH / 2
    return [mid + 2 * PITCH * (i - (count - 1) / 2) for i in range(count)]


def legacy_aligned(cols, clearance, wall):
    snaps = legacy_snaps(cols, clearance, wall)
    if not snaps:
        return False, "no snaps (too narrow)"
    off = [(c - PITCH / 2) % PITCH for c in snaps]
    if all(abs(o) < 1e-6 or abs(o - PITCH) < 1e-6 for o in off):
        return True, "aligned"
    return False, "half-cell offset: edges sit 14 mm off the grid lines"


def cmd_table(a):
    print(f"{'cols':>4}  {'outer':>7}  {'inner':>7}  legacy script")
    for n in range(1, a.max + 1):
        _, why = legacy_aligned(n, a.clearance, a.wall)
        print(f"{n:>4}  {outer_width(n, a.clearance):>7.1f}  "
              f"{inner_width(n, a.clearance, a.wall):>7.1f}  {why}")


def cmd_cols(a):
    n = a.n
    ok, why = legacy_aligned(n, a.clearance, a.wall)
    print(f"cols            {n}")
    print(f"footprint       {n * PITCH:.1f} (grid span)")
    print(f"outer width     {outer_width(n, a.clearance):.1f} "
          f"(bin_width, clearance {a.clearance})")
    print(f"inner width     {inner_width(n, a.clearance, a.wall):.1f} "
          f"(wall {a.wall})")
    print("library snaps   on cell centres for any cols, both end cells used "
          "(exact list: og_bin_snap_positions)")
    print(f"legacy snaps    {legacy_snaps(n, a.clearance, a.wall)} -> {why}")
    if not ok and n > 1:
        print(f"legacy fix      use {n - 1} or {n + 1} cols, or the library module")


def cmd_inner(a):
    n = max(1, math.ceil((a.mm + 2 * a.wall + a.clearance) / PITCH))
    print(f"need inner {a.mm}: {n} cols -> outer "
          f"{outer_width(n, a.clearance):.1f}, inner "
          f"{inner_width(n, a.clearance, a.wall):.1f}")
    if n < 2:
        print("note: 1 col bins get no snaps from the legacy script; use the library")
    if n % 2 == 0:
        print(f"legacy script: {n} is even, use {n + 1} cols "
              f"(inner {inner_width(n + 1, a.clearance, a.wall):.1f}) to stay on grid")


def cmd_outer(a):
    n = math.floor((a.mm + a.clearance) / PITCH)
    print(f"space {a.mm}: max {n} cols -> outer {outer_width(n, a.clearance):.1f}, "
          f"spare {a.mm - n * PITCH:.1f}")
    if n % 2 == 0 and n > 1:
        print(f"legacy script: largest odd is {n - 1} cols")


def splits(total, count, odd_only):
    """All non-increasing partitions of total into count parts (>= 2 each)."""
    out = []

    def rec(left, parts, cap):
        if len(parts) == count:
            if left == 0:
                out.append(parts)
            return
        for p in range(min(cap, left), 1, -1):
            if odd_only and p % 2 == 0:
                continue
            rec(left - p, parts + [p], p)

    rec(total, [], total)
    out.sort(key=lambda p: (max(p) - min(p), p))
    return out


def cmd_split(a):
    b, k = a.board_cols, a.count
    print(f"board {b} cols ({b * PITCH:.0f} mm) into {k} bins, "
          f"clearance {a.clearance} per bin")
    for label, odd in (("library", False), ("legacy (odd only)", True)):
        opts = splits(b, k, odd)[:3]
        if not opts:
            hint = " (a sum of odd widths is odd for an odd bin count: board cols parity must match bin count parity)" if odd else ""
            print(f"  {label}: no exact split{hint}")
            continue
        for p in opts:
            widths = ", ".join(f"{outer_width(c, a.clearance):.1f}" for c in p)
            print(f"  {label}: cols {p} -> bin_width {widths}")
    if b % k:
        print(f"  note: {b} is not divisible by {k}, so equal bins leave "
              f"{b % k} col(s) spare")


def cmd_height(a):
    rows = math.floor(a.mm / PITCH)
    if a.mm < PITCH:
        print(f"height {a.mm} < 28: snap will not fit on the back wall. Use >= 28.")
        return
    lo, hi = rows * PITCH, (rows + 1) * PITCH
    print(f"height {a.mm}: covers {rows} full grid row(s)")
    print(f"stack-friendly: {lo:.0f} or {hi:.0f} (minus clearance, e.g. "
          f"{lo - a.clearance:.1f})")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--clearance", type=float, default=0.5)
    p.add_argument("--wall", type=float, default=2.0)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("table"); s.add_argument("--max", type=int, default=10)
    s.set_defaults(f=cmd_table)
    s = sub.add_parser("cols"); s.add_argument("n", type=int); s.set_defaults(f=cmd_cols)
    s = sub.add_parser("inner"); s.add_argument("mm", type=float); s.set_defaults(f=cmd_inner)
    s = sub.add_parser("outer"); s.add_argument("mm", type=float); s.set_defaults(f=cmd_outer)
    s = sub.add_parser("split"); s.add_argument("board_cols", type=int)
    s.add_argument("count", type=int); s.set_defaults(f=cmd_split)
    s = sub.add_parser("height"); s.add_argument("mm", type=float); s.set_defaults(f=cmd_height)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
