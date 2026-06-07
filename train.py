from ultralytics import YOLO

import config


def main():
    if not config.YAML_PATH.exists():
        raise FileNotFoundError(
            f"Missing dataset YAML: {config.YAML_PATH}. "
            "Run create_dataset_yaml.py first."
        )

    model = YOLO(config.MODEL_NAME)
    model.train(
        data=str(config.YAML_PATH),
        epochs=config.EPOCHS,
        imgsz=config.IMAGE_SIZE,
        batch=config.BATCH_SIZE,
        device=config.DEVICE,
        project=str(config.TRAIN_PROJECT_DIR),
        name=config.RUN_NAME,
        pretrained=True,
        seed=42,
        exist_ok=True,
    )


if __name__ == "__main__":
    main()

