import argparse
import time

import cv2
import numpy as np
from ultralytics import YOLO

import config
from slot_detection import detect_slots


def parse_source(value):
    return int(value) if value.isdigit() else value


def bbox_overlap_ratio(vehicle_box, slot_polygon):
    """Match the original demo: intersection / axis-aligned slot-box area."""
    vehicle_x1, vehicle_y1, vehicle_x2, vehicle_y2 = vehicle_box
    slot = np.asarray(slot_polygon, dtype=np.float32)
    slot_x1, slot_y1 = slot.min(axis=0)
    slot_x2, slot_y2 = slot.max(axis=0)

    intersection_x1 = max(vehicle_x1, slot_x1)
    intersection_y1 = max(vehicle_y1, slot_y1)
    intersection_x2 = min(vehicle_x2, slot_x2)
    intersection_y2 = min(vehicle_y2, slot_y2)
    intersection = (
        max(0.0, intersection_x2 - intersection_x1)
        * max(0.0, intersection_y2 - intersection_y1)
    )
    slot_area = max(0.0, slot_x2 - slot_x1) * max(0.0, slot_y2 - slot_y1)
    return float(intersection / slot_area) if slot_area > 0 else 0.0


def polygon_overlap_ratio(vehicle_box, slot_polygon):
    """Optional improvement: intersection / actual polygon area."""
    x1, y1, x2, y2 = vehicle_box
    vehicle_polygon = np.asarray(
        [[x1, y1], [x2, y1], [x2, y2], [x1, y2]],
        dtype=np.float32,
    )
    slot = np.asarray(slot_polygon, dtype=np.float32)
    slot_area = abs(cv2.contourArea(slot))
    if slot_area <= 0:
        return 0.0
    intersection_area, _ = cv2.intersectConvexConvex(slot, vehicle_polygon)
    return float(intersection_area) / slot_area


def overlap_ratio(vehicle_box, slot_polygon, mode="bbox"):
    if mode == "bbox":
        return bbox_overlap_ratio(vehicle_box, slot_polygon)
    if mode == "polygon":
        return polygon_overlap_ratio(vehicle_box, slot_polygon)
    raise ValueError(f"Unsupported overlap mode: {mode}")


def draw_summary(frame, total, occupied):
    cv2.rectangle(frame, (0, 0), (420, 52), (30, 30, 30), -1)
    text = f"Total: {total} | Occupied: {occupied} | Free: {total - occupied}"
    cv2.putText(
        frame,
        text,
        (15, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Run the smart parking monitor.")
    parser.add_argument("--source", default="0", help="Camera index or video path.")
    parser.add_argument("--model", default=str(config.MODEL_PATH))
    parser.add_argument("--conf", type=float, default=config.CONFIDENCE_THRESHOLD)
    parser.add_argument("--refresh", type=float, default=config.SLOT_REFRESH_SECONDS)
    parser.add_argument(
        "--overlap-mode",
        choices=("bbox", "polygon"),
        default="bbox",
        help="bbox matches the original demo; polygon uses the actual ROI area.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    model = YOLO(args.model)
    capture = cv2.VideoCapture(parse_source(args.source))
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open source: {args.source}")

    slots = []
    last_slot_update = float("-inf")
    class_ids = set(config.CLASS_MAP.values())

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        now = time.monotonic()
        should_refresh = args.refresh > 0 and now - last_slot_update >= args.refresh
        if should_refresh:
            detected, _ = detect_slots(frame)
            if detected:
                slots = detected
            last_slot_update = now

        display = frame.copy()
        overlay = frame.copy()
        result = model(frame, conf=args.conf, verbose=False)[0]

        vehicle_boxes = []
        for box in result.boxes:
            if int(box.cls[0]) not in class_ids:
                continue
            coordinates = tuple(map(int, box.xyxy[0]))
            vehicle_boxes.append(coordinates)
            x1, y1, x2, y2 = coordinates
            cv2.rectangle(display, (x1, y1), (x2, y2), (255, 165, 0), 2)

        occupied_count = 0
        for slot_id, polygon in enumerate(slots, start=1):
            occupied = any(
                overlap_ratio(vehicle_box, polygon, args.overlap_mode)
                >= config.OCCUPANCY_THRESHOLD
                for vehicle_box in vehicle_boxes
            )
            color = (0, 0, 255) if occupied else (0, 255, 0)
            occupied_count += int(occupied)

            cv2.fillPoly(overlay, [polygon], color)
            cv2.polylines(display, [polygon], True, color, 2)
            center = polygon.mean(axis=0).astype(int)
            status = "OCCUPIED" if occupied else "EMPTY"
            cv2.putText(
                display,
                f"#{slot_id} {status}",
                tuple(center),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                2,
            )

        cv2.addWeighted(overlay, 0.35, display, 0.65, 0, display)
        draw_summary(display, len(slots), occupied_count)
        cv2.imshow("Smart Parking Monitor", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            detected, _ = detect_slots(frame)
            if detected:
                slots = detected
                last_slot_update = now

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
