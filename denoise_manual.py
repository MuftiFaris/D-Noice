#!/usr/bin/env python3
"""Mengurangi noise salt-and-pepper pada citra grayscale secara manual.

Hanya menggunakan modul bawaan Python. PNG yang didukung: 8-bit, tanpa
interlace, dengan warna grayscale/RGB/RGBA. Algoritma filter, pembuatan
noise, PSNR, dan SSIM blok dihitung di dalam file ini.
"""

import argparse
import csv
import math
import random
import struct
import zlib
from pathlib import Path


PNG_SIG = b"\x89PNG\r\n\x1a\n"


def paeth(a, b, c):
    """Memilih nilai tetangga terdekat untuk membuka data PNG terkompresi."""
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def read_png_gray(path):
    """Membaca PNG lalu mengubahnya menjadi daftar angka grayscale.

    zlib hanya dipakai untuk membuka kompresi data PNG; zlib adalah modul
    bawaan Python, bukan library pengolah citra.
    """
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
            else:  # Untuk gambar grayscale dengan transparansi, ambil tingkat abu-abunya.
                y = scan[j]
            row.append(y)
        rows.append(row)
        previous = scan
    return rows


def png_chunk(kind, payload):
    """Membuat satu bagian data PNG dan checksum-nya saat menyimpan gambar."""
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)


