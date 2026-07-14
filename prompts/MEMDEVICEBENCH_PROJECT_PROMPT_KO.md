# MemDeviceBench 설명·설계·구현·프로젝트화 마스터 프롬프트

아래 내용을 코드 생성형 AI, 연구 프로젝트 기획 AI, 또는 오픈소스 저장소 생성 에이전트에 그대로 입력할 수 있다. `[대괄호]` 변수만 필요에 따라 바꾼다.

---

당신은 **반도체 소자 물리, 전기적 측정, scientific Python, 데이터 표준화, 오픈소스 거버넌스**를 모두 이해하는 senior research software architect다. 아래 개념을 단순 아이디어 수준이 아니라 **실행 가능한 연구 소프트웨어 프로젝트**로 설명하고 설계하며 구현하라.

## 0. 작업 모드

다음 모드를 모두 수행하라.

1. `EXPLAIN`: 연구자에게 프로젝트의 필요성과 물리적 차별점을 설명한다.
2. `DESIGN`: taxonomy, metadata, schema, API, CLI, architecture를 설계한다.
3. `BUILD`: 실행 가능한 repository와 테스트를 만든다.
4. `PROJECTIZE`: roadmap, contribution units, governance, launch plan을 작성한다.
5. `PITCH`: 연구비·오픈소스 지원·공동연구 제안에 사용할 수 있는 사실 기반 설명을 작성한다.

질문으로 작업을 미루지 말고 합리적인 default를 사용한다. 단, 물리적으로 불확실한 부분은 assertion이 아니라 warning, metadata field, 또는 roadmap item으로 남긴다.

## 1. 프로젝트 정체성

프로젝트명은 **`MemDeviceBench`**로 한다.

한 문장 정의:

> 2-terminal, 3-terminal, 4-terminal, multi-terminal memory/adaptive electronic devices를 technology, terminal topology, platform, physical mechanism, material, behavior, experiment profile의 독립적인 태그 축으로 기록하고, 재현 가능한 validation과 benchmark를 제공하는 오픈소스 연구 인프라.

프로젝트를 ECRAM, RRAM, FRAM 등 특정 한 기술의 전용 코드로 설명하지 마라. ECRAM은 지원되는 technology tag 중 하나일 뿐이다.

## 2. 반드시 지켜야 할 분류 원칙

### 2.1 Flat enum 금지

다음 용어는 서로 같은 축이 아니다.

- technology/device concept: `RRAM`, `PRAM/PCM`, `FRAM`, `FeFET`, `FTJ`, `ECRAM`, `CBRAM`, `MRAM`, `flash`, `memtransistor`
- accessible terminal topology: `2T`, `3T`, `4T`, `N-terminal`
- platform/form factor: `resistor`, `capacitor`, `diode`, `transistor`, `FET`, `TFT`, `MOSFET`, `OECT`, `crossbar`, `1T1R`, `1T1C`
- physical mechanism: `filamentary`, `phase-change`, `ferroelectric`, `electrochemical`, `ion-insertion`, `charge-trap`, `magnetic`, `tunneling`
- behavior: `analog`, `binary`, `multilevel`, `volatile`, `nonvolatile`, `synaptic`
- experiment: `pulse-update`, `dc-iv`, `transfer-curve`, `retention`, `polarization`, `impedance`

한 소자가 다음 태그를 동시에 가져야 한다.

```text
technology: ecram
terminal:   three-terminal
platform:   tft, transistor
mechanism:  electrochemical, ion-insertion, redox
material:   oxide, electrolyte
behavior:   analog, multilevel, nonvolatile
experiment: pulse-update
```

`TFT`를 `RRAM/FRAM/ECRAM`과 동일한 단일 선택지로 구현하지 마라.

### 2.2 Terminal count 정의

`terminal_count`는 측정된 DUT에서 전기적으로 접근 가능한 terminal 수다.

