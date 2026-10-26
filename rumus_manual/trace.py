"""Trace piksel menggunakan fungsi filter yang sama dengan hasil gambar."""
import math
from .common import pad_image
from .filters import median_pixel, adaptive_pixel, gaussian_pixel, gaussian_kernel

def filter_trace(image, method, x, y):
    center = image[y][x]
    if method == 0:
        data = median_pixel(pad_image(image, 1), y, x, 1, trace=True)
    elif method == 1:
        data = adaptive_pixel(pad_image(image, 3), center, y, x, 7, trace=True)
    elif method == 2:
        data = gaussian_pixel(pad_image(image, 1), y, x, gaussian_kernel(), trace=True)
        sigma = math.sqrt(1 / (2 * math.log(2)))
        raw = []
        total = 0.0
        for v in (-1, 0, 1):
            row = []
            for u in (-1, 0, 1):
                weight = math.exp(-(u*u + v*v) / (2*sigma*sigma))
                row.append(weight)
                total += weight
            raw.append(row)
        data.update(raw_kernel=raw, raw_sum=total, sigma=sigma)
    else:
        raise ValueError('Metode tidak dikenal.')
    data.update(method=method, x=x, y=y, center=center)
    return data
