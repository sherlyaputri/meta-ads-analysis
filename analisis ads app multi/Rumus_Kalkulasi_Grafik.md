# Detail Penjelasan Rumus Kalkulasi Grafik Analisis Meta Ads

Secara garis besar, hampir semua pemahaman Anda sudah **BENAR**. Berikut adalah rincian lengkap dari setiap grafik, termasuk perbaikan pada bagian perhitungan rata-rata (CTR & CVR) agar lebih presisi.

---

## BAGIAN 1: GRAFIK UTAMA (SPEND, TTK, KG)

**1. Grafik Total TTK (Resi) per Minggu**
*   **Tebakan Anda:** *Diambil dari sum TTK per minggu.*
*   **Status:** **BENAR 100%.**
*   **Formula:** Menjumlahkan (`sum`) seluruh nilai TTK dari semua lokasi/region pada minggu yang sama.

**2. Total Kontribusi Resi (TTK) per Lokasi**
*   **Tebakan Anda:** *Diambil dari sum total TTK per lokasi.*
*   **Status:** **BENAR 100%.**
*   **Formula:** Menjumlahkan (`sum`) nilai TTK per lokasi dari awal hingga akhir periode.

**3. Efisiensi Biaya per Lokasi (Cost per TTK)**
*   **Tebakan Anda:** *Diambil dari spend/cost yang dikeluarkan dibagi jumlah TTK (sum).*
*   **Status:** **BENAR 100%.**
*   **Formula:** `(Total Actual Spend di suatu lokasi) / (Total TTK di lokasi tersebut)`
*   *Catatan:* Tidak dihitung dari rata-rata *Cost per TTK* harian/mingguan (karena rata-rata dari rata-rata tidak akurat), melainkan di-sum dulu pengeluarannya baru dibagi total resinya.

**4. Cost per TTK per Bulan**
*   **Tebakan Anda:** *Diambil dari sum cost per bulan dibagi sum TTK per bulan.*
*   **Status:** **BENAR 100%.**
*   **Formula:** `(Total Actual Spend di bulan tersebut) / (Total TTK di bulan tersebut)`

---

## BAGIAN 2: KESEHATAN KONTEN & INTERAKSI IKLAN

**5. Funnel Konversi Keseluruhan**
*   **Tebakan Anda:** *Diambil dari sum Views, sum Link Clicks, dan sum TTK.*
*   **Status:** **BENAR 100%.**
*   **Formula:** Menyandingkan 3 angka global dari seluruh data: Total *Views* ➔ Total *Link Clicks* ➔ Total *TTK*.

**6. Tren Kesehatan Konten Mingguan (Garis)**
*   **Tebakan Anda:** *Diambil dari sum CTR/Link Clicks compare dengan CVR/jumlah TTK.*
*   **Status:** **ADA KOREKSI SEDIKIT.** 
*   **Formula Sebenarnya:** Anda tidak boleh me-sum persentase (sum CTR/sum CVR). Algoritma menghitungnya dengan me-sum angka mentah per minggu terlebih dahulu, baru dikonversi menjadi persentase:
    *   **CTR Mingguan:** `(Sum Link Clicks minggu tsb / Sum Views minggu tsb) × 100%`
    *   **CVR Mingguan:** `(Sum TTK minggu tsb / Sum Link Clicks minggu tsb) × 100%`

**7. Interaksi Iklan vs Volume Pengiriman (Titik-Titik / Scatter Plot)**
*   **Tebakan Anda:** *Diambil dari perbandingan Total KG dengan jumlah Link Clicks.*
*   **Status:** **BENAR 100%.**
*   **Formula:** 
    *   Sumbu-X (Mendatar) mewakili **Sum Link Clicks per lokasi**.
    *   Sumbu-Y (Vertikal) mewakili **Sum KG per lokasi**.
    *   Tujuannya untuk melihat apakah semakin banyak orang yang klik iklan (Interaksi), berbanding lurus dengan besarnya berat barang yang dikirim (Volume).

**8. Kesehatan Konten: CTR vs CVR per Lokasi (Sebaran Kuadran)**
*   **Tebakan Anda:** *Diambil dari sum CTR dan jumlah CVR per lokasi.*
*   **Status:** **ADA KOREKSI SEDIKIT.**
*   **Formula Sebenarnya:** Sama seperti poin 6, kita tidak menjumlahkan nilai persentasenya. Script menjumlahkan dulu interaksinya per lokasi, lalu dibuat persentase:
    *   **Sumbu-X (CTR Lokasi):** `(Sum Link Clicks lokasi tsb / Sum Views lokasi tsb) × 100%`
    *   **Sumbu-Y (CVR Lokasi):** `(Sum TTK lokasi tsb / Sum Link Clicks lokasi tsb) × 100%`
    *   **Ukuran Bulatan (Titik):** Besarnya bulatan mewakili Total Pengeluaran (Spend) di daerah tersebut.
    *   **Warna Bulatan:** Gelap terangnya warna mewakili jumlah Resi (TTK). Semakin terang (Kuning/Hijau) berarti semakin banyak TTK.
