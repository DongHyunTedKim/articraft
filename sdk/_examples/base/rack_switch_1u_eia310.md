---
title: '1U Rackmount Network Switch with EIA-310 Ears'
description: 'Nexus-style 1U switch: 482.6mm rack face, 44.45mm (1U) height, three 2x8 RJ45 clusters at real port size in tight vertical pairs and a 2x2 SFP+ uplink cluster as real recessed cavities cut into the sheet-metal chassis, EIA-310 mounting ears with screw holes.'
tags:
  - rack
  - rackmount
  - 1u
  - switch
  - network
  - rj45
  - sfp-plus
  - sfp
  - eia-310
  - mounting-ear
  - chassis
  - telecom
  - datacenter
---

Rackmount canon: the front face including mounting ears is exactly 0.4826 m
(19 in); the body between the ears is 0.438 m; height is 1U = 0.04445 m.
Declare these as module constants. Port openings are modeled as real recessed
cavities (CadQuery cuts with a rear wall), not decals: each cavity gets a dark
backing visual and RJ45 cavities get a gold contact strip, so the front reads
correctly at inspection distance.

```python
from __future__ import annotations

import cadquery as cq

from sdk import (
    ArticulatedObject,
    Box,
    Material,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)


BODY_WIDTH = 0.438          # 19 in rack body between mounting ears, meters
RACK_WIDTH = 0.4826         # standard rack face width including ears
BODY_DEPTH = 0.460
U1_HEIGHT = 0.04445
EAR_WIDTH = (RACK_WIDTH - BODY_WIDTH) / 2.0
EAR_DEPTH = 0.018
FRONT_Y = -BODY_DEPTH / 2.0
PORT_RECESS = 0.010

RJ_SIZE = (0.0150, 0.0130)      # RJ45 aperture at real size (15 x 13 mm)
RJ_PITCH = (0.0154, 0.0145)     # row pitch 14.5 = 13 port + 1.5 tight pair gap
SFP_SIZE = (0.0145, 0.0095)     # SFP+ uplink cage at real size
SFP_PITCH = (0.0160, 0.0105)
CLUSTER_GAP = 0.008

METAL = Material("cool_galvanized_sheet_metal", rgba=(0.62, 0.66, 0.68, 1.0))
DARK = Material("black_recess_shadow", rgba=(0.015, 0.016, 0.018, 1.0))
DARK_GREY = Material("dark_vent_perforation", rgba=(0.05, 0.055, 0.058, 1.0))
WHITE = Material("white_port_numbering", rgba=(0.88, 0.90, 0.86, 1.0))
BLUE = Material("pale_blue_asset_label", rgba=(0.58, 0.78, 0.90, 1.0))
GOLD = Material("muted_contact_gold", rgba=(0.92, 0.70, 0.25, 1.0))


def _port_centers(center_x: float, cols: int, rows: int, pitch: tuple[float, float]) -> list[tuple[float, float, int, int]]:
    """Return (x, z, row, col) port centers on the front panel."""
    centers: list[tuple[float, float, int, int]] = []
    for row in range(rows):
        z = U1_HEIGHT / 2.0 + (row - (rows - 1) / 2.0) * pitch[1]
        for col in range(cols):
            x = center_x + (col - (cols - 1) / 2.0) * pitch[0]
            centers.append((x, z, row, col))
    return centers


def _all_port_layouts() -> tuple[list[tuple[int, float, float, int, int]], list[tuple[float, float, int, int]]]:
    rj_cluster_width = (8 - 1) * RJ_PITCH[0] + RJ_SIZE[0]
    sfp_cluster_width = (2 - 1) * SFP_PITCH[0] + SFP_SIZE[0]
    total_width = 3 * rj_cluster_width + 3 * CLUSTER_GAP + sfp_cluster_width
    cursor = -total_width / 2.0

    rj_ports: list[tuple[int, float, float, int, int]] = []
    for cluster in range(3):
        center_x = cursor + rj_cluster_width / 2.0
        for x, z, row, col in _port_centers(center_x, 8, 2, RJ_PITCH):
            rj_ports.append((cluster, x, z, row, col))
        cursor += rj_cluster_width + CLUSTER_GAP

    cursor += CLUSTER_GAP - CLUSTER_GAP  # keep the explicit final inter-family gap in the formula above
    sfp_center_x = cursor + sfp_cluster_width / 2.0
    sfp_ports = _port_centers(sfp_center_x, 2, 2, SFP_PITCH)
    return rj_ports, sfp_ports


def _box_cutter(width: float, height: float, x: float, z: float, depth: float = PORT_RECESS) -> cq.Workplane:
    # The cutter begins slightly in front of the face and stops inside the chassis,
    # leaving a real rear wall so each opening is a recessed cavity, not a tunnel.
    cutter_depth = depth + 0.003
    y = FRONT_Y + depth / 2.0 - 0.0015
    return cq.Workplane("XY").box(width, cutter_depth, height).translate((x, y, z))


def _build_chassis_body() -> cq.Workplane:
    body = cq.Workplane("XY").box(BODY_WIDTH, BODY_DEPTH, U1_HEIGHT).translate((0.0, 0.0, U1_HEIGHT / 2.0))

    rj_ports, sfp_ports = _all_port_layouts()
    for _cluster, x, z, _row, _col in rj_ports:
        body = body.cut(_box_cutter(RJ_SIZE[0], RJ_SIZE[1], x, z))
    for x, z, _row, _col in sfp_ports:
        body = body.cut(_box_cutter(SFP_SIZE[0], SFP_SIZE[1], x, z))

    # Shallow sheet-metal panel seams across the front face, visible on Nexus-style appliances.
    seam_height = 0.0014
    for z in (0.0065, U1_HEIGHT - 0.0065):
        body = body.cut(_box_cutter(BODY_WIDTH - 0.022, seam_height, 0.0, z, depth=0.0022))

    return body


def _build_ear_plate() -> cq.Workplane:
    ear = cq.Workplane("XY").box(EAR_WIDTH, EAR_DEPTH, U1_HEIGHT)
    screw_holes = (
        cq.Workplane("XZ")
        .pushPoints([(0.0, -0.0125), (0.0, 0.0125)])
        .circle(0.0033)
        .extrude(EAR_DEPTH + 0.004, both=True)
    )
    ear = ear.cut(screw_holes)
    ear = ear.edges("|Y").fillet(0.0012)
    return ear


def _add_port_backing_visuals(chassis, rj_ports, sfp_ports) -> None:
    backing_thickness = 0.0008
    backing_y = FRONT_Y + PORT_RECESS - backing_thickness / 2.0

    for cluster, x, z, row, col in rj_ports:
        chassis.visual(
            Box((RJ_SIZE[0] * 0.78, backing_thickness, RJ_SIZE[1] * 0.62)),
            origin=Origin(xyz=(x, backing_y, z)),
            material=DARK,
            name=f"rj_{cluster}_{row}_{col}",
        )
        # One thin gold contact strip is seated into the rear wall of each cavity so it is supported.
        chassis.visual(
            Box((RJ_SIZE[0] * 0.62, backing_thickness * 0.75, 0.0009)),
            origin=Origin(xyz=(x, backing_y - backing_thickness * 0.30, z - RJ_SIZE[1] * 0.28)),
            material=GOLD,
            name=f"rj_contact_{cluster}_{row}_{col}",
        )

    for x, z, row, col in sfp_ports:
        chassis.visual(
            Box((SFP_SIZE[0] * 0.82, backing_thickness, SFP_SIZE[1] * 0.62)),
            origin=Origin(xyz=(x, backing_y, z)),
            material=DARK,
            name=f"sfp_{row}_{col}",
        )


def _add_front_surface_details(chassis) -> None:
    # Two perforation bands are represented as many dark, flush rectangular marks on the sheet metal.
    mark_y = FRONT_Y - 0.0002
    pitch = 0.0052
    count = 80
    start = -(count - 1) * pitch / 2.0
    for row, z in enumerate((0.0042, U1_HEIGHT - 0.0042)):
        for i in range(count):
            x = start + i * pitch
            chassis.visual(
                Box((0.0016, 0.0004, 0.0011)),
                origin=Origin(xyz=(x, mark_y, z)),
                material=DARK_GREY,
                name=f"vent_{row}_{i}",
            )

    # Small front-panel status dots and a top paper label echo the referenced Nexus front view.
    for i, z in enumerate((0.014, 0.019, 0.024, 0.029)):
        chassis.visual(
            Box((0.0022, 0.00045, 0.0022)),
            origin=Origin(xyz=(-BODY_WIDTH / 2.0 + 0.008, mark_y, z)),
            material=WHITE,
            name=f"status_dot_{i}",
        )

    chassis.visual(
        Box((0.060, 0.040, 0.0005)),
        origin=Origin(xyz=(-0.120, -0.090, U1_HEIGHT + 0.00025)),
        material=BLUE,
        name="top_asset_label",
    )


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="nexus_style_1u_rack_switch",
        meta={
            "rj_cluster_count": 3,
            "rj_ports_per_cluster": 16,
            "sfp_uplink_ports": 4,
            "rack_width_m": RACK_WIDTH,
            "u_height_m": U1_HEIGHT,
        },
    )

    chassis = model.part("chassis")
    chassis.visual(
        mesh_from_cadquery(_build_chassis_body(), "recessed_sheet_metal_chassis", tolerance=0.00045),
        origin=Origin(),
        material=METAL,
        name="body_shell",
    )

    ear_mesh = _build_ear_plate()
    y_ear = FRONT_Y + EAR_DEPTH / 2.0
    for side, sign in (("ear_left", -1.0), ("ear_right", 1.0)):
        chassis.visual(
            mesh_from_cadquery(ear_mesh, side, tolerance=0.00035),
            origin=Origin(xyz=(sign * (BODY_WIDTH / 2.0 + EAR_WIDTH / 2.0), y_ear, U1_HEIGHT / 2.0)),
            material=METAL,
            name=side,
        )

    rj_ports, sfp_ports = _all_port_layouts()
    _add_port_backing_visuals(chassis, rj_ports, sfp_ports)
    _add_front_surface_details(chassis)

    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)
    chassis = object_model.get_part("chassis")

    ctx.check(
        "single fixed chassis part",
        len(object_model.parts) == 1 and len(object_model.articulations) == 0,
        details=f"parts={len(object_model.parts)}, articulations={len(object_model.articulations)}",
    )

    visual_names = {visual.name for visual in chassis.visuals}
    rj_ports = [name for name in visual_names if name and name.startswith("rj_") and name.split("_")[1].isdigit()]
    sfp_ports = [name for name in visual_names if name and name.startswith("sfp_")]
    ctx.check("three 2-by-8 RJ45 clusters", len(rj_ports) == 48, details=f"found {len(rj_ports)} RJ45 cavities")
    ctx.check("one 2-by-2 SFP+ uplink cluster", len(sfp_ports) == 4, details=f"found {len(sfp_ports)} SFP+ cavities")

    aabb = ctx.part_world_aabb(chassis)
    if aabb is None:
        ctx.fail("rack switch has measurable bounds", "no chassis AABB")
    else:
        lo, hi = aabb
        dims = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        ctx.check(
            "1U rackmount proportions",
            0.480 <= dims[0] <= 0.486 and 0.455 <= dims[1] <= 0.465 and 0.044 <= dims[2] <= 0.046,
            details=f"dims={dims}",
        )

    # Representative black backs sit well behind the front face, proving the ports are recessed cavities.
    rj_aabb = ctx.part_element_world_aabb(chassis, elem="rj_0_0_0")
    sfp_aabb = ctx.part_element_world_aabb(chassis, elem="sfp_0_0")
    for label, elem_aabb in (("RJ45", rj_aabb), ("SFP+", sfp_aabb)):
        if elem_aabb is None:
            ctx.fail(f"{label} representative cavity exists", "missing visual AABB")
        else:
            lo, hi = elem_aabb
            ctx.check(
                f"{label} cavity backing is recessed",
                lo[1] > FRONT_Y + 0.0085 and hi[1] <= FRONT_Y + PORT_RECESS + 0.0002,
                details=f"front_y={FRONT_Y}, aabb={elem_aabb}",
            )

    return ctx.report()


object_model = build_object_model()
```
