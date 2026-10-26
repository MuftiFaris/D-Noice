# ✅ Checklist Lengkap Project Denoising-Web

**Status:** Near completion, ada beberapa P0 gap perlu fix

---

## 📦 BACKEND (Python)

### ✅ Core Algorithms
- [x] **Salt-and-Pepper Noise** (`rumus_manual/noise.py`)
  - Implementasi: `add_salt_pepper(image, percent, seed)`
  - Seeding reproducible ✓
  - Teori ada di `docs/TEORI_DAN_RUMUS.md` ✓

- [x] **Median Filter** (`rumus_manual/filters.py`)
  - 3×3 kernel ✓
  - Manual insertion sort ✓
  - Replicate edge padding ✓
  - Teori + rumus + code examples ✓

- [x] **Adaptive Median Filter** (`rumus_manual/filters.py`)
  - 3×3 → 7×7 window expansion ✓
  - Tahap A & B logic ✓
  - Teori lengkap ✓

- [x] **Gaussian Filter** (`rumus_manual/filters.py`)
  - Configurable kernel size & sigma ✓
  - Half-up rounding ✓
  - Teori + formula ✓

### ✅ Image I/O
- [x] **PNG Codec Manual** (`src/png_io/png_codec.py` + `denoise_manual.py`)
  - read_png_gray() ✓
  - write_png_gray() ✓
  - PNG filters (Sub, Up, Average, Paeth) ✓
  - Support: Grayscale, RGB, RGBA ✓
  - **⚠️ ISSUE:** Dua codec (old di denoise_manual.py, new di src/png_io) belum integrated

### ✅ Metrics
- [x] **PSNR** (`rumus_manual/metrics.py`)
  - MSE calculation ✓
  - 10 × log₁₀(255²/MSE) ✓
  - Handle edge case: MSE=0 → ∞ ✓
  - Teori lengkap ✓

- [x] **SSIM** (`rumus_manual/metrics.py`)
  - 8×8 non-overlapping blocks ✓
  - Luminance, Contrast, Structure ✓
  - k1=0.01, k2=0.03 constants ✓
  - Average semua blocks ✓
  - Teori + rumus detail ✓

- [x] **MSE** (`rumus_manual/metrics.py`)
  - Pixel-wise squared difference ✓
  - Support `on_progress` callback ✓

### ✅ Analysis (Visualization Support)
- [x] **Histogram** (`rumus_manual/analysis.py`)
  - 256 bins untuk 8-bit ✓
  - Exact pixel counts ✓

- [x] **Row Profile** (`rumus_manual/analysis.py`)
  - Extract center row ✓
  - Selectable row index ✓

- [x] **Filter Trace** (`rumus_manual/trace.py`)
  - Single-pixel walkthrough ✓
  - Step-by-step output ✓

### ✅ HTTP Server
- [x] **Server Core** (`server.py`)
  - ThreadingHTTPServer ✓
  - Port 8000 default ✓

- [x] **API Endpoints**
  - `/api/images` — list Set12 ✓
  - `/api/prepare` — init session ✓
  - `/api/process` — run filter + stream NDJSON ✓
  - `/api/trace` — single-pixel debug ✓

- [x] **Session Management**
  - Max 8 concurrent ✓
  - 1.5 hour timeout ✓
  - Busy lock ✓

### ⚠️ Backend Issues Found

| Issue | Status | Impact | Fix Time |
|-------|--------|--------|----------|
| **PNG codec duplication** | 🔴 Not integrated | Code confusion | 10 min |
| **gaussian_filter() streaming** | 🟡 Unclear | Incomplete progress bar | 15 min |
| **/api/download missing** | 🟡 Nice-to-have | Can't export images | 15 min |

---

## 🎨 FRONTEND (JavaScript/HTML/CSS)

### ✅ UI Components
- [x] **Image Gallery** (`app.js`)
  - Load 12 images from `/api/images` ✓
  - Thumbnail preview ✓
  - Select image ✓

- [x] **Noise Level Selector** (`app.js`)
  - Buttons: 5%, 10%, 20%, 30% ✓
  - Default 10% ✓

- [x] **Experiment Workflow** (`app.js`)
  - /api/prepare → get session ✓
  - Show original + noisy ✓
  - Run /api/process → stream results ✓
  - Display 3 filter outputs ✓

- [x] **Metrics Cards** (`app.js`)
  - MSE, PSNR, SSIM per method ✓
  - Best method highlight ✓

