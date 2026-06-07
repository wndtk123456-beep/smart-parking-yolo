import json
import shutil
from pathlib import Path

import numpy as np

import config

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def resolve_source_dir(candidates):
    for name in candidates:
        source_dir = config.SOURCE_ROOT / name
        if source_dir.exists():
            return source_dir
    raise FileNotFoundError(f"Could not find any source directory: {candidates}")


def convert_shape(shape, image_width, image_height):
    label = config.LABEL_ALIAS.get(shape["label"].strip(), shape["label"].strip())
    if label not in config.CLASS_MAP:
        return None

    points = np.asarray(shape["points"], dtype=float)
    x1, y1 = points.min(axis=0)
    x2, y2 = points.max(axis=0)
    width, height = x2 - x1, y2 - y1
    center_x, center_y = x1 + width / 2, y1 + height / 2
    values = (
        center_x / image_width,
        center_y / image_height,
        width / image_width,
        height / image_height,
    )
    return config.CLASS_MAP[label], values


def convert_split(destination_split, candidates):
    source_dir = resolve_source_dir(candidates)
    image_output = config.DATASET_ROOT / "images" / destination_split
    label_output = config.DATASET_ROOT / "labels" / destination_split
    image_output.mkdir(parents=True, exist_ok=True)
    label_output.mkdir(parents=True, exist_ok=True)

    saved = 0
    for image_path in sorted(source_dir.rglob("*")):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        annotation_path = image_path.with_suffix(".json")
        if not annotation_path.exists():
            continue

        annotation = json.loads(annotation_path.read_text(encoding="utf-8"))
        image_width = annotation.get("imageWidth")
        image_height = annotation.get("imageHeight")
        if not image_width or not image_height:
            continue

        labels = []
        for shape in annotation.get("shapes", []):
            converted = convert_shape(shape, image_width, image_height)
            if converted is None:
                continue
            class_id, values = converted
            labels.append(f"{class_id} " + " ".join(f"{value:.6f}" for value in values))

        if not labels:
            continue

        output_name = f"{saved:04d}"
        shutil.copyfile(
            image_path,
            image_output / f"{output_name}{image_path.suffix.lower()}",
        )
        (label_output / f"{output_name}.txt").write_text(
            "\n".join(labels) + "\n",
            encoding="utf-8",
        )
        saved += 1

    print(f"{source_dir.name} -> {destination_split}: {saved} images")


def main():
    for destination_split, candidates in config.SOURCE_SPLITS.items():
        convert_split(destination_split, candidates)


if __name__ == "__main__":
    main()

