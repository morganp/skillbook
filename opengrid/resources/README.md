# openGrid resource scripts

Reference OpenSCAD Customizer scripts. Copy them into the project folder
before editing; never edit these originals.

| File | Makes | Deps | Licence / origin |
|---|---|---|---|
| `openGrid.scad` | openGrid boards (Full 6.8 mm, Lite 4.0 mm), stacks, fill-a-space tile sets | BOSL2 | CC BY-NC-SA 4.0. openGrid design by DavidD, OpenSCAD by BlackjackDuck (Andy). Keep the header intact. |
| `opengrid-bin.scad` | Wall bin with chamfered walls, optional dividers, snaps on the back wall | none | Origin not recorded (openGrid community bin generator). Treat as third party: do not relicense. |

## openGrid.scad key parameters

| Parameter | Default | Notes |
|---|---|---|
| `Full_or_Lite` | `"Lite"` | Full 6.8 mm is double sided; Lite 4.0 mm is wall mounted, one sided |
| `Board_Width`, `Board_Height` | 2, 2 | In cells (28 mm each) |
| `Chamfers` | `"Corners"` | `Everywhere`, `Corners`, `None`; per-corner toggles follow |
| `Connector_Holes` (+ `_Top/_Bottom/_Left/_Right`) | true | Edge slots for tile-to-tile connectors. Turn off on outside edges of a wall |
| `Screw_Mounting` | `"Corners"` | `Everywhere`, `Corners`, `By Row and Column`, `Custom`, `None` |
| `Screw_Diameter`, `Screw_Head_Diameter` | 4.1, 7.2 | Countersunk 90 degree by default |
| `Tile_Size` | 28 | openGrid standard. See SKILL.md before changing |
| `Stack_Count`, `Stacking_Method` | 1 | Print several boards in one job |
| `Fill_Space_Mode` | `"None"` | `Complete Tiles Only` or `Fill Available Space` using `Space_Width/Depth`, `Max_Tile_Width/Depth` |

## opengrid-bin.scad key parameters

| Parameter | Default | Notes |
|---|---|---|
| `bin_width` | 100 | Outer width along the wall. Use `cols * 28 - clearance`, odd `cols` only |
| `bin_depth` | 40 | Distance out from the wall. Not grid constrained |
| `bin_height` | 32 | Must be 28 or more. Top edge lands on a grid line |
| `wall_thickness`, `floor_thickness` | 2, 2 | Outer chamfer is `1.5 * wall` |
| `width_sub_bins`, `depth_sub_bins` | 1, 1 | Divider counts |
| `snap_type` | `"Directional"` | `Lite` (Lite boards), `Full`, `Directional` (Full thickness, load bearing downwards) |
| `preferred_snap_count` | 10 | Capped at the max; `-1` means max. Snaps sit every other cell |
| `snap_fitment` | 0.5 | 0.5 standard, 0.66 to 0.75 tight |

Measured behaviour (rendered with snap centre echo, widths `N * 28`):

| N | Snap centres from left edge | Grid fit |
|---|---|---|
| 1 | none | unusable |
| 2 | 28 | half-cell offset |
| 3 | 42 | aligned |
| 4 | 28, 84 | half-cell offset |
| 5 | 42, 98 | aligned |
| 7 | 42, 98, 154 | aligned |

Snaps are centred on the bin midline and spaced 56 mm, so only odd `N`
puts the edges on grid lines. The snap band is the top 28 mm of the back
wall (`z = bin_height - 28` upwards).
