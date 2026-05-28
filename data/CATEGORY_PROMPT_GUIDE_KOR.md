# 카테고리 프롬프트 가이드 (Category Prompt Guide)

이 문서는 `data/batch_specs/` 하위의 배치 스펙(batch specs) 작성을 위한 카테고리 프롬프트 작성 방법을 정의합니다.

현재 배치 스펙은 통일된 기본 모델링 스택을 사용합니다. 프롬프트 내에 툴링 변형이나 파이프라인 변형을 언급하지 마십시오. 일반적인 배치 CSV에서는 추가적인 스택 선택 필드가 필요하지 않습니다.

## 핵심 원칙 (Core Principle)

**기계 엔지니어가 냅킨에 그린 스케치처럼 프롬프트를 작성하세요. 빌드할 수 있을 만큼 구체적이되, 시방서(spec sheet)를 가득 채울 만큼 상세할 필요는 없습니다.**

시스템 프롬프트가 사실성, 재질 선택, 검증, 툴 선택 및 빌드 프로세스를 이미 알아서 처리합니다. 사용자 프롬프트는 **무엇을 만들지**, **어떤 주요 부품들로 구성되는지**, 그리고 **어떻게 움직이는지(관절 동작)**만 명시하면 됩니다.

프롬프트가 너무 상세해질수록 = 기하학(geometry)이 복잡해지고 = 빌드 턴이 늘어나며 = 소요 비용이 커지고 = 에러 발생 표면적이 넓어집니다. 추가하는 모든 문장은 객체 이름만으로는 에이전트가 추론할 수 없는 새로운 정보를 담고 있어야만 그 가치를 합니다.

---

## 시스템 프롬프트가 이미 처리하는 사항들 (프롬프트에 반복 작성 금지)

에이전트의 시스템 프롬프트가 아래 사항들을 강력하게 강제하고 있으므로, **프롬프트에 절대 중복해서 작성하지 마십시오**:

- 사실적인 지오메트리 및 적절한 모델링/CadQuery 툴의 자동 선택
- 공중에 떠 있는 부품 방지, 의도하지 않은 파트 간 겹침(overlap) 차단
- 컴파일 피드백을 기반으로 하는 점진적 빌드 프로세스
- 배치, 연결성 및 관절(articulation) 작동에 대한 자체 테스트 및 검증
- 재질 및 색상의 사실성 확보
- 기계적 타당성 준수

아래의 문구들은 **토큰 낭비(wasted tokens)**입니다. 프롬프트에 절대 포함하지 마십시오:

- `"realistic, highly detailed"` (사실적이고 상세한)
- `"standalone mechanical study assembly"` (독립형 기계 스터디 어셈블리)
- `"for a specific tooling or pipeline variant"` (특정 툴링 또는 파이프라인 버전을 위한)
- `"emphasize rigid brackets, exposed bearing hardware"` (단단한 브래킷, 노출된 베어링 하드웨어 강조)
- `"disciplined machined-or-fabricated hard-surface geometry"` (정밀하게 가공/제작된 하드서페이스 지오메트리)
- `"avoid product styling, decorative housings"` (제품 스타일링이나 장식용 하우징 지양)
- `"keep it as a pure mechanical assembly with explicit joints"` (명시적인 관절을 가진 순수 기계 어셈블리로 유지)
- `"a short realism and buildability clause"` (짧은 사실성 및 빌드 가능성 조항)

---

## 프롬프트 템플릿 (Prompt Template)

모든 프롬프트는 대략 아래의 순서로 **세 가지 요소**를 반드시 포함해야 합니다:

### 1. 객체의 정체성 (Object identity - 필수, 1문장)
사람들이 쉽게 인식할 수 있는 수준으로 객체가 무엇인지 명시합니다. 카테고리에 여러 흔한 형태가 존재할 경우 구체적인 변형(variant)의 이름을 지정합니다.

### 2. 부품 구조 (Part structure - 필수, 1~2문장)
주요 부품들의 이름을 나열하고 그것들이 물리적으로 어떻게 연결되는지 설명합니다. 이는 에이전트에게 뼈대가 될 부품 트리 구조를 제공합니다. 모든 세부 요소를 적기보다는 실루엣을 정의하는 파트와 움직이는 파트에 집중하세요.

