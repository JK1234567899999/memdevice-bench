# MemDeviceBench 프로젝트 기획서

## 한 문장 정의

**MemDeviceBench는 특정 소자명에 종속되지 않고, 2T·3T·4T·다단자 메모리 및 적응형 전자소자를 technology, terminal topology, platform, mechanism, material, behavior, experiment profile의 독립적인 태그 축으로 표준화하고 분석하는 오픈소스 연구 인프라다.**

## 가장 가능성 높은 문제 정의

이 분야의 핵심 병목은 새로운 metric 부족보다 **데이터 의미와 측정 경로가 통일되지 않는 것**이다. 같은 `energy`, `linearity`, `retention`, `endurance`라는 표현도 논문마다 다음이 다르다.

- programming path와 read path
- DUT terminal 정의와 circuit-cell 표기
- pulse amplitude, width, rise/fall time, compliance
- state를 읽는 시점과 averaging window
- conductance normalization 및 endpoint 처리
- current가 직접 측정값인지 모델 기반 추정값인지
- 초기 RC/displacement transient 또는 ionic relaxation의 포함 여부

특히 2단자 RRAM/PCM의 current path와 3단자 ECRAM/FeFET/TFT의 gate/write path를 같은 모델로 처리하면 programming energy가 물리적으로 잘못될 수 있다.

따라서 프로젝트의 첫 번째 가치는 모든 소자를 하나의 평면적인 enum으로 분류하는 것이 아니라, 다음을 분리하는 데 있다.

1. 기술/소자 개념: `rram`, `pcm`, `fram`, `fefet`, `ecram`, `mram` 등
2. 접근 가능한 terminal topology: 2T, 3T, 4T, N-terminal
3. 플랫폼/형태: `resistor`, `capacitor`, `tft`, `oect`, `crossbar`, `1t1r-cell` 등
4. 물리 메커니즘: filamentary, phase-change, ferroelectric, electrochemical, charge-trap 등
5. 재료계와 관측된 behavior
6. 측정 프로파일: pulse update, DC I–V, transfer, retention, polarization, EIS 등

## 핵심 예시

| 사례 | 태그 조합 |
|---|---|
| 2T oxide RRAM | `rram + two-terminal + resistor + oxide + unknown/filamentary` |
| 2T PCM/PRAM | `pcm + pram + two-terminal + phase-change + chalcogenide` |
| 2T FRAM capacitor | `fram + two-terminal + capacitor + ferroelectric` |
| 3T FeFET | `fefet + three-terminal + fet/tft + ferroelectric` |
| 3T ECRAM | `ecram + three-terminal + tft + electrochemical + ion-insertion` |
| 3T memory TFT | `memtransistor + three-terminal + tft + charge-trap/unknown` |
| 4T dual-gate device | `memtransistor + four-terminal + tft + gate-tunable` |

`TFT`는 RRAM/ECRAM/FRAM과 같은 축의 소자 종류가 아니라 platform tag다. 따라서 `ecram + tft + three-terminal`처럼 동시에 존재해야 한다.

## 타깃 사용자

- RRAM/PCM/FRAM/FeFET/ECRAM/OECT/memtransistor 연구실
- oxide electronics 및 neuromorphic device 연구자
- parameter analyzer, SMU, PMU, pulse generator 데이터를 정리하는 실험 연구자
- 논문 간 device benchmark를 수행하는 연구자와 리뷰어
- 공개 데이터셋과 재현 가능한 figure pipeline을 만드는 저자
- QCoDeS, PyMeasure, SweepMe!, LabVIEW 기반 측정 시스템 개발자

## MVP

`v0.2`는 범위를 의도적으로 제한한다.

- pulse-by-pulse conductance-update CSV 표준
- JSON metadata sidecar와 controlled tag taxonomy
- 2T/3T/4T topology 검증
- 공통 device-profile template
- potentiation/depression linearity, monotonicity, variability, asymmetry
- conductance window, cycle drift, retention fit
- measured programming-path `V·I·t` energy
- 명시적 2T에서만 제한적으로 사용하는 `V²G_readt` fallback
- multi-terminal 또는 topology 미확인 상태에서 programming current가 없으면 energy 미계산
- CLI, Python API, JSON/CSV/PNG report
- synthetic software-test preset과 unit test

DC I–V, TFT transfer/output, FRAM polarization/PUND, EIS까지 구현했다고 과장하지 않는다. 각 profile은 schema, metric, artifact check, real-data regression test가 준비된 뒤 지원 상태로 승격한다.

## 핵심 차별점

### 1. Terminal-centric이지만 terminal count만으로 소자를 정의하지 않는다

2T/3T/4T topology를 일차적으로 명시하되, technology·platform·mechanism을 별도 축으로 유지한다. 같은 3T라도 FeFET, ECRAM, OECT, charge-trap TFT의 write current와 time scale은 다르기 때문이다.

