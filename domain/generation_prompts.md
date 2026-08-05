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

### 6. hpe-dl380-gen10-8sff `[ready]` — 실물 대조로 전면 배열 전면 수정, 2변형 생성 완료(2026-08-03)
> An HPE ProLiant DL380 Gen10 2U rackmount server in the 8-bay SFF
> configuration. 445.4 mm wide body, 482.6 mm face across the rack ears,
> 87.3 mm (2U) tall, 679.4 mm deep, 19.5 kg. Front, left to right — three
> EQUAL-width boxes (~140 mm each, per the datasheet diagram) left of a
> narrow control strip: Box 1 (blank filler, or universal media bay in the
> media-bay variant: DVD-RW slot + eject, USB / display port / USB row,
> vent panel), Box 2 blank filler, Box 3 the 8-bay block of vertical
> 2.5-inch hot-swap SFF carriers (numbered 1-8). Then the vertical control
> strip: four square LEDs stacked (power, health, NIC, blue UID), below
> them iLO service port then USB 3.0, both portrait-oriented. Both ears
> wear full-height black latch covers protruding ~8 mm (no exposed screw
> holes); left cover Drive Box ID label, right cover HPE badge +
> ProLiant DL380 Gen10 plate.
>
> 주의(과거 오류): 초판 프롬프트의 "drive block on the left"는 실물과
> 반대(드라이브는 우측). LED·포트를 가로로 깔거나 드라이브 블록이 전면
> 절반을 차지하는 회귀도 반복됨 — 균등 3분할과 세로 컨트롤 스트립을
> 명시할 것. 생성 완료: 미디어베이 無 rec_...f8b34dbd / 有
> rec_...6088ca90 (물성 19.5 kg 분배 포함, 2026-08-03).

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

### 11. arista-7010t-48 `[ready]` — 신 SOP 재생성 완료(rec_...2bb37860, 2026-08-04); 구 gridfix 폐기
> An Arista 7010T-48 1U rackmount access switch in a light-gray chassis,
> shallow: 445 mm wide body, 482.6 mm face, 44 mm (1U) tall, only 254 mm
> deep, 4.6 kg. Front: ARISTA 7010T-48 top-left; 48 RJ45 as THREE 16-port
> groups (two tight rows of eight), EACH group enclosed by a thin raised
> bezel frame (~1.5 mm face, >=0.5 mm proud) wrapping both rows and the
> light number band between them (odd top with up-triangle, even bottom
> with down-triangle). Stacked rows are MIRROR-mounted (top jacks
> notch-up, contacts bottom; bottom jacks opposite); every aperture the
> true RJ45 silhouette with subtly different interior colors (cavity /
> contact block / gold pins / latch floor). Right: four SFP+ cages 2x2
> (ports 49-52), square vent patches, console-over-management RJ45 stack
> (IOIOI legend), vertical USB, STATUS/FAN/PS1/PS2 LED column. Distribute
> the 4.6 kg across links; no two visible faces coplanar.

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

## Patch panels / consoles (2026-08-03 신규)

### 24. gaon-cat6-pp24 `[ready]` — 실측 치수, 생성 완료(rec_...63efac50, 2026-08-03)
> A GAON (Gaon Cable) CAT.6 24-port 1U rackmount UTP patch panel. 482.6 mm
> wide flat face plate spanning the rack with oval mounting slots at each
> end, 44.45 mm (1U) tall, body 32 mm deep plus a rear cable-management
> bracket to ~95 mm total, 0.75 kg. Front, left to right: GAON logo; 24
> RJ45 jacks in a single row as FOUR blocks of six, each block topped by a
> recessed white label strip; port numbers 1-24 below; CAT.6 marking right.
> Each jack aperture is the RJ45 silhouette — a wide opening plus a
> narrower bottom-center latch-tab notch (upside-down T), cut 2-3 mm deep.
> Rear: 24 punch-down blocks + lacing bar. Static, jacks named
> port_01..24. Distribute the 0.75 kg across all links with box-approx
> inertia. No two visible faces coplanar (label strips must not reach the
> faceplate rear plane).

### 25. aten-cl5716n `[ready]` — 공식 데이터시트, 생성 완료(rec_...3d9b32e6, 2026-08-03)
> An ATEN CL5716N Slideaway 16-port LCD KVM switch: a 1U slide-out console
> drawer with a fold-up 19-inch LCD. 480 mm wide body, 482.6 mm face
> across the mounting brackets, 44 mm (1U) tall, 689.2 mm deep, 13.65 kg.
> Closed: flat 1U face — LCD lid top cover with ribbed center grip, two
> release latch sliders, slim drawer bar with USB Type-A and a green POWER
> LED right, ATEN logo centered. Articulations: drawer prismatic ~0.45 m;
> LCD lid revolute 0..110 deg revealing keyboard + touchpad + port
> pushbutton/LED strip. Distribute the 13.65 kg across links with
> box-approx inertia. z-fighting hazards fixed in v1: bezel strips must
> sit inboard of the lid outer planes; screen backing recessed below the
> bezel frame; logo glyphs from non-overlapping boxes.

## Rack accessories / firewalls / shelves (2026-08-04 신규)