def write_png_gray(path, image):
    """Menyimpan daftar angka grayscale sebagai file PNG."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    h, w = len(image), len(image[0])
    raw = b"".join(b"\0" + bytes(max(0, min(255, int(v))) for v in row) for row in image)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    data = PNG_SIG + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(raw, 6)) + png_chunk(b"IEND", b"")
    Path(path).write_bytes(data)


def pad_image(image, radius):
    """Memperpanjang tepi gambar dengan menyalin piksel tepi terdekat.

    Ini membuat piksel yang berada di pinggir tetap bisa dihitung oleh filter.
    """
    h, w = len(image), len(image[0])
    # Salin nilai piksel tepi supaya piksel pinggir diproses seperti piksel lain.
    return [[image[min(max(y, 0), h - 1)][min(max(x, 0), w - 1)]
             for x in range(-radius, w + radius)]
            for y in range(-radius, h + radius)]


def neighborhood(padded, y, x, radius, pad_radius=None):
    """Mengambil nilai piksel tetangga di dalam jendela, misalnya 3x3."""
    offset = radius if pad_radius is None else pad_radius
    yy, xx = y + offset, x + offset
    return [padded[yy + dy][xx + dx]
            for dy in range(-radius, radius + 1)
            for dx in range(-radius, radius + 1)]


def median_filter(image, size=3):
    """Filter median: urutkan piksel tetangga lalu pilih nilai tengahnya."""
    radius = size // 2
    src, h, w = pad_image(image, radius), len(image), len(image[0])
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            vals = neighborhood(src, y, x, radius)
            vals.sort()
            row.append(vals[len(vals) // 2])
        result.append(row)
    return result


def adaptive_median_filter(image, max_size=7):
    """Filter median adaptif: memperbesar jendela jika ukuran kecil belum cukup.

    Tahap A memeriksa apakah median bukan nilai paling gelap/terang di jendela.
    Tahap B mempertahankan piksel tengah jika tampak normal; jika ekstrem,
    piksel tersebut diganti dengan median.
    """
    if max_size < 3 or max_size % 2 == 0:
        raise ValueError("Ukuran maksimum adaptive median harus ganjil dan minimal 3")
    h, w = len(image), len(image[0])
    src = pad_image(image, max_size // 2)
    result = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            center = image[y][x]
            chosen = center
            for size in range(3, max_size + 1, 2):
                r = size // 2
                vals = neighborhood(src, y, x, r, max_size // 2)
                vals.sort()
                z_min, z_max = vals[0], vals[-1]
                z_med = vals[len(vals) // 2]
                # Tahap A: apakah median bukan nilai minimum atau maksimum?
                if z_min < z_med < z_max:
                    # Tahap B: pertahankan piksel tengah jika bukan nilai ekstrem.
                    # Jika ekstrem, ganti dengan median tetangganya.
                    chosen = center if z_min < center < z_max else z_med
                    break
                chosen = z_med
            result[y][x] = chosen
    return result


def gaussian_filter(image):
    """Filter Gaussian lowpass 3x3 sesuai contoh PDF (K=1 dan sigma=1).

    Bobot mentah dihitung dengan exp(-(x²+y²)/2). Kernel kemudian dinormalisasi
    dengan membagi setiap bobot dengan jumlah seluruh bobot (sekitar 4.8976),
    sehingga jumlah bobot akhirnya sama dengan 1.
    """
    kernel = (
        (0.3679, 0.6065, 0.3679),
        (0.6065, 1.0000, 0.6065),
        (0.3679, 0.6065, 0.3679),
    )
    jumlah_bobot = sum(sum(baris) for baris in kernel)
    kernel = tuple(
        tuple(bobot / jumlah_bobot for bobot in baris)
        for baris in kernel
    )
    src, h, w = pad_image(image, 1), len(image), len(image[0])
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            total = sum(
                kernel[dy + 1][dx + 1] * src[y + 1 + dy][x + 1 + dx]
                for dy in (-1, 0, 1)
                for dx in (-1, 0, 1)
            )
            # Membulatkan hasil ke bilangan bulat terdekat untuk nilai piksel.
            row.append(max(0, min(255, int(total + 0.5))))
        result.append(row)
    return result


def add_salt_pepper(image, percent, seed):
    """Menambahkan noise salt-and-pepper pada persentase posisi yang diminta.

    Separuh posisi dibuat hitam (0), separuh lainnya putih (255). Seed
    membuat posisi noise dapat diulang pada eksperimen berikutnya.
    """
    h, w = len(image), len(image[0])
    out = [row[:] for row in image]
    count = round(h * w * percent / 100)
    positions = random.Random(seed).sample(range(h * w), count)
    for i, p in enumerate(positions):
        y, x = divmod(p, w)
        out[y][x] = 0 if i % 2 == 0 else 255
    return out


def psnr(original, restored):
    """Menghitung PSNR dari MSE; PSNR lebih tinggi biasanya berarti hasil lebih dekat.

    MSE = jumlah kuadrat selisih piksel / jumlah piksel.
    PSNR = 10 * log10(255^2 / MSE), dalam satuan desibel (dB).
    """
    h, w = len(original), len(original[0])
    mse = sum((original[y][x] - restored[y][x]) ** 2
              for y in range(h) for x in range(w)) / (h * w)
    return float("inf") if mse == 0 else 10 * math.log10((255 * 255) / mse)


def ssim_block_average(original, restored, block=8):
    """Menghitung SSIM pada blok-blok 8x8 yang tidak saling tumpang tindih.

    Untuk setiap blok, hitung rata-rata kecerahan, variasi (variansi), dan
    kovariansi antara gambar acuan dan hasil. Rumus SSIM blok:
    ((2*ma*mb + C1) * (2*kov + C2)) /
    ((ma^2 + mb^2 + C1) * (va + vb + C2)).
    Nilai akhir adalah rata-rata semua nilai SSIM blok. Ini versi blok sederhana;
    beberapa perangkat lunak memakai jendela dan bobot Gaussian yang berbeda.
    """
    h, w = len(original), len(original[0])
    k1, k2, L = 0.01, 0.03, 255
    c1, c2 = (k1 * L) ** 2, (k2 * L) ** 2
    values = []
    for y0 in range(0, h, block):
        for x0 in range(0, w, block):
            a, b = [], []
            for y in range(y0, min(y0 + block, h)):
                for x in range(x0, min(x0 + block, w)):
                    a.append(float(original[y][x]))
                    b.append(float(restored[y][x]))
            n = len(a)
            ma, mb = sum(a) / n, sum(b) / n
            va = sum((v - ma) ** 2 for v in a) / (n - 1) if n > 1 else 0.0
            vb = sum((v - mb) ** 2 for v in b) / (n - 1) if n > 1 else 0.0
            cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (n - 1) if n > 1 else 0.0
            numerator = (2 * ma * mb + c1) * (2 * cov + c2)
            denominator = (ma * ma + mb * mb + c1) * (va + vb + c2)
            values.append(numerator / denominator)
    return sum(values) / len(values)


def main():
    parser = argparse.ArgumentParser(description="Bandingkan filter noise dengan perhitungan manual.")
    parser.add_argument("--input", required=True, help="Folder dataset PNG, misalnya data/Set12")
    parser.add_argument("--output", default="hasil_denoising", help="Folder penyimpanan gambar hasil dan file CSV")
    parser.add_argument("--levels", default="5,10,20,30", help="Persentase noise, pisahkan dengan koma")
    parser.add_argument("--seed", type=int, default=42, help="Angka agar pola noise bisa diulang")
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
            # Seed berbeda untuk gambar/tingkat noise, tetapi hasilnya tetap bisa diulang.
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