### 2. 에너지 계산을 topology-aware하게 강제한다

- measured programming current가 있으면 `|VIt|`
- metadata가 명시적으로 2T일 때만 `V²G_readt` fallback
- 3T/4T 또는 topology 미확인 상태에서 programming current가 없으면 `not_computed`

이 설계는 channel read conductance를 gate/electrolyte current로 오인하는 오류를 코드 수준에서 방지한다.

### 3. Tag template를 제공하되 mechanism을 단정하지 않는다

`rram-2t`, `fram-capacitor-2t`, `ecram-tft-3t`, `tft-generic-3t`, `dual-gate-memtransistor-4t` 같은 시작 템플릿을 제공한다. 하지만 mechanism, material, nonvolatile 여부는 실제 증거에 따라 수정해야 하며 `unknown`과 `mixed`를 허용한다.

### 4. Universal score를 만들지 않는다

서로 다른 pulse width, read bias, temperature, state range, terminal path를 하나의 점수로 압축하지 않는다. 프로젝트의 목적은 비교 조건과 provenance를 보존하는 것이다.

## 데이터 모델

```text
Dataset
├── device
│   ├── device_id
│   ├── terminal_count
│   ├── technology_tags
│   ├── platform_tags
│   ├── mechanism_tags
│   ├── material_tags
│   └── behavior_tags
├── experiment
│   ├── profile
│   ├── instrument
│   ├── temperature_k
│   └── notes
└── numerical table
    ├── programming/read electrical quantities
    ├── state sequence
    └── timestamps
```

## 물리 메커니즘과 측정 artifact

프로젝트 문서와 report는 다음 가능성을 명시적으로 다룬다.

- two-terminal electronic/ionic conduction 및 filament evolution
- three-terminal gate/electrolyte current와 channel read current의 분리
- charge trapping/detrapping과 threshold shift
- electrochemical ion insertion 및 relaxation
- ferroelectric polarization switching과 depolarization
- phase-change Joule heating 및 thermal history
- RC charging, displacement current, cable/probe parasitic
- compliance clipping, pulse overshoot, finite bandwidth
- sampling/averaging window에 의한 apparent linearity와 variability 변화

## Critical validation experiment

초기 공개 전에 최소 두 가지 검증이 필요하다.

1. **2T 대 3T energy-path 비교**
   - 2T RRAM/PCM trace와 3T ECRAM/FeFET trace를 동일 workflow로 분석한다.
   - 3T 데이터에서 programming current를 제거했을 때 energy가 `not_computed`가 되는지 확인한다.

2. **실제 waveform 기반 검증**
   - pulse source와 current monitor의 sampled waveform을 적분한 energy를 scalar `VIt`와 비교한다.
   - RC/displacement transient, compliance, rise/fall time이 큰 경우 차이를 정량화한다.

## 연구 논문에서의 해석

적절한 표현:

> Device data were converted to a topology-aware canonical schema and analyzed using versioned, explicitly defined update metrics.

피해야 할 표현:

> The software provides a universal score proving that one memory technology is superior.

리뷰어는 다음을 질문할 가능성이 높다.

- terminal count가 DUT 기준인가, circuit-cell 표기인가?
- `pulse_current_a`가 실제 programming path current인가?
- pulse waveform과 compliance를 직접 확인했는가?
- read timing과 averaging이 update trajectory를 바꾸지 않았는가?
- mechanism tag가 직접적인 증거에 기반하는가?
- 서로 다른 조건의 소자를 단순 수치로 비교하지 않았는가?
- synthetic data를 physical model처럼 사용하지 않았는가?

## 개발 로드맵

### Phase 1 — 신뢰 가능한 core

- tag/metadata schema 안정화
- Keithley/Keysight importer 2~3종
- pulse update와 retention real-data regression test
- 2T/3T/4T 대표 공개 dataset card

### Phase 2 — measurement profile 확장

- DC I–V 및 set/reset event extraction
- TFT transfer/output curve와 threshold/hysteresis 분석
- FRAM/FeFET polarization/PUND profile
- transient waveform과 true energy integration
- EIS/impedance profile

### Phase 3 — cross-lab benchmark

- replicate statistics와 uncertainty
- instrument timing/bandwidth metadata
- condition-aware cross-device comparison
- DOI와 versioned public dataset registry
- 독립 연구실 adopter/contributor 확보

## 성공 기준

- 최소 3개 technology tag와 2개 이상의 terminal topology에서 동일 workflow가 작동
- 실제 raw export를 canonical data로 변환하는 importer 존재
- metadata가 잘못된 multi-terminal energy 추정을 실제로 차단
- 공개 데이터 기반 regression test 존재
- 외부 연구자가 dataset/profile/importer를 독립적으로 추가할 수 있음
- adoption, download, citation, contributor 수는 검증 가능한 사실만 기록