### 3. 관절 사양 (Articulation spec - 필수, 1~2문장)
**이 부분이 가장 중요합니다.** 
각 조인트 타입(revolute, prismatic, continuous), 조인트가 연결하는 파트들, 그리고 축의 방향을 아주 명확하게 설명해 주세요. 모든 모션은 물리적인 지지대(support)와 연결되어 있어야 합니다. 수치적인 가동 범위(limits)를 직접 적지 마십시오. 에이전트가 기계적으로 타당한 가동 한계를 스스로 선택합니다.

만약 객체에 키패드, 버튼 뱅크, 제어 클러스터 등 객체의 정체성을 정의하는 전면부 제어 장치가 있는 경우 프롬프트에 명시적으로 기재해 줍니다. 이러한 제어 장치들이 개별적으로 보일 경우, 하나의 굳어 있는 정적 패널로 인식되지 않고 "각각 독립적으로 작동(articulate independently)"한다고 구체화해야 합니다.

### 4. 크기 또는 비율 힌트 (Scale or proportion hint - 선택, 1문장)
기본 크기가 모호할 때만 추가합니다. (예: `"desktop-scale"` vs `"industrial floor-mounted"`, 혹은 `"arm span roughly 0.5m"`)

---

## 복잡성 예산 (Complexity Budget)

| 객체 복잡도 | 목표 부품 수 | 프롬프트 권장 길이 | 권장 최대 턴 수 |
|---|---|---|---|
| **낮음** (관절 1~2개) | 3~6개 부품 | 2~3문장 | 100 턴 |
| **보통** (관절 3~5개) | 6~12개 부품 | 3~4문장 | 140 턴 |
| **높음** (관절 6개 이상) | 12~20개 부품 | 4~6문장 | 180 턴 |

만약 프롬프트를 6문장 넘게 작성하고 있다면, 과도하게 세부 사항을 명세하고 있을 가능성이 높습니다. 두 개의 객체로 분리하거나 내용을 단순화하십시오.

위 가이드라인은 현재 작동 기준 예산이며 엄격한 한계치는 아닙니다. 이 레포지토리에서 새로운 카테고리를 탐색할 때는 보통 `100-200` 턴 범위가 소요됩니다. 객체에 실제 지오메트리나 관절 복잡성이 있다면 예산 한도를 늘리되, 단순히 턴 수 목표를 맞추기 위해 프롬프트의 품질을 떨어뜨리지는 마십시오.

---

## 작성 예시 (Examples)

### 좋은 예시 (Good)

**단일 회전 힌지 (Single revolute hinge):**
> A heavy-duty door hinge. Two rectangular leaf plates connected by a barrel-and-pin hinge with alternating knuckles. One revolute joint along the barrel axis.
> *(번역: 고하중용 도어 힌지. 교차하는 너클 구조를 가진 배럴-핀 힌지로 연결된 두 개의 직사각형 리프 플레이트. 배럴 축 방향을 따르는 하나의 레볼루트 조인트.)*

**요-피치 모듈 (Yaw-pitch module):**
> A two-axis gimbal mount. A yaw turntable base carries a U-shaped fork, which supports a pitch cradle between its arms. Yaw is continuous rotation about vertical; pitch is revolute about the horizontal fork axis.
> *(번역: 2축 김벌 마운트. 요(Yaw) 회전판 베이스가 U자형 포크를 지지하며, 포크 양팔 사이에 피치(Pitch) 요람이 지지됩니다. 요 모션은 수직 축 기준 자유 회전(continuous)이며, 피치는 수평 포크 축 기준 회전(revolute) 조인트입니다.)*

**다단계 신축 붐 (Telescoping boom):**
> A three-stage telescoping boom. Three nested rectangular tube sections that extend from a fixed root mount. Each stage slides prismatically along the boom axis.
> *(번역: 3단계 신축식 붐. 고정된 루트 마운트에서 연장되는 중첩된 3개의 직사각형 튜브 섹션. 각 단계는 붐 축을 따라 프리즈매틱 조인트로 미끄러지듯 인출됩니다.)*

