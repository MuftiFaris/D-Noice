#!/usr/bin/env python
"""Tahap 1: membaca citra dan mengenali nilai piksel grayscale."""

import argparse
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "gambar", nargs="?", type=Path,
        default=Path(__file__).parent / "data" / "original" / "01.png",
        help="Lokasi gambar yang ingin diperiksa.",
    )
    args = parser.parse_args()

    try:
        with Image.open(args.gambar) as sumber:
            mode_awal = sumber.mode
            # Pillow hanya menangani pembacaan dan konversi format citra.
            gambar = sumber.convert("L")
    except (OSError, UnidentifiedImageError) as error:
        parser.exit(1, f"Gambar tidak dapat dibaca: {error}\n")

    lebar, tinggi = gambar.size
    print(f"Gambar       : {args.gambar.name}")
    print(f"Ukuran       : {lebar} x {tinggi} piksel")
    print(f"Mode awal    : {mode_awal}")
    print(f"Mode dipakai : {gambar.mode} (grayscale)")

    # Matriks disusun manual: baris = y, kolom = x.
    matriks = []
    for y in range(tinggi):
        baris = []
        for x in range(lebar):
            baris.append(gambar.getpixel((x, y)))
        matriks.append(baris)

    print("\nNilai piksel pojok kiri atas (maksimal 5 x 5):")
    for baris in matriks[:5]:
        print(" ".join(f"{nilai:3d}" for nilai in baris[:5]))
    print("\n0 = hitam, 255 = putih, nilai di antaranya = abu-abu.")


if __name__ == "__main__":
    main()