- 2 → `two-terminal`
- 3 → `three-terminal`
- 4 → `four-terminal`
- 5 이상 → `multi-terminal`

`1T1R`, `1T1C`, `1S1R`은 회로 셀/통합 구조를 나타내는 별도 platform tag다. terminal count를 회로 이름에서 자동 추론하지 마라.

Kelvin/four-wire sensing, body/back gate, separate write/read gate가 존재할 수 있으므로 실제 wiring과 measurement nodes를 notes 및 terminal path field로 기록한다.

### 2.3 Mechanism 과신 금지

소자명만 보고 mechanism을 자동 확정하지 마라.

- generic `rram-2t` template의 mechanism default는 `unknown`으로 둘 수 있다.
- 직접적인 증거가 있을 때만 `filamentary`, `valence-change`, `interfacial-switching` 등을 선택한다.
- 복합 동작은 `mixed`, 불명확한 경우 `unknown`을 허용한다.
- `OECT`는 platform이며, 모든 electrolyte-gated transistor를 OECT로 합치지 마라.

## 3. Controlled tag vocabulary

최소 다음 canonical tag를 구현하고 alias normalization을 제공하라.

### technology

```text
rram, memristor, pram, pcm, fram, fefet, ftj, ecram, cbram,
mram, stt-mram, sot-mram, flash, floating-gate-memory,
charge-trap-memory, memtransistor, redox-transistor, memcapacitor,
memdiode, mott-memory, molecular-memory, selector, other
```

### platform

```text
two-terminal, three-terminal, four-terminal, multi-terminal,
resistor, capacitor, diode, transistor, fet, tft, mosfet, oect,
electrolyte-gated-transistor, crosspoint, crossbar, 1r-cell,
1t1r-cell, 1s1r-cell, 1t1c-cell, vertical, planar, flexible, other
```

### mechanism

```text
filamentary, valence-change, electrochemical-metallization,
phase-change, ferroelectric, electrochemical, ion-insertion,
ionic-gating, redox, charge-trap, floating-gate, magnetic,
magnetic-tunnel-junction, interfacial-barrier,
interfacial-switching, mott-transition, tunneling, thermal,
mixed, unknown
```

### material

```text
oxide, metal-oxide, ferroelectric-oxide, chalcogenide, organic,
polymer, two-dimensional, silicon, perovskite, nitride,
electrolyte, solid-electrolyte, ionic-liquid, metal, other
```

### behavior

```text
analog, binary, multilevel, volatile, nonvolatile,
threshold-switching, bipolar, unipolar, incremental, gate-tunable,
stochastic, symmetric, asymmetric, potentiation-depression,
reservoir, synaptic
```

### experiment

```text
pulse-update, dc-iv, transfer-curve, output-curve, retention,
endurance, transient, noise, variability, impedance, polarization,
switching, switching-speed, temperature, frequency, read-disturb,
write-disturb, stp, ltp, ppf, stdp, reservoir-computing
```

Alias 예:

- `ReRAM` → `rram`
- `FeRAM` → `fram`
- `Fe-FET` → `fefet`
- `2T` → `two-terminal`
- `thin-film-transistor` → `tft`
- `ECM` → `electrochemical-metallization`
- `intercalation` → `ion-insertion`
- `2D` → `two-dimensional`
- `non-volatile` → `nonvolatile`
- `I-V` → `dc-iv`

## 4. 공통 device-profile template

다음 illustrative metadata template를 제공하라.

```text
rram-2t
cbram-2t
pcm-pram-2t
fram-capacitor-2t
ftj-2t
mram-mtj-2t
tft-generic-3t
fefet-tft-3t
ecram-tft-3t
oect-memory-3t
charge-trap-tft-3t
flash-mosfet-3t
dual-gate-memtransistor-4t
```

각 template에는 terminal count, technology/platform/mechanism/material/behavior tag, description, caution을 포함한다.

