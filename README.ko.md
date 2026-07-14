# MemDeviceBench

**MemDeviceBench**는 특정 ECRAM·RRAM 소자에 종속되지 않고, **2단자·3단자·4단자·다단자 메모리 및 적응형 전자소자**의 측정 데이터를 표준화하고 분석하는 오픈소스 Python 프로젝트입니다.

프로젝트 이름에서 ECRAM을 제거하고, 소자를 다음과 같은 **독립적인 태그 축**으로 표현하도록 다시 설계했습니다.

| 축 | 대표 태그 |
|---|---|
| 기술/소자 개념 | `rram`, `pram`, `pcm`, `fram`, `fefet`, `ecram`, `cbram`, `mram`, `memtransistor` |
| 접근 가능한 단자 | `two-terminal`, `three-terminal`, `four-terminal`, `multi-terminal` |
| 플랫폼/형태 | `resistor`, `capacitor`, `transistor`, `fet`, `tft`, `oect`, `crossbar`, `1t1r-cell`, `1t1c-cell` |
| 물리 메커니즘 | `filamentary`, `phase-change`, `ferroelectric`, `electrochemical`, `ion-insertion`, `charge-trap`, `magnetic`, `unknown` |
| 재료 | `oxide`, `chalcogenide`, `ferroelectric-oxide`, `organic`, `two-dimensional`, `electrolyte` |
| 관측된 거동 | `analog`, `binary`, `multilevel`, `volatile`, `nonvolatile`, `synaptic`, `stochastic` |
| 측정 프로파일 | `pulse-update`, `dc-iv`, `transfer-curve`, `retention`, `endurance`, `polarization`, `impedance` |

핵심은 `RRAM`, `TFT`, `3T`를 같은 종류의 단일 선택지로 만들지 않는 것입니다. 예를 들어 3단자 ECRAM은 다음처럼 동시에 태깅됩니다.

```text
technology: ecram
terminal:   three-terminal
platform:   tft, transistor
mechanism:  electrochemical, ion-insertion, redox
material:   oxide, electrolyte
behavior:   analog, multilevel, nonvolatile
```

## 대표 조합

| 측정 대상 | 기술 태그 | 단자 구조 | 플랫폼 태그 |
|---|---|---:|---|
| oxide RRAM element | `rram` | 2T | `resistor`, `crossbar` |
| PCM/PRAM element | `pcm`, `pram` | 2T | `resistor` |
| FRAM capacitor test structure | `fram` | 2T | `capacitor` |
| FeFET test structure | `fefet` | 3T | `fet`, `tft`, `transistor` |
| ECRAM transistor | `ecram` | 3T | `tft`, `transistor` |
| charge-trap memory TFT | `charge-trap-memory`, `memtransistor` | 3T | `tft`, `transistor` |
| dual-gate memtransistor | `memtransistor` | 4T | `tft`, `transistor` |

`terminal_count`는 논문의 회로 표기인 `1T1R`, `1T1C`와 동일하지 않습니다. 실제 측정에서 DUT 외부로 접근 가능한 전기적 단자 수를 기록하고, 회로 셀 구성은 별도 platform tag로 남깁니다.

## 현재 구현 범위

`v0.2.0`의 검증된 core는 **pulse-by-pulse conductance update** 데이터에 집중합니다.

- canonical long-form CSV와 JSON metadata sidecar
- tag alias 정규화와 topology/tag 충돌 검출
- potentiation/depression 선형성, 단조성, update variability, asymmetry
- conductance window와 cycle drift
- power-law retention fitting
- programming-path `V·I·t` energy
- JSON/CSV/PNG 자동 보고서
- CLI 및 Python API

DC I–V, TFT transfer/output curve, FRAM polarization/PUND, transient waveform, EIS, noise는 taxonomy와 roadmap에는 포함하지만, 현재 core가 모두 분석한다고 주장하지 않습니다.

## 빠른 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

memdevice-bench taxonomy
memdevice-bench device-profiles
memdevice-bench presets
```

2단자 RRAM software-test trace 생성 및 분석:

```bash
memdevice-bench generate \
  --preset rram-2t \
  --output examples/rram_2t.csv

