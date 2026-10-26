# Ruang Citra — Perbandingan Denoising

Website lokal untuk membandingkan Median, Adaptive Median, dan Gaussian terhadap salt-and-pepper noise pada citra grayscale Set12. Semua rumus ditulis manual dengan Python, tanpa paket tambahan.

## Menjalankan

Dari folder `denoising-web`, jalankan:

```sh
python server.py
```

Buka `http://127.0.0.1:8000`. Setelah pembaruan, hentikan server lama, jalankan kembali, lalu muat ulang halaman dengan Ctrl+F5. Seluruh folder proyek perlu disertakan saat dibagikan; HTML saja tidak menjalankan backend Python.

## Alur visual

1. Pilih foto. Citra asli langsung tampil.
2. Pilih noise 5%, 10%, 20%, atau 30%. Citra noisy muncul, kemudian ketiga filter otomatis dijalankan berurutan dengan masukan noisy yang sama.
3. Setiap kartu menampilkan pratinjau hasil dari atas ke bawah. Baris di atas garis merupakan keluaran yang sudah dihitung; baris di bawah masih noisy. Server mengirim pratinjau sekitar 12 kali per metode, tanpa jeda komputasi buatan. Pada gambar kecil proses bisa singkat.
4. MSE, PSNR, dan SSIM muncul setelah dihitung. Tidak perlu melewati slide rumus atau menyelesaikan evaluasi secara manual.
5. Bandingkan grafik semua metode atau satu metode. Tombol pada setiap kartu memilih metode tersebut di grafik. Unduh metrik atau data titik grafik sebagai CSV.

Kontrol pengaturan dinonaktifkan selama proses. Mengubah foto atau seed membersihkan hasil sebelumnya. Setelah mengubah seed, pilih noise atau tekan **Jalankan ulang**. Kegagalan menampilkan pesan dan memungkinkan pengulangan; hasil metode yang sudah selesai tetap dapat dianalisis.

Animasi transisi menghormati pengaturan reduced motion. Kecepatan filter mengikuti waktu perhitungan sebenarnya, bukan timer. Grafik dan angka belum diperiksa secara visual di browser oleh agen sesuai permintaan pengguna; pengujian alur dan data dijalankan melalui kode.

## Satu folder untuk semua rumus

Lihat [panduan rumus](rumus_manual/README.md) untuk urutan penjelasan dari noise hingga metrik.

```text
rumus_manual/
  __init__.py   pintu impor fungsi
  common.py     padding, tetangga, insertion sort
  filters.py    Median, Adaptive Median, Gaussian
  noise.py      salt-and-pepper noise
  metrics.py    MSE, PSNR, SSIM dan statistik evaluasi
  analysis.py   histogram dan profil intensitas
  trace.py      penelusuran satu piksel untuk API tambahan
  README.md     peta fungsi dan rumus untuk presentasi
```

Server memanggil implementasi di folder tersebut. `denoise_manual.py` menyimpan codec PNG serta perintah batch dan mengimpor ulang fungsi lama untuk kompatibilitas. `lesson_engine.py` hanya meneruskan impor. `charts.js` menggambar data dari Python dengan SVG tanpa library grafik.

`math` dipakai untuk operasi skalar (exp, akar, log), `random` untuk lokasi noise. Filter, pengurutan, normalisasi kernel, konvolusi, statistik, dan metrik tidak menggunakan fungsi library pihak ketiga. Codec PNG dan HTTP juga memakai standard library Python.

## Konfigurasi eksperimen

- Dataset: Set12 di `data/Set12`, sumber FFDNet: https://github.com/cszn/FFDNet/tree/master/testsets/Set12.
- Noise: lokasi unik sebanyak `round(lebar * tinggi * persen / 100)`, penggantian bergantian 0 dan 255, seed dapat diulang. Lokasi terpilih yang nilainya sudah sama mungkin tidak berubah.
- Median: window 3x3, insertion sort manual.
- Adaptive Median: window 3x3 hingga 7x7, tahap A dan B.
- Gaussian: kernel 3x3, sigma bawaan sekitar 0,8493218; bobot setara [1,2,1;2,4,2;1,2,1]/16. Bukan sigma 1.
- Padding: replicate untuk semua filter. Hasil grayscale 8-bit; Gaussian dibulatkan half-up.
- SSIM: mean, varians sampel, kovarians sampel per blok 8x8 tidak tumpang tindih, lalu rata-rata blok. Ini berbeda dari SSIM Gaussian 11x11.
- MSE nol: PSNR tak hingga, ditulis `null` pada API dan ditampilkan sebagai simbol infinity. Tidak digambar sebagai batang dengan panjang hingga.

## Grafik analisis

Profil intensitas mengambil baris tengah yang sama (`y = tinggi // 2`) pada semua citra, dengan sumbu intensitas 0 sampai 255 dan tanpa smoothing. Ini analisis lokal, bukan skor seluruh citra.

Histogram menghitung frekuensi 256 intensitas dari seluruh piksel. Total semua bin harus sama dengan jumlah piksel. Histogram tidak menyimpan posisi spasial.

Grafik MSE/PSNR/SSIM dan tabel mencakup citra asli, noisy, dan hasil metode yang selesai. Citra asli memiliki MSE 0, PSNR tak hingga, dan SSIM 1. SSIM memakai skala tetap -1 sampai 1. MSE dan PSNR memakai maksimum nilai hingga pada seri yang sedang ditampilkan, jadi baca sumbu ketika berpindah pilihan.

CSV metrik memuat identitas citra, noise, seed, metode, MSE, PSNR, dan SSIM. CSV grafik memuat setiap titik profil dan bin histogram, termasuk baris y untuk profil. Nilai ekspor tidak dibulatkan seperti tampilan.

## Pengujian tanpa browser

```sh
python -B -m unittest discover -v
node test_visual.cjs
```

Node hanya untuk pengujian alur antarmuka, bukan syarat menjalankan situs. Tes memeriksa rumus, tepi citra, trace, progres, pratinjau tiap baris, kecocokan metrik dan grafik, alur otomatis, reset, serta pemulihan setelah error.

Sesi disimpan di memori server, maksimum 8 sesi dan kedaluwarsa 90 menit. Restart menghapus sesi. Rute `/api/images`, `/api/prepare`, `/api/process`, `/api/trace`, dan rute lama `/api/run` tetap tersedia.