Template는 시작점일 뿐이라고 명시한다. 실제 sample에 맞게 terminal count, mechanism, material, volatile/nonvolatile 여부를 수정해야 한다.

FRAM capacitor template는 2T capacitor test structure이며 완전한 1T1C cell로 자동 해석하지 않는다. OECT template는 nonvolatile을 자동 부여하지 않는다.

## 5. 현재 MVP 분석 범위

검증된 numerical core는 `pulse-update` conductance trace에 집중한다.

구현할 항목:

- long-form canonical CSV
- JSON metadata sidecar
- direction alias normalization: potentiation/depression, set/reset, LTP/LTD, up/down, +1/-1
- schema validation
- branch linearity NRMSE
- linear-fit `R²`
- monotonicity
- mean/median `|ΔG|`
- update coefficient of variation
- early/late update ratio 또는 saturation index
- potentiation/depression asymmetry
- conductance window 및 dynamic-range ratio
- cycle-to-cycle window drift
- power-law retention fit
- topology-aware programming energy
- JSON/CSV/PNG report
- CLI와 Python API

DC I–V, transfer/output, polarization/PUND, transient waveform, noise, impedance는 taxonomy와 roadmap에는 포함하되, 실제 구현하지 않았다면 지원 완료라고 표현하지 마라.

## 6. Canonical pulse table

필수 columns:

```text
device_id
cycle
pulse_index
direction
conductance_s
```

권장 generic columns:

```text
pulse_voltage_v
pulse_width_s
pulse_current_a
read_voltage_v
read_current_a
timestamp_s
pulse_terminal
read_terminal
```

선택 terminal-resolved columns:

```text
gate_voltage_v, drain_voltage_v, source_voltage_v, body_voltage_v
gate_current_a, drain_current_a, source_current_a, body_current_a
```

모든 canonical numerical field는 SI unit을 사용한다. `conductance_s`는 positive read-conductance magnitude다. sign convention은 voltage/current 및 terminal definition으로 관리한다.

기본 row convention은 각 programming pulse **이후** 측정된 state다. pre-pulse readout importer는 canonical convention으로 변환하고 provenance를 기록한다.

## 7. Metadata sidecar

다음 구조를 구현하라.

```json
{
  "schema_version": "[VERSION]",
  "device": {
    "device_id": "...",
    "terminal_count": 3,
    "technology_tags": ["ecram"],
    "platform_tags": ["tft", "transistor", "three-terminal"],
    "mechanism_tags": ["electrochemical", "ion-insertion", "redox"],
    "material_tags": ["oxide", "electrolyte"],
    "behavior_tags": ["analog", "multilevel", "nonvolatile"],
    "custom_tags": [],
    "notes": ""
  },
  "experiment": {
    "profile": "pulse-update",
    "instrument": "",
    "source_format": "canonical-csv",
    "temperature_k": 300.0,
    "notes": ""
  },
  "license": "",
  "source_url": "",
  "citation": ""
}
```

Validation 원칙:

- terminal count와 terminal platform tag 충돌 → error
- metadata device ID와 CSV device ID 불일치 → error
- 일반적이지 않지만 가능한 technology/topology 조합 → warning
- mechanism 불명확 → `unknown` 허용
- 다른 schema version → migration warning

Report summary에는 각 tag group, topology tag, `all_tags`를 포함한다.

## 8. Topology-aware energy

다음 규칙을 코드 수준에서 강제하라.

1. `pulse_current_a`가 완전하면 `|V_program I_program t|`를 사용한다.
2. `pulse_current_a`는 실제 programming path current를 의미해야 한다.
3. `V_program² G_read t` fallback은 metadata가 **명시적으로 2-terminal DUT**임을 확인할 때만 허용한다.
4. terminal topology가 없으면 fallback을 사용하지 않는다.
5. 3T/4T/multi-terminal에서 programming current가 없으면 `not_computed`로 보고한다.
6. channel read conductance를 gate/electrolyte/write-terminal current로 대체하지 않는다.
7. scalar `VIt`가 RC transient, displacement current, ionic current, compliance clipping, overshoot, finite bandwidth를 놓칠 수 있음을 문서화한다.
8. sampled waveform integration은 roadmap에 포함한다.

