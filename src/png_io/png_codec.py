"""
PNG Manual Codec Module

Implementasi manual untuk membaca dan menulis PNG images tanpa library eksternal.
Menggunakan hanya Python standard library (struct, zlib).

Teori & Formula tersimpan di: docs/TEORI_DAN_RUMUS.md
"""

import struct
import zlib
from pathlib import Path


PNG_SIG = b"\x89PNG\r\n\x1a\n"


def paeth(a, b, c):
    """
    Paeth Predictor untuk PNG filtering.
    
    Digunakan dalam filter type 4 (Paeth) pada PNG decompression.
    Algoritma: memilih nearest value dari {a, b, c}.
    
    Args:
        a: int — piksel left
        b: int — piksel up
        c: int — piksel upper-left
    
    Returns:
        int — predicted value
    
    Reference: PNG Specification (RFC 2083)
    """
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)


def read_png_gray(path):
    """
    Manual PNG Decoder untuk Grayscale Images.
    
    Algoritma:
    1. Validasi PNG signature
    2. Parse IHDR chunk (image properties)
    3. Collect IDAT chunks (compressed data)
    4. Decompress dengan zlib
    5. Apply PNG filters (Sub, Up, Average, Paeth)
    6. Convert RGB/RGBA ke grayscale jika perlu
    
    Supported formats:
    - Grayscale 8-bit (color type 0)
    - RGB 8-bit (color type 2)
    - Grayscale + Alpha 8-bit (color type 4)
    - RGBA 8-bit (color type 6)
    
    Args:
        path: str or Path — lokasi file PNG
    
    Returns:
        List[List[int]] — 2D grayscale image (0-255)
    
    Raises:
        ValueError: Jika format tidak didukung atau file bukan PNG
    
    Complexity: O(H × W) untuk decompression & filtering
    
    Reference: PNG Specification (RFC 2083)
    """
    data = Path(path).read_bytes()
    
    # Validasi PNG signature
    if not data.startswith(PNG_SIG):
        raise ValueError(f"{path}: bukan berkas PNG")
    
    # State untuk parsing chunks
    pos = 8  # Skip PNG signature
    width, height, color, depth, interlace = None, None, None, None, None
    compressed = bytearray()
    
    # Parse chunks
    while pos < len(data):
        # Baca length (4 bytes, big-endian)
        length = struct.unpack_from(">I", data, pos)[0]
        # Baca chunk type (4 bytes)
        kind = data[pos + 4:pos + 8]
        # Baca chunk data
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        
        # IHDR = Image Header
        if kind == b"IHDR":
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if depth != 8 or interlace != 0 or compression != 0 or filtering != 0:
                raise ValueError(f"{path}: hanya PNG 8-bit non-interlaced yang didukung")
            if color not in (0, 2, 4, 6):
                raise ValueError(f"{path}: jenis warna PNG belum didukung")
        
        # IDAT = Image Data (compressed)
        elif kind == b"IDAT":
            compressed.extend(payload)
        
        # IEND = Image End (chunk terakhir)
        elif kind == b"IEND":
            break
    
    # Tentukan jumlah channel berdasarkan color type
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color]
    stride = width * channels
    
    # Decompress image data
    raw = zlib.decompress(bytes(compressed))
    
    # Reconstruct image dengan filter
    rows, offset = [], 0
    previous = bytearray(stride)  # Previous row (for Up filter)
    
    for _ in range(height):
        # Filter type (1 byte)
        filt = raw[offset]
        # Scan line data
        scan = bytearray(raw[offset + 1:offset + 1 + stride])
        offset += stride + 1
        
        # Apply PNG filter untuk setiap byte dalam scan line
        for i in range(stride):
            # Filter predictors
            left = scan[i - channels] if i >= channels else 0
            up = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            
            # Reconstruct byte: original = (filtered + predicted) mod 256
            if filt == 0:  # None
                pass
            elif filt == 1:  # Sub (left predictor)
                scan[i] = (scan[i] + left) & 255
            elif filt == 2:  # Up (up predictor)
                scan[i] = (scan[i] + up) & 255
            elif filt == 3:  # Average ((left+up)/2)
                scan[i] = (scan[i] + ((left + up) // 2)) & 255
            elif filt == 4:  # Paeth
                scan[i] = (scan[i] + paeth(left, up, upper_left)) & 255
            else:
                raise ValueError(f"{path}: filter PNG tidak dikenal: {filt}")
        
        # Convert pixels ke row format
        row = []
        for x in range(width):
            j = x * channels
            if color == 0:  # Grayscale
                y = scan[j]
            elif color in (2, 6):  # RGB atau RGBA → convert ke grayscale
                r, g, b = scan[j], scan[j + 1], scan[j + 2]
                # ITU-R BT.601 luma: Y = 0.299R + 0.587G + 0.114B
                y = (299 * r + 587 * g + 114 * b + 500) // 1000
            else:  # color == 4: Grayscale + Alpha → ambil grayscale
                y = scan[j]
            row.append(y)
        
        rows.append(row)
        previous = scan
    
    return rows


def png_chunk(kind, payload):
    """
    Helper untuk membuat PNG chunk.
    
    Format PNG chunk:
    - Length (4 bytes)
    - Type (4 bytes)
    - Data (variable)
    - CRC32 (4 bytes)
    
    Args:
        kind: bytes — chunk type (e.g., b"IHDR", b"IDAT")
        payload: bytes — chunk data
    
    Returns:
        bytes — complete chunk (with length & CRC)
    """
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xffffffff)


def write_png_gray(path, image):
    """
    Manual PNG Encoder untuk Grayscale Images.
    
    Algoritma:
    1. Buat IHDR chunk (image properties)
    2. Prepare raw pixel data dengan filter type 0 (no filter)
    3. Compress dengan zlib
    4. Buat IDAT chunk
    5. Buat IEND chunk
    6. Write to file
    
    Args:
        path: str or Path — output file location
        image: List[List[int]] — 2D grayscale image
    
    Raises:
        IOError: Jika tidak bisa menulis file
    
    Complexity: O(H × W) untuk compression
    
    Reference: PNG Specification (RFC 2083)
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    h, w = len(image), len(image[0])
    
    # Buat raw image data dengan filter type 0
    # Filter type byte (1) + scan line bytes
    raw = b"".join(
        b"\0" + bytes(max(0, min(255, int(v))) for v in row)
        for row in image
    )
    
    # IHDR: Image Header Chunk
    # Format: width(4) height(4) depth(1) color(1) compress(1) filter(1) interlace(1)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
    
    # Buat PNG file
    # PNG signature + IHDR + IDAT + IEND
    data = PNG_SIG + png_chunk(b"IHDR", ihdr) + png_chunk(b"IDAT", zlib.compress(raw, 6)) + png_chunk(b"IEND", b"")
    
    Path(path).write_bytes(data)
