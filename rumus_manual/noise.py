"""Implementasi rumus manual; operasi skalar dan perulangan Python."""
import random


def add_salt_pepper(image, percent, seed):
    h, w = len(image), len(image[0])
    out = [row[:] for row in image]
    count = round(h * w * percent / 100)
    positions = random.Random(seed).sample(range(h * w), count)
    for i, p in enumerate(positions):
        y, x = divmod(p, w)
        out[y][x] = 0 if i % 2 == 0 else 255
    return out