- [x] **CSV Export** (`app.js`)
  - Download metrics as CSV ✓

### 🔴 Frontend Issues

| Issue | Status | Impact | Fix Time |
|-------|--------|--------|----------|
| **Chart.js not loaded** | 🔴 Missing | No graphs/histograms shown | 5 min |
| **renderCombinedAnalysis() not implemented** | 🔴 Broken | Chart display fails | 30 min |
| **renderChartData() not defined** | 🔴 Broken | Data format unclear | 20 min |
| **downloadChartCsv() not defined** | 🔴 Broken | Can't export chart data | 10 min |
| **Histogram/Profile rendering** | 🔴 Missing | Visual analysis incomplete | 30 min |

### ✅ Styling
- [x] HTML structure (`index.html`) ✓
- [x] CSS files (`research.css`, `theme.css`, etc.) ✓
- [x] Responsive layout ✓

---

## 📚 DOCUMENTATION

### ✅ Theory & Formulas
- [x] **TEORI_DAN_RUMUS.md** — Comprehensive
  - Salt-and-Pepper Noise ✓
  - Median Filter ✓
  - Adaptive Median ✓
  - Gaussian Filter ✓
  - PSNR ✓
  - SSIM ✓
  - Semua punya teori + rumus + code + example ✓

### ✅ Code Documentation
- [x] **PNG Codec** (`src/png_io/png_codec.py`)
  - Docstrings lengkap ✓
  - Algorithm explanation ✓
  - References ✓

- [x] **Module READMEs**
  - `rumus_manual/README.md` ✓

### ✅ Folder Structure
- [x] **STRUKTUR_FOLDER.md** — Complete ✓

### ⚠️ Documentation Gaps

| Gap | Status | Impact |
|-----|--------|--------|
| **API_DOCS.md** | 🟡 Mentioned but not created | Hard to understand endpoints |
| **Gaussian streaming** | 🟡 Not documented | Unclear if implemented |

---

## 🧪 TESTING

### ✅ Unit Tests Exist
- [x] `test_manual_filters.py` — Filter tests ✓
- [x] `test_analysis.py` — Analysis + server integration ✓
- [x] `test_lesson_engine.py` — Callback system ✓
- [x] `test_visual.py` — Visual validation ✓

### 🔴 Testing Gaps

| Gap | Status | Impact | Fix Time |
|-----|--------|--------|----------|
| **PNG codec validation** | 🔴 Missing | Can't verify src/png_io works | 15 min |
| **Chart rendering tests** | 🔴 Missing | Chart code untested | 10 min |
| **Server stability test** | 🔴 Missing | Don't know if /api works under load | 20 min |

---

## 📊 DATA

### ✅ Dataset
- [x] `data/Set12/` — 12 test images (256×256 grayscale PNG) ✓

### ✅ Output
- [x] `hasil/` — Output folder for experiment results ✓

### ✅ References
- [x] `papers_denoising/` — 10 research papers ✓
- [x] `papers_denoising/DAFTAR_PAPER.md` — Bibliography ✓

---

## 🔧 INTEGRATION GAPS (Critical to Fix)

### P0 — Fix Before Using

#### 1. **PNG Codec Integration**
```
Current state: 2 PNG codec implementations
- denoise_manual.py (old, inline)
- src/png_io/png_codec.py (new, modular)

Issue: Not integrated → confusion & potential mismatch

Fix: Use src/png_io as primary
```

**Action:**
```python
# denoise_manual.py (modify imports)
from src.png_io.png_codec import read_png_gray, write_png_gray
# Remove inline PNG codec from denoise_manual.py
```

**Time:** 5-10 min

---

#### 2. **Frontend Chart Rendering**
```
Current state: app.js calls renderCombinedAnalysis() 
              but function doesn't exist

Issue: 
- No Chart.js library loaded
- renderCombinedAnalysis() not implemented
- renderChartData() not defined
- downloadChartCsv() not defined

Fix: Add Chart.js + implement functions
```

**Action:**
```html
<!-- Add to index.html <head> -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

```javascript
// Implement in app.js:
function renderCombinedAnalysis(data) {
  // Draw histogram for original
  // Draw histogram for filtered
  // Draw row profile comparison
}

function renderChartData() {
  // Return chart data for export
}

function downloadChartCsv() {
  // Export chart as CSV
}
```

**Time:** 30-45 min

---

#### 3. **Gaussian Filter Streaming (Verify)**
```
Current state: gaussian_filter() may not have on_progress callback

