import unittest

import cv2

from monitor import bbox_overlap_ratio, overlap_ratio, polygon_overlap_ratio
from slot_detection import detect_slots


class OccupancyTests(unittest.TestCase):
    def setUp(self):
        self.slot = [[0, 0], [100, 0], [100, 100], [0, 100]]

    def test_bbox_overlap_matches_original_formula(self):
        self.assertAlmostEqual(bbox_overlap_ratio((0, 0, 50, 100), self.slot), 0.5)
        self.assertEqual(bbox_overlap_ratio((200, 200, 300, 300), self.slot), 0.0)

    def test_polygon_overlap_is_available_as_option(self):
        self.assertAlmostEqual(
            polygon_overlap_ratio((0, 0, 50, 100), self.slot),
            0.5,
        )
        self.assertAlmostEqual(
            overlap_ratio((0, 0, 50, 100), self.slot, "polygon"),
            0.5,
        )


class SlotDetectionTests(unittest.TestCase):
    def test_reference_image_has_ten_slots(self):
        image = cv2.imread("assets/empty_parking.jpg")
        self.assertIsNotNone(image)
        slots, _ = detect_slots(image)
        self.assertEqual(len(slots), 10)


if __name__ == "__main__":
    unittest.main()