**직교 XY 스테이지 (Orthogonal XY stage):**
> A two-axis positioning stage. A base carries an X-axis rail with sliding carriage; on top of that carriage sits a Y-axis rail with its own carriage, oriented 90 degrees to the first. Both axes are prismatic.
> *(번역: 2축 포지셔닝 스테이지. 베이스 위에 슬라이딩 캐리지가 결합된 X축 레일이 있고, 그 캐리지 상단에 90도 교차하여 작동하는 캐리지 결합 Y축 레일이 위치합니다. 두 축 모두 프리즈매틱 조인트입니다.)*

### 나쁜 예시 (Bad) — 너무 장황함
> Design a realistic, highly detailed single revolute hinge as a standalone mechanical study assembly for a special pipeline variant, with one clear rotary axis joining two rigid leaves or clevis members in a heavy-duty hinge. The hinge pin, barrel segments, and support cheeks should be prominent and mechanically plausible... (이하 생략)
* **이유**: 시스템 프롬프트가 이미 규정하고 있는 사실성 관련 토큰을 약 50%나 반복 낭비하고 있습니다. 또한 정밀한 관절 종류나 운동 방향을 구체적으로 알려주지 않아 에이전트가 축을 알아서 추측해야 합니다. 잔가지 디테일들(윤활 캡, 고정 고리 등)은 지오메트리 복잡도만 높여 에러 표면적을 크게 만듭니다.

### 나쁜 예시 (Bad) — 너무 부실함
> A hinge. (힌지.)
* **이유**: 부품 구조도, 관절 사양도, 크기 힌트도 없습니다. 에이전트가 무언가 만들어내긴 하겠지만, 당신이 원하는 형태와 완전히 다를 확률이 높습니다.

### 나쁜 예시 (Bad) — 모호한 제어부 표현
> A cash register with a drawer, screen, and controls.
* **이유**: "controls"라는 단어가 너무 모호합니다. 버튼이나 키패드가 디자인의 정체성에 중요한 요소라면, "버튼들이 독립적으로 움직인다(articulate independently)"고 명시해 주어야 렌더링 시 하나의 통짜 플라스틱 덩어리로 굳어버리는 참사를 막을 수 있습니다.

---

## 관절 동작 설계 원칙 (Articulation Policy)

일반적인 기계 장치의 정상 인스턴스에서 기대할 수 있는 상식적인 동작들을 프롬프트에 포함해 주세요. 이는 보통 하나 이상의 모션을 의미합니다.

- 하나의 모션만 억지로 남기기 위해 객체의 동작을 인위적으로 단순화하지 마십시오.
- 미세한 부품들의 움직임(예: 손잡이, 다이얼, 바퀴의 캐스터 축 등)을 무시하지 마십시오.
- 가시적인 제어부 조작 장치(버튼, 다이얼 등)가 디자인의 정체성이라면, 에이전트가 알아서 구현해 주길 바라기보다는 프롬프트에 명확히 명시해 주는 편이 안전합니다.
- 객체의 정체성과 무관한 억지스럽고 기이한 모션은 추가하지 마십시오.
- 한 쌍의 지지대(좌/우 브래킷 등)가 하나의 강체 플레이트를 동시에 지지하는 구조라면 이를 명확히 밝히십시오. 각각 따로 독립적으로 노는 부품이 아니라, "동일한 축 정렬을 유지하며 하나의 몸체로 연결되어 작동(stay aligned as one rigid assembly)"함을 구체적으로 알려주어야 합니다.
- **모든 명시적인 동작은 반드시 물리적인 지지대와 짝을 이루어야 합니다**:
  - ❌ "바퀴가 회전한다" ➡️ ⭕ "바퀴가 포크 프레임에 마운트되어 회전한다"
  - ❌ "뚜껑이 열린다" ➡️ ⭕ "뚜껑이 하우징 후면 모서리의 힌지를 축으로 열린다"
  - ❌ "캐리지가 움직인다" ➡️ ⭕ "캐리지가 두 개의 가이드 레일 위를 슬라이딩한다"

---

## SDK 모델링 스택 적합성 안내 (SDK Fit)

