import cv2
import numpy as np

import config


def nothing(_):
    pass


def main():
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not capture.isOpened():
        raise RuntimeError("Could not open camera 0.")

    cv2.namedWindow("controls")
    cv2.resizeWindow("controls", 500, 300)

    defaults = (
        ("H low", config.GREEN_LOWER[0], 179),
        ("H high", config.GREEN_UPPER[0], 179),
        ("S low", config.GREEN_LOWER[1], 255),
        ("S high", config.GREEN_UPPER[1], 255),
        ("V low", config.GREEN_LOWER[2], 255),
        ("V high", config.GREEN_UPPER[2], 255),
    )
    for name, value, maximum in defaults:
        cv2.createTrackbar(name, "controls", value, maximum, nothing)

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        lower = np.asarray(
            [
                cv2.getTrackbarPos("H low", "controls"),
                cv2.getTrackbarPos("S low", "controls"),
                cv2.getTrackbarPos("V low", "controls"),
            ],
            dtype=np.uint8,
        )
        upper = np.asarray(
            [
                cv2.getTrackbarPos("H high", "controls"),
                cv2.getTrackbarPos("S high", "controls"),
                cv2.getTrackbarPos("V high", "controls"),
            ],
            dtype=np.uint8,
        )

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        preview = frame.copy()
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1_500:
                continue
            x, y, width, height = cv2.boundingRect(contour)
            count += 1
            cv2.rectangle(
                preview,
                (x, y),
                (x + width, y + height),
                (0, 255, 0),
                2,
            )
            cv2.putText(
                preview,
                f"green_{count} area={int(area)}",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.imshow("original_with_boxes", preview)
        cv2.imshow("green_mask", mask)
        cv2.imshow("green_only", cv2.bitwise_and(frame, frame, mask=mask))

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("s"):
            cv2.imwrite("green_test_original.jpg", preview)
            cv2.imwrite("green_test_mask.jpg", mask)

    capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
