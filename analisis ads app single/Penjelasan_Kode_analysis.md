# Penjelasan Kode: `analysis_fixed.py`

File `analysis_fixed.py` adalah script Python yang dirancang untuk menganalisis data performa Meta Ads secara otomatis. Script ini membersihkan data mentah, menghitung berbagai metrik efektivitas (seperti biaya per resi dan per KG), mengukur tren, membuat laporan tertulis, dan menghasilkan visualisasi grafik.

Berikut adalah penjelasan detail untuk setiap bagian kode, fungsi, dan cara perhitungannya.

---

## 1. Import Library & Persiapan Awal
Di bagian teratas (baris 14-26), script mengimpor beberapa *library* penting:
- `pandas (pd)`: Untuk manipulasi dan analisis data (membaca file Excel/CSV, membersihkan kolom, manipulasi baris, dan menghitung agregasi).
- `numpy (np)`: Untuk komputasi numerik matematis (seperti menghitung regresi linear untuk tren, rata-rata, dan menangani nilai kosong/NaN).
- `matplotlib.pyplot (plt)` & `matplotlib.dates (mdates)`: Untuk membuat visualisasi gambar grafik (bar chart, line chart, scatter plot).
- `pathlib.Path`: Untuk menangani path file secara sistematis sehingga script dapat dijalankan di OS apa saja (Windows/Mac) tanpa masalah.
- Kode `sys.stdout = io.TextIOWrapper(...)` bertujuan mengubah encoding teks di terminal menjadi UTF-8 agar karakter tertentu (seperti simbol Rupiah) tidak menyebabkan error saat diprint.

## 2. Bagian 1: Konfigurasi (Baris 28-39)
Mengatur di mana letak file sumber data dan direktori penyimpanannya.
- `FILE_PATH`: Menunjuk secara dinamis ke letak file data sumber di folder yang sama (saat ini menunjuk ke `master_ads.xlsx`).
- `OUTPUT_DIR`: Menentukan folder bernama `analysis_output/` tempat disimpannya laporan, grafik, dan CSV hasil olahan. `OUTPUT_DIR.mkdir(exist_ok=True)` akan otomatis membuat folder ini jika belum ada.

## 3. Bagian 2: Membaca Data Excel (Baris 40-46)
Menggunakan fungsi `pd.read_excel(FILE_PATH)` untuk memuat data dari file sumber. Proses ini mengambil keseluruhan baris dan kolom yang terisi dan menyimpannya dalam bentuk struktur tabel virtual (disebut `DataFrame` atau `df`).

## 4. Bagian 3: Data Cleaning / Pembersihan Data (Baris 47-107)
Data mentah (raw data) sering kali formatnya tidak konsisten atau kotor. Proses pembersihan data mutlak diperlukan agar kalkulasi angka tidak error.
- **Memisahkan Tanggal:** Kolom `Week` (misalnya string `"04/10/25 - 10/10/25"`) dipecah (menggunakan fungsi `.str.split('-')`) menjadi kolom `Tanggal_Mulai_str` dan `Tanggal_Akhir_str`. Setelahnya, kedua kolom dikonversi (menggunakan `pd.to_datetime`) menjadi objek `DateTime` resmi agar Python mengerti urutan waktu.
- **Fungsi `clean_currency(val)`:**
  Fungsi kustom (custom function) ini bertugas membersihkan teks nilai uang seperti `"Rp 2,005,129"` menjadi tipe float `2005129.0`. Prosesnya meliputi: menghapus kata "Rp" / "rp", menghilangkan spasi kosong, dan memanipulasi posisi tanda koma (`,`) serta titik (`.`) sesuai kaidah ribuan desimal, sehingga Python bisa menjumlahkannya.
- **Pembersihan Kolom Angka (Numerik):**
  Kolom-kolom teks seperti *Views, Viewers, Link Clicks, Jumlah TTK, Jumlah KG* dipaksa menjadi tipe angka (menggunakan `pd.to_numeric()`) sambil membuang koma ribuan (contoh: "1,200" diubah menjadi `1200`).
- **Set Index & Status Iklan:**
  - `df.set_index('Tanggal_Mulai')`: Menjadikan Tanggal Mulai sebagai basis penomoran (index), sehingga data terurut berdasar waktu.
  - Kolom bantuan `Iklan_Aktif`: Akan bernilai `True` jika `Actual_Spend` (biaya iklan) lebih besar dari 0, dan sebaliknya bernilai `False` jika tidak ada biaya yang keluar.

## 5. Bagian 4: Menghitung Metrik (Baris 108-186)
Di sinilah perhitungan bisnis utama terjadi:
- **Filtering:** Membuat tabel pecahan `df_ttk` (minggu yang punya angka Resi > 0) dan `df_kg` (minggu yang punya angka KG > 0).
- **Sum & Mean:** Semua kolom angka dijumlah dengan metode `.sum()` (seperti Total Resi & Total Views). Untuk mencari rata-rata per minggu, script menggunakan `.mean()`.
- **Cost per TTK (Biaya per Resi) & Cost per KG:**
  - *Metrik Periode (Average Keseluruhan)*: `spend_ttk_period / total_ttk`.
  - *Metrik Mingguan*: Di dalam perulangan mingguan, dihitung `Actual_Spend / TTK` sehingga per minggu Anda tahu biayanya berapa.
