# OIC TB equipment generation prompts

One prompt per device in `equipment_registry.csv` — real OIC TB equipment
(source=`real_equipment_oic_tb`) plus AC 기준 자산(`reference_spec`).
Dimensions and mass come from the registry (SI-normalized). Run with the
domain QC checklist:

```bash
uv run articraft generate --qc-blurb qc/network_equipment_checklist.md "<prompt>"
```

Add `--image <front-photo>` when the reference photo DB (field survey) or a
datasheet front-view crop is available — image-conditioned runs are strictly
better. Front-panel descriptions below are drawn from public product layouts;
verify against the datasheet/photo before large batches.

Status legend: `[ready]` dims+mass confirmed · `[proxy]` similar-model dims ·
`[blocked]` needs field measurement.

---

## Servers

### 1. supermicro-sys1019d `[proxy]`
> A Supermicro SYS-1019D compact 1U short-depth server. EIA-310 rackmount:
> 438 mm wide body, 43 mm (1U) tall, only 381 mm deep, 11.34 kg. Flat
> sheet-metal front with a row of network ports (multiple RJ45 and two SFP+
> cages), small status LEDs, and ventilation perforation. Mounting ears with
> screw holes.

### 2. dell-r770 `[ready]`
> A Dell PowerEdge R770 2U rackmount server. 482 mm front face including
> mounting ears, 86.8 mm (2U) tall, 802 mm deep, 28.53 kg. Front: two
> horizontal rows of 2.5-inch hot-swap drive carriers with individual release
> latches and activity LEDs, a slim right-hand control bezel with power button
> and status display.

### 3. hpe-dl360-gen10 `[ready]`
> An HPE ProLiant DL360 Gen10 1U rackmount server. 434.6 mm wide, 42.9 mm
> (1U) tall, 707 mm deep, 16.78 kg. Front: eight 2.5-inch SFF hot-swap drive
> bays across the center-left with ejector levers, a right end-cap with power
> button, health LEDs and USB, HPE quick-release mounting ears.

### 4. dell-r6615 `[proxy]`
> A Dell PowerEdge R6615 1U rackmount server. 482 mm face, 42.8 mm (1U)
> tall, 772 mm deep, 20.4 kg. Front: a single row of 2.5-inch hot-swap drive
> carriers, right-hand control panel with power button and identification
> button, left mounting ear with luggage-tag service label.

### 5. dell-r760 `[ready]` — 레퍼런스 이미지가 베젤 장착 상태라 프롬프트 일치화(2026-07-16)
> A Dell PowerEdge R760 2U rackmount server with its front bezel installed.
> 482 mm face, 86.8 mm (2U) tall, 772 mm deep, 36.1 kg. Front: a black
> perforated bezel with a large hexagonal-hole pattern and a centered DELL
> logo, drive carrier LEDs faintly visible through the openings, a slim
> left ear panel with status light strip, power button and ports on the
> right ear panel.

### 6. hpe-dl380-gen10-8sff `[ready]`
> An HPE ProLiant DL380 Gen10 2U rackmount server in the 8-bay SFF
> configuration. 445.4 mm wide, 87.3 mm (2U) tall, 679.4 mm deep, 19.5 kg.
> Front: one 8-bay block of 2.5-inch hot-swap drives on the left, blank bay
> fillers to the right, universal media bay, power/health LED strip on the
> right ear.

### 7. hpe-dl380-gen10plus-a `[proxy]`
> An HPE ProLiant DL380 Gen10 Plus 2U rackmount server. 445.4 mm wide,
> 87.3 mm (2U) tall, 749 mm deep, 33.99 kg. Front: 2.5-inch SFF hot-swap
> bays in modular blocks, optical drive slot, right-hand power and health
> LED cluster, quick-release mounting ears.

### 8. hpe-dl380-gen10plus-b `[ready]`
> An HPE ProLiant DL380 Gen10 Plus 2U rackmount server (short-depth config).
> 445.4 mm wide, 87.3 mm (2U) tall, 710 mm deep, 28.77 kg. Same front layout
> as the Gen10 Plus: SFF drive blocks, blank fillers, right LED cluster.

### 9. dell-r730 `[ready]` — 로드쇼 실물, 사진 확보 최우선
> A Dell PowerEdge R730 2U rackmount server. 444 mm wide, 87.3 mm (2U) tall,
> 684 mm deep, 31.5 kg. Front: eight 3.5-inch hot-swap drive carriers in two
> rows, left control panel with LCD diagnostic display, right ear with
> power button, optional front bezel removed.

