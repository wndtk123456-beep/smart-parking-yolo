import argparse

import cv2

import config
from slot_detection import detect_slots, draw_slot_preview, save_slots


def parse_args():
    parser = argparse.ArgumentParser(description="Extract parking-slot polygons.")
    parser.add_argument("--image", default=str(config.EMPTY_IMAGE_PATH))
    parser.add_argument("--output", default=str(config.SLOTS_JSON_PATH))
    parser.add_argument("--preview", default=str(config.SLOT_PREVIEW_PATH))
    return parser.parse_args()


def main():
    args = parse_args()
    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {args.image}")

    slots, mask = detect_slots(image)
    if not slots:
        cv2.imwrite("debug_green_mask.jpg", mask)
        raise RuntimeError("No parking slots found. Adjust the HSV and size filters.")

    save_slots(slots, image.shape, args.output)
    cv2.imwrite(args.preview, draw_slot_preview(image, slots))
    print(f"Saved {len(slots)} slots to {args.output}")


if __name__ == "__main__":
    main()

