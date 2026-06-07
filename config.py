from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ASSET_DIR = BASE_DIR / "assets"
MODEL_PATH = BASE_DIR / "models" / "best.pt"
EMPTY_IMAGE_PATH = ASSET_DIR / "empty_parking.jpg"
SLOTS_JSON_PATH = BASE_DIR / "slots.json"
SLOT_PREVIEW_PATH = ASSET_DIR / "slot_preview.jpg"

SOURCE_ROOT = BASE_DIR / "project_data"
SOURCE_SPLITS = {
    "train": ("train",),
    "val": ("valid", "val"),
}
DATASET_NAME = "mini_parking"
DATASET_ROOT = BASE_DIR / "datasets" / DATASET_NAME
YAML_PATH = BASE_DIR / f"{DATASET_NAME}.yaml"

CLASS_MAP = {
    "car": 0,
    "motorcycle": 1,
}
LABEL_ALIAS = {
    "automobile": "car",
    "bike": "motorcycle",
    "motorbike": "motorcycle",
}

MODEL_NAME = "yolo26n.pt"
IMAGE_SIZE = 640
EPOCHS = 300
BATCH_SIZE = 16
DEVICE = 0
TRAIN_PROJECT_DIR = BASE_DIR / "runs" / "train"
RUN_NAME = f"{DATASET_NAME}_yolo26n"

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
CONFIDENCE_THRESHOLD = 0.30
OCCUPANCY_THRESHOLD = 0.30
SLOT_REFRESH_SECONDS = 0.0

GREEN_LOWER = (35, 70, 70)
GREEN_UPPER = (85, 255, 255)
MIN_SLOT_AREA = 2_000
MAX_SLOT_AREA = 500_000
MIN_SLOT_WIDTH = 20
MAX_SLOT_WIDTH = 800
MIN_SLOT_HEIGHT = 20
MAX_SLOT_HEIGHT = 1_000
MIN_ASPECT_RATIO = 0.1
MAX_ASPECT_RATIO = 10.0
