# Struktur Folder Project

Dokumentasi struktur folder dan organisasi file untuk mudah dipahami.

```
denoising-web/
│
├─ README.md                          # Pengenalan project
├─ AUDIT_REPORT.md                    # Laporan audit & bug findings
│
├─ docs/                              # Dokumentasi & teori
│  ├─ TEORI_DAN_RUMUS.md             # Semua rumus matematika + implementasi
│  ├─ STRUKTUR_FOLDER.md             # File ini (penjelasan struktur)
│  └─ API_DOCS.md                    # Dokumentasi endpoint API (di folder ini)
│
├─ src/                               # Source code production
│  ├─ filters/
│  │  ├─ __init__.py
│  │  └─ image_filters.py            # Median, Adaptive Median, Gaussian
│  ├─ metrics/
│  │  ├─ __init__.py
│  │  └─ quality_metrics.py          # PSNR, SSIM
│  ├─ noise/
│  │  ├─ __init__.py
│  │  └─ noise_generators.py         # Salt-and-Pepper
│  ├─ png_io/
│  │  ├─ __init__.py
│  │  └─ png_codec.py                # PNG read/write manual
│  │
│  ├─ server.py                       # HTTP server & API handlers
│  └─ app.js                          # Frontend JavaScript
│
├─ tests/                             # Unit tests
│  ├─ __init__.py
│  ├─ test_filters.py                # Test untuk semua filter
│  ├─ test_metrics.py                # Test PSNR & SSIM
│  ├─ test_noise.py                  # Test noise generation
│  └─ test_integration.py            # End-to-end tests
│
├─ data/                              # Dataset input
│  └─ Set12/
│     ├─ 01.png
│     ├─ 02.png
│     └─ ... (12 gambar test)
│
├─ static/                            # HTML & CSS (frontend assets)
│  ├─ index.html                     # Main page
│  ├─ app.js                         # (symlink ke src/app.js)
│  ├─ style.css
│  ├─ research.css
│  └─ theme.css
│
├─ hasil/                             # Output folder (results)
│  └─ (generated files dari experiments)
│
├─ papers_denoising/                  # Research papers
│  ├─ 01_Gao_2018_...pdf
│  ├─ 02_Ramadan_2018_...pdf
│  └─ DAFTAR_PAPER.md
│
└─ requirements.txt                   # Python dependencies (empty - std lib only)
```

---

## 📁 Penjelasan Per Folder

### `docs/` — Dokumentasi

**TEORI_DAN_RUMUS.md** (FILE PENTING)
- Semua rumus matematika dalam satu file
- Setiap rumus ada:
  - 📖 **Teori** — Penjelasan konsep
  - 🧮 **Rumus Matematika** — Formula lengkap dengan notasi
  - 💻 **Implementasi Kode** — Fungsi Python dengan comment detail
  - ✅ **Contoh Numerik** — Walkthrough perhitungan
- Gunakan untuk presentasi & pembelajaran

**STRUKTUR_FOLDER.md** (File ini)
- Menjelaskan organisasi folder & file

**API_DOCS.md** (Akan dibuat)
- Dokumentasi endpoint `/api/run`, `/api/images`
- Request/response format
- Error handling

### `src/` — Source Code

Diorganisir per **module** (bukan per-file monolith):

#### `src/filters/`
```python
# image_filters.py
def insertion_sort(values):
    """Manual sort implementation."""
    # ... code ...

def median_filter(image, size=3):
    """Median filter dengan detail comments."""
    # ... code ...

def adaptive_median_filter(image, max_size=7):
    """Adaptive median dengan Tahap A & B."""
    # ... code ...

def gaussian_kernel(size=3, sigma=None):
    """Generate Gaussian kernel."""
    # ... code ...

def gaussian_filter(image, size=3, sigma=None):
    """Gaussian convolution."""
    # ... code ...
```

#### `src/metrics/`
```python
# quality_metrics.py
def psnr(original, restored):
    """PSNR calculation (Peak Signal-to-Noise Ratio)."""
    # ... code ...

def ssim_block_average(original, restored, block=8):
    """SSIM (Structural Similarity Index)."""
    # ... code ...
```

#### `src/noise/`
```python
# noise_generators.py
def add_salt_pepper(image, percent, seed):
    """Generate salt-and-pepper noise."""
    # ... code ...
```

#### `src/png_io/`
```python
# png_codec.py
def read_png_gray(path):
    """Manual PNG decoder (zlib only)."""
    # ... code ...

def write_png_gray(path, image):
    """Manual PNG encoder."""
    # ... code ...
```

#### `src/server.py`
- HTTP server endpoints
- `/api/images` — list available images
- `/api/run` — run filtering experiment

---

### `tests/` — Unit Tests

