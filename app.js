const methods = ['Median Filter', 'Adaptive Median', 'Gaussian Filter'];
const images = { original: 'Gambar acuan bersih', noisy: 'Setelah diberi noise', method0: 'Hasil Median Filter', method1: 'Hasil Adaptive Median', method2: 'Hasil Gaussian Filter' };
const $ = selector => document.querySelector(selector);
let previewName = null;
let activeName = null;
let experiment = null;
let noiseLevel = 10;
const fmt = (value, digits = 3) => new Intl.NumberFormat('id-ID', { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);

async function loadGallery() {
  try {
    const response = await fetch('/api/images');
    if (!response.ok) throw new Error('Server belum merespons.');
    const data = await response.json();
    if (!data.images?.length) throw new Error('Gambar Set12 belum tersedia.');
    $('#gallery-count').textContent = `${String(data.images.length).padStart(2, '0')} GAMBAR`;
    $('#image-gallery').innerHTML = data.images.map((name, i) => `<button class="gallery-item" type="button" data-image="${name}" data-index="${String(i + 1).padStart(2, '0')} / ${String(data.images.length).padStart(2, '0')}" aria-label="Pratinjau gambar ${name}"><span class="gallery-thumb"><img src="/data/Set12/${encodeURIComponent(name)}" alt="Thumbnail gambar ${name}" loading="lazy"></span><span class="gallery-label"><span>${name}</span><i>${String(i + 1).padStart(2, '0')} / ${String(data.images.length).padStart(2, '0')}</i></span></button>`).join('');
    const params = new URLSearchParams(location.search);
    if (params.has('image')) openPreview(params.get('image'));
  } catch (error) {
    $('#gallery-count').textContent = 'DATASET BELUM TERSEDIA';
    $('#status').textContent = `Gambar belum dapat dimuat: ${error.message}`;
    $('#status').className = 'status error';
  }
}

function openPreview(name) {
  if (!name || !/^[\w.-]+\.png$/i.test(name)) return;
  previewName = name;
  const image = $('#preview-image');
  image.hidden = true;
  $('#preview-empty').hidden = false;
  $('#preview-state').textContent = activeName === name ? 'SUDAH DIPILIH' : 'PRATINJAU';
  $('#preview-state').classList.toggle('ready', activeName === name);
  $('#preview-name').textContent = name;
  $('#preview-size').textContent = 'Membaca ukuran…';
  $('#confirm-image').disabled = true;
  $('#confirm-image').innerHTML = activeName === name ? 'Gunakan gambar ini lagi <span>→</span>' : 'Gunakan gambar ini <span>→</span>';
  $('#preview-hint').textContent = activeName === name ? 'Gambar ini sudah menjadi acuan eksperimen.' : 'Pratinjau saja — belum dipakai untuk eksperimen.';
  document.querySelectorAll('.gallery-item').forEach(card => card.classList.toggle('previewing', card.dataset.image === name));
  image.onload = () => {
    $('#preview-size').textContent = `${image.naturalWidth} × ${image.naturalHeight} piksel`;
    image.hidden = false;
    $('#preview-empty').hidden = true;
    $('#confirm-image').disabled = false;
  };
  image.onerror = () => { $('#preview-size').textContent = 'Tidak dapat dibaca'; $('#preview-empty').hidden = false; $('#confirm-image').disabled = true; };
  image.src = `/data/Set12/${encodeURIComponent(name)}`;
}

function confirmPreview() {
  if (!previewName) return;
  activeName = previewName;
  $('#preview-state').textContent = 'TERPILIH';
  $('#preview-state').classList.add('ready');
  $('#preview-hint').textContent = 'Gambar ini sudah dikonfirmasi sebagai acuan bersih.';
  $('#confirm-image').innerHTML = 'Gambar ini digunakan <span>✓</span>';
  $('#confirm-image').disabled = true;
  $('#selected-banner').hidden = false;
  $('#selected-name').textContent = activeName;
  $('#selected-dimensions').textContent = $('#preview-size').textContent;
  $('#run-button').disabled = false;
  $('#run-hint').textContent = 'Filter hanya berjalan setelah tombol ini ditekan.';
  document.querySelectorAll('.gallery-item').forEach(card => {
    const chosen = card.dataset.image === activeName;
    card.classList.toggle('chosen', chosen);
    card.querySelector('.gallery-label i').textContent = chosen ? 'DIPILIH' : card.dataset.index;
  });
  $('#selected-banner').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function changeImage() {
  $('#pilih-gambar').scrollIntoView({ behavior: 'smooth', block: 'start' });
  if (previewName) $('#confirm-image').disabled = false;
}

async function runExperiment() {
  if (!activeName) return;
  const seed = Number($('#seed-input').value);
  if (!Number.isInteger(seed) || seed < 0 || seed > 2147483647) {
    showStatus('Seed harus berupa angka bulat dari 0 sampai 2147483647.', true);
    return;
  }
  const button = $('#run-button');
  button.disabled = true;
  button.innerHTML = '<span>Memproses gambar…</span><b class="spinner">◌</b>';
  showStatus('Menghitung noise, menjalankan filter, dan membandingkan piksel…');
  try {
    const response = await fetch('/api/run', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ image: activeName, noise: noiseLevel, seed }) });
    const body = await response.json();
    if (!response.ok) throw new Error(body.error || 'Percobaan tidak berhasil.');
    experiment = body;
    renderExperiment(body);
    showStatus(`Percobaan selesai untuk ${body.image} dengan noise ${body.noise}% dan seed ${body.seed}.`);
    $('#status').classList.add('success');
  } catch (error) {
    showStatus(error instanceof Error ? error.message : 'Percobaan gagal.', true);
  } finally {
    button.disabled = !activeName;
    button.innerHTML = '<span>Jalankan eksperimen</span><b>→</b>';
  }
}

