# Peta rumus manual

Ini folder implementasi yang **benar-benar dipanggil server**, bukan salinan untuk presentasi. Semua filter, noise, statistik, dan data grafik berada di sini. `denoise_manual.py` mengurus codec PNG serta perintah batch; `lesson_engine.py` hanya menjaga jalur impor lama tetap bekerja.

Urutan yang bisa dipakai saat menjelaskan kode:

1. **`noise.py` → `add_salt_pepper`**: salin citra bersih, hitung `round(tinggi × lebar × persen / 100)`, pilih lokasi unik memakai seed, lalu ganti bergantian dengan 0 dan 255. Proporsi adalah lokasi terpilih; nilai yang sudah sama mungkin tidak berubah. `random` hanya memilih lokasi, bukan menjalankan filter.
2. **`common.py`**: `pad_image` mengulang piksel tepi agar semua posisi memiliki tetangga; `neighborhood` mengambil window; `insertion_sort` mengurutkan secara manual. Piksel keluaran tidak dipakai sebagai masukan piksel berikutnya.
3. **`filters.py` → `median_pixel` / `median_filter`**: ambil sembilan nilai dari window 3×3, urutkan, ambil indeks `9 // 2 = 4`. Ulangi pada seluruh piksel.
4. **`filters.py` → `adaptive_pixel` / `adaptive_median_filter`**: window mulai 3×3. Tahap A memeriksa `zmin < zmed < zmax`; jika gagal, perluas sampai 7×7. Jika A lolos, tahap B memeriksa `zmin < zxy < zmax`: pertahankan pusat jika lolos, gunakan median jika gagal. Jika A terus gagal sampai batas, gunakan median terakhir.
5. **`filters.py` → `gaussian_kernel` / `gaussian_pixel` / `gaussian_filter`**: hitung `exp(−(u²+v²)/(2σ²))`, bagi setiap bobot dengan jumlah bobot, kalikan setiap tetangga dengan bobot yang sesuai, jumlahkan, lalu bulatkan half-up ke 0–255. Sigma bawaan `sqrt(1/(2 ln 2)) ≈ 0,8493218` menghasilkan kernel 3×3 setara `[1,2,1;2,4,2;1,2,1]/16`.
6. **`metrics.py` → `manual_metrics`**: jalur evaluasi web. MSE = jumlah `(asli − hasil)²` dibagi jumlah piksel. PSNR = `10 log10(255²/MSE)`; MSE nol berarti ∞, ditulis `null` dalam JSON. SSIM menghitung mean, varians sampel, dan kovarians per blok 8×8 tanpa overlap, lalu merata-ratakan skor blok. Pembagi varians/kovarians adalah `n−1`; blok satu piksel memiliki varians nol. Rumus SSIM gabungan: `((2μaμb+C1)(2σab+C2))/((μa²+μb²+C1)(σa²+σb²+C2))`, dengan `C1=(0,01×255)²`, `C2=(0,03×255)²`.
7. **`analysis.py` → `image_analysis`**: histogram 256 bin dari seluruh piksel dan profil baris tengah `tinggi // 2`. Jumlah histogram harus sama dengan jumlah piksel. Grafik di JavaScript hanya menggambar nilai ini, tanpa menghitung ulang rumus filter/metrik.
8. **`trace.py` → `filter_trace`**: fasilitas tambahan untuk melihat langkah satu piksel lewat API. Memanggil helper filter yang sama; tidak wajib dibuka pada alur visual utama.

`psnr` dan `ssim_block_average` di `metrics.py` mempertahankan fungsi batch dan pengujian lama. `manual_metrics` mengembalikan statistik yang lebih lengkap untuk web; keduanya diuji agar menghasilkan skor yang sama.

## Animasi hasil

Ketiga filter menerima callback `on_preview(rows, done, total)`. Setelah sebuah baris selesai, server dapat mengirim citra gabungan: **hasil filter pada baris `0:done` + noisy pada baris sisanya**. Ini menunjukkan hasil komputasi yang sudah ada, tanpa menambah jeda buatan. Callback hanya mengamati hasil dan tidak mengubah rumus.

## Penggunaan library

Tidak ada NumPy, OpenCV, SciPy, atau fungsi median/Gaussian/SSIM siap pakai. `math` menyediakan operasi skalar seperti eksponensial, akar, dan logaritma; statistik dan konvolusi tetap ditulis dengan perulangan. Codec, HTTP, pengacakan, dan ekspor memakai standard library Python.
