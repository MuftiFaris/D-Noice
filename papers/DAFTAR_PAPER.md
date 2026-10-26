# Daftar Paper Denoising Citra

Kumpulan ini berisi 10 paper yang berhubungan dengan penghilangan noise pada citra, terutama filter median/adaptif, filter Gaussian, jenis noise, serta penilaian kualitas memakai PSNR/SSIM. Paper tidak semuanya membandingkan tiga metode yang sama persis; beberapa dipilih sebagai dasar metode atau penjelasan metrik.

## Daftar paper

1. **Zhongxin Gao (2018), “An Adaptive Median Filtering of Salt and Pepper Noise based on Local Pixel Distribution.”** Membahas adaptive median untuk citra grayscale yang terkena salt-and-pepper; menyebut PSNR, MSE, dan SSIM. DOI: https://doi.org/10.2991/tlicsc-18.2018.77. [Sumber/PDF](https://www.atlantis-press.com/proceedings/tlicsc-18/25907284)
2. **Zayed M. Ramadan (2018), “Optimum Image Filters for Various Types of Noise.”** Membandingkan filter median dan Gaussian (juga filter lain) pada beberapa jenis noise dan mengevaluasi PSNR/SSIM. DOI: https://doi.org/10.12928/telkomnika.v16i5.10508. [Sumber](https://telkomnika.uad.ac.id/index.php/TELKOMNIKA/article/view/10508)
3. **V. Jayaraj & D. Ebenezer (2010), “A New Switching-Based Median Filtering Scheme and Algorithm for Removal of High-Density Salt and Pepper Noise in Images.”** Rujukan tentang penghilangan salt-and-pepper berkepadatan tinggi dengan pendekatan median dan evaluasi kualitas/PSNR. DOI: https://doi.org/10.1155/2010/690218. [Sumber](https://link.springer.com/article/10.1155/2010/690218)
4. **Zhou Wang, A. C. Bovik, H. R. Sheikh & E. P. Simoncelli (2004), “Image Quality Assessment: From Error Visibility to Structural Similarity.”** Paper dasar untuk memahami SSIM dan bedanya dengan ukuran error seperti MSE/PSNR. DOI: https://doi.org/10.1109/TIP.2003.819861. [Sumber](https://www.colorado.edu/lab/live/publications/zwang_ssim_ieeeip2004.pdf)
5. **“A Comparative Study of Removal Noise from Remote Sensing Image” (2010, arXiv).** Membandingkan median, adaptive median, Gaussian dan filter lain untuk berbagai noise serta tingkat noise. [Sumber](https://arxiv.org/abs/1002.1148)
6. **Sajid Khan & Dong-Ho Lee (2017), “An adaptive dynamically weighted median filter for impulse noise removal.”** Menjelaskan filter median adaptif yang mengubah bobot/jendela menurut noise impulsif. DOI: https://doi.org/10.1186/s13634-017-0502-z. [Sumber](https://link.springer.com/article/10.1186/s13634-017-0502-z)
7. **Yunyun Jiang, Hefei Wang, Yi Cai & Bo Fu (2022), “Salt and Pepper Noise Removal Method Based on the Edge-Adaptive Total Variation Model.”** Bukan salah satu dari tiga filter utama, tetapi membahas median sebagai pembanding dan evaluasi PSNR/SSIM pada berbagai tingkat noise. DOI: https://doi.org/10.3389/fams.2022.918357. [Sumber](https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2022.918357/full)
8. **Hanspran Limbong, Lailan Sofinah Harahap & Rafli Arya Gading (2025), “Comparison of Median Filter and Gaussian Filter Performance in Removing Salt and Pepper Noise.”** Perbandingan langsung median dan Gaussian untuk salt-and-pepper menggunakan PSNR dan MSE. DOI: https://doi.org/10.59934/jaiea.v4i3.1033. [Sumber](https://ioinformatic.org/index.php/JAIEA/article/view/1033)
9. **Anand Prakash Shukla & Suneeta Agarwal (2014), “An Enhanced Cellular Automata based Scheme for Noise Filtering.”** Menguji beberapa filter standar termasuk median dan Gaussian serta melaporkan PSNR dan MSSIM/SSIM untuk noise salt-and-pepper dan Gaussian. DOI: https://doi.org/10.14257/ijsip.2014.7.4.23. [PDF sumber](https://article.nadiapub.com/IJSIP/vol7_no4/23.pdf)
10. **Dr. Senthil Vadivu M (2022), “Evaluation of Image Denoising Filters.”** Ulasan/perbandingan metode linear dan non-linear untuk beberapa noise, termasuk salt-and-pepper dan Gaussian, dengan PSNR dan MSE. DOI: https://doi.org/10.17148/IJARCCE.2022.11219. [Sumber/PDF](https://ijarcce.com/wp-content/uploads/2022/03/IJARCCE.2022.11219.pdf)

## Saran urutan membaca

- Mulai dari nomor **2** untuk gambaran perbandingan median dan Gaussian.
- Baca nomor **1** dan **6** untuk memahami adaptive median/adaptive weighting.
- Baca nomor **4** untuk memahami SSIM; PSNR dibahas bersama MSE di paper perbandingan.
- Gunakan nomor **8** sebagai contoh studi yang sangat dekat dengan topik proyek.

Semua PDF pada folder ini diperoleh dari tautan sumber terbuka yang dicantumkan. Hak cipta dan lisensi tetap mengikuti masing-masing penerbit/penulis. Daftar ini untuk bacaan awal, bukan jaminan semua sumber memiliki kualitas/metode setara; periksa metodologi dan tahun terbit sebelum dijadikan landasan utama.