```
test_filters.py
├─ test_median_filter()
├─ test_adaptive_median()
├─ test_gaussian_filter()
└─ ...

test_metrics.py
├─ test_psnr()
├─ test_ssim()
└─ ...

test_noise.py
├─ test_salt_pepper_generation()
├─ test_reproducibility_with_seed()
└─ ...

test_integration.py
├─ test_full_pipeline()
├─ test_api_endpoint()
└─ ...
```

**Run tests:**
```bash
python -m pytest tests/
# atau
python -B -m unittest discover -s tests -p "test_*.py" -v
```

---

### `data/Set12/` — Input Dataset

12 grayscale reference images dari FFDNet project:
- `01.png` — camera (256×256)
- `02.png` — house (256×256)
- ... (10 more)

**Dataset source:** https://github.com/cszn/FFDNet/tree/master/testsets/Set12

---

### `hasil/` — Output Folder

Berisi hasil experiment (generated):
- `terakhir_asli.png` — Original reference image
- `terakhir_noise.png` — Image dengan noise
- `terakhir_method0.png` — Median filter result
- `terakhir_method1.png` — Adaptive Median result
- `terakhir_method2.png` — Gaussian filter result

Dinamically generated setiap kali experiment dijalankan.

---

### `papers_denoising/` — Research Literature

Referensi paper yang dikutip:
- Denoising methods (Median, Adaptive Median, Gaussian)
- SSIM formula (Wang et al. 2004)
- Comparative studies
- Noise modeling

File `DAFTAR_PAPER.md` berisi daftar lengkap dengan citation.

---

## 🔧 Setup & Run

### 1. Clone/Setup

```bash
cd d:\KULIAH\SEMESTER 5\PCD\Berkas\denoising-web
```

### 2. Run Server

```bash
python src/server.py
```

Buka: http://127.0.0.1:8000

### 3. Run Tests

```bash
python -m unittest tests/test_filters.py -v
```

### 4. Study Documentation

```bash
# Baca semua teori & rumus
cat docs/TEORI_DAN_RUMUS.md

# Baca struktur folder
cat docs/STRUKTUR_FOLDER.md

# Baca API docs
cat docs/API_DOCS.md
```

---

## 🎓 Pembelajaran & Presentasi

### Urutan Belajar:

1. **Baca teori** → `docs/TEORI_DAN_RUMUS.md`
   - Pahami salt-and-pepper noise
   - Pahami algoritma Median & Adaptive Median
   - Pahami Gaussian Filter
   - Pahami PSNR & SSIM

2. **Baca kode implementasi** → `src/filters/image_filters.py`
   - Lihat kode sebenarnya
   - Lihat comment detail setiap step

3. **Jalankan tests** → `python -m unittest tests/`
   - Verify kode bekerja
   - Lihat edge cases

4. **Jalankan web UI** → `python src/server.py`
   - Eksperimen live dengan image
   - Lihat hasil filtering
   - Lihat metrik PSNR/SSIM

5. **Presentasi** → Gunakan `docs/TEORI_DAN_RUMUS.md`
   - Rumus lengkap siap pakai
   - Contoh numerik untuk demo
   - Kode sudah tercatat di same file

---

## 📝 Comment Guidelines

Setiap function harus punya:

```python
def my_function(arg1, arg2):
    """
    One-line description.
    
    Detailed explanation of algorithm or concept.
    
    Args:
        arg1: type — description
        arg2: type — description
    
    Returns:
        type — description
    
    Example:
        >>> result = my_function(input1, input2)
        >>> print(result)
        expected_output
    
    Complexity: O(n log n)
    Reference: [Paper/Algorithm name]
    """
    # Detailed inline comments for each logical step
    ...
```

---

## ✅ Migration dari Old Structure

**Old:** `denoise_manual.py` (semua fungsi jadi satu file)  
**New:** Terpisah per module di `src/`

**Migration steps** (akan dilakukan):
1. Split `denoise_manual.py` → `src/filters/`, `src/metrics/`, `src/noise/`, `src/png_io/`
2. Rewrite imports di `src/server.py`
3. Move tests → `tests/`
4. Create documentation
5. Keep `denoise_manual.py` sebagai fallback (untuk compatibility)

---

## 🔒 Security & Maintainability

**Keuntungan struktur baru:**
- ✅ **Modular** — Mudah dicari fungsi tertentu
- ✅ **Documented** — Teori & rumus dalam 1 file (`TEORI_DAN_RUMUS.md`)
- ✅ **Testable** — Setiap module punya unit tests
- ✅ **Reproducible** — Daftar referensi jelas
- ✅ **Presentable** — Siap untuk skripsi/paper

---

**Next:** Reorganisasi code akan dilakukan dalam beberapa step
