"""Package records as handoff assets for the environment team.

Usage:
    uv run python domain/make_handoff.py <record-id> [<record-id> ...]

Builds handoff/<asset_name>/ (model.urdf with renamed robot, meshes,
README) + <asset_name>.zip per record. Asset names follow the convention
in domain/README.md: <src>_<category>_<form>_<vendor>_<ref>style_v<n>,
with versions auto-numbered per base name by record timestamp, continuing
from whatever already exists in handoff/.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HANDOFF = REPO / "handoff"

# slug fragment -> (category, form, vendor, ref, display name)
DEVICE_MAP = {
    "arista-7010t": ("switch", "1u", "arista", "7010t", "Arista 7010T-48 1U 스위치"),
    "cisco-nexus-93180yc": ("switch", "1u", "cisco", "93180yc", "Cisco Nexus 93180YC-EX 1U 스위치"),
    "dell-poweredge-r760": ("server", "2u", "dell", "r760", "Dell PowerEdge R760 2U 서버"),
    "hpe-proliant-dl360": ("server", "1u", "hpe", "dl360", "HPE ProLiant DL360 Gen10 1U 서버"),
}

README_TMPL = """{asset}
{display} - AI 생성 3D 자산
{bar}

*** 본 모델은 제조사 공식 CAD가 아닙니다 ***
Articraft(LLM 기반 생성기)가 참조 사진과 공개 스펙을 바탕으로 생성한
자산으로, 실제 제품과 세부 형상이 다를 수 있습니다. 제조사 원본
모델(oem_*)이나 구매 모델(cg_*)과 구분하기 위해 ac_ 접두어를 사용합니다.

생성: Articraft, {date} / 내부 육안 평가 {rating}/5
원본 레코드: {record_id}

구성:
  model.urdf          - 관절형 모델 정의 (루트 파일, 이걸 로드하세요)
  assets/meshes/*.obj - 시각 메시 (URDF가 상대경로로 참조)

사양:
  - 단위: 미터(m) / 라디안(rad), 스케일 변환 불필요
  - 전체 치수(실측 바운딩박스): {dims}
  - 관절: {joints}
  - 좌표계: Z-up

로드 방법:
  - Isaac Sim: File > Import > URDF (거리 스케일 1.0)
  - Blender: URDF importer 애드온 또는 OBJ 직접 임포트
  - 임의 URDF 로더: model.urdf 기준, 폴더 구조 유지 필수

주의:
  - 충돌(collision) 지오메트리는 시각 메시와 동일(볼록 분해 미적용).
    물리 시뮬레이션 용도면 임포터의 convex decomposition 옵션 권장
  - 재질은 URDF 색상(rgba)만 포함, 텍스처 없음
"""


def detect_device(record_id: str):
    slug = record_id.replace("_", "-")
    for frag, meta in DEVICE_MAP.items():
        if frag in slug:
            return meta
    return None


def measured_dims_mm(record_id: str) -> str:
    sys.path.insert(0, str(REPO))
    from domain.experiments.measure import model_metrics

    m = model_metrics(REPO / "data" / "records" / record_id)
    w, d, h = (round(v * 1000, 1) for v in m["dims"])
    return f"{w} x {h} x {d} mm (W x H x D)"


def joints_desc(urdf_text: str) -> str:
    joints = re.findall(r'<joint name="([^"]+)" type="([^"]+)"', urdf_text)
    movable = [(n, t) for n, t in joints if t != "fixed"]
    fixed_n = len(joints) - len(movable)
    parts = [f"{n}({t})" for n, t in movable]
    if fixed_n:
        parts.append(f"고정 {fixed_n}개")
    return ", ".join(parts) if parts else "없음 (단일 강체)"


def next_version(base: str) -> int:
    existing = (
        [p.name for p in HANDOFF.iterdir() if p.name.startswith(base)] if HANDOFF.exists() else []
    )
    versions = [int(m.group(1)) for n in existing for m in [re.search(r"_v(\d+)", n)] if m]
    return max(versions, default=0) + 1


def package(record_id: str) -> str | None:
    meta = detect_device(record_id)
    if meta is None:
        print(f"  ! {record_id}: 장비 인식 실패 — DEVICE_MAP에 추가 필요")
        return None
    category, form, vendor, ref, display = meta
    mat = REPO / "data" / "cache" / "record_materialization" / record_id
    if not (mat / "model.urdf").exists():
        print(f"  ! {record_id}: 컴파일 산출물 없음 — 먼저 articraft compile 실행")
        return None

    base = f"ac_{category}_{form}_{vendor}_{ref}style"
    asset = f"{base}_v{next_version(base)}"
    out = HANDOFF / asset
    out.mkdir(parents=True)
    (out / "assets" / "meshes").mkdir(parents=True)

    urdf = (mat / "model.urdf").read_text(encoding="utf-8")
    urdf = re.sub(r'<robot name="[^"]*"', f'<robot name="{asset}"', urdf, count=1)
    (out / "model.urdf").write_text(urdf, encoding="utf-8")
    for obj in (mat / "assets" / "meshes").glob("*.obj"):
        shutil.copy2(obj, out / "assets" / "meshes" / obj.name)

    record = json.loads((REPO / "data" / "records" / record_id / "record.json").read_text())
    date = record_id.split("_")[-4][:8]
    readme = README_TMPL.format(
        asset=asset,
        display=display,
        bar="=" * 60,
        date=f"{date[:4]}-{date[4:6]}-{date[6:8]}",
        rating=record.get("rating", "-"),
        record_id=record_id,
        dims=measured_dims_mm(record_id),
        joints=joints_desc(urdf),
    )
    (out / "README.txt").write_text(readme, encoding="utf-8")

    zip_path = HANDOFF / f"{asset}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(HANDOFF))

    refs = set(re.findall(r'filename="([^"]+)"', urdf))
    with zipfile.ZipFile(zip_path) as z:
        missing = [r for r in refs if f"{asset}/{r}" not in z.namelist()]
    flag = "OK" if not missing else f"메시 누락 {missing}"
    print(f"  {asset}.zip  ({zip_path.stat().st_size // 1024}KB, 관절: {joints_desc(urdf)}) {flag}")
    return asset


def main() -> int:
    ids = sys.argv[1:]
    if not ids:
        print(__doc__)
        return 1
    ok = 0
    for rid in ids:
        if package(rid.strip()):
            ok += 1
    print(f"\n{ok}/{len(ids)} 패키징 완료 → {HANDOFF}/")
    return 0 if ok == len(ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