Issue: Incomplete progress bar for Gaussian filter

Fix: Check filters.py gaussian_filter() 
     implements on_progress(rows, done, total)
```

**Action:**
```python
# In rumus_manual/filters.py - gaussian_filter()
# Add progress callbacks like median_filter does
```

**Time:** 15 min

---

### P1 — Validation & Testing

#### 4. **Validate PNG Codec Match**
```
Current state: Old codec in denoise_manual.py works

Issue: After migration to src/png_io, need to verify
       output byte-for-byte identical

Fix: Run tests that compare both codecs
```

**Time:** 15 min

---

#### 5. **API Documentation** (`docs/API_DOCS.md`)
```
Current state: Endpoints exist but no formal docs

Issue: Hard to understand request/response format

Fix: Create docs/API_DOCS.md with:
- /api/images (GET)
- /api/prepare (POST)
- /api/process (POST, NDJSON streaming)
- /api/trace (POST)
```

**Time:** 20 min

---

### P2 — Nice-to-Have Features

#### 6. **Image Download Endpoints**
```
Missing: /api/download/image/<method>
Benefit: Export filtered images directly
Impact: Low (CSV export sufficient for now)
```

**Time:** 15 min

---

## 📋 QUICK COMPLETION CHECKLIST

```bash
# 1. Integrate PNG codec (P0)
[ ] Remove src/png_io from imports (use denoise_manual.py reference instead)
[ ] Keep old codec in denoise_manual.py as is
[ ] Run tests to verify still working

# 2. Add Chart.js (P0)
[ ] Add <script> to index.html
[ ] Implement renderCombinedAnalysis() in app.js
[ ] Implement renderChartData()
[ ] Implement downloadChartCsv()
[ ] Test chart rendering live

# 3. Verify Gaussian streaming (P0)
[ ] Check rumus_manual/filters.py
[ ] Confirm on_progress() is called
[ ] Test streaming progress bar in UI

# 4. Validate PNG codec (P1)
[ ] Write comparison test
[ ] Verify old vs new produce same bytes

# 5. Add API docs (P1)
[ ] Create docs/API_DOCS.md
[ ] Document all 4 endpoints

# 6. Run full test suite (P1)
[ ] python -m unittest discover -s . -p "test_*.py" -v
[ ] Fix any failures

# 7. Manual testing (P1)
[ ] Start server: python server.py
[ ] Load http://localhost:8000
[ ] Select image
[ ] Run experiment
[ ] Verify:
    - All 3 filters run
    - Metrics display
    - CSV downloads
    - Charts show (if implemented)
    - Progress bar smooth

# 8. Document setup (P2)
[ ] Create SETUP.md for quick start
[ ] Create DEVELOPER_GUIDE.md
```

---

## 🎯 FINAL STATUS

### What's Ready ✅
- Backend algorithms (all working)
- PNG codec (working, but duplicated)
- HTTP server (working)
- Metrics calculation (working)
- Documentation structure (good)
- Test framework (in place)

### What Needs Work 🔴
- **Frontend charts** (HIGH PRIORITY)
- **PNG codec integration** (HIGH PRIORITY)
- **Gaussian streaming verification** (MEDIUM)

### Estimated Time to "Production Ready"
- **P0 fixes:** ~60-90 min
- **P1 fixes:** ~70 min  
- **P2 features:** ~30 min
- **Total:** ~3-4 hours

---

## 🚀 RECOMMENDED ORDER

1. **Add Chart.js + chart functions** (30 min) — Unblock frontend
2. **Verify Gaussian streaming** (15 min) — Ensure complete UX
3. **Validate PNG codec** (15 min) — Risk mitigation
4. **Create API_DOCS.md** (20 min) — Documentation
5. **Test suite run** (20 min) — Regression check
6. **Manual testing** (30 min) — User acceptance
7. **Cleanup & setup guides** (20 min) — Final polish

**Est. total:** 150 min = **~2.5 hours**

---

## ❓ Questions to Answer

1. **Chart library preference?** (Chart.js, D3.js, Plotly?)
2. **Export filtered images?** (Add /api/download?)
3. **Need GUI installer?** (Or shell script?)
4. **Deploy target?** (Localhost only, or publish?)
5. **Browser compatibility?** (Modern only, or IE11?)

---

**Document created:** Comprehensive project state assessment
**Next step:** Choose which P0 fix to do first
