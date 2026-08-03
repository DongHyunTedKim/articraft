# Domain data

Fork-specific network/telecom domain data for the OIC testbed digital-twin
work. Not part of upstream Articraft.

## equipment_registry.csv

Unified, normalized registry built from three Notion tables
(2026-07-15): the real OIC TB equipment list, the free 3D-model
collection, and the paid 3D-model collection.

- Units are SI meters / kilograms. `u_height` is derived from
  `height_m / 0.04445` (rounded).
- Width is split (2026-07-20): `body_width_m` = chassis between rails
  (Cisco/HPE/Arista style), `face_width_m` = ears/latches included
  (0.4826 for rackmount; Dell quotes this directly). Dell rows have
  `body_width_pending_field_measure` until measured on site.
- `source`: `real_equipment_oic_tb` | `free_3d_model` | `paid_3d_model` |
  `reference_spec` (AC 생성 기준 자산 — 실물이 아니라 공개 스펙/동급 제품
  차용값으로 정의된 행, 2026-08-03 신설).
- `scope=skip`: whole-server-room scene models, excluded from the
  per-object pipeline by decision (2026-07-15).
- `reference`: `notion:<page-id>` points at the Notion row page, which
  holds the datasheet attachment (real equipment) or representative
  capture images + model file (3D models). `notion-file:<id>` is the
  raw attachment id.
- `quality_flags` records normalization fixes (unit typos, inch/lbs
  conversion) and open gaps (`dims_missing;from_datasheet_pending`).

Intended consumers:
1. Generation prompt pack for the 20 real devices (`articraft generate`
   inputs with exact dimensions/mass).
2. Cloud-vs-local model A/B benchmark set (redesign plan §3).
3. Scene-composer equipment inventory (rack elevation → placement).
4. Mass ground truth for Isaac inertia synthesis (plan §4, real masses
   preferred over density estimates).

## Asset naming convention (2026-07-20)

Deliverable assets use a three-way source prefix so AI-generated
lookalikes can never be mistaken for vendor CAD:

- `ac_` — Articraft-generated, reference-style (not vendor CAD; details
  may differ from the real product). e.g. `ac_server_2u_dell_r760style_v1`
- `cg_` — purchased/free 3D models (CGTrader etc.)
- `oem_` — official vendor CAD (when obtained)

Pattern: `<prefix>_<category>_<form>_<vendor>_<ref>style_v<n>`. Keep the
vendor and reference device in the name for traceability, always suffixed with `style` for
`ac_` assets. Apply the same name to the URDF `<robot name>` so it
propagates into simulators.
