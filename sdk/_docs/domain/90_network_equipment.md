# Network / Telecom Equipment Reference (EIA-310 rack canon)

Read this document before modeling any rackmount, network, server, or telecom
facility equipment. All values are SI meters unless noted. Values marked
`(approx)` are working approximations pending field measurement; treat them as
defaults, not hard constraints.

## Two widths — read this before anything else

Every rackmount unit has TWO widths, and vendor datasheets quote either one:

- **Body width** (~`0.434`–`0.446` m): the chassis box that slides between
  the rack rails. Cisco/HPE/Arista/Siemens datasheets quote this.
- **Face width** (`0.4826` m exactly): body + bolted-on mounting ears,
  spanning the 19-inch rack front. Dell datasheets quote this
  ("width with rack latches").

Rule: if the prompt gives a width **below 0.470 m, it is the BODY width** —
keep the chassis at exactly that width and ADD mounting ears so the overall
face reaches `0.4826` m. If the given width is ~`0.482` m it already
includes the ears.

## Prompt vs canon — priority rules

- **Body dimensions (width/depth) and overall height: the prompt's measured
  values win.** They are real-device measurements; do not round them to
  canon values.
- **Face/ear geometry: the canon wins.** Ears always bring the face to
  `0.4826` m with hole columns `0.4651` m apart, regardless of body width.
- Height nuance: nominal height is n × `0.04445` m (1U), but real units run
  `0.001`–`0.002` m short for insertion clearance (e.g. a "1U" switch
  measures `0.0429`–`0.044` m). **Keep the prompt's measured height**; only
  fall back to n × `0.04445` when the prompt gives no height.

## Hard rules for rackmount equipment

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
