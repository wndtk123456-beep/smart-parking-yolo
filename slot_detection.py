import json
from pathlib import Path

import cv2
import numpy as np

import config


def order_points_clockwise(points):
    points = np.asarray(points, dtype=np.float32)
    center = points.mean(axis=0)
    angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
    ordered = points[np.argsort(angles)]
    start = np.argmin(ordered[:, 1] + ordered[:, 0] * 0.001)
    return np.roll(ordered, -start, axis=0).astype(np.int32)


def bounding_box_iou(poly_a, poly_b):
    ax, ay, aw, ah = cv2.boundingRect(np.asarray(poly_a, dtype=np.int32))
    bx, by, bw, bh = cv2.boundingRect(np.asarray(poly_b, dtype=np.int32))
    ix1, iy1 = max(ax, bx), max(ay, by)
    ix2, iy2 = min(ax + aw, bx + bw), min(ay + ah, by + bh)
    intersection = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0.0


def detect_slots(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        np.asarray(config.GREEN_LOWER, dtype=np.uint8),
        np.asarray(config.GREEN_UPPER, dtype=np.uint8),
    )
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if not config.MIN_SLOT_AREA <= area <= config.MAX_SLOT_AREA:
            continue

        rect = cv2.minAreaRect(contour)
        (_, _), (width, height), _ = rect
        long_side, short_side = max(width, height), min(width, height)
        ratio = long_side / max(short_side, 1)

        if not config.MIN_SLOT_HEIGHT <= long_side <= config.MAX_SLOT_HEIGHT:
            continue
        if not config.MIN_SLOT_WIDTH <= short_side <= config.MAX_SLOT_WIDTH:
            continue
        if not config.MIN_ASPECT_RATIO <= ratio <= config.MAX_ASPECT_RATIO:
            continue

        candidates.append(order_points_clockwise(cv2.boxPoints(rect)))

    filtered = []
    for candidate in candidates:
        if all(bounding_box_iou(candidate, saved) <= 0.20 for saved in filtered):
            filtered.append(candidate)

    return sorted(
        filtered,
        key=lambda poly: (
            int(np.mean(poly[:, 1]) // 60),
            int(np.mean(poly[:, 0])),
        ),
    ), mask


def save_slots(slots, image_shape, output_path):
    height, width = image_shape[:2]
    payload = {
        "image_width": int(width),
        "image_height": int(height),
        "slots": {
            str(index): polygon.astype(int).tolist()
            for index, polygon in enumerate(slots, start=1)
        },
    }
    Path(output_path).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def draw_slot_preview(image, slots):
    preview = image.copy()
    for index, polygon in enumerate(slots, start=1):
        cv2.polylines(preview, [polygon], True, (0, 255, 0), 3)
        center = polygon.mean(axis=0).astype(int)
        cv2.putText(
            preview,
            f"slot_{index}",
            tuple(center),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
    return preview

