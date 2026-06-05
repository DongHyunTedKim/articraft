# Articraft 3D 에셋 생성 및 뷰어 활용 가이드라인

본 가이드라인은 Articraft 프로젝트에서 **새로운 3D 에셋(URDF 모델)을 생성**하고, 이를 **3D 뷰어 화면(Web Dashboard)에서 시각화하여 탐색**하는 전체 워크플로우와 CLI 명령어 사용법을 안내합니다.

---

## 🚀 1. 3D 모델 생성하기 (Generation & Draft)

Articraft의 CLI 명령어를 사용하여 프롬프트 기반으로 3D 관절 객체(Articulated Object) 데이터를 생성할 수 있습니다.

### A. 새로운 3D 모델 생성 (AI Inference 실행)
프롬프트를 입력하여 인공지능 생성 런타임을 통해 완전한 3D 모델(URDF, 메쉬 에셋, 파라미터 등)을 빌드합니다.
```bash
# 기본 생성 (GPT 모델 및 기본 설정 사용)
uv run articraft generate "a benchtop monocular laboratory microscope"

# 특정 AI 모델 및 이미지 레퍼런스를 지정하여 생성
uv run articraft generate --model gemini-3-flash-preview --image reference_photo.png "a detailed robotic arm"
```
> [!NOTE]
> 생성된 레코드는 `data/records/rec_<id>` 경로에 저장됩니다.

### B. 가벼운 드래프트(Draft) 생성하기
생성 엔진을 돌리지 않고, 먼저 구조와 프롬프트 사양만 정의한 초안(Draft) 레코드를 생성하여 나중에 디테일 작업을 하고 싶을 때 사용합니다.
```bash
# 드래프트 생성
uv run articraft draft "a complex dual-arm robot workstation"

# 이미지 레퍼런스를 포함한 드래프트 생성
uv run articraft draft --image reference.png "custom gaming desk setup"
```

### C. 기존 레코드 다시 실행하기 (Rerun)
이전에 생성해 둔 기존 레코드를 기반으로 생성을 다시 트리거합니다.
```bash
uv run articraft rerun data/records/rec_<record_id>
```

---

## 📦 2. 뷰어로 보기 전 필수 단계: 컴파일 (Compile & Materialize)

> [!IMPORTANT]
> **새로 생성한 3D 모델을 웹 뷰어(Dashboard)에서 깨끗하게 보려면 반드시 "컴파일" 과정이 선행되어야 합니다.** 
> 이 단계는 로우 데이터(JSON/URDF)를 뷰어의 Three.js 엔진이 읽을 수 있는 캐시 및 렌더링용 에셋으로 재구성해 줍니다.

### A. 단일 3D 모델만 조준하여 컴파일
특정 새로 만든 모델 하나만 골라서 빠르게 3D 에셋 캐시를 빌드합니다.
```bash
uv run articraft compile data/records/rec_<record_id>
```

### B. 전체 3D 모델 일괄 컴파일 (추천 🌟)
뷰어 대시보드를 열기 전에 로컬에 있는 모든 에셋들의 시각화 캐시를 가장 빠르게 대량 구축하는 명령어입니다.
```bash
# 시각화용 렌더링 데이터 일괄 고속 컴파일
uv run articraft compile-all

# 엄격한 검증을 포함하여 원본의 모든 포맷을 검사하며 풀 컴파일
uv run articraft compile-all --target full --strict
```

---

## 🖥️ 3. 3D 뷰어로 탐색하고 관찰하기 (Visualization)

현재 백그라운드에서 실행해 둔 `just viewer-dev`는 Uvicorn API 서버와 Vite 웹 뷰어를 동시에 가동하므로, 전체 3D 모델 대시보드를 모니터링하기 가장 좋은 방법입니다.

