# Ruang Citra — Laboratorium Denoising

Website lokal untuk melihat perbandingan Median Filter, Adaptive Median, dan Gaussian Filter pada Set12.

## Menjalankan

Pastikan Python 3 tersedia. Tidak perlu memasang paket tambahan.

```sh
cd /Users/revanzhafran/Desktop/denoising-web
python3 server.py
```

Buka `http://127.0.0.1:8000` di browser. Biarkan Terminal tetap berjalan selama website digunakan.

Pilih gambar, tingkat noise 5/10/20/30%, dan seed, lalu tekan **Jalankan eksperimen**. Klik gambar untuk memperbesar. Tabel skor dapat diunduh sebagai CSV.

## Menjalankan program Python langsung (tanpa website)

Program lengkap ada di `denoise_manual.py`. File ini juga dipakai oleh website untuk menghitung noise, tiga filter, PSNR, dan SSIM. Program memakai modul bawaan Python saja; tidak membutuhkan OpenCV, NumPy, atau Pillow. Modul `zlib` bawaan Python dipakai untuk membuka/menyimpan kompresi PNG.

Di Windows, buka Terminal di folder proyek lalu jalankan:

```powershell
py denoise_manual.py --input data/Set12 --output hasil_denoising
```

Jika perintah `py` tidak tersedia, gunakan `python`:

```powershell
python denoise_manual.py --input data/Set12 --output hasil_denoising
```

Hasil gambar dan file `hasil_metrik.csv` akan dibuat di folder `hasil_denoising`. Tingkat noise bawaan adalah 5%, 10%, 20%, dan 30%. Untuk mengubahnya, misalnya menjadi 10% dan 20% saja:

```powershell
py denoise_manual.py --input data/Set12 --output hasil_denoising --levels 10,20
```

Gambar PNG yang didukung adalah PNG grayscale/RGB/RGBA 8-bit tanpa interlace. Semua gambar yang ditemukan di dalam folder input dan subfoldernya akan diproses.

## Isi eksperimen

- Dataset: 12 gambar Set12 dalam `data/Set12`.
- Noise buatan: salt-and-pepper dengan jumlah posisi noise yang ditentukan dari persentase; setengah piksel dipilih hitam dan setengah putih.
- Filter: Median 3×3, Adaptive Median 3×3–7×7, Gaussian lowpass 3×3 dari materi (K=1, σ=1; bobot dinormalisasi agar jumlahnya 1).
- Metrik: PSNR dibanding citra asli dan SSIM rata-rata blok 8×8 tidak tumpang tindih.
- Perhitungan: menampilkan MSE, substitusi PSNR, sampel piksel yang berubah, statistik blok SSIM pertama, dan rata-rata SSIM.
- Semua filter, noise, pembacaan/penulisan PNG, PSNR, dan SSIM dibuat manual. Program menggunakan `zlib` bawaan Python untuk mendekompresi/mengompresi PNG.

Set12 dan catatan dataset tersedia di [repositori FFDNet](https://github.com/cszn/FFDNet/tree/master/testsets/Set12). Dataset dipakai sebagai gambar acuan bersih; noise pada eksperimen ini ditambahkan oleh website.
