---
title: '42U Server Rack Cabinet with Hinged Front Door'
description: 'Enclosed 42U rack cabinet (600 x 1000 x 2000 mm): steel panel shell, four vertical EIA-310 mounting rails at 465.1mm hole span, and a front door on a revolute hinge swinging 130 degrees outward with realistic joint limits.'
tags:
  - rack
  - cabinet
  - 42u
  - server
  - enclosure
  - door
  - hinge
  - revolute
  - eia-310
  - rail
  - datacenter
  - telecom
---

Cabinet canon: 600 mm wide, 1000 mm deep, ~2000 mm tall for 42U. The four
internal mounting rails carry the EIA-310 hole span (465.1 mm between hole
columns). The front door is a separate part on a `revolute` hinge at the left
front corner; the hinge axis points down (`(0,0,-1)`) so positive joint travel
swings the door outward and clear of the cabinet. The closed pose keeps a
1 mm clearance in front of the frame so nothing overlaps, and `run_tests`
sweeps the hinge range to prove the door never collides.

```python
from __future__ import annotations

from sdk import (
    ArticulatedObject,
    Box,
    Material,
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
)

# EIA-310 canon (SI meters)
RACK_HOLE_SPAN = 0.4651
U_HEIGHT = 0.04445

CAB_W = 0.600
CAB_D = 1.000
CAB_H = 2.000
PANEL_T = 0.015
INNER_H = CAB_H - 2 * PANEL_T

DOOR_W = 0.580
DOOR_H = CAB_H - 0.040
DOOR_T = 0.018
DOOR_GAP = 0.001            # closed-pose clearance in front of the frame
HINGE_INSET = 0.009

RAIL_W = 0.040
RAIL_D = 0.020
RAIL_X = RACK_HOLE_SPAN / 2.0
FRONT_RAIL_Y = -CAB_D / 2.0 + 0.100
REAR_RAIL_Y = CAB_D / 2.0 - 0.250

DOOR_SWING = 2.27           # ~130 degrees

FRAME = Material("powder_coated_steel", rgba=(0.16, 0.17, 0.19, 1.0))
DOOR_STEEL = Material("perforated_door_steel", rgba=(0.13, 0.14, 0.16, 1.0))
HANDLE_ZINC = Material("cast_zinc_handle", rgba=(0.72, 0.73, 0.75, 1.0))
RAIL_ZINC = Material("zinc_plated_rail", rgba=(0.55, 0.58, 0.60, 1.0))


def build_object_model() -> ArticulatedObject:
    model = ArticulatedObject(
        name="rack_cabinet_42u_hinged_door",
        meta={
            "u_capacity": 42,
            "rack_hole_span_m": RACK_HOLE_SPAN,
            "door_swing_rad": DOOR_SWING,
        },
    )

    cabinet = model.part("cabinet")
    cabinet.visual(
        Box((CAB_W, CAB_D, PANEL_T)),
        origin=Origin(xyz=(0.0, 0.0, PANEL_T / 2.0)),
        material=FRAME,
        name="panel_bottom",
    )
    cabinet.visual(
        Box((CAB_W, CAB_D, PANEL_T)),
        origin=Origin(xyz=(0.0, 0.0, CAB_H - PANEL_T / 2.0)),
        material=FRAME,
        name="panel_top",
    )
    for name, sx in (("panel_side_left", -1.0), ("panel_side_right", 1.0)):
        cabinet.visual(
            Box((PANEL_T, CAB_D, INNER_H)),
            origin=Origin(xyz=(sx * (CAB_W - PANEL_T) / 2.0, 0.0, CAB_H / 2.0)),
            material=FRAME,
            name=name,
        )
    cabinet.visual(
        Box((CAB_W - 2 * PANEL_T, PANEL_T, INNER_H)),
        origin=Origin(xyz=(0.0, (CAB_D - PANEL_T) / 2.0, CAB_H / 2.0)),
        material=FRAME,
        name="panel_rear",
    )
    # Four vertical EIA mounting rails span bottom panel to top panel.
    for name, rx, ry in (
        ("rail_front_left", -RAIL_X, FRONT_RAIL_Y),
        ("rail_front_right", RAIL_X, FRONT_RAIL_Y),
        ("rail_rear_left", -RAIL_X, REAR_RAIL_Y),
        ("rail_rear_right", RAIL_X, REAR_RAIL_Y),
    ):
        cabinet.visual(
            Box((RAIL_W, RAIL_D, INNER_H)),
            origin=Origin(xyz=(rx, ry, CAB_H / 2.0)),
            material=RAIL_ZINC,
            name=name,
        )

    # Door geometry lives in the hinge frame: axis at local (0, 0), panel extends +x.
    door = model.part("door_front")
    door.visual(
        Box((DOOR_W, DOOR_T, DOOR_H)),
        origin=Origin(xyz=(DOOR_W / 2.0, 0.0, DOOR_H / 2.0)),
        material=DOOR_STEEL,
        name="door_panel",
    )
    door.visual(
        Box((0.020, 0.012, 0.140)),
        origin=Origin(xyz=(DOOR_W - 0.035, -(DOOR_T / 2.0 + 0.006), DOOR_H / 2.0)),
        material=HANDLE_ZINC,
        name="handle_1",
    )

    model.joint(
        "door_front_hinge",
        "revolute",
        "cabinet",
        "door_front",
        origin=Origin(
            xyz=(-CAB_W / 2.0 + HINGE_INSET, -CAB_D / 2.0 - DOOR_GAP - DOOR_T / 2.0, 0.020)
        ),
        axis=(0.0, 0.0, -1.0),
        limit=MotionLimits(lower=0.0, upper=DOOR_SWING, effort=30.0, velocity=1.5),
        dynamics=MotionProperties(damping=0.5, friction=0.2),
    )
    return model


def run_tests() -> TestReport:
    ctx = TestContext(object_model)

    ctx.check(
        "cabinet plus hinged door",
        len(object_model.parts) == 2 and len(object_model.articulations) == 1,
        details=f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}",
    )

    hinge = object_model.get_joint("door_front_hinge")
    ctx.check(
        "door hinge is a limited revolute with real dynamics",
        hinge.articulation_type.value == "revolute"
        and hinge.motion_limits is not None
        and abs(hinge.motion_limits.upper - DOOR_SWING) < 1e-9
        and hinge.motion_limits.effort == 30.0,
        details=f"limits={hinge.motion_limits}",
    )

    cabinet = object_model.get_part("cabinet")
    aabb = ctx.part_world_aabb(cabinet)
    if aabb is None:
        ctx.fail("cabinet has measurable bounds", "no AABB")
    else:
        lo, hi = aabb
        dims = (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])
        ctx.check(
            "42U cabinet proportions",
            0.595 <= dims[0] <= 0.605 and 0.995 <= dims[1] <= 1.005 and 1.995 <= dims[2] <= 2.005,
            details=f"dims={dims}",
        )
        ctx.check(
            "rails leave EIA hole span",
            abs(2 * RAIL_X - RACK_HOLE_SPAN) < 1e-9,
            details=f"rail_span={2 * RAIL_X}",
        )

    # Sweep the hinge range: the door must clear the shell in every sampled pose.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=16)

    return ctx.report()


object_model = build_object_model()
```
