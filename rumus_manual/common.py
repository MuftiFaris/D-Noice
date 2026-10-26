"""Implementasi rumus manual; operasi skalar dan perulangan Python."""


def pad_image(image, radius):
    h, w = len(image), len(image[0])
    # Replicate edge pixels so border pixels are processed consistently.
    return [[image[min(max(y, 0), h - 1)][min(max(x, 0), w - 1)]
             for x in range(-radius, w + radius)]
            for y in range(-radius, h + radius)]


def neighborhood(padded, y, x, radius, pad_radius=None):
    offset = radius if pad_radius is None else pad_radius
    yy, xx = y + offset, x + offset
    return [padded[yy + dy][xx + dx]
            for dy in range(-radius, radius + 1)
            for dx in range(-radius, radius + 1)]


def insertion_sort(values):
    """Urutkan salinan nilai secara manual, tanpa sort/sorted/median library."""
    ordered = list(values)
    for i in range(1, len(ordered)):
        current = ordered[i]
        j = i - 1
        while j >= 0 and ordered[j] > current:
            ordered[j + 1] = ordered[j]
            j -= 1
        ordered[j + 1] = current
    return ordered


def validate_window_size(size):
    if isinstance(size, bool) or not isinstance(size, int) or size < 1 or size % 2 == 0:
        raise ValueError("Ukuran jendela harus bilangan bulat positif dan ganjil")
