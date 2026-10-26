"""Implementasi rumus manual; operasi skalar dan perulangan Python."""
import math
from .common import pad_image, neighborhood, insertion_sort, validate_window_size


def median_pixel(src, y, x, radius, trace=False):
    values = neighborhood(src, y, x, radius)
    ordered = insertion_sort(values)
    value = ordered[len(ordered) // 2]
    if trace:
        return {"values": values, "ordered": ordered, "index": len(ordered) // 2,
                "value": value, "size": radius * 2 + 1}
    return value


def adaptive_pixel(src, center, y, x, max_size, trace=False):
    levels = []
    chosen = center
    for size in range(3, max_size + 1, 2):
        values = neighborhood(src, y, x, size // 2, max_size // 2)
        ordered = insertion_sort(values)
        low, high, med = ordered[0], ordered[-1], ordered[len(ordered) // 2]
        a1, a2 = med - low, med - high
        b1, b2 = center - low, center - high
        passed_a = a1 > 0 and a2 < 0
        passed_b = b1 > 0 and b2 < 0
        chosen = (center if passed_b else med) if passed_a else med
        if trace:
            levels.append(dict(size=size, values=values, ordered=ordered, minimum=low,
                               maximum=high, median=med, a1=a1, a2=a2, b1=b1, b2=b2,
                               passed_a=passed_a, passed_b=passed_b, value=chosen))
        if passed_a:
            break
    return {"levels": levels, "center": center, "value": chosen} if trace else chosen


def median_filter(image, size=3, on_progress=None, on_preview=None):
    """Ambil tetangga, urutkan manual, lalu pilih nilai tengah."""
    validate_window_size(size)
    radius = size // 2
    src, h, w = pad_image(image, radius), len(image), len(image[0])
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(median_pixel(src, y, x, radius))
        result.append(row)
        if on_progress:
            on_progress(y + 1, h)
        if on_preview:
            on_preview(result, y + 1, h)
    return result


def adaptive_median_filter(image, max_size=7, on_progress=None, on_preview=None):
    """Adaptive median klasik: tahap A, tahap B, dan perluasan jendela."""
    validate_window_size(max_size)
    if max_size < 3 or max_size % 2 == 0:
        raise ValueError("Ukuran maksimum adaptive median harus ganjil dan minimal 3")
    h, w = len(image), len(image[0])
    src = pad_image(image, max_size // 2)
    result = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            result[y][x] = adaptive_pixel(src, image[y][x], y, x, max_size)
        if on_progress:
            on_progress(y + 1, h)
        if on_preview:
            on_preview(result, y + 1, h)
    return result


def gaussian_kernel(size=3, sigma=None):
    """Bentuk kernel dari exp(-(u^2+v^2)/(2*sigma^2)), lalu normalisasi.

    math hanya menyediakan operasi skalar exp/log/sqrt; bukan fungsi filter.
    Default sigma = sqrt(1/(2*ln(2))) membuat bobot 1D relatif [1,2,1]
    pada ukuran 3, sehingga mempertahankan konfigurasi Gaussian lama.
    Faktor 1/(2*pi*sigma^2) saling membatalkan saat normalisasi diskret.
    """
    validate_window_size(size)
    if sigma is None:
        sigma = math.sqrt(1.0 / (2.0 * math.log(2.0)))
    if isinstance(sigma, bool) or not isinstance(sigma, (int, float)) or not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("Sigma harus angka positif dan berhingga")
    radius = size // 2
    kernel = []
    total_weight = 0.0
    for v in range(-radius, radius + 1):
        row = []
        for u in range(-radius, radius + 1):
            # Rasio jarak/sigma juga menghindari pembagian oleh sigma^2
            # yang bisa membulat ke nol untuk sigma sangat kecil.
            scaled_u = u / sigma
            scaled_v = v / sigma
            distance_squared = scaled_u * scaled_u + scaled_v * scaled_v
            weight = math.exp(-0.5 * distance_squared)
            row.append(weight)
            total_weight += weight
        kernel.append(row)
    for y in range(size):
        for x in range(size):
            kernel[y][x] = kernel[y][x] / total_weight
    return kernel


def gaussian_pixel(src, y, x, kernel, trace=False):
    radius = len(kernel) // 2
    total = 0.0
    values, products = [], []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            weight = kernel[radius - dy][radius - dx]
            pixel = src[y + radius + dy][x + radius + dx]
            product = weight * pixel
            total += product
            if trace:
                values.append(pixel)
                products.append(product)
    value = max(0, min(255, int(total + 0.5 + 1e-10)))
    if trace:
        return dict(values=values, products=products, total=total, value=value, kernel=kernel)
    return value


def gaussian_filter(image, size=3, sigma=None, on_progress=None, on_preview=None):
    """Konvolusi Gaussian manual dengan replicate padding dan hasil 8-bit."""
    kernel = gaussian_kernel(size, sigma)
    radius = size // 2
    src, h, w = pad_image(image, radius), len(image), len(image[0])
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            row.append(gaussian_pixel(src, y, x, kernel))
        result.append(row)
        if on_progress:
            on_progress(y + 1, h)
        if on_preview:
            on_preview(result, y + 1, h)
    return result