- **CTR (Click-Through Rate):**
  - Rumusnya: `(Link_Clicks / Views) * 100`. Metrik ini mendeskripsikan persentase jumlah orang yang mengklik link setelah iklannya muncul (view).

### Fungsi `calc_trend(series)`
Fungsi ini menghitung apakah tren angka (seperti tren jumlah Resi atau Cost per TTK) itu sedang **NAIK, TURUN, atau STABIL**.
- **Cara Perhitungan (Regresi Linear):** Script menggunakan fungsi matematis `np.polyfit(x, y, 1)` untuk menghasilkan kemiringan (slope) garis trend dengan polinomial berderajat 1 (garis linear / lurus). 
- **Persentase Perubahan:** Jika nilai awal data dibandingkan terhadap kemiringan garis hingga akhir, didapat persentase `pct_change`.
- Apabila perubahan kurang dari 5% baik ke atas maupun ke bawah, script mengkategorikannya sebagai `[STABIL]`. Jika > 5% ke atas `[NAIK]`, dan sebaliknya `[TURUN]`.

### Hitungan Agregasi Bulanan
`df_aktif.groupby('Bulan')` mengelompokkan data berdasarkan indeks bulannya. Kemudian script menggunakan `.agg()` untuk melakukan perhitungan (SUM) atas pengeluaran, TTK, views, dll di setiap bulannya.

## 6. Bagian 5: Susun & Cetak Laporan Teks (Baris 187-355)
Bagian ini menggunakan perintah `print()` yang dibungkus fungsi khusus bernama `p(text)` untuk mem-print teks ke layar (terminal) SEKALIGUS menambahkannya ke sebuah list (`report_lines`).
Beberapa informasi kunci dalam teks laporan yang ter-generate:
- **A. Ringkasan Keseluruhan**: Total pengeluaran, total traffic, dll.
- **B. Efisiensi Biaya**: Menampilkan rata-rata (Cost per TTK/KG) yang didapat dari Bagian 4. Di sini ada logika pembanding otomatis: *Jika Profit Resi > Biaya TTK, berarti strategi iklan Worth It.*
- **C. Analisis Tren**: Menuliskan kata `[NAIK] / [TURUN]` hasil kalkulasi regresi linear.
- **D. Performa Per Bulan**: Menampilkan tabel sederhana per bulan, diakhiri dengan logika `.idxmin()` dan `.idxmax()` untuk mendeteksi bulan paling hemat & bulan paling boros Cost per TTK nya.
- **E. Dampak ON/OFF Iklan**: Melakukan perulangan (`for loop`) pada baris iklan mati. Script mengambil baris seminggu sebelumnya (`pos - 1`) dan seminggu sesudahnya (`pos + 1`), lalu menghitung lonjakan angka Resinya.
- **F. Rekomendasi Pintar**: Memadukan aturan percabangan (if-else). Jika tren 'Cost per TTK' dinyatakan `NAIK`, maka akan muncul teks peringatan otomatis ("Pertimbangkan: refresh creative...").

Setelah list penuh, script menggunakan `open(report_path, 'w')` dan fungsi `.write()` untuk menyimpan semua baris kalimat ke dalam file `laporan_analisis_ads.txt`.

## 7. Bagian 6: Visualisasi Grafik (Baris 356-520)
Script menggunakan `matplotlib` untuk "menggambar" data menjadi grafik `PNG`:
- `plt.subplots(2, 2)`: Mendefinisikan canvas gambar berskala 2x2 letak (total 4 grafik gabungan utama).
- **Grafik 1 (TTK/KG vs Spend):** Memakai sumbu ganda (`twinx`). Sumbu kiri menumpuk bar chart Resi (biru) dan KG (hijau), sedangkan sumbu kanan (garis merah) menimpa dengan jumlah uang yang dihabiskan. Ini membuat perbandingan pertumbuhan Resi dan Pengeluaran terlihat kasatmata.
- **Grafik 2 & 3 (Cost per TTK/KG):** Digambarkan menggunakan bar chart. Pewarnaan dihitung otomatis (jika biayanya di bawah rata-rata diwarnai hijau, jika boros diwarnai oranye/kuning). Sebuah garis tren putus-putus biru tua diselipkan dengan mengambil nilai fungsi polinomial tadi (`p_trend = np.poly1d(z)`).
- **Grafik 4 (Perbandingan Bulanan):** Menggabungkan 2 bar chart secara berdampingan (side-by-side) untuk menunjukkan perbedaan Cost/TTK (biru) vs Cost/KG (hijau) di per bulannya.

**Grafik Detail (`grafik_detail.png`):**
- Menggambar Views vs CTR menggunakan sumbu ganda.
- Menampilkan grafik *Scatter Plot* (titik sebaran). Ini disertai rumus Korelasi Pearson (`.corr()`). Korelasi menghitung kedekatan/hubungan matematika antara besaran Resi dengan besar KG yang terjadi. Nilai $r$ yang mendekati 1 menandakan hubungan positif yang sangat kuat.

## 8. Export Data Bersih (Baris 522-527)
Tahapan finalisasi. Seluruh data mentah yang telah diparsing, dibersihkan format uangnya, dipecah tanggalnya, ditambahkan kolom Cost_per_TTK/KG, disimpan kembali menjadi satu tabel rapi menggunakan `df.to_csv()` ke bentuk file bernama `data_bersih.csv`. Data ini kini sudah aman untuk dibaca ulang sistem lain, atau dimanfaatkan lebih jauh dengan aplikasi semacam Tableau/Looker Studio.
