# Teori dan Rumus — Image Denoising

Dokumentasi lengkap teori, rumus matematika, dan implementasi untuk setiap algoritma dan metrik yang digunakan dalam program denoising.

---

## 📋 Daftar Isi

1. [Noise: Salt-and-Pepper](#1-noise-salt-and-pepper)
2. [Median Filter](#2-median-filter)
3. [Adaptive Median Filter](#3-adaptive-median-filter)
4. [Gaussian Filter](#4-gaussian-filter)
5. [PSNR (Peak Signal-to-Noise Ratio)](#5-psnr)
6. [SSIM (Structural Similarity Index)](#6-ssim)

---

## 1. Noise: Salt-and-Pepper

### 📖 Teori

**Salt-and-Pepper Noise** adalah jenis noise impulsif yang mengubah sejumlah piksel random menjadi nilai ekstrem:
- **Salt**: Piksel berubah menjadi putih (255 untuk 8-bit)
- **Pepper**: Piksel berubah menjadi hitam (0 untuk 8-bit)

Noise ini umum terjadi pada:
- Transmisi data yang error
- Sensor imaging dengan dead pixels
- Kompresi image yang buruk

### 🧮 Rumus Matematika

Jika persentase noise adalah P%, maka jumlah piksel yang diubah:

```
Count = Round(H × W × P / 100)
```

Dimana:
- `H` = tinggi image (pixels)
- `W` = lebar image (pixels)
- `P` = persentase noise (0-100%)

Pemilihan piksel dilakukan secara **random tetapi reproducible** menggunakan seed:

```
positions = Random(seed).sample(range(H × W), Count)
```

Setengah dipilih menjadi **0 (black/pepper)**, setengah menjadi **255 (white/salt)**:

```
for i, pos in enumerate(positions):
    y, x = divmod(pos, W)
    image[y][x] = 0 if (i % 2 == 0) else 255
```

### 💻 Implementasi Kode

```python
def add_salt_pepper(image, percent, seed):
    """
    Tambah salt-and-pepper noise ke image.
    
    Args:
        image: List[List[int]] — image grayscale 8-bit
        percent: float — persentase noise (0-100%)
        seed: int — random seed untuk reproducibility
    
    Returns:
        List[List[int]] — image dengan noise
    """
    h, w = len(image), len(image[0])
    out = [row[:] for row in image]  # Copy image
    
    # Hitung jumlah piksel yang akan di-noise
    count = round(h * w * percent / 100)
    
    # Pilih posisi random (reproducible dengan seed)
    positions = random.Random(seed).sample(range(h * w), count)
    
    # Ubah piksel: genap → 0 (pepper), ganjil → 255 (salt)
    for i, p in enumerate(positions):
        y, x = divmod(p, w)
        out[y][x] = 0 if i % 2 == 0 else 255
    
    return out
```

### ✅ Contoh

Image 256×256 dengan noise 10%, seed 42:

```
H = 256, W = 256, P = 10
Count = Round(256 × 256 × 10 / 100) = Round(6553.6) = 6554 pixels
Hasil: ~3277 pixel hitam (pepper), ~3277 pixel putih (salt)
```

---

## 2. Median Filter

### 📖 Teori

**Median Filter** adalah filter berbasis ranking yang mengganti setiap piksel dengan nilai median dari neighborhood-nya.

**Keuntungan:**
- Sangat efektif untuk salt-and-pepper noise
- Mempertahankan edge (boundary) dengan baik
- Tidak memperkenalkan nilai baru

**Kerugian:**
- Slow untuk image besar
- Dapat menghapus detail kecil

**Ukuran Kernel:** Biasanya 3×3 atau 5×5 (harus ganjil)

### 🧮 Rumus Matematika

Untuk setiap piksel `(x, y)`, ambil nilai-nilai di dalam kernel neighborhood ukuran `K×K`:

```
N = {image[y+dy][x+dx] | -K/2 ≤ dx,dy ≤ K/2}
```

Urutkan nilai-nilai dalam `N`:

```
N_sorted = SORT(N)  (ascending order)
```

Median adalah nilai tengah:

```
output[y][x] = N_sorted[len(N) / 2]  (untuk ukuran ganjil: floor division)
```

Contoh untuk kernel 3×3:

```
Piksel original: 100, 102, 101
                 99,  255, 103
                 101, 98,  102

Nilai dalam kernel (9 piksel): [100, 102, 101, 99, 255, 103, 101, 98, 102]
Sorted: [98, 99, 100, 101, 101, 102, 102, 103, 255]
Median (index 4): 101
```

Piksel noise (255) tergantikan dengan 101 ✓

### 💻 Implementasi Kode

```python
def insertion_sort(values):
    """
    Sort manual menggunakan insertion sort.
    Tidak mengubah list original.
    
    Args:
        values: List[int] — nilai yang akan disort
    
    Returns:
        List[int] — copy yang sudah sorted
    """
    ordered = list(values)  # Copy
    for i in range(1, len(ordered)):
        current = ordered[i]
        j = i - 1
        # Geser nilai yang lebih besar ke kanan
        while j >= 0 and ordered[j] > current:
            ordered[j + 1] = ordered[j]
            j -= 1
        ordered[j + 1] = current
    return ordered


def pad_image(image, radius):
    """
    Tambah padding pada image dengan replicate edge pixels.
    
    Contoh kernel 3×3 (radius=1):
    Original:        Padded:
    [1 2]            [1 1 2 2]
    [3 4]            [1 1 2 2]
                     [3 3 4 4]
                     [3 3 4 4]
    
    Args:
        image: List[List[int]]
        radius: int — ukuran padding
    
    Returns:
        List[List[int]] — padded image
    """
    h, w = len(image), len(image[0])
    return [[image[min(max(y, 0), h - 1)][min(max(x, 0), w - 1)]
             for x in range(-radius, w + radius)]
            for y in range(-radius, h + radius)]


def neighborhood(padded, y, x, radius, pad_radius=None):
    """
    Ambil semua nilai piksel dalam kernel neighborhood.
    
    Args:
        padded: List[List[int]] — padded image
        y, x: int — koordinat center pixel
        radius: int — kernel radius (untuk 3×3, radius=1)
        pad_radius: int — padding offset (default=radius)
    
    Returns:
        List[int] — nilai piksel dalam kernel
    """
    offset = radius if pad_radius is None else pad_radius
    yy, xx = y + offset, x + offset
    return [padded[yy + dy][xx + dx]
            for dy in range(-radius, radius + 1)
            for dx in range(-radius, radius + 1)]


def median_filter(image, size=3):
    """
    Implementasi Median Filter.
    
    Algoritma:
    1. Pad image dengan replicate edge
    2. Untuk setiap piksel:
       a. Ekstrak neighborhood kernel
       b. Sort nilai secara manual
       c. Ambil median (nilai tengah)
    3. Return image filtered
    
    Args:
        image: List[List[int]] — grayscale image
        size: int — kernel size (harus ganjil, minimum 3)
    
    Returns:
        List[List[int]] — filtered image
    
    Complexity: O(H × W × K² × log(K²)) ≈ O(n log n) per pixel
    """
    validate_window_size(size)
    radius = size // 2
    src, h, w = pad_image(image, radius), len(image), len(image[0])
    
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            # Ekstrak nilai dalam kernel
            vals = insertion_sort(neighborhood(src, y, x, radius))
            # Median adalah nilai tengah
            # Untuk 9 nilai (3×3): index 4 adalah median
            row.append(vals[len(vals) // 2])
        result.append(row)
    
    return result
```

### ✅ Contoh

```
3×3 kernel, input dengan noise:
Input:   Output:
100 200  100
255  99  150  ← noise (255) di-replace dengan median (150)
100 200  100
```

---

## 3. Adaptive Median Filter

### 📖 Teori

**Adaptive Median Filter** adalah evolusi dari Median Filter yang:
1. Dimulai dari kernel kecil (3×3)
2. Secara otomatis **memperbesar jendela** jika noise terdeteksi
3. Bisa mencapai kernel 7×7 atau lebih besar
4. Mempertahankan detail sharp lebih baik dari Median biasa

**Algoritma:**

**Tahap A (Level A):** Cek apakah median adalah nilai "normal" (bukan extremum):
```
IF z_min < z_med < z_max THEN
    Go to Tahap B
ELSE
    Expand kernel, coba ukuran berikutnya
```

**Tahap B (Level B):** Cek apakah center piksel adalah noise atau detail asli:
```
IF z_min < z_center < z_max THEN
    Keep center pixel (it's real detail)
ELSE
    Replace with median (it's noise)
```

**Adaptivitas:** Jika Tahap A gagal di ukuran 3×3, coba 5×5, lalu 7×7.

### 🧮 Rumus Matematika

Untuk kernel ukuran `S`:

```
z_min = MIN(neighborhood)
z_max = MAX(neighborhood)
z_med = MEDIAN(neighborhood)
```

**Tahap A:**
```
A1 = z_med - z_min
A2 = z_med - z_max
IF A1 > 0 AND A2 < 0 THEN
    median_is_normal = TRUE
```

**Tahap B:**
```
B1 = z_center - z_min
B2 = z_center - z_max
IF B1 > 0 AND B2 < 0 THEN
    output = z_center  (preserve detail)
ELSE
    output = z_med     (replace noise)
```

### 💻 Implementasi Kode

```python
def adaptive_median_filter(image, max_size=7):
    """
    Implementasi Adaptive Median Filter.
    
    Algoritma:
    1. Untuk setiap piksel, mulai dari kernel 3×3
    2. Tahap A: Cek apakah median adalah nilai normal
       - Jika YES: lanjut ke Tahap B
       - Jika NO: perbesar kernel, coba lagi
    3. Tahap B: Cek apakah center adalah noise atau detail
       - Jika real detail: pertahankan center
       - Jika noise: ganti dengan median
    
    Args:
        image: List[List[int]]
        max_size: int — maksimal kernel size (default 7×7)
    
    Returns:
        List[List[int]] — filtered image
    """
    validate_window_size(max_size)
    if max_size < 3 or max_size % 2 == 0:
        raise ValueError("Max size harus ganjil dan >= 3")
    
    h, w = len(image), len(image[0])
    src = pad_image(image, max_size // 2)
    result = [[0] * w for _ in range(h)]
    
    for y in range(h):
        for x in range(w):
            center = image[y][x]
            chosen = center  # Default ke center
            
            # Coba kernel size mulai dari 3 hingga max_size
            for size in range(3, max_size + 1, 2):
                r = size // 2
                # Ekstrak dan sort neighborhood
                vals = insertion_sort(neighborhood(src, y, x, r, max_size // 2))
                
                z_min = vals[0]
                z_max = vals[-1]
                z_med = vals[len(vals) // 2]
                
                # === TAHAP A: Cek apakah median normal? ===
                # Median "normal" jika diantara min dan max
                # (bukan extremum seperti noise)
                a1 = z_med - z_min
                a2 = z_med - z_max
                
                if a1 > 0 and a2 < 0:
                    # TAHAP B: Cek apakah center adalah real detail?
                    b1 = center - z_min
                    b2 = center - z_max
                    
                    if b1 > 0 and b2 < 0:
                        # Center adalah real detail, pertahankan
                        chosen = center
                    else:
                        # Center adalah noise, ganti dengan median
                        chosen = z_med
                    # Tahap B selesai, keluar loop
                    break
                
                # Jika Tahap A gagal, fallback ke median
                # (akan diupdate jika kernel berikutnya lebih baik)
                chosen = z_med
            
            result[y][x] = chosen
    
    return result
```

### ✅ Contoh

Kernel 3×3 dengan piksel noise di tengah:

```
Input:           Tahap A (3×3):           Tahap B:
100 100 100      z_min=100, z_max=255    center=255
100 255 100      z_med=100                255 bukan antara 100-255? NO
100 100 100      A1=0 (not > 0), fail!    → Perbesar ke 5×5

Tahap A (5×5):
z_min=100, z_max=255, z_med=100
A1=0, fail lagi! → Perbesar ke 7×7

...dan seterusnya
```

---

## 4. Gaussian Filter

### 📖 Teori

**Gaussian Filter** adalah low-pass filter yang menggunakan distribusi Gaussian (normal distribution) sebagai kernel weights.

**Kernel Gaussian:**
```
G(u,v) = exp(-(u² + v²) / (2σ²))
```

Dimana:
- `u, v` = koordinat relative dari center
- `σ` (sigma) = standard deviation (mengontrol "blur" amount)

**Keuntungan:**
- Smooth hasil filtering
- Mempertahankan edge lebih halus
- Basis matematika kuat

**Kerugian:**
- Salt-and-pepper noise besar masih berpengaruh ke neighbor pixels
- Blur dapat menghapus detail

### 🧮 Rumus Matematika

**Kernel 3×3 Default (σ = sqrt(1/(2×ln(2))) ≈ 0.849):**

```
Kernel weights (normalized):
[1  2  1]     1
[2  4  2]  ÷ --
[1  2  1]    16

Contoh:
[0.0625  0.125  0.0625]
[0.125   0.25   0.125 ]
[0.0625  0.125  0.0625]
```

**Konvolusi (dengan half-up rounding):**

```
output[y][x] = ROUND(Σ(kernel[dy][dx] × image[y+dy][x+dx]))
               dy,dx
```

**Contoh perhitungan 3×3:**

```
Image patch:     Kernel:        Hasil:
[100 102 101]    [1  2  1]      1×100 + 2×102 + 1×101
[99  255 103]  ÷ [2  4  2]  16  + 2×99 + 4×255 + 2×103
[101 98  102]    [1  2  1]      + 1×101 + 2×98 + 1×102

= (100+204+101+198+1020+206+101+196+102) / 16
= 2228 / 16
= 139.25
≈ ROUND(139.25) = 139
```

### 💻 Implementasi Kode

```python
def gaussian_kernel(size=3, sigma=None):
    """
    Generate Gaussian kernel dengan normalization.
    
    Rumus: G(u,v) = exp(-(u² + v²) / (2σ²))
    
    Args:
        size: int — kernel size (harus ganjil)
        sigma: float — standard deviation
                      Default: sqrt(1/(2×ln(2))) untuk legacy compatibility
    
    Returns:
        List[List[float]] — normalized kernel (sum = 1.0)
    
    Contoh output (size=3, default sigma):
    [[0.0625, 0.125, 0.0625],
     [0.125,  0.25,  0.125 ],
     [0.0625, 0.125, 0.0625]]
    """
    validate_window_size(size)
    
    if sigma is None:
        # Default sigma untuk kernel 3×3 → bobot [1,2,1]
        sigma = math.sqrt(1.0 / (2.0 * math.log(2.0)))
    
    if isinstance(sigma, bool) or not isinstance(sigma, (int, float)) or not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("Sigma harus angka positif dan berhingga")
    
    radius = size // 2
    kernel = []
    total_weight = 0.0
    
    # Generate kernel weights dari formula Gaussian
    for v in range(-radius, radius + 1):
        row = []
        for u in range(-radius, radius + 1):
            # Hitung jarak dari center, scaled by sigma
            scaled_u = u / sigma
            scaled_v = v / sigma
            distance_squared = scaled_u * scaled_u + scaled_v * scaled_v
            
            # Gaussian formula: exp(-0.5 × distance_squared)
            weight = math.exp(-0.5 * distance_squared)
            row.append(weight)
            total_weight += weight
        kernel.append(row)
    
    # Normalize kernel sehingga sum = 1.0
    for y in range(size):
        for x in range(size):
            kernel[y][x] = kernel[y][x] / total_weight
    
    return kernel


def gaussian_filter(image, size=3, sigma=None):
    """
    Implementasi Gaussian Filter (convolution).
    
    Algoritma:
    1. Generate kernel Gaussian
    2. Pad image dengan replicate edge
    3. Untuk setiap piksel:
       a. Ekstrak patch (kernel neighborhood)
       b. Konvolusi: Σ(kernel × patch)
       c. Round ke integer 8-bit
    
    Args:
        image: List[List[int]] — grayscale image
        size: int — kernel size (default 3×3)
        sigma: float — Gaussian standard deviation
    
    Returns:
        List[List[int]] — filtered image
    
    Complexity: O(H × W × size²)
    """
    kernel = gaussian_kernel(size, sigma)
    radius = size // 2
    src, h, w = pad_image(image, radius), len(image), len(image[0])
    
    result = []
    for y in range(h):
        row = []
        for x in range(w):
            total = 0.0
            
            # Konvolusi: Σ(kernel × patch)
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    # Kernel dibalik untuk konvolusi (flipped)
                    # (Gaussian simetris, jadi hasil sama dengan cross-correlation)
                    weight = kernel[radius - dy][radius - dx]
                    pixel = src[y + radius + dy][x + radius + dx]
                    total += weight * pixel
            
            # Half-up rounding ke 8-bit integer
            # Tambah 0.5 untuk rounding, + 1e-10 untuk floating-point tolerance
            value = int(total + 0.5 + 1e-10)
            # Clamp ke range [0, 255]
            row.append(max(0, min(255, value)))
        
        result.append(row)
    
    return result
```

### ✅ Contoh

```
Input dengan noise:      Output (Gaussian 3×3):
[100 200 100]            [100 150 100]
[255  99 255]    ──→     [160 115 160]
[100 200 100]            [100 150 100]

Noise (255) menjadi lebih halus dan terdistribusi ke tetangga
```

---

## 5. PSNR (Peak Signal-to-Noise Ratio)

### 📖 Teori

**PSNR** mengukur kualitas image dengan membandingkan **nilai piksel** original dan restored.

**Satuan:** Desibel (dB) — semakin tinggi semakin baik

**Interpretasi:**
- PSNR > 40 dB: Sangat baik (sulit dibedakan dengan mata)
- PSNR 30-40 dB: Baik (terlihat mirip)
- PSNR 20-30 dB: Cukup (ada distorsi)
- PSNR < 20 dB: Buruk (banyak distorsi)

### 🧮 Rumus Matematika

**Mean Squared Error (MSE):**
```
MSE = (1 / (H × W)) × Σ(original[y][x] - restored[y][x])²
      y,x
```

**PSNR:**
```
PSNR = 10 × log₁₀(MAX² / MSE)
```

Dimana:
- `MAX` = nilai maksimal piksel (255 untuk 8-bit)
- Jika `MSE = 0` (image identical): `PSNR = ∞`

**Contoh numerik:**

```
MSE = 100
PSNR = 10 × log₁₀(255² / 100)
     = 10 × log₁₀(65025 / 100)
     = 10 × log₁₀(650.25)
     = 10 × 2.813
     = 28.13 dB
```

### 💻 Implementasi Kode

```python
def psnr(original, restored):
    """
    Hitung Peak Signal-to-Noise Ratio.
    
    Algoritma:
    1. Hitung MSE (Mean Squared Error)
    2. Konversi ke PSNR menggunakan formula: 10 × log₁₀(MAX² / MSE)
    
    Args:
        original: List[List[int]] — gambar reference (bersih)
        restored: List[List[int]] — gambar filtered
    
    Returns:
        float — PSNR dalam desibel (dB)
                Special case: float('inf') jika MSE = 0
    """
    h, w = len(original), len(original[0])
    
    # Hitung MSE
    # MSE = Σ(piksel_asli - piksel_hasil)² / jumlah_piksel
    mse = sum((original[y][x] - restored[y][x]) ** 2
              for y in range(h) for x in range(w)) / (h * w)
    
    # Jika MSE = 0 (image identical), PSNR = ∞
    if mse == 0:
        return float("inf")
    
    # PSNR = 10 × log₁₀(255² / MSE)
    # 255² = 65025 (untuk 8-bit grayscale)
    return 10 * math.log10((255 * 255) / mse)
```

### ✅ Contoh

```
Original image: [100, 102, 101, ...]
Restored:       [101, 100, 101, ...]

Σ(selisih²) = 1 + 4 + 0 + ... = 500
Jumlah pixel = 65536 (256×256)
MSE = 500 / 65536 ≈ 0.00763

PSNR = 10 × log₁₀(65025 / 0.00763)
     ≈ 10 × 3.917
     ≈ 39.17 dB ✓ (Sangat baik)
```

---

## 6. SSIM (Structural Similarity Index)

### 📖 Teori

**SSIM** mengukur **kemiripan struktur** antara dua image, bukan hanya nilai piksel.

Mempertimbangkan tiga komponen:
1. **Luminance (L)** — kecerahan rata-rata
2. **Contrast (C)** — variasi tingkat terang-gelap
3. **Structure (S)** — pola/korelasi antar piksel

**Interpretasi:**
- SSIM = 1.0: Image identik
- SSIM = 0.9-1.0: Sangat mirip
- SSIM = 0.8-0.9: Mirip
- SSIM < 0.8: Cukup berbeda

**Keuntungan vs PSNR:**
- Lebih sesuai dengan persepsi mata manusia
- Lebih sensitif terhadap distorsi struktur
- Penghargaan untuk blur lebih dari distorsi acak

### 🧮 Rumus Matematika

**Untuk blok 8×8 (non-overlapping):**

**Mean (rata-rata kecerahan):**
```
μₐ = (1/N) × Σ aᵢ    (N = 64 pixels)
μᵦ = (1/N) × Σ bᵢ
```

**Variance (variasi/kontras):**
```
σₐ² = (1/(N-1)) × Σ(aᵢ - μₐ)²
σᵦ² = (1/(N-1)) × Σ(bᵢ - μᵦ)²
```

**Covariance (korelasi pola):**
```
σₐᵦ = (1/(N-1)) × Σ(aᵢ - μₐ)(bᵢ - μᵦ)
```

**Konstanta stabilisasi (prevent division by zero):**
```
C₁ = (k₁ × L)²  = (0.01 × 255)² ≈ 6.5
C₂ = (k₂ × L)²  = (0.03 × 255)² ≈ 58.5
```

Dimana `L = 255` untuk 8-bit.

**SSIM untuk satu blok:**
```
SSIM = (2μₐμᵦ + C₁)(2σₐᵦ + C₂) / (μₐ² + μᵦ² + C₁)(σₐ² + σᵦ² + C₂)
       ─────────────────────────   ──────────────────────────
       Similarity of luminance     Similarity of contrast & structure
```

**SSIM Final (Average semua blok):**
```
SSIM_final = (1/M) × Σ SSIM_block(i)
             i=1..M
```

### 💻 Implementasi Kode

```python
def ssim_block_average(original, restored, block=8):
    """
    Implementasi SSIM (Structural Similarity Index).
    
    Algoritma:
    1. Bagi image menjadi blok 8×8 non-overlapping
    2. Untuk setiap blok:
       a. Hitung mean, variance, covariance
       b. Hitung SSIM menggunakan formula
    3. Average SSIM dari semua blok
    
    Args:
        original: List[List[int]] — reference image
        restored: List[List[int]] — filtered image
        block: int — ukuran blok (default 8×8)
    
    Returns:
        float — SSIM average (0.0 hingga 1.0)
    
    Catatan: 
    - Menggunakan block=8×8 non-overlapping (standar SSIM)
    - Formula sesuai Wang et al. 2004
    """
    h, w = len(original), len(original[0])
    
    # Konstanta stabilisasi (sesuai Wang et al. 2004)
    k1, k2 = 0.01, 0.03
    L = 255  # dynamic range untuk 8-bit
    c1 = (k1 * L) ** 2
    c2 = (k2 * L) ** 2
    
    values = []
    
    # Loop blok non-overlapping: top-left corner di (y0, x0)
    for y0 in range(0, h, block):
        for x0 in range(0, w, block):
            # Ekstrak blok (handle edge: blok terakhir bisa < 8×8)
            a, b = [], []
            for y in range(y0, min(y0 + block, h)):
                for x in range(x0, min(x0 + block, w)):
                    a.append(float(original[y][x]))
                    b.append(float(restored[y][x]))
            
            n = len(a)  # Jumlah pixel dalam blok
            
            # === STATISTIK BLOK ===
            # Mean luminance
            ma = sum(a) / n
            mb = sum(b) / n
            
            # Variance (kontras)
            va = sum((v - ma) ** 2 for v in a) / (n - 1) if n > 1 else 0.0
            vb = sum((v - mb) ** 2 for v in b) / (n - 1) if n > 1 else 0.0
            
            # Covariance (structural correlation)
            cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n)) / (n - 1) if n > 1 else 0.0
            
            # === SSIM FORMULA ===
            numerator = (2 * ma * mb + c1) * (2 * cov + c2)
            denominator = (ma * ma + mb * mb + c1) * (va + vb + c2)
            
            ssim_block = numerator / denominator
            values.append(ssim_block)
    
    # Average SSIM dari semua blok
    return sum(values) / len(values) if values else 1.0
```

### ✅ Contoh

```
Blok 8×8 dari original:  [100, 102, 101, ...]
Blok 8×8 dari restored:  [101, 100, 101, ...]

μₐ ≈ 100.5
μᵦ ≈ 100.3
σₐ² ≈ 1.5
σᵦ² ≈ 1.2
σₐᵦ ≈ 1.4

SSIM_block ≈ (2×100.5×100.3 + C₁)(2×1.4 + C₂) / (...)
           ≈ 0.95 ✓ (Sangat mirip)

Jika 16 blok total, masing-masing ≈ 0.95
SSIM_final = (0.95 + 0.95 + ... ) / 16 ≈ 0.95
```

---

## 📚 Referensi

1. **Noise Modeling:**
   - Gonzalez & Woods. "Digital Image Processing" (3rd ed.)

2. **Median Filter:**
   - Jayaraj et al. 2010. "Switching Median Filter for Salt-and-Pepper Noise"
   - Huang et al. 1979. "Fast Two-Dimensional Median Filtering Algorithm"

3. **Adaptive Median:**
   - Gao et al. 2018. "Adaptive Median Local Distribution Filter"
   - Lee & Lee. "Adaptive Median Filters"

4. **Gaussian Filter:**
   - Lindeberg. "Gaussian Scale-Space Theory"

5. **PSNR & SSIM:**
   - Wang et al. 2004. "Image Quality Assessment: From Error Visibility to Structural Similarity" (IEEE TIP)
   - Hore & Ziou. 2010. "Image Quality Metrics: PSNR vs SSIM"

---

**Dokumen ini:** Teori lengkap dengan rumus matematika dan implementasi kode untuk presentasi & pembelajaran
