---
name: opengrid
description: >
  Create openGrid wall-storage components in OpenSCAD from a prompt: boards and
  tiles, snap-mounted bins, containers, trays and custom accessories sized to the
  28 mm openGrid pitch. Use this skill whenever the user mentions openGrid,
  opengrid boards, tiles or snaps, Underware or Multiconnect on openGrid, or asks
  for a wall bin, pegboard-style holder or container that mounts on a grid. Also
  trigger when the user asks what width a bin needs to be to fit the grid, how
  many bins fit on a board, or how to fill a wall space with openGrid tiles.
---

# openGrid components

Turns a prompt ("a bin for my calipers", "three bins across a 12 wide board",
"a Lite board for 330 x 500 of wall") into an OpenSCAD file sized to the
openGrid grid, plus a clear statement of how it fits next to its neighbours.

## Sources, in order of preference

1. **Library** `openscad-opengrid` (MIT, pure OpenSCAD, no BOSL2).
   Installed at `~/Documents/OpenSCAD/libraries/opengrid/`, source at
   `~/Library/Mobile Documents/com~apple~CloudDocs/Documents (home)/3DPrinter/library/opengrid/`,
   public repo `github.com/morganp/openscad-opengrid`. Use it for snaps,
   bins and custom accessories: `include <opengrid/opengrid.scad>`. Read its
   README for the current module list before writing code. Key API (v1.1.0):
   ```scad
   opengrid_bin(cols=3, depth=40, height=28, wall=2, floor=2,
                divisions_x=1, divisions_y=1, divider=1.6,
                clearance=0.5, snap_spacing=2,
                snap_rows="top",   // "top" | "ends" | "all"
                snap_cols=undef, lite=false, nubs=true, corner_clearance=0);
   og_bin_width(cols, clearance)    og_cols_for(outer_mm)
   og_cols_for_inner(inner_mm, wall)  og_bin_rows(height)
   og_bin_snap_positions(cols, height, spacing, snap_rows)
   opengrid_snaps(positions, lite)
   opengrid_tile(cols, rows, lite)  // test-fit patch, not a printable board
   ```
   Coordinates: bin back on z = 0, bin extends +z; x = 0 is the left grid
   line, y = height is the top grid line. Print **front face down, snaps
   up**: all snap faces stay at 45 degrees or less; the back wall bridges
   between side walls, so add `divisions_x` to keep spans under about 60 mm.
2. **Resource scripts** in `resources/` (see `resources/README.md`):
   - `openGrid.scad`: board / tile generator (needs BOSL2). The only source
     for printable boards.
   - `opengrid-bin.scad`: Mikey Ward's Customizable openGrid Bins
     (CC BY-SA 4.0). Use when the user asks for it or wants its Directional
     snap. Mind the odd-width rule below.

   Derived files keep the source licence and credit line (see
   `resources/README.md`). Library code must stay clean-room MIT.

Never edit the resource files in place. Copy into the project folder, rename
for the part (`opengrid-bin-3c-40d-56h.scad`), then change the Customizer
defaults at the top so the file stays usable in the OpenSCAD Customizer.

## The grid is 28 mm. Keep it.

`Tile_Size = 28` in `openGrid.scad`, `cell_width = 28` in the bin script and
`OG_PITCH` in the library are the openGrid standard. The snap is fixed 25 mm
geometry, so a different pitch breaks every snap, bin and third party
accessory (Underware, Multiconnect, Printables parts).

Change the pitch only when **all** of these hold, and say so explicitly:
- The user has an existing non-standard board (measured pitch is not 28), or
  asks for a deliberately scaled system that will never take standard parts.
- They accept that snaps and accessories must be regenerated at the same pitch.

"It does not quite fit my wall" or "I want a 100 mm bin" are **not** reasons.
Change the cell count, use `Fill_Space_Mode`, or change the bin width in
whole cells instead. If unsure, ask before changing it.

## Sizing rules

Run the calculator rather than doing arithmetic by hand:

