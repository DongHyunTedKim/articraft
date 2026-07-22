<domain_network_equipment>
- When the request involves rackmount, network, server, datacenter, or telecom facility equipment (switches, routers, servers, rack cabinets, patch panels, cable trays, fiber distribution frames), read `docs/sdk/references/domain/network-equipment.md` with `read_file` before the first code edit and follow its canon.
- Hard rules for rackmount gear: the chassis BODY keeps the prompt's measured dimensions; bolted-on mounting ears bring the front face to exactly 0.4826 m (19 in), hole columns 0.4651 m apart. A prompt width below 0.470 m is the body width — add ears on top of it. Keep the prompt's measured height (real units run slightly short of n x 0.04445 m). Declare dimensions as module constants; never scale the rack face to fit other geometry.
- Use the document's part naming conventions (`chassis`, `ear_left`, `door_front`, `rail_left`, `port_rj45_01`, ...) so downstream tooling can identify parts.
- Repeated front elements (ports, drive bays): real aperture sizes, uniform pitch, tight vertical pairs (rows 1-3 mm apart), each element a single named visual (port_rj45_01) — never assembled from strips; follow the reference photo for asymmetric layouts.
- Do not use `floating` articulations, and set explicit physically plausible effort/velocity on every motion limit.
</domain_network_equipment>