### A. 대시보드에서 전체 모델 탐색 (현재 실행 중인 모드)
웹 브라우저를 열고 다음 주소에 접속하면 생성/컴파일이 완료된 모든 3D 레코드 카탈로그를 탐색하고 테스트할 수 있습니다.
👉 **[http://127.0.0.1:5173/](http://127.0.0.1:5173/)**

### B. 특정 모델 하나만 타겟팅하여 단독 뷰어로 실행
대시보드를 통하지 않고, 터미널 명령을 통해 특정 3D 관절 객체(URDF) 렌더링 화면만 브라우저 단독 뷰어로 즉시 실행하는 특수 모드입니다.
```bash
uv run articraft view --dev data/records/rec_<record_id>
```
*이 명령을 실행하면 해당 모델 전용 로컬 서버가 가동되며 웹 화면에 바로 3D 캔버스가 나타납니다.*

### C. 뷰어 검색 인덱스 갱신하기
새로운 모델이 계속 추가된 뒤 대시보드 내 검색창에서 잘 검색되지 않을 때는 인덱스를 빌드해 줍니다.
```bash
uv run articraft workbench search-index
```

---

## 💡 요약 워크플로우 카드
새로운 3D 에셋을 완성하여 대시보드에서 최종 감상하기까지의 3단계 흐름은 아래와 같습니다.

```mermaid
graph TD
    A["1. 에셋 생성 (Inference) <br> uv run articraft generate '프롬프트'"] --> B["2. 렌더 캐시 컴파일 (Compile) <br> uv run articraft compile-all"]
    B --> C["3. 대시보드 접속 <br> http://127.0.0.1:5173"]
```

---

## 🛠️ 부록: 로컬 가격 산정 (Cost Override) 및 래퍼 실행

원작자의 소스 코드를 완전히 순정(Vanilla) 상태로 유지하면서, 로컬 환경에서 OpenRouter 등 특정 프로바이더/모델에 대해 커스텀 요율을 강제로 적용하고 싶을 때 사용하는 방법입니다.

이 기능은 `.gitignore`에 등록되어 외부로 노출되지 않는 로컬 디렉토리(`data/local/`)에 격리된 설정 및 래퍼 스크립트를 통해 작동합니다.

### A. 커스텀 가격 설정 파일 (`data/local/cost_override.json`)
가격 산정 요율을 아래 형식의 JSON 구조로 정의하여 이 파일에 기록합니다.

```json
{
  "openrouter": {
    "openai/gpt-5.5": {
      "input_uncached": 5.00,
      "input_cached": 0.00,
      "output": 30.00
    },
    "anthropic/claude-opus-4.7": {
      "input_uncached": 5.00,
      "input_cached": 0.00,
      "output": 25.00
    },
    "google/gemini-3.5-flash": {
      "input_uncached": 1.50,
      "input_cached": 0.15,
      "output": 9.00
    }
  }
}
```

*   **주요 설정 항목**:
    *   `input_uncached`: 캐시되지 않은 입력 토큰 1백만 개당 비용 (USD)
    *   `input_cached`: Context Caching 히트된 입력 토큰 1백만 개당 비용 (USD)
    *   `output`: 출력 토큰 1백만 개당 비용 (USD)
    *   `prompt_tier_threshold_tokens` (선택): 고컨텍스트 임계값 기준 토큰 수
    *   `input_uncached_above_threshold` / `input_cached_above_threshold` / `output_above_threshold` (선택): 임계값 초과 시의 비용 (USD)

### B. 로컬 전용 래퍼를 통한 실행 (`data/local/run_local.py`)
`run_local.py`는 실행 시점에만 가격 매칭 함수를 커스텀 JSON 가격표를 읽도록 런타임 몽키 패치(Monkey Patching)를 수행하고, 실제 CLI 명령은 동일하게 동작시킵니다. 

기존 `uv run articraft ...` 명령어 대신 앞부분을 다음과 같이 래퍼 스크립트로 대체하여 실행합니다.

```bash
# [Mac/Linux]
uv run data/local/run_local.py generate "prompt text"
uv run data/local/run_local.py status

# [Windows]
uv run python data/local/run_local.py generate "prompt text"
uv run python data/local/run_local.py status
```

### C. 누락된 기존 레코드 가격 정보 일괄 정산 (`data/local/backfill_costs.py`)
기존에 가격 산정이 누적되지 않고 누락된(또는 0원 처리된) 생성 레코드들의 경우, 각 레코드 폴더의 `traces/trajectory.jsonl.zst` 압축 로그를 분석하여 가격을 재계산한 후 일괄 기입해 주는 백필 도구입니다.

```bash
# [Mac/Linux]
uv run data/local/backfill_costs.py

# [Windows]
uv run python data/local/backfill_costs.py
```
*이 명령을 실행하면 누락된 레코드들을 스캔하여 `cost.json` 생성 및 메타데이터 갱신을 자동으로 처리해 줍니다.*


