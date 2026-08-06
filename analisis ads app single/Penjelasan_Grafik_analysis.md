# Panduan Membaca Grafik Analisis Meta Ads

Script analisis ini akan menghasilkan dua buah file gambar grafik di dalam folder `analysis_output/`, yaitu `grafik_analisis_ads.png` dan `grafik_detail.png`. Dokumen ini bertujuan untuk menjelaskan cara membaca dan menginterpretasikan visualisasi data tersebut untuk keperluan evaluasi bisnis.

---

## 1. Grafik Utama (`grafik_analisis_ads.png`)
File gambar ini merupakan kompilasi dari 4 grafik utama (2 baris x 2 kolom) yang saling berkaitan. Fokus utamanya adalah memvisualisasikan rasio keseimbangan pengeluaran uang iklan (Spending) melawan hasil pengiriman paket (Resi & KG).

### A. Kiri Atas: "TTK & KG vs Spending per Minggu"
**Fokus Utama:** Mengevaluasi sejauh mana biaya mendatangkan hasil secara absolut per minggu.
- **Batang Biru:** Mewakili jumlah Resi (TTK) yang didapat minggu tersebut.
- **Batang Hijau:** Mewakili total bobot paket (KG) yang masuk.
- **Garis Merah ber-titik:** Mewakili nominal Pengeluaran Iklan (Spending) dalam skala Juta Rupiah.
- **Garis Putus-putus Merah vertikal dengan label "OFF":** Menandakan minggu di mana mesin iklan Anda sengaja dimatikan (jeda).
- **Cara Baca:**
  Pergerakan garis merah dan tingginya batang biru/hijau idealnya harus seirama. Jika garis merah di suatu minggu melonjak (pengeluaran besar) namun batang biru/hijaunya bantet (kecil), itu mengindikasikan bahwa performa iklan minggu tersebut sangat merugi. Sebaliknya, saat melewati garis "OFF", Anda dapat melihat langsung secara nyata seberapa tajam penurunan omzet resi Anda ketika bensin iklan dihentikan.

### B. Kanan Atas: "Biaya per Resi (Cost per TTK) per Minggu"
**Fokus Utama:** Mengecek level boros / efisiennya biaya akuisisi pelanggan dari waktu ke waktu.
- **Warna Batang Hijau:** Menandakan efisiensi (**BAGUS**). Berarti biaya untuk mendapatkan 1 resi pada minggu itu lebih murah (atau sama dengan) batas toleransi rata-rata.
- **Warna Batang Oranye/Kuning:** Menandakan pemborosan (**BURUK**). Berarti Anda membayar Meta Ads terlampau mahal dari biasanya hanya demi secarik resi.
- **Garis Merah Horisontal:** Garis lurus putus-putus mendatar ini adalah garis patokan (Average nilai rata-rata keseluruhan).
- **Garis Titik-Titik Biru Tua:** Ini adalah "Garis Tren Regresi". Jika garis ini terlihat makin menurun meluncur ke arah kanan, ini adalah hal yang luar biasa positif! Artinya, semakin lama iklan Anda menyala, algoritmanya semakin pintar menemukan audiens dengan harga akuisisi resi yang makin murah.

### C. Kiri Bawah: "Biaya per KG per Minggu"
**Fokus Utama:** Sama dengan grafik di atas, namun dievaluasi berdasarkan berat barang.
- Menggunakan konsep psikologi warna yang sama (Hijau = Murah/Sehat, Oranye = Mahal/Boros).
- **Cara Baca Taktikal:** Jika Anda mendapati batang "Cost per TTK" berwarna oranye (mahal), TAPI di saat yang sama batang "Cost per KG"-nya berwarna Hijau (murah)... maka santai saja! Itu berarti, minggu tersebut iklan Anda sukses menarik pelanggan pengirim kargo berat bervolume raksasa (meski jumlah resinya sedikit).

### D. Kanan Bawah: "Cost/TTK vs Cost/KG per Bulan"
**Fokus Utama:** Rangkuman evaluasi eksekutif per penutup bulan.
- **Format:** Bar chart (diagram batang) sederhana yang bersanding membandingkan bulan-bulan performa.
- **Cara Baca:**
  Ini untuk di-review akhir bulan. Cukup cari bulan mana yang puncak batang birunya paling rendah. Itulah bulan juara di mana operasional periklanan Anda paling maksimal dan efisien.

---

## 2. Grafik Detail (`grafik_detail.png`)
File gambar kedua ini sifatnya melengkapi, dengan dua panel grafik yang ditujukan untuk mengetahui kesehatan materi kreatif (foto/video iklan) dan memahami tabiat bentuk paketan yang paling laris dikirim.

### A. Kiri: "Views & Click-Through Rate (CTR)"
**Fokus Utama:** Mendiagnosis fenomena Kejenuhan Materi Iklan (*Creative Fatigue*).
- **Batang Ungu tebal:** Menunjukkan seberapa masif iklan Anda menampakkan diri di HP orang (Views/Impressions).
- **Garis Kotak Merah Muda (Pink):** Persentase CTR (Tingkat Ketertarikan/Klik).
- **Cara Baca & Alarm Bahaya:**
  Idealnya, saat pandangan (Views) mendaki, garis klik (CTR) ikut merangkak stabil. **Hati-hati** bila terjadi anomali di mana jumlah tayangan (ungu) sedang gencar dinaikkan tapi persentase CTR (pink) justru **merosot turun menukik**. 
  Ini sering disebut *Creative Fatigue*. Artinya gambar atau video promo Anda sudah terlalu sering lewat dan membosankan, sehingga audiens merasa jengah dan langsung melewatinya. Solusinya tak lain dan tak bukan adalah mengganti, mendesain ulang, dan meremajakan materi kreatif iklan Anda sebelum uangnya hangus sia-sia.

### B. Kanan: "Korelasi TTK vs KG"
**Fokus Utama:** Menebak karakteristik paket pelanggan (Prediksi Kestabilan Bobot).
- **Format:** *Scatter Plot* (Titik acak yang ditabur) beserta garis bantu biru di perpisahannya. Sumbu vertikal mewakili berat, sumbu horizontal mewakili resi.
- **Cara Baca:**
  Semakin pola titik-titik tersebut mengantri merapatkan diri dan menyusun garis lurus mendaki (diiringi dengan label nilai r=mendekati 1.00), itu berarti profil paket kiriman bisnis Anda sungguh sangat kokoh nan konsisten—tiap kali ada kenaikan resi, otomatis diikuti secara pasti penambahan KG proporsional (bukan barang kosongan).
  Namun, jika polanya menyebar layaknya pecahan kaca berserakan tak beraturan, ini mengisyaratkan tingginya fluktuasi orderan Anda; pelanggan kerap mengirimkan paket bermacam-macam bentuk yang sangat "random" besar/kecilnya tiap minggu.