### 10. dell-xr2 `[ready]`
> A Dell EMC PowerEdge XR2 rugged 1U short-depth server. 482 mm face,
> 42.8 mm (1U) tall, 611 mm deep, 13.0 kg. Front: four 2.5-inch drive bays
> behind a reinforced face, recessed power button, rugged mounting ears with
> reinforced screw bosses.

## Network switches

### 11. arista-7010t-48 `[ready]` — 이미지 대조로 포트 배열 수정(2026-07-16)
> An Arista 7010T-48 1U rackmount access switch, shallow chassis: 445 mm
> wide, 44 mm (1U) tall, only 254 mm deep, 4.6 kg. Front: 48 RJ45 copper
> ports in three 16-port groups (each two rows of eight) with per-port link
> LEDs, four SFP+ uplink cages in a 2x2 block to their right, then console
> and management RJ45 ports, USB, and a small status LED column at the far
> right edge.

### 12. alcatel-os6450-48x `[ready]`
> An Alcatel-Lucent OmniSwitch 6450-48X 1U rackmount switch. 440 mm wide,
> 44 mm (1U) tall, 391 mm deep, 6.6 kg. Front: 48 RJ45 gigabit ports in two
> stacked rows of 24, two SFP+ uplink cages on the right, port LED matrix
> and console port on the far left.

### 13. cisco-n9k-93180yc-ex `[ready]` — 로드쇼 실물 + 기존 레코드 존재 (A/B 비교 대상)
> A Cisco Nexus 93180YC-EX 1U rackmount data-center switch. 439 mm wide,
> 44 mm (1U) tall, 571 mm deep, 7.8 kg. Front: 48 SFP28 cages in two rows
> of 24 with paired port LEDs, six QSFP28 uplink cages on the right in a
> 2x3 block, a narrow left legend strip with status LEDs and port numbering only (management and console ports are on the rear side, not the front).

### 14. arista-7280sr3-48yc8 `[ready]` — 실물 정면 사진 대조로 포트 배열 수정(2026-07-31): QSFP는 우측이 아니라 중앙
> An Arista 7280SR3-48YC8 1U rackmount router-switch. 439.9 mm wide,
> 43.5 mm (1U) tall, 467 mm deep, 9.18 kg. Front, three port blocks left
> to right: 24 SFP28 cages (ports 1-24) in two tight rows of twelve, then
> eight larger QSFP28 cages (ports 49-56) in the CENTER as two tight rows
> of four, then 24 more SFP28 cages (ports 25-48) in two tight rows of
> twelve. A teal port-number label band runs between the rows (blue over
> the QSFP block). Perforated ventilation rows above and below the port
> field, ARISTA logo and model name on the upper-left face, PS1/PS2
> status LEDs upper-right. No management or console ports on the front
> (they are on the rear beside the PSUs and the two fan modules).

### 21. arista-7050s-52 `[ready]` — 실물 사진 확보, 생성 완료(rec_...2aef4233, 2026-07-31)
> An Arista 7050S-52 1U rackmount data-center top-of-rack switch. 445 mm
> wide body, 44 mm (1U) tall, 406 mm deep, 7.71 kg. Front, left to right:
> 48 SFP+ cages as THREE separate groups of sixteen (ports 1-16, 17-32,
> 33-48), each group two tight rows of eight with a thin number strip
> between the rows; then a right-hand utility block with four more SFP+
> cages in a 2x2 block (ports 49-52), a USB port beneath, two stacked
> RJ45 (console above management) at the far right edge, and a vertical
> STATUS/FAN/PSU LED cluster above them. Port numbering pairs each column
> vertically: odd number top cage, even number directly below. ARISTA
> logo and model name lower-left. Rear: two hot-swap PSUs at the outer
> edges, four fan modules between them.

## Security appliances

### 15. secui-bluemax-nfg800 `[proxy]` — NGF 510 치수 대용
> A SECUI BLUEMAX NGF royal-blue 1U rackmount security gateway. 438 mm wide,
> 44 mm (1U) tall, 432 mm deep. Distinctive glossy blue sheet-metal front:
> a small rectangular LCD status panel with buttons on the left, a bank of
> eight RJ45 ports and four SFP cages on the right, brand lettering across
> the center, black mounting ears.

