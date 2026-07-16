---
title: '24-Port 1U Keystone Patch Panel'
description: 'Flat 1U patch panel spanning the full 482.6mm EIA-310 rack face: single row of 24 RJ45 keystone openings at 18mm pitch, numbered flush labels, and a rear cable-support bar on two brackets. Static object.'
tags:
  - rack
  - rackmount
  - 1u
  - patch-panel
  - keystone
  - rj45
  - network
  - cabling
  - eia-310
  - telecom
  - datacenter
---

Patch panels are flat plates, so the whole front face spans the full
0.4826 m rack width (the ear region is part of the same plate, with screw
slots implied). Ports and labels are flush surface elements a fraction of a
millimeter proud of the face — the same technique the 1U switch example uses
for vents — and the rear cable bar is carried by two brackets that touch the
plate, so nothing floats.

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    Box,
    Material,
    Origin,
    TestContext,
    TestReport,
)

# EIA-310 canon (SI meters)
RACK_FACE_W = 0.4826
U_HEIGHT = 0.04445
RACK_HOLE_SPAN = 0.4651

PLATE_T = 0.0030
FRONT_Y = -PLATE_T / 2.0

PORT_COUNT = 24
PORT_W = 0.0150
PORT_H = 0.0165
PORT_PITCH = 0.0180
PORT_ROW_Z = U_HEIGHT * 0.42

LABEL_W = 0.0100
LABEL_H = 0.0040
LABEL_ROW_Z = PORT_ROW_Z + PORT_H / 2.0 + 0.0055

BAR_W = 0.400
BAR_SQ = 0.012
BAR_Y = 0.0250
BRACKET_X = 0.170

STEEL_BLACK = Material("black_powder_coat_plate", rgba=(0.10, 0.105, 0.115, 1.0))
JACK_DARK = Material("keystone_jack_black", rgba=(0.02, 0.02, 0.025, 1.0))
LABEL_WHITE = Material("white_port_label", rgba=(0.88, 0.90, 0.86, 1.0))
BAR_ZINC = Material("zinc_cable_bar", rgba=(0.58, 0.60, 0.62, 1.0))


def _port_x(index: int) -> float:
    return (index - (PORT_COUNT - 1) / 2.0) * PORT_PITCH


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="patch_panel_24port_1u",
        meta={
            "port_count": PORT_COUNT,
            "rack_face_w_m": RACK_FACE_W,
            "u_height_m": U_HEIGHT,
        },
    )

    panel = model.part("panel")
    panel.visual(
        Box((RACK_FACE_W, PLATE_T, U_HEIGHT)),
        origin=Origin(xyz=(0.0, 0.0, U_HEIGHT / 2.0)),
        material=STEEL_BLACK,
        name="faceplate",
    )

    # Flush keystone openings and printed numbers, a hair proud of the face.
    mark_y = FRONT_Y - 0.0002
    for i in range(PORT_COUNT):
        x = _port_x(i)
        panel.visual(
            Box((PORT_W, 0.0004, PORT_H)),
            origin=Origin(xyz=(x, mark_y, PORT_ROW_Z)),
            material=JACK_DARK,
            name=f"port_rj45_{i + 1:02d}",
        )
        panel.visual(
            Box((LABEL_W, 0.0003, LABEL_H)),
            origin=Origin(xyz=(x, mark_y, LABEL_ROW_Z)),
            material=LABEL_WHITE,
            name=f"label_{i + 1:02d}",
        )

    # Rear cable-support bar on two brackets that seat against the plate.
    bracket_depth = BAR_Y - BAR_SQ / 2.0 - PLATE_T / 2.0
    for side, sx in (("bracket_left", -1.0), ("bracket_right", 1.0)):
        panel.visual(
            Box((BAR_SQ, bracket_depth, BAR_SQ)),
            origin=Origin(
                xyz=(sx * BRACKET_X, PLATE_T / 2.0 + bracket_depth / 2.0, U_HEIGHT / 2.0)
            ),
            material=BAR_ZINC,
            name=side,
        )
    panel.visual(
        Box((BAR_W, BAR_SQ, BAR_SQ)),
        origin=Origin(xyz=(0.0, BAR_Y, U_HEIGHT / 2.0)),
        material=BAR_ZINC,
        name="cable_bar",
    )

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    panel = object_model.get_part("panel")

    ctx.check(
        "single static plate",
        len(object_model.parts) == 1 and len(object_model.articulations) == 0,
        details=f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}",
    )

    names = {v.name for v in panel.visuals}
    ports = [n for n in names if n and n.startswith("port_rj45_")]
    ctx.check("24 keystone ports", len(ports) == PORT_COUNT, details=f"found {len(ports)}")

    aabb = ctx.part_world_aabb(panel)
    if aabb is None:
        ctx.fail("panel has measurable bounds", "no AABB")
    else:
        lo, hi = aabb
        dims = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        ctx.check(
            "full EIA rack face, 1U tall",
            0.482 <= dims[0] <= 0.484 and 0.0440 <= dims[2] <= 0.0450,
            details=f"dims={dims}",
        )

    row_width = (PORT_COUNT - 1) * PORT_PITCH + PORT_W
    ctx.check(
        "port row fits between mounting-hole columns",
        row_width < RACK_HOLE_SPAN - 0.010,
        details=f"row_width={row_width}",
    )

    return ctx.report()


object_model = build_object_model()
```