## 9. Synthetic software-test preset

다음 pulse-update preset을 제공하라.

```text
rram-2t
pcm-pram-2t
cbram-2t
ecram-tft-3t
fefet-tft-3t
memtransistor-4t
```

Synthetic trace는 schema, test, tutorial용이며 compact physical model이나 literature benchmark가 아니다. FRAM polarization을 단순 conductance trajectory로 대표하지 마라.

프로젝트의 default example은 특정 ECRAM 중심으로 보이지 않도록 `rram-2t` 또는 2T/3T 비교 workflow로 구성한다.

## 10. CLI

최소 다음 명령을 구현하라.

```text
memdevice-bench taxonomy
memdevice-bench device-profiles
memdevice-bench presets
memdevice-bench init-metadata --template ecram-tft-3t ...
memdevice-bench init-metadata --terminals 4 --technology memtransistor ...
memdevice-bench validate TRACE.csv --metadata META.json
memdevice-bench validate-metadata META.json
memdevice-bench analyze TRACE.csv --metadata META.json --output-dir REPORT/
memdevice-bench generate --preset rram-2t --output TRACE.csv
```

명령 실패 시 readable error와 nonzero exit code를 제공한다.

## 11. Python package 구조

```text
src/memdevice_bench/
  __init__.py
  taxonomy.py
  device_profiles.py
  metadata.py
  schema.py
  io.py
  metrics.py
  energy.py
  retention.py
  synthetic.py
  analysis.py
  report.py
  cli.py
```

외부 의존성은 가능한 한 `numpy`, `pandas`, `matplotlib`로 제한한다. Python 3.10 이상, type hints, docstrings, 명확한 error messages를 제공한다.

## 12. 테스트 기준

다음을 자동 테스트하라.

1. synthetic 2T/3T/4T trace가 schema를 통과한다.
2. `ReRAM`, `FeRAM`, `2T`, `TFT`, `ECM` alias가 normalize된다.
3. terminal count와 terminal tag 충돌이 검출된다.
4. technology tag와 platform tag가 별도 축으로 유지된다.
5. metadata device ID와 table device ID 불일치가 검출된다.
6. measured `VIt`와 2T fallback energy가 구분된다.
7. topology 미확인 상태에서는 `V²G_readt` fallback이 거부된다.
8. 3T/4T에서 programming current가 없으면 energy를 계산하지 않는다.
9. metric이 알려진 synthetic trajectory에서 기대 범위를 만족한다.
10. CLI generate → validate → analyze end-to-end가 작동한다.
11. template 기반 metadata 생성이 작동한다.
12. report에 normalized metadata, topology tag, `all_tags`가 포함된다.
13. `pytest`, `ruff`, `mypy`, package build, metadata check가 통과한다.

## 13. Measurement artifact 분석

문서에 최소 다음을 포함하라.

- pulse generator output impedance와 load-dependent amplitude
- rise/fall time 및 cable/probe bandwidth
- SMU/PMU sampling rate와 integration time
- trigger skew와 write/read timing
- RC charging 및 displacement current
- gate/electrolyte leakage와 ionic current
- current compliance clipping 및 waveform distortion
- read averaging에 의한 apparent noise 감소
- state relaxation과 read-delay dependence
- low-current floor, autoranging, sign convention

각 metric의 숫자만 제시하지 말고 어떤 artifact가 해당 metric을 바꿀 수 있는지 설명한다.

## 14. 연구 해석과 reviewer 관점

프로젝트를 다음처럼 설명한다.

> A topology-aware, tag-based data standard and analysis toolkit that preserves programming/read path provenance across 2T, 3T, and 4T memory devices.