function showStatus(text, isError = false) {
  $('#status').textContent = text;
  $('#status').className = `status${isError ? ' error' : ''}`;
}

function renderExperiment(data) {
  document.querySelectorAll('[data-result]').forEach(img => {
    img.src = data.images[img.dataset.result];
    img.hidden = false;
    img.closest('.result-image').querySelector('.image-empty').hidden = true;
  });
  $('#image-meta').textContent = `${data.image} · ${data.width} × ${data.height} piksel · noise ${data.noise}% · seed ${data.seed}`;
  $('#summary-noise').textContent = `${data.noise}% · ${data.image}`;
  renderScores(data);
  renderCalculations(data, $('#method-select').value);
  $('#download-csv').disabled = false;
  $('#hasil').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderScores(data) {
  const bestPsnr = methods.reduce((best, name) => data.methods[name].psnr > data.methods[best].psnr ? name : best, methods[0]);
  const bestSsim = methods.reduce((best, name) => data.methods[name].ssim > data.methods[best].ssim ? name : best, methods[0]);
  $('#metrics-body').innerHTML = methods.map(name => {
    const rowBest = name === bestPsnr || name === bestSsim;
    const badges = [name === bestPsnr ? '<small class="best-label">PSNR TERTINGGI</small>' : '', name === bestSsim ? '<small class="best-label">SSIM TERTINGGI</small>' : ''].join('');
    return `<tr class="${rowBest ? 'best' : ''}"><td>${name}${badges}</td><td>${fmt(data.methods[name].psnr, 2)}</td><td>${fmt(data.methods[name].ssim, 4)}</td></tr>`;
  }).join('');
  $('#psnr-bars').innerHTML = makeBars(data, 'psnr', 50, bestPsnr, 1);
  $('#ssim-bars').innerHTML = makeBars(data, 'ssim', 1, bestSsim, 3);
}

function makeBars(data, metric, scale, best, digits) {
  return methods.map(name => {
    const value = data.methods[name][metric];
    const friendlyName = name === 'Adaptive Median' ? name : name.replace(' Filter', '');
    return `<div class="bar-row ${name === best ? 'best' : ''}"><span>${friendlyName}</span><div><i style="width:${Math.min(100, Math.max(0, value / scale * 100))}%"></i></div><b>${fmt(value, digits)}</b></div>`;
  }).join('');
}

function renderCalculations(data, selectedMethod) {
  const m = data.methods[selectedMethod];
  const bestPsnr = methods.reduce((best, name) => data.methods[name].psnr > data.methods[best].psnr ? name : best, methods[0]);
  const samples = m.samples.length ? m.samples.map(p => `<tr><td>(${p.x}, ${p.y})</td><td>${p.original}</td><td>${p.result}</td><td>${p.square}</td></tr>`).join('') : '<tr><td colspan="4">Tidak ada piksel berbeda.</td></tr>';
  const b = m.ssim_block;
  $('#calculation-content').innerHTML = `
  <article class="calc-card"><span class="calc-kicker">A / KESALAHAN NILAI PIKSEL</span><h3>Menghitung MSE</h3><p>MSE merangkum selisih setiap piksel gambar acuan dan hasil filter. Ini adalah jumlah kesalahan kuadrat dibagi jumlah piksel.</p><code class="formula">MSE = Σ (piksel asli − piksel hasil)² ÷ jumlah piksel</code><div class="substitution">${m.sum_squared_error.toLocaleString('id-ID')} ÷ ${m.pixel_count.toLocaleString('id-ID')} = <strong>${fmt(m.mse, 5)}</strong></div><div class="pixel-samples"><strong>Contoh piksel berbeda · koordinat (x, y)</strong><table><thead><tr><th>Posisi</th><th>Asli</th><th>Hasil</th><th>Selisih²</th></tr></thead><tbody>${samples}</tbody></table></div></article>
  <article class="calc-card"><span class="calc-kicker">B / KEMIRIPAN NILAI</span><h3>Dari MSE menjadi PSNR</h3><p>Untuk gambar 8-bit, nilai piksel paling terang adalah 255. Logaritma mengubah rasio kesalahan menjadi satuan desibel (dB).</p><code class="formula">PSNR = 10 × log₁₀(255² ÷ MSE)</code><div class="substitution">10 × log₁₀(65025 ÷ ${fmt(m.mse, 5)})</div><div class="answer">${fmt(m.psnr, 4)} <small>dB</small></div><p>Nilai paling tinggi pada percobaan ini: <b>${bestPsnr}</b>.</p></article>
  <article class="calc-card wide"><span class="calc-kicker">C / KEMIRIPAN STRUKTUR</span><h3>Contoh perhitungan SSIM pada blok 8×8</h3><p>SSIM melihat kecerahan, kontras, dan keterkaitan pola. Nilai statistik di bawah berasal dari blok pertama gambar yang dibandingkan.</p><code class="formula">SSIM = ((2μₐμᵦ + C₁)(2σₐᵦ + C₂)) ÷ ((μₐ² + μᵦ² + C₁)(σₐ² + σᵦ² + C₂))</code><div class="ssim-values"><div><span>Rata-rata kecerahan gambar acuan (μₐ)</span><b>${fmt(b.mean_original, 3)}</b></div><div><span>Rata-rata kecerahan hasil filter (μᵦ)</span><b>${fmt(b.mean_result, 3)}</b></div><div><span>Variasi / kontras acuan (σₐ²)</span><b>${fmt(b.variance_original, 3)}</b></div><div><span>Variasi / kontras hasil (σᵦ²)</span><b>${fmt(b.variance_result, 3)}</b></div><div><span>Kovariansi pola (σₐᵦ)</span><b>${fmt(b.covariance, 3)}</b></div><div><span>Konstanta penstabil (C₁ / C₂)</span><b>${fmt(b.c1, 3)} / ${fmt(b.c2, 3)}</b></div></div><div class="substitution">SSIM blok pertama = <strong>${fmt(b.value, 6)}</strong></div><div class="answer">${fmt(m.ssim, 5)} <small>rata-rata seluruh blok</small></div></article>`;
}

function downloadCsv() {
  if (!experiment) return;
  const rows = [['Gambar', 'Noise (%)', 'Seed', 'Metode', 'PSNR (dB)', 'SSIM blok 8x8'], ...methods.map(name => [experiment.image, experiment.noise, experiment.seed, name, experiment.methods[name].psnr.toFixed(6), experiment.methods[name].ssim.toFixed(6)])];
  const csv = '\ufeff' + rows.map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(',')).join('\r\n');
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  link.download = `hasil_${experiment.image.replace('.png', '')}_noise${experiment.noise}.csv`;
  link.click(); URL.revokeObjectURL(link.href);
}

