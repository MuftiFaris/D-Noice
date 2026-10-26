#!/usr/bin/env python
"""Manual grayscale salt-and-pepper denoising using Python standard library only.

Supported input PNGs: 8-bit, non-interlaced grayscale/RGB/RGBA images.
Manual formulas are implemented in rumus_manual/ and re-exported here.
"""

import argparse
import csv
import struct
import zlib
from pathlib import Path

from rumus_manual import adaptive_median_filter, adaptive_pixel, add_salt_pepper, gaussian_filter, gaussian_kernel, gaussian_pixel, insertion_sort, median_filter, median_pixel, neighborhood, pad_image, psnr, ssim_block_average, validate_window_size


PNG_SIG = b"\x89PNG\r\n\x1a\n"


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def read_png_gray(path):
    """Decode supported PNG bytes manually; zlib only expands PNG compression."""
    data = Path(path).read_bytes()
    if not data.startswith(PNG_SIG):
        raise ValueError(f"{path}: bukan berkas PNG")
    pos, width, height, color, depth, interlace = 8, None, None, None, None, None
    compressed = bytearray()
    while pos < len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if depth != 8 or interlace != 0 or compression != 0 or filtering != 0:
                raise ValueError(f"{path}: hanya PNG 8-bit non-interlaced yang didukung")
            if color not in (0, 2, 4, 6):
                raise ValueError(f"{path}: jenis warna PNG belum didukung")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    stride = width * channels
    raw = zlib.decompress(compressed)
    rows, offset = [], 0
    previous = bytearray(stride)
    for _ in range(height):
        filt = raw[offset]
        scan = bytearray(raw[offset + 1:offset + 1 + stride])
        offset += stride + 1
        for i in range(stride):
            left = scan[i - channels] if i >= channels else 0
            up = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            if filt == 1:
                scan[i] = (scan[i] + left) & 255
            elif filt == 2:
                scan[i] = (scan[i] + up) & 255
            elif filt == 3:
                scan[i] = (scan[i] + ((left + up) // 2)) & 255
            elif filt == 4:
                scan[i] = (scan[i] + paeth(left, up, upper_left)) & 255
            elif filt != 0:
                raise ValueError(f"{path}: filter PNG tidak dikenal: {filt}")
        row = []
        for x in range(width):
            j = x * channels
            if color == 0:
                y = scan[j]
            elif color in (2, 6):
                r, g, b = scan[j], scan[j + 1], scan[j + 2]
                y = (299 * r + 587 * g + 114 * b + 500) // 1000
            else:  # grayscale + alpha
                y = scan[j]
            row.append(y)
        rows.append(row)
        previous = scan
    return rows


def png_chunk(kind, payload):
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)


def write_png_gray(path, image):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png_gray_bytes(image))


def png_gray_bytes(image):
    """Encode PNG ke memori untuk pratinjau; codec sama dengan penulisan berkas."""
    h, w = len(image), len(image[0])
    raw = b"".join(b"\0" + bytes(max(0, min(255, int(v))) for v in row) for row in image)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    data = PNG_SIG + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(raw, 6)) + png_chunk(b"IEND", b"")
    return data


def main():
    parser = argparse.ArgumentParser(description="Bandingkan filter noise secara manual (tanpa pustaka citra pihak ketiga).")
    parser.add_argument("--input", required=True, help="Folder dataset PNG, misalnya testsets/Set12")
    parser.add_argument("--output", default="hasil_denoising", help="Folder untuk hasil dan CSV")
    parser.add_argument("--levels", default="5,10,20,30", help="Persentase salt-and-pepper, dipisahkan koma")
    parser.add_argument("--seed", type=int, default=42, help="Seed agar posisi noise bisa diulang")
    args = parser.parse_args()

    source, output = Path(args.input), Path(args.output)
    files = sorted(source.rglob("*.png"))
    if not files:
        raise SystemExit(f"Tidak ada PNG di {source}")
    levels = [float(s) for s in args.levels.split(",")]
    rows = []
    for file_index, path in enumerate(files):
        clean = read_png_gray(path)
        for level in levels:
            # Different reproducible noise realization per image and noise level.
            seed = args.seed + file_index * 1000 + int(level * 10)
            noisy = add_salt_pepper(clean, level, seed)
            stem = f"{path.stem}_noise{level:g}"
            write_png_gray(output / "noisy" / f"{stem}.png", noisy)
            methods = {
                "Median_3x3": median_filter(noisy, 3),
                "AdaptiveMedian_3to7": adaptive_median_filter(noisy, 7),
                "Gaussian_3x3": gaussian_filter(noisy),
            }
            for name, restored in methods.items():
                write_png_gray(output / name / f"{stem}_{name}.png", restored)
                rows.append({
                    "image": path.name, "noise_percent": level, "method": name,
                    "psnr_db": f"{psnr(clean, restored):.6f}",
                    "ssim_block8": f"{ssim_block_average(clean, restored):.6f}",
                    "seed": seed,
                })
        print(f"Selesai: {path.name} ({len(clean[0])}x{len(clean)})")
    output.mkdir(parents=True, exist_ok=True)
    with (output / "hasil_metrik.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nHasil tersimpan di: {output.resolve()}")


if __name__ == "__main__":
    main()