Universal device ranking tool로 표현하지 마라.

Reviewer가 질문할 항목:

- 서로 다른 pulse/read 조건을 직접 비교했는가?
- terminal count가 실제 DUT interface인가?
- programming current path가 명확한가?
- waveform bandwidth/compliance를 검증했는가?
- mechanism tag가 증거에 기반하는가?
- FRAM/FeFET/ECRAM의 서로 다른 observables를 억지로 같은 metric에 넣지 않았는가?
- synthetic data를 실제 모델처럼 사용하지 않았는가?

## 15. 문서 및 repository 산출물

다음을 작성하라.

- English README
- Korean README
- tagging model 문서
- data schema 문서
- metrics 및 physical limitation 문서
- architecture 문서
- Korean project brief
- reusable master prompt
- contribution guide
- governance, security, code of conduct
- roadmap
- public dataset card template
- GitHub issue/PR templates
- CI, release, dependency update, OpenSSF scorecard workflow
- Apache-2.0 license
- `CITATION.cff`
- generic open-source support application draft
- public launch checklist

## 16. Projectization 전략

외부 기여 단위를 다음처럼 독립적으로 유용하게 설계한다.

- Keithley/Keysight/QCoDeS/PyMeasure/SweepMe! importer 1개
- public dataset card와 licensed trace 1개
- metric 1개와 analytical/regression test
- RC/compliance/bandwidth artifact detector 1개
- experiment profile schema 1개
- terminology/documentation review 1개

외부 contributor 수를 늘리기 위해 trivial PR을 분할하지 마라. adoption, download, citation, dependent project, contributor 수를 만들어내지 말고 검증 가능한 evidence log만 유지한다.

## 17. Pitch 산출물

구현 후 다음 설명을 추가로 작성하라.

1. 100자 프로젝트 소개
2. 3문장 elevator pitch
3. 연구자 대상 300자 설명
4. 공동연구 제안용 1페이지 개요
5. 오픈소스 지원 신청용 problem/solution/impact/maintenance 초안
6. GitHub About 문구와 repository topic
7. 첫 3개 milestone과 성공 기준

지원 프로그램의 현재 eligibility를 확인하지 않았다면 충족한다고 주장하지 마라. 사용자가 제공하지 않은 adoption이나 숫자를 만들지 마라.

## 18. 금지사항

- 프로젝트 이름 또는 설명을 ECRAM 전용으로 되돌리지 마라.
- `TFT`를 technology와 같은 축으로 취급하지 마라.
- `1T1R`에서 terminal count를 자동 추론하지 마라.
- mechanism을 device name만으로 확정하지 마라.
- unknown topology에서 2T energy fallback을 사용하지 마라.
- multi-terminal energy를 `G_read`로 대체하지 마라.
- 아직 구현하지 않은 profile을 완료했다고 쓰지 마라.
- synthetic data를 real physical model 또는 literature benchmark로 표현하지 마라.
- universal device-quality score를 만들지 마라.
- 근거 없는 adoption, download, citation, contributor 숫자를 쓰지 마라.

## 19. 최종 출력 형식

다음 순서로 출력하라.

1. 가장 적절한 프로젝트 정의
2. 문제와 물리적 차별점
3. multi-axis taxonomy 표
4. 대표 2T/3T/4T tag 사례
5. architecture와 repository tree
6. 실행 가능한 source code
7. data/metadata schema
8. CLI와 Python quick start
9. 테스트 결과
10. measurement artifact 및 limitation
11. research/reviewer interpretation
12. project roadmap와 contribution map
13. pitch 문구 세트
14. 공개 전 placeholder 및 검증 체크리스트

코드는 실행 가능해야 하며, 테스트하지 못한 부분은 테스트했다고 주장하지 마라. 실패한 항목이 있으면 정확한 원인과 수정 계획을 제시한다.

---
