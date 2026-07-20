# Network equipment QC checklist

This checklist verifies engineering constraints. It must NOT make the model
plainer: never omit, shrink, or simplify visible front-face detail (ports,
LEDs, labels, vents, latches, handles) to make a check easier to pass. The
front face should carry the same element density as the reference photo —
a dimensionally perfect but featureless slab is a FAILED result.

Before declaring the model finished, verify every applicable item:

- Rackmount unit: front face (ears included) is exactly 0.4826 m wide.
  The chassis BODY keeps the prompt's measured width (typically
  0.434-0.446 m) — ears make up the difference.
- Overall height matches the prompt's measured value when given (real units
  run 0.001-0.002 m short of n x 0.04445 m); use n x 0.04445 m only when
  the prompt gives no height.
- Mounting ears: hole columns 0.4651 m apart center-to-center; ears are
  flush with the front face plane.
- Front elements (RJ45/SFP ports, LEDs, buttons) are coplanar with or
  recessed 0.001-0.002 m behind the faceplate — never floating in front.
- Every door, rail, tray, or module articulation sweeps its full motion
  range without colliding into neighboring parts
  (verify with fail_if_parts_overlap_in_sampled_poses).
- Every motion limit declares explicit, physically plausible effort and
  velocity (doors ~30 N·m / 1.5 rad/s; rails ~80 N / 0.3 m/s) — never the
  1.0 defaults.
- No `floating` articulations; no `mimic` unless the prompt demanded it.
- Cable entry/exit paths (rear or top) are not blocked by solid geometry.
- Part names follow the domain conventions (chassis, ear_left, door_front,
  rail_left, port_rj45_01, fan_1, psu_1).
- All dimensions are module-level constants in SI meters, not inline
  literals scattered through builder code.