function showLightbox(img, caption) {
  $('#lightbox img').src = img.src;
  $('#lightbox img').alt = caption;
  $('#lightbox span').textContent = caption;
  $('#lightbox').hidden = false;
}

document.querySelectorAll('.noise-options button').forEach(button => button.addEventListener('click', () => {
  noiseLevel = Number(button.dataset.noise);
  document.querySelectorAll('.noise-options button').forEach(option => option.classList.toggle('active', option === button));
  $('#noise-explainer').textContent = `${noiseLevel}% berarti sekitar ${noiseLevel} dari setiap 100 piksel diubah menjadi hitam atau putih.`;
}));
$('#image-gallery').addEventListener('click', event => {
  const button = event.target.closest('.gallery-item');
  if (button) openPreview(button.dataset.image);
});
$('#confirm-image').addEventListener('click', confirmPreview);
$('#change-image').addEventListener('click', () => $('#pilih-gambar').scrollIntoView({ behavior: 'smooth', block: 'start' }));
$('#run-button').addEventListener('click', runExperiment);
$('#method-select').addEventListener('change', () => { if (experiment) renderCalculations(experiment, $('#method-select').value); });
$('#download-csv').addEventListener('click', downloadCsv);
document.querySelectorAll('.result-image').forEach(box => box.addEventListener('click', () => { const img = box.querySelector('img'); if (!img.hidden) showLightbox(img, img.alt); }));
$('#lightbox-close').addEventListener('click', () => { $('#lightbox').hidden = true; });
$('#lightbox').addEventListener('click', event => { if (event.target.id === 'lightbox') $('#lightbox').hidden = true; });
document.addEventListener('keydown', event => { if (event.key === 'Escape') $('#lightbox').hidden = true; });
loadGallery();
