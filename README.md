# YOLO Smart Parking Monitor

YOLO 차량 검출 결과와 주차면 ROI의 중첩률을 결합해 주차 공간의
`EMPTY / OCCUPIED` 상태를 표시하는 실시간 주차 관제 프로젝트입니다.

> 이 저장소는 부트캠프에서 완료한 3인 팀 프로젝트를 포트폴리오 목적으로
> 정리해 공개한 버전입니다. Git 커밋 날짜는 최초 개발 기간이 아니라
> 코드 정리 및 공개 시점을 나타냅니다.

## 담당 역할

- YOLO 차량 검출 모델 학습 및 결과 검증
- HSV, Contour 기반 주차면 ROI 추출
- 차량 Bounding Box와 ROI 중첩률 계산
- 중첩률 30% 기준 `EMPTY / OCCUPIED` 판정
- 차량 Box, 주차면 상태, 전체·점유·빈자리 결과 화면 구현

## 실행 화면

![Parking slot preview](assets/slot_preview.jpg)

## 처리 과정

```text
Camera frame
  -> YOLO vehicle detection
  -> HSV/Contour parking-slot extraction
  -> Vehicle box and ROI intersection
  -> Occupied when overlap ratio >= 30%
  -> OpenCV monitoring screen
```

원본 시연 코드는 `s` 키를 눌러 주차면을 갱신합니다. 공개본에서는 필요할
때 `--refresh 5` 옵션으로 5초 간격 자동 갱신도 사용할 수 있습니다.
주차면 번호는 화면의 위에서 아래, 같은 행에서는 왼쪽에서 오른쪽 순으로
정렬합니다.

## 모델 학습

| 항목 | 설정 |
|---|---:|
| Model | YOLO26n |
| Image size | 640 |
| Batch size | 16 |
| Epochs | 300 |
| Classes | car, motorcycle |
| Data split | Train 80% / Validation 20% |

실시간 모니터의 기본 confidence는 원본 `cam.py` 설정과 같은 `0.30`입니다.
`--conf 0.35`처럼 실행 시점에 변경할 수 있습니다.

포함된 학습 로그의 마지막 기록(epoch 295)은 다음과 같습니다.

| Precision | Recall | mAP50 | mAP50-95 |
|---:|---:|---:|---:|
| 0.953 | 0.884 | 0.948 | 0.781 |

![Training results](assets/training_results.png)

![Validation predictions](assets/validation_predictions.jpg)

## 프로젝트 구조

```text
.
├── arduino/
│   └── parking_led.ino
├── assets/
├── models/
│   └── best.pt
├── config.py
├── create_dataset_yaml.py
├── detect_slots.py
├── monitor.py
├── prepare_dataset.py
├── slot_detection.py
├── tests/
│   └── test_logic.py
├── tune_hsv.py
├── train.py
└── slots.json
```

## 설치 및 실행

Python 3.10 이상을 권장합니다.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python monitor.py --source 0
```

영상 파일을 사용할 수도 있습니다.

```bash
python monitor.py --source path/to/video.mp4
```

원본과 동일한 사각형 중첩 방식이 기본값입니다. 실제 Polygon 면적을
사용하려면 다음 옵션을 추가합니다.

```bash
python monitor.py --source 0 --overlap-mode polygon
```

주차면을 5초마다 자동으로 다시 검출하려면:

```bash
python monitor.py --source 0 --refresh 5
```

주차면만 다시 추출하려면:

```bash
python detect_slots.py --image assets/empty_parking.jpg
```

## 데이터셋 준비와 재학습

원본 촬영 데이터는 용량과 팀 데이터 관리 문제로 저장소에 포함하지
않았습니다. LabelMe 형식의 `train`, `valid` 폴더를 `project_data` 아래에
배치한 후 실행합니다.

```bash
python prepare_dataset.py
python create_dataset_yaml.py
python train.py
```


## 트러블슈팅

| 문제 | 원인 | 해결 |
|---|---|---|
| 주차면 ROI가 중복 검출됨 | HSV/Contour로 주차선을 찾을 때 같은 주차면의 외곽선이 여러 개 잡힘 | ROI 간 IoU를 계산해 중복 후보를 제거하고 위에서 아래, 왼쪽에서 오른쪽 순서로 정렬 |
| 조명 변화에 따라 주차선 검출이 흔들림 | 촬영 환경의 밝기와 바닥 반사 때문에 HSV 범위가 고정값으로 맞지 않음 | `tune_hsv.py`로 환경별 HSV 범위를 조정하고 contour 면적, 종횡비 조건을 함께 적용 |
| 경계에 걸친 차량이 빈자리로 판정됨 | 차량 박스와 주차면 ROI의 중첩 면적이 낮게 계산됨 | bbox 중첩 기본값을 유지하되 `--overlap-mode polygon` 옵션으로 실제 polygon 면적 계산을 선택 가능하게 구성 |
| 주차면 번호가 매 실행마다 달라짐 | contour 검출 순서가 OpenCV 내부 순서에 의존함 | ROI 중심 좌표 기준으로 행/열 정렬을 적용해 번호를 고정 |
| 원본 데이터셋을 저장소에 포함하기 어려움 | 팀 프로젝트 촬영 데이터와 라벨 데이터의 용량 및 관리 이슈 | 재학습 절차와 LabelMe 변환 스크립트를 제공하고, 공개 가능한 모델 가중치와 결과 이미지만 포함 |

## 한계와 개선 방향

- 고정 카메라와 특정 색상의 주차선에 맞춘 방식입니다.
- 조명 변화가 크면 HSV 범위를 환경에 맞게 다시 조정해야 합니다.
- 차량 위치와 촬영 각도에 따라 경계 부근의 점유 판정 오차가 발생할 수 있습니다.
- 향후 주차면 검출 모델 또는 카메라 캘리브레이션을 적용할 수 있습니다.