프롬프트에 작성하는 기하학적 요소들은 현재 SDK 스택이 안정적으로 모델링할 수 있는 범주 내에 머물러야 합니다. 아래의 **두 가지 강력한 한계 조건**을 명심하십시오:

1. **엄격한 트리 구조(Strict Tree Structure)**: 모든 부품은 단 하나의 부모 조인트만을 가져야 하며 순환 경로(Cycle)가 없어야 합니다. 하나의 부품이 두 개의 독립된 경로로 연결되어 구동되는 **폐루프 링크 구조(Closed kinematic chain)**는 모델링할 수 없습니다.
2. **URDF 단일 축 조인트**: 모든 조인트는 오직 1축 모션(1 revolute, 1 prismatic, 1 continuous)만 가집니다. 조인트끼리 서로 연동되어 기어로 묶여 움직이는 구동 세맨틱스는 지원되지 않습니다.

### 👍 모델링이 매우 잘 되는 지오메트리 패턴:
- **기본 입체 도형 (Box, Cylinder, Sphere)**: URDF 기본 프리미티브로 다이렉트 변환되므로 가볍고 에러가 나지 않습니다. 가능하면 이 형태를 기본 뼈대로 사용하십시오.
- **압출 프로파일 및 패널 (Extruded profiles/panels)**: 평평한 판재, L자 브래킷, C자 채널, 직사각형 컷아웃 구멍이 뚫린 패널 등은 매우 안정적으로 설계됩니다.
- **회전체 형상 (Revolved/Lathe shapes)**: 노브, 핸들, 캡, 원통, 노즐 등 축대칭 형태의 파트는 완벽하게 소화됩니다.
- **불리언 컷 형상 (Boolean-carved solids)**: 실린더를 빼서 구멍을 뚫은 힌지 구멍이나 샤프트, 홈이 파인 상자 등도 잘 빌드됩니다.
- **다중 분기 트리 어셈블리 (Multi-branch assemblies)**: 하나의 부모 아래에 여러 독립된 자식이 병렬로 붙는 구조(여러 서랍이 있는 캐비닛, 바퀴 허브와 스포크들, 로봇 몸체에 붙은 양팔 등)는 각 분기가 독립적으로 보장되므로 완벽히 지원됩니다.

### 👎 모델링이 잘 안 되는 부적합 패턴:
- **유기적인 곡면 (Organic freeform surfaces)**: 자동차 바디 라인이나 인체공학적 그립 하우징 같은 3D 곡면은 복잡한 로프트 가이드 곡선이 필요하여 컴파일 오류를 내기 쉽습니다. 납작한 평면, 원통, 회전 프로파일이 뚜렷한 기계식 장치 위주로 기획해 주세요.
- **부피가 모호한 얇은 껍데기**: 벽 두께가 중요한 물리적 기능이 아니라면 solid(꽉 찬 입체)로 묘사하는 것이 기하학적으로 훨씬 견고하게 생성됩니다.
- **유연한 소모품 및 탄성체**: 천, 고무 씰, 벨트, 전선 케이블, 스프링, 체인 등은 URDF에서 정의할 수 없습니다. 오직 단단한 리지드(Rigid) 기계 프레임 부품 위주로 묘사해 주세요.

---

## 📋 최종 작성 체크리스트
프롬프트를 제출하기 전에 아래 항목들을 마지막으로 점검하세요:

- [ ] 객체의 이름을 명확하게 선언했는가?
- [ ] 핵심 부품들과 그것들이 물리적으로 결합하는 방식을 적었는가?
- [ ] 모든 조인트의 타입(revolute, prismatic 등)과 운동 축 방향을 규정했는가?
- [ ] 정렬 상태가 중요한 다중 지지대나 대칭 브래킷 그룹을 강체 결합체로 명시했는가?
- [ ] 수치적인 가동 범위 한계(도단위, 밀리미터 단위 등)를 프롬프트에 직접 기재하지 않았는가?
- [ ] 전체 프롬프트 길이가 6문장 이하인가?
- [ ] 시스템 프롬프트가 보장하는 퀄리티/현실성 단어를 생략했는가?
- [ ] 기계 엔지니어가 이 설명만 읽고도 의도한 기계 구조를 바로 머릿속에 그릴 수 있는가?
