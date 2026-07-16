<domain_network_equipment>
- When the request involves rackmount, network, server, datacenter, or telecom facility equipment (switches, routers, servers, rack cabinets, patch panels, cable trays, fiber distribution frames), read `docs/sdk/references/domain/network-equipment.md` with `read_file` before the first code edit and follow its canon.
- Hard rules for rackmount gear: front face including mounting ears is exactly 0.4826 m wide (19 in), height is an integer multiple of 0.04445 m (1U), mounting-hole columns are 0.4651 m apart. Declare these as module constants; never scale the rack face to fit other geometry.
- Use the document's part naming conventions (`chassis`, `ear_left`, `door_front`, `rail_left`, `port_rj45_01`, ...) so downstream tooling can identify parts.
- Do not use `floating` articulations, and set explicit physically plausible effort/velocity on every motion limit.
</domain_network_equipment>