memdevice-bench validate \
  examples/rram_2t.csv \
  --metadata examples/rram_2t.metadata.json

memdevice-bench analyze \
  examples/rram_2t.csv \
  --metadata examples/rram_2t.metadata.json \
  --output-dir examples/rram_2t_report
```

공통 소자 템플릿에서 metadata 생성:

```bash
memdevice-bench init-metadata \
  --template ecram-tft-3t \
  --device-id wafer03-d17 \
  --output wafer03-d17.metadata.json \
  --instrument "Keithley 4200A-SCS"
```

완전 수동 태깅:

```bash
memdevice-bench init-metadata \
  --output device.metadata.json \
  --device-id device-001 \
  --terminals 4 \
  --technology memtransistor \
  --platform tft transistor \
  --mechanism charge-trap \
  --material oxide two-dimensional \
  --behavior analog multilevel nonvolatile
```

## 에너지 계산에서의 핵심 물리

우선순위는 실제 programming path의 측정값입니다.

```text
E = |V_program I_program t_pulse|
```

`V_program² G_read t_pulse` fallback은 metadata가 **명시적으로 2단자 DUT임을 확인할 때만** 허용됩니다. terminal topology가 없거나 3T/4T로 기록된 경우에는 channel read conductance를 gate/electrolyte/write-path current로 대체하지 않고 `not_computed`로 남깁니다.

또한 scalar `VIt`만으로는 짧은 RC transient, displacement current, ionic relaxation, compliance clipping, pulse overshoot, 케이블/프로브 대역폭을 충분히 반영하지 못할 수 있습니다. 실제 논문용 energy는 가능하면 sampled waveform 적분과 instrument timing 검증이 필요합니다.

## 내장 tag profile

`memdevice-bench device-profiles` 명령은 다음과 같은 시작 템플릿을 JSON으로 제공합니다.

- `rram-2t`
- `cbram-2t`
- `pcm-pram-2t`
- `fram-capacitor-2t`
- `ftj-2t`
- `mram-mtj-2t`
- `tft-generic-3t`
- `fefet-tft-3t`
- `ecram-tft-3t`
- `oect-memory-3t`
- `charge-trap-tft-3t`
- `flash-mosfet-3t`
- `dual-gate-memtransistor-4t`

이 템플릿은 분류 시작점일 뿐입니다. mechanism, material, volatile/nonvolatile 여부는 실제 소자의 구조와 측정 증거에 맞게 수정해야 합니다.

## Synthetic preset

pulse-update software test용으로 다음 preset을 제공합니다.

- `rram-2t`
- `pcm-pram-2t`
- `cbram-2t`
- `ecram-tft-3t`
- `fefet-tft-3t`
- `memtransistor-4t`

Synthetic data는 코드와 schema 검증용이며 compact physical model이나 문헌 benchmark가 아닙니다. 특히 FRAM capacitor를 단순 conductance trajectory로 대표하지 않으며, polarization/PUND profile은 향후 확장 항목입니다.

## 프로젝트화 자료

- 프로젝트 기획서: [`docs/project-brief-ko.md`](docs/project-brief-ko.md)
- 태그 모델: [`docs/tagging.md`](docs/tagging.md)
- 데이터 형식: [`docs/data-format.md`](docs/data-format.md)
- 분석 지표와 물리적 한계: [`docs/metrics.md`](docs/metrics.md)
- 구현 아키텍처: [`docs/architecture.md`](docs/architecture.md)
- 구현·설명·로드맵 작성을 위한 마스터 프롬프트: [`prompts/MEMDEVICEBENCH_PROJECT_PROMPT_KO.md`](prompts/MEMDEVICEBENCH_PROJECT_PROMPT_KO.md)
- 공개 준비 체크리스트: [`PROJECT_LAUNCH.md`](PROJECT_LAUNCH.md)

이 프로젝트의 목적은 모든 소자를 하나의 점수로 순위화하는 것이 아니라, 비교 조건과 물리적 가정을 드러내고 분석 provenance를 보존하는 것입니다.