```bash
S=~/.claude/skills/opengrid/scripts/grid_fit.py
$S table                 # cols -> outer / inner width, legacy alignment
$S inner 100             # columns needed for 100 mm inside
$S outer 330             # most columns that fit a 330 mm space
$S split 12 3            # three bins across a 12 column board
$S height 40             # snap rows and stack-friendly heights
$S --clearance 0.3 --wall 1.6 cols 5
```

**Width (along the wall).** Always a whole number of cells:
`bin_width = cols * 28 - clearance`, default clearance 0.5 mm, so bins sit
flush side by side without binding. Report the cell count, outer width and
inner width.

- Library bin: any `cols` (even 1) lands on the grid; snaps always use
  both end cells.
- Legacy `opengrid-bin.scad`: snaps are centred on the bin midline and 56 mm
  apart, so **only odd cols (3, 5, 7: 83.5, 139.5, 195.5 mm) align** with
  grid lines. Even cols sit 14 mm off, and a mix of odd and even leaves a
  14 mm gap. 1 col gets no snaps at all. When the user asks for an even
  width with the legacy script, offer the nearest odd widths or the library.

**Height.** At least 28 mm, because a snap needs a full cell on the back wall.
The top edge lands on a grid line. For bins stacked above each other use
multiples of 28 (minus clearance) so the next row starts on a grid line.

**Depth (out from the wall).** Free. Pick from the contents plus 2 x wall.
Deep heavy bins: suggest Directional or Full snaps and more snaps
(`preferred_snap_count = -1`).

**Snap type must match the board.** Lite board (4.0 mm) -> `Lite` snap.
Full board (6.8 mm) -> `Full` or `Directional`. Ask which board they have if
the prompt does not say; the user's own boards default to Lite.

**Bed size.** Check the part fits the printer. An A1 mini (180 x 180) takes
a board of at most 6 x 6 cells (168 mm) and bins up to 6 cols wide.

## Always tell the user how it fits

Every answer that produces a container ends with a short fit note, e.g.:

> 3 cols: 83.5 mm outer, 79.5 mm inner, Lite snaps. Sits flush next to any
> other 3, 5 or 7 col bin. To fill a 12 col board: 5 + 4 + 3 (library) or
> 5 + 5 + 3 on a 13 col board (legacy).

If the requested size is not on the grid, say what it was rounded to and
give the next size down and up. Never silently produce an off-grid width.

## Workflow

1. Parse the prompt: component (board, bin, custom accessory), contents or
   target size, board type (Full / Lite), printer, how many side by side.
2. Size it with `grid_fit.py`. If a dimension is off grid, round to cells
   and note it.
3. Choose the source: library for bins and accessories, `openGrid.scad`
   for boards, legacy bin script only when asked.
4. Write the `.scad` file in the project folder. Header comment: what it
   is, cols x depth x height, board and snap type, source used, version
   (Semantic Versioning, start 1.0.0). With the library, pass `lite=true`
   for Lite boards; `snap_rows="ends"` or `"all"` for tall or heavy bins.
5. Render and check:
   ```bash
   openscad -o part.3mf part.scad                  # must finish without WARNING
   openscad --render --imgsize=800,600 --camera=0,0,0,55,0,25,300 -o part.png part.scad
   ```
   Parameter overrides from the CLI: `-D bin_width=83.5 -D 'snap_type="Lite"'`.
   Look at the PNG before reporting.
6. Report: file paths, the fit note, print orientation (from the source's
   README), and any rounding you did.

## Boards with openGrid.scad

- `Board_Width` x `Board_Height` in cells. Turn off `Connector_Holes_*` on
  edges that face a wall corner or ceiling.
- To cover a wall area: `Fill_Space_Mode = "Fill Available Space"` with
  `Space_Width`, `Space_Depth` and `Max_Tile_Width/Depth` set to the bed
  limit (6 on an A1 mini). This keeps 28 mm pitch and handles the remainder.
- `Screw_Mounting = "Corners"` is fine for Lite boards; heavy loads want
  `By Row and Column`.

## New accessories

For anything that is not a bin (holders, hooks, trays), build a backplate
of whole cells and place snaps at cell centres with the library
(`opengrid_snaps`, `og_grid_positions`). Keep snap centres at least 14 mm
from a plate edge. Reusable shapes go into the library (module, example,
PNG, README), following that repo's conventions.