### 26. lacing-bar-offset-1u + lacing-bar-flat-1u `[ready]` — 2계열 x 4변형 = 8종 생성 완료(2026-08-04, 전량 원샷 클린)
> (offset) A 1U 19-inch rack cable lacing bar in galvanized silver steel.
> 482.6 mm across the end mounting flanges with EIA-pattern holes;
> Z-shaped end brackets offset the bar about 50 mm behind the mounting
> plane. The bar is a shallow hat-channel strip ~20 mm tall, 2 mm thick,
> with a single centered row of N square lacing holes (about 10 x 10 mm,
> uniform pitch). 0.5 kg distributed across links.
>
> (flat) A flat steel strip 482.6 x ~22 x 2 mm mounted FLUSH against the
> posts, one screw hole at each end - no brackets, no channel. Single row
> of N square slots. 0.2 kg distributed.
>
> 변형은 N(18/20/22/24)만 변경 - 같은 스팬에서 피치만 조정하는 fork가
> 가장 싸다. 공통: 참조 사진의 케이블·벨크로는 "ignore ..."로 제외,
> box-approx inertia 합계 정확히 일치, 가시면 동일평면 금지.

### 27. fortinet-fg601e `[ready]` — 생성 완료(rec_...ea2a88fb, 2026-08-04)
> A Fortinet FortiGate 601E 1U rackmount NGFW in a WHITE light-gray
> chassis. 432 mm body, 482.6 mm face, 44.45 mm (1U), 380 mm deep,
> 7.5 kg. Front, left to right: Fortinet mark + FortiGate 601E label
> top-left with a barcode strip beneath, round-hole vent field below,
> the four-LED column (STATUS/ALARM/HA/POWER) standing separately right
> of that field; a second vent patch above USB/CONSOLE; two stacked blue
> USB 3.0 ports each with a slot beneath; CONSOLE RJ45 with metal bezel;
> HA(top)/MGMT(bottom) stack; a LARGE 9x7 staggered honeycomb vent
> between the service zone and the data ports; 8 GE RJ45 as two 2x2
> blocks (odd top / even bottom); 8 SFP as two 2x2 blocks; SFP+ X1/X2
> vertical pair. Ears with exactly TWO screw holes each. Rear: four fan
> modules, blank PSU2 bay, one AC PSU (C14). 7.5 kg distributed.
>
> 표준 문구 (모든 RJ45 장비에 재사용): (1) "stacked RJ45 pairs are
> MIRROR-mounted - top jack latch-notch UP with contacts near the
> bottom, bottom jack the opposite; single jacks notch-down." (2) "port
> interior parts in subtly DIFFERENT colors for simulator readability -
> near-black cavity, lighter dark-gray contact block, gold pin row,
> medium-dark latch floor."

### 28. netapp-naj1501 `[ready]` — 생성 완료(rec_...39d2deb3, 2026-08-04)
> A NetApp NAJ-1501 2U rackmount storage shelf chassis with its front
> bezel installed. 447 mm body, 482.6 mm face, 86.4 mm (2U), 484 mm
> deep, 24.4 kg fully populated (empty 16 kg). TWO-LAYER bezel: a
> brushed-SILVER outer diamond-lattice frame with curved top/bottom
> bands, over a recessed FINER dark mesh screen (>=2 mm behind, visible
> through the diamond openings); a white label plate left-of-center with
> the blue NetApp cube logo (non-overlapping glyph boxes); black left
> end cap with three icons (power/attention/location) and a two-digit
> green seven-segment shelf-ID display (raised glyphs); plain black
> right end cap. Ears: slim dark flanges with two oval slots per U.
> Rear: plain flat panel - 자료 없음, 포트·팬 지어내지 말 것. 내부
> 드라이브 비모델링(베젤 장착 상태).

### 29. agilent-e7900a `[proxy]` — 생성 완료(rec_...daf4573e, 2026-08-05)
> Agilent E7900A RouterTester 900 four-slot network test chassis, a
> freestanding benchtop instrument (NOT rack-mounted). 425 x 88.1 x
> 500 mm cream/ivory Agilent beige; molded rounded end caps wrap the
> left/right front edges (caps overhang every neighbor plane); four
> rubber feet. 11.0 kg distributed. FRONT: cream fascia strip (Agilent
> logo left, model plate right); 2x2 module grid over thin bay rails;
> far-left vertical recessed power strip with black rocker switch.
> Modules: E5216A (light blue-gray, 2 yellow-framed GBIC ports, TX/RX
> LEDs, lime XP badge) / E7920A (royal blue, 12 gold coax in a row =
> six TX/RX pairs, SGNL/ALRM dots) / E7919A x2 (royal blue, 2 GBIC
> ports, orange Routing badge - lettering sized INSIDE the badge with
> margin). Each module: green LED display reading 'RIP' at left, white
> ejector latch, silver thumbscrews. REAR: recessed blue-gray
> controller panel (RJ45 MDI/MDI-X + LINK/ACT, D-sub15 DAISY CHAIN
> IN=lime/OUT=pink fields, BNC IN/OUT + 10MHz + 1PPS, SERIAL RJ45),
> large recessed label field center, IEC C14 right. 치수·질량 추정치
> (공개 데이터시트 없음). 표준 문구(2) 포트 내부 색 구분 적용.
