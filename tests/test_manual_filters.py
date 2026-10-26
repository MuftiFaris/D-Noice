"""Jalankan: python -B -m unittest -v test_manual_filters.py."""
import math
import unittest

from denoise_manual import (
    adaptive_median_filter, gaussian_filter, gaussian_kernel,
    insertion_sort, median_filter,
)


class ManualFilterTests(unittest.TestCase):
    def test_sort_duplicates_and_input_preserved(self):
        values = [255, 0, 100, 100, 2]
        self.assertEqual(insertion_sort(values), [0, 2, 100, 100, 255])
        self.assertEqual(values, [255, 0, 100, 100, 2])

    def test_median_impulse(self):
        image = [[100, 102, 101], [99, 255, 103], [101, 98, 102]]
        self.assertEqual(median_filter(image)[1][1], 101)
        self.assertEqual(image[1][1], 255)

    def test_adaptive_preserves_center(self):
        image = [[0, 100, 255], [100, 110, 100], [100, 100, 100]]
        self.assertEqual(adaptive_median_filter(image)[1][1], 110)

    def test_adaptive_expands_window(self):
        image = [
            [100, 100, 100, 100, 100],
            [100, 0, 0, 255, 100],
            [100, 0, 255, 0, 100],
            [100, 255, 0, 100, 100],
            [100, 100, 100, 100, 100],
        ]
        self.assertEqual(adaptive_median_filter(image, 3)[2][2], 0)
        self.assertEqual(adaptive_median_filter(image, 5)[2][2], 100)

    def test_constant_and_single_pixel(self):
        for image in ([[80]], [[80, 80, 80], [80, 80, 80]]):
            for fn in (median_filter, adaptive_median_filter, gaussian_filter):
                self.assertEqual(fn(image), image)

    def test_default_gaussian_matches_legacy_kernel(self):
        expected = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
        kernel = gaussian_kernel()
        for y in range(3):
            for x in range(3):
                self.assertAlmostEqual(kernel[y][x], expected[y][x] / 16, places=14)

    def test_sigma_one_is_explicitly_different(self):
        kernel = gaussian_kernel(3, 1)
        self.assertAlmostEqual(kernel[1][1], 0.2041799555716581, places=13)
        self.assertAlmostEqual(sum(sum(row) for row in kernel), 1.0, places=14)
        self.assertEqual(kernel[0][0], kernel[2][2])

    def test_gaussian_hand_calculation(self):
        image = [[100, 102, 101], [99, 255, 103], [101, 98, 102]]
        # (405 + 1424 + 399) / 16 = 139.25 -> 139.
        self.assertEqual(gaussian_filter(image)[1][1], 139)

    def test_half_up_rounding(self):
        image = [[0, 0, 0], [0, 2, 0], [0, 0, 0]]
        self.assertEqual(gaussian_filter(image)[1][1], 1)

    def test_invalid_parameters(self):
        for size in (0, 2, -3, 3.5, True):
            with self.assertRaises(ValueError):
                median_filter([[100]], size)
            with self.assertRaises(ValueError):
                gaussian_kernel(size)
        for sigma in (0, -1, math.inf, math.nan, True):
            with self.assertRaises(ValueError):
                gaussian_kernel(sigma=sigma)


if __name__ == "__main__":
    unittest.main()
