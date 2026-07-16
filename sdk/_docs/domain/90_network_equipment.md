# Network / Telecom Equipment Reference (EIA-310 rack canon)

Read this document before modeling any rackmount, network, server, or telecom
facility equipment. All values are SI meters unless noted. Values marked
`(approx)` are working approximations pending field measurement; treat them as
defaults, not hard constraints.

## Hard rules for rackmount equipment

- The front face of a rack-mounted unit (including mounting ears) is exactly
  `0.4826` m wide (19 inches, EIA-310).
- Equipment height is an integer multiple of one rack unit `U = 0.04445` m.
  Real units are typically built `0.0008` m short of the full multiple for
  insertion clearance (e.g. a 1U chassis is ~`0.04365` m tall).
- Mounting-ear hole columns are `0.4651` m apart, center to center.
- The chassis body between the rack rails is at most `0.45085` m wide;
  `0.438` m is the common body width.
- Never scale a rack face to fit other geometry. If something does not fit,
  the other geometry is wrong.

## EIA-310 canon (SI meters)

| Constant | Value | Meaning |
| --- | --- | --- |
| `RACK_FACE_W` | `0.4826` | 19 in front panel width, ears included |
| `U_HEIGHT` | `0.04445` | one rack unit |
| `RACK_HOLE_SPAN` | `0.4651` | horizontal hole-center spacing |
| `RACK_OPENING_W` | `0.45085` | clear width between rails |
| `RACK_BODY_W` | `0.438` | common chassis body width |
| `U_HOLE_PITCH` | `0.015875 / 0.015875 / 0.0127` | vertical hole pattern within one U |

Suggested module-constant block for rackmount models:

```python
# EIA-310 canon (SI meters)
RACK_FACE_W = 0.4826
U_HEIGHT = 0.04445
RACK_HOLE_SPAN = 0.4651
RACK_BODY_W = 0.438
```

## Cabinets and open racks

| Item | Value | Note |
| --- | --- | --- |
| Cabinet width | `0.6` or `0.8` | 0.8 m variants leave side cable space |
| Cabinet depth | `0.8` / `1.0` / `1.2` | telecom rooms commonly use 1.0 m (approx) |
| Cabinet height | 42U ≈ `2.0` overall | frame + top/bottom panels |
| Front door | hinged, swing ≈ 130° | model as a `revolute` joint, axis vertical at one edge |
| Rear door | hinged or split double door | double doors hinge outward from center |
| Side panels | lift-off, usually static | do not articulate unless asked |

## Front-face elements (approx — refine with field measurements)

| Element | W × H | Note |
| --- | --- | --- |
| RJ45 port opening | `0.015 × 0.013` | 24-port rows use ~`0.0158` pitch, often 12+12 blocks |
| SFP/SFP+ cage | `0.0145 × 0.0095` | usually paired in 2×N blocks |
| Status LED | `0.002`–`0.003` dia | one per port, above or beside it |
| Power inlet (C14) | `0.030 × 0.022` | rear face |
| 40mm fan opening | `0.040` dia | 1U rear/side; 80/120 mm in larger units |
| Handle / latch | `0.010`–`0.015` deep | on removable modules and PSUs |

## Articulation guidance

- Cabinet/enclosure doors: `revolute`, lower/upper `0.0 .. ~2.27` rad
  (130°), realistic effort ~`30`, velocity ~`1.5`.
- Server sliding rails / drawers: `prismatic`, travel `0.0 .. ~0.7`,
  effort ~`80`, velocity ~`0.3`.
- Hot-swap fan/PSU modules: `prismatic` with short travel if the prompt asks
  for serviceable modules; otherwise static.
- Do NOT use `floating` joints. Avoid `mimic` unless explicitly requested
  (downstream simulators ignore it).
- Always set explicit, physically plausible `effort` and `velocity` on
  motion limits; never leave the defaults.

## Part naming conventions

Use these names so downstream tooling can label parts automatically:

- `chassis`, `ear_left`, `ear_right`, `faceplate`
- `door_front`, `door_rear`, `door_rear_left`, `door_rear_right`
- `rail_left`, `rail_right`, `tray`, `shelf_<n>`
- `port_rj45_<nn>`, `port_sfp_<nn>`, `led_<nn>` (or a grouped
  `port_block_<n>` visual when ports are purely visual detail)
- `fan_<n>`, `psu_<n>`, `handle_<n>`

## Company facility standards

(Reserved. This section is populated from field-survey results: cabinet
vendor dimensions, aisle widths, cable-tray profiles, DC power plant racks,
FDF/MDF layouts. Until then, prefer the EIA values above.)