### 16. csni-appinsight-2000r `[ready]`
> A MonitorApp APPLICATION INSIGHT AIWAF-2000 2U rackmount web application
> firewall appliance. 438 mm wide, 88 mm (2U) tall, 598 mm deep, 15.2 kg.
> Front: modular NIC slot bays with 4-port blocks, small LCD status display
> with navigation buttons on the left, ventilation grille, dual redundant
> power supplies at the rear.

### 17. wins-sniper-one-2300 `[blocked — 현장 실측 후 진행]`
> (물리 치수 비공개. OIC TB 실측 후 프롬프트 확정. 참고: 1U/2U급 IPS
> 어플라이언스, Xeon Silver 4210R, 이중화 전원, 1G 4포트 NIC 슬롯 구조)

## Storage / GPU / Console

### 18. dell-unity-xt380 `[ready]` — 공식 스펙시트(h17713) DPE 값으로 교체(2026-08-03); 구값은 DAE 스펙 오기
> A Dell EMC Unity XT 380 2U storage array (25-drive disk processor
> enclosure). 447.6 mm wide, 88.8 mm (2U) tall, 613.9 mm deep, 24.6 kg
> (empty enclosure, drives excluded). Front: 25 vertical 2.5-inch drive
> slots across the full width with thin carrier latches and per-drive
> LEDs, thin top bezel strip with array status LEDs.

### 19. mitac-ft83-4u-gpu `[ready]` — 로드쇼 실물 + 기존 레코드 존재 (A/B 비교 대상)
> A MiTAC Thunder HX FT83 4U rackmount 10-GPU server. 439 mm wide, 175 mm
> (4U) tall, 831 mm deep, 39.3 kg. Front: two large square ventilation
> grilles with honeycomb perforation covering most of the face, a vertical
> control strip with power button and LEDs, heavy-duty mounting ears with
> handles.

### 20. hpe-lcd8500-console `[ready]` — 관절 장비: 편집/관절 예제 소재
> An HPE LCD8500 1U rackmount console: a slide-out KVM drawer with a
> fold-up 18.5-inch LCD. 436.1 mm wide, 42.3 mm (1U) tall, 433 mm deep,
> 5.2 kg. Closed pose: flat 1U drawer face with a recessed pull handle and
> two release latches. Articulations: the drawer slides forward on rails
> (prismatic, ~0.4 m travel) and the LCD lid flips up from the drawer
> (revolute, 0 to ~110 degrees), revealing the keyboard and touchpad
> beneath. Model both articulations with realistic limits.

### 22. dell-emc-unity-300 `[ready]` — 실물 사진 확보, 생성 완료(rec_...b2a7f9d0, 2026-07-30)
> A Dell EMC Unity 300 2U rackmount storage array — the 25-drive disk
> processor enclosure. 444.5 mm wide body, 86.4 mm (2U) tall, 613.9 mm
> deep, 20.0 kg. Front, left to right: a black left end cap with a
> vertical blue status LED strip and a recessed release handle; 25
> identical vertical 2.5-inch hot-swap drive carriers filling the full
> width in three visual groups of 8/9/8 (uniform 17.3 mm pitch, slightly
> wider seam between groups), each carrier a brushed-chrome upper
> faceplate with recessed label window, a bright ORANGE release latch
> block across its lower third, and a blue activity LED at the bottom;
> a black right end cap with power button and release handle. Name the
> carriers drive_bay_01..25 (static in v1) so ejection can be forked on
> later. z-fighting hazard: seat the top cover into a recessed body
> (cover >= 1 mm thick), never coplanar with the shell top.

## Enclosures

### 23. ac-server-rack-42u `[ready]` — AC 생성 기준 자산(실물 아님), 최종 rec_...6fe37d9f
> A closed 42U server rack cabinet, 600 mm wide, 2.0 m tall, 1070 mm
> deep, 125.09 kg empty (mass borrowed from the APC NetShelter SX AR3100
> class). Articulations follow the adopted cabinet-door pattern:
> door_front revolute about the vertical hinge edge 0..2.27 rad (effort
> 30, velocity 1.5, damping 1.2, friction 0.45); handle_1 swing-handle
> turn revolute about the door normal 0..90 deg; handle_lever_1 lift-out
> revolute as a CHILD of handle_1, 0..60 deg; latch_cam_1 mimics the turn
> joint only (never the lift); release_button_1 an independent 6 mm
> prismatic spring trigger at the BOTTOM of the escutcheon (below lever
> pocket and lock cylinder), causal intent in meta.positive_motion, not
> mimic-coupled. All joints rest at 0 within limits.
