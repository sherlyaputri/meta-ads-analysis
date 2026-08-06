"""
==========================================================
ANALISIS TREN META ADS - PENGIRIMAN BARANG LUAR NEGERI
(Wahana Express)
==========================================================
Script ini menganalisis data Meta Ads dari file master_ads.xlsx
untuk menentukan efektivitas iklan berdasarkan:
- Biaya per TTK (Cost per Resi)
- Biaya per KG
- Tren mingguan dan bulanan
- Perbandingan periode iklan ON vs OFF
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. KONFIGURASI
# ==========================================
FILE_PATH = Path(__file__).parent / 'data_malaysia.xlsx'
OUTPUT_DIR = Path(__file__).parent / 'analysis_output'
OUTPUT_DIR.mkdir(exist_ok=True)

print("=" * 60)
print("ANALISIS TREN META ADS - WAHANA EXPRESS")
print("Pengiriman Barang Luar Negeri")
print("=" * 60)

# ==========================================
# 2. BACA DATA DARI EXCEL
# ==========================================
print("\n[1/5] Membaca data dari excel...")

temp_df = pd.read_excel(FILE_PATH, header=None)
header_row = 0
for i in range(min(10, len(temp_df))):
    row_vals = [str(v).lower() for v in temp_df.iloc[i].values]
    if 'region' in row_vals or 'campaign title' in row_vals or 'date' in row_vals or 'week' in row_vals:
        header_row = i
        break

df = pd.read_excel(FILE_PATH, header=header_row)
print(f"   Jumlah baris mentah: {len(df)}")

# ==========================================
# 3. DATA CLEANING & AGGREGATION
# ==========================================
print("\n[2/5] Membersihkan data...")

# Standardize column names if it's the new format
rename_map = {
    'Date': 'Week',
    'Actual Spend (aft. tax)': 'Actual Spend',
    'Budget per-week (bef. tax)': 'Total Budget',
    'Views': 'Total Views',
    'Viewers': 'Total Viewers',
    'Link Clicks': 'Total Link Clicks',
    'Total TTK': 'Jumlah TTK',
    'Total KG': 'Jumlah KG'
}
df = df.rename(columns=rename_map)

# Hapus baris kosong yang tidak punya Week
if 'Week' in df.columns:
    df = df.dropna(subset=['Week'])

def clean_currency(val):
    if pd.isna(val) or str(val).strip() == '' or str(val).strip() == 'nan':
        return np.nan
    s = str(val).replace('Rp', '').replace('rp', '').replace(' ', '').replace('\xa0', '')
    if ',' in s and '.' in s:
        if s.rindex(',') > s.rindex('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        if s.count(',') > 1:
            s = s.replace(',', '')
        else:
            parts = s.split(',')
            if len(parts[1]) == 3:
                s = s.replace(',', '')
            else:
                s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return np.nan

if 'Actual Spend' in df.columns:
    df['Actual_Spend'] = df['Actual Spend'].apply(clean_currency)
else:
    df['Actual_Spend'] = np.nan

if 'Total Budget' in df.columns:
    df['Budget'] = df['Total Budget'].apply(clean_currency)
else:
    df['Budget'] = np.nan

numeric_cols_map = {
    'Total Views': 'Views',
    'Total Viewers': 'Viewers',
    'Total Link Clicks': 'Link_Clicks',
    'Jumlah TTK': 'TTK',
    'Jumlah KG': 'KG'
}
for orig_col, new_col in numeric_cols_map.items():
    if orig_col in df.columns:
        df[new_col] = pd.to_numeric(
            df[orig_col].astype(str).str.replace(',', '').str.replace(' ', ''),
            errors='coerce'
        )
    else:
        df[new_col] = np.nan

if 'Week' in df.columns:
    # Agregasi data jika ada duplikat Week (misal dari beberapa region/lokasi)
    agg_dict = {
        'Actual_Spend': 'sum',
        'Budget': 'max',
        'Views': 'sum',
        'Viewers': 'sum',
        'Link_Clicks': 'sum',
        'TTK': 'sum',
        'KG': 'sum'
    }
    
    def sum_min1(x): 
        return x.sum(min_count=1)
        
    agg_funcs = {}
    for k, v in agg_dict.items():
        if k in df.columns:
            agg_funcs[k] = sum_min1 if v == 'sum' else v
            
    if len(agg_funcs) > 0:
        df = df.groupby('Week', as_index=False).agg(agg_funcs)

    df['Week_str'] = df['Week'].astype(str)
    df['Tanggal_Mulai_str'] = df['Week_str'].str.split('-').str[0].str.strip()
    df['Tanggal_Akhir_str'] = df['Week_str'].str.split('-').str[-1].str.strip()
    df = df[df['Tanggal_Mulai_str'].str.match(r'^\d{2}/\d{2}/\d{2}$', na=False)].copy()
    df['Tanggal_Mulai'] = pd.to_datetime(df['Tanggal_Mulai_str'], format='%d/%m/%y')
    df['Tanggal_Akhir'] = pd.to_datetime(df['Tanggal_Akhir_str'], format='%d/%m/%y')
    
    df.set_index('Tanggal_Mulai', inplace=True)
    df = df.sort_index()

df['Iklan_Aktif'] = df['Actual_Spend'].notna() & (df['Actual_Spend'] > 0)

print(f"   Jumlah minggu data valid: {len(df)}")
print(f"   Periode: {df.index.min().strftime('%d/%m/%Y')} - {df.index.max().strftime('%d/%m/%Y')}")
print(f"   Minggu iklan aktif: {df['Iklan_Aktif'].sum()}")
print(f"   Minggu iklan mati: {(~df['Iklan_Aktif']).sum()}")

# ==========================================
# 4. HITUNG METRIK
# ==========================================
print("\n[3/5] Menghitung metrik...")

df_aktif = df[df['Iklan_Aktif']].copy()

# --- Metrik yang ada TTK ---
df_ttk = df_aktif[df_aktif['TTK'].notna() & (df_aktif['TTK'] > 0)].copy()
# --- Metrik yang ada KG ---
df_kg = df_aktif[df_aktif['KG'].notna() & (df_aktif['KG'] > 0)].copy()

# Keseluruhan
total_spend = df_aktif['Actual_Spend'].sum()
total_views = df_aktif['Views'].sum()
total_viewers = df_aktif['Viewers'].sum()
total_clicks = df_aktif['Link_Clicks'].sum()

# TTK
total_ttk = df_ttk['TTK'].sum()
spend_ttk_period = df_ttk['Actual_Spend'].sum()
avg_ttk_per_week = df_ttk['TTK'].mean()
avg_cost_per_ttk = spend_ttk_period / total_ttk if total_ttk > 0 else 0

# KG
total_kg = df_kg['KG'].sum()
spend_kg_period = df_kg['Actual_Spend'].sum()
avg_kg_per_week = df_kg['KG'].mean()
avg_cost_per_kg = spend_kg_period / total_kg if total_kg > 0 else 0

# Hitung per minggu
df_ttk['Cost_per_TTK'] = df_ttk['Actual_Spend'] / df_ttk['TTK']
df_kg['Cost_per_KG'] = df_kg['Actual_Spend'] / df_kg['KG']
df_aktif['CTR'] = (df_aktif['Link_Clicks'] / df_aktif['Views']) * 100

# Perhitungan tren (regresi linear)
def calc_trend(series):
    valid = series.dropna()
    if len(valid) < 3:
        return {'slope': 0, 'direction': 'Tidak cukup data', 'pct_change': 0}
    x = np.arange(len(valid))
    y = valid.values
    if np.std(x) == 0 or np.std(y) == 0:
        return {'slope': 0, 'direction': '[STABIL]', 'pct_change': 0}
    coeffs = np.polyfit(x, y, 1)
    slope = coeffs[0]
    first_val = y[0] if y[0] != 0 else 1
    pct_change = (slope * len(valid) / abs(first_val)) * 100
    if abs(pct_change) < 5:
        direction = '[STABIL]'
    elif pct_change > 0:
        direction = '[NAIK]'
    else:
        direction = '[TURUN]'
    return {'slope': slope, 'direction': direction, 'pct_change': pct_change}

trend_ttk = calc_trend(df_ttk['TTK'])
trend_kg = calc_trend(df_kg['KG'])
trend_spend = calc_trend(df_aktif['Actual_Spend'])
trend_cost_per_ttk = calc_trend(df_ttk['Cost_per_TTK'])
trend_cost_per_kg = calc_trend(df_kg['Cost_per_KG'])
trend_views = calc_trend(df_aktif['Views'])
trend_ctr = calc_trend(df_aktif['CTR'])

# Bulanan
df_aktif['Bulan'] = df_aktif.index.to_period('M')
monthly = df_aktif.groupby('Bulan').agg({
    'Actual_Spend': 'sum',
    'TTK': 'sum',
    'KG': 'sum',
    'Views': 'sum',
    'Viewers': 'sum',
    'Link_Clicks': 'sum'
})
monthly['Cost_per_TTK'] = monthly.apply(
    lambda r: r['Actual_Spend'] / r['TTK'] if r['TTK'] > 0 else np.nan, axis=1)
monthly['Cost_per_KG'] = monthly.apply(
    lambda r: r['Actual_Spend'] / r['KG'] if r['KG'] > 0 else np.nan, axis=1)

# ==========================================
# 5. CETAK LAPORAN
# ==========================================
print("\n[4/5] Menyusun laporan...\n")

report_lines = []
def p(text=""):
    print(text)
    report_lines.append(text)

p("=" * 65)
p("           LAPORAN ANALISIS META ADS")
p("        WAHANA EXPRESS - PENGIRIMAN LUAR NEGERI")
p("=" * 65)

p(f"\nPeriode Data  : {df.index.min().strftime('%d %b %Y')} - {df.index.max().strftime('%d %b %Y')}")
p(f"Total Minggu  : {len(df)} minggu ({df['Iklan_Aktif'].sum()} aktif, {(~df['Iklan_Aktif']).sum()} mati)")

# --- A. RINGKASAN ---
p("\n" + "-" * 65)
p("A. RINGKASAN KESELURUHAN")
p("-" * 65)
p(f"  Total Spending Iklan    : Rp {total_spend:>15,.0f}")
p(f"  Total Views             : {total_views:>15,.0f}")
p(f"  Total Viewers           : {total_viewers:>15,.0f}")
p(f"  Total Link Clicks       : {total_clicks:>15,.0f}")
p(f"  Total TTK (Resi)        : {total_ttk:>15,.0f}  ({len(df_ttk)} minggu ada data)")
p(f"  Total KG Pengiriman     : {total_kg:>15,.0f}  ({len(df_kg)} minggu ada data)")

# --- B. EFISIENSI BIAYA ---
p("\n" + "-" * 65)
p("B. EFISIENSI BIAYA (Spend vs TTK vs KG)")
p("-" * 65)
p(f"  Cost per TTK (rata-rata)  : Rp {avg_cost_per_ttk:>12,.0f} /resi")
p(f"  Cost per KG  (rata-rata)  : Rp {avg_cost_per_kg:>12,.0f} /kg")
p(f"  Rata-rata TTK/Minggu      : {avg_ttk_per_week:>12.1f} resi")
p(f"  Rata-rata KG/Minggu       : {avg_kg_per_week:>12.1f} kg")
p(f"  Rata-rata Spend/Minggu    : Rp {df_aktif['Actual_Spend'].mean():>12,.0f}")
p("")

# Evaluasi efisiensi
p("  EVALUASI:")
if avg_cost_per_ttk > 0:
    p(f"  - Setiap 1 resi (TTK) butuh biaya iklan Rp {avg_cost_per_ttk:,.0f}")
if avg_cost_per_kg > 0:
    p(f"  - Setiap 1 kg pengiriman butuh biaya iklan Rp {avg_cost_per_kg:,.0f}")
p(f"  - Untuk menilai WORTH IT atau tidak:")
p(f"    Bandingkan Cost/TTK (Rp {avg_cost_per_ttk:,.0f}) dengan profit per resi Anda.")
p(f"    Bandingkan Cost/KG (Rp {avg_cost_per_kg:,.0f}) dengan profit per kg Anda.")
p(f"    Jika profit per resi > Rp {avg_cost_per_ttk:,.0f} --> WORTH IT")
p(f"    Jika profit per resi < Rp {avg_cost_per_ttk:,.0f} --> TIDAK WORTH IT")

# --- C. TREN ---
p("\n" + "-" * 65)
p("C. ANALISIS TREN")
p("-" * 65)
p(f"  Jumlah TTK    : {trend_ttk['direction']} ({trend_ttk['pct_change']:+.1f}%)")
p(f"  Jumlah KG     : {trend_kg['direction']} ({trend_kg['pct_change']:+.1f}%)")
p(f"  Total Spend   : {trend_spend['direction']} ({trend_spend['pct_change']:+.1f}%)")
p(f"  Cost per TTK  : {trend_cost_per_ttk['direction']} ({trend_cost_per_ttk['pct_change']:+.1f}%)")
p(f"  Cost per KG   : {trend_cost_per_kg['direction']} ({trend_cost_per_kg['pct_change']:+.1f}%)")
p(f"  Total Views   : {trend_views['direction']} ({trend_views['pct_change']:+.1f}%)")
p(f"  CTR           : {trend_ctr['direction']} ({trend_ctr['pct_change']:+.1f}%)")

# --- D. PERFORMA PER BULAN ---
p("\n" + "-" * 65)
p("D. PERFORMA PER BULAN")
p("-" * 65)
p(f"  {'Bulan':<10} {'Spend':>15} {'TTK':>6} {'KG':>7} {'Cost/TTK':>12} {'Cost/KG':>12}")
p(f"  {'-'*10} {'-'*15} {'-'*6} {'-'*7} {'-'*12} {'-'*12}")
for idx, row in monthly.iterrows():
    ttk_str = f"{row['TTK']:>6.0f}" if row['TTK'] > 0 else "     -"
    kg_str = f"{row['KG']:>7.0f}" if row['KG'] > 0 else "      -"
    cpt_str = f"Rp {row['Cost_per_TTK']:>9,.0f}" if pd.notna(row['Cost_per_TTK']) else "          -"
    cpk_str = f"Rp {row['Cost_per_KG']:>9,.0f}" if pd.notna(row['Cost_per_KG']) else "          -"
    p(f"  {str(idx):<10} Rp {row['Actual_Spend']:>12,.0f} {ttk_str} {kg_str} {cpt_str} {cpk_str}")

# Bulan terbaik/terburuk berdasarkan Cost per TTK
monthly_with_ttk = monthly[monthly['Cost_per_TTK'].notna()].copy()
if len(monthly_with_ttk) > 0:
    best = monthly_with_ttk['Cost_per_TTK'].idxmin()
    worst = monthly_with_ttk['Cost_per_TTK'].idxmax()
    p(f"\n  Paling efisien (Cost/TTK terendah)  : {best} (Rp {monthly_with_ttk.loc[best, 'Cost_per_TTK']:,.0f}/resi)")
    p(f"  Paling boros   (Cost/TTK tertinggi) : {worst} (Rp {monthly_with_ttk.loc[worst, 'Cost_per_TTK']:,.0f}/resi)")

# --- E. DAMPAK ON/OFF ---
p("\n" + "-" * 65)
p("E. ANALISIS DAMPAK: MINGGU IKLAN MATI")
p("-" * 65)

minggu_mati = df[~df['Iklan_Aktif']]
if len(minggu_mati) > 0:
    for idx, row in minggu_mati.iterrows():
        p(f"  [OFF] {idx.strftime('%d/%m/%Y')} - Iklan tidak aktif")

    for mati_idx in minggu_mati.index:
        pos = df.index.get_loc(mati_idx)
        if pos > 0 and pos < len(df) - 1:
            sebelum = df.iloc[pos - 1]
            sesudah = df.iloc[pos + 1]
            if pd.notna(sebelum['TTK']) and pd.notna(sesudah['TTK']):
                p(f"\n  Minggu sebelum ({df.index[pos-1].strftime('%d/%m/%Y')}): "
                  f"{sebelum['TTK']:.0f} TTK, {sebelum['KG']:.0f} KG" if pd.notna(sebelum['KG']) else
                  f"\n  Minggu sebelum ({df.index[pos-1].strftime('%d/%m/%Y')}): {sebelum['TTK']:.0f} TTK")
                p(f"  Minggu seudah ({df.index[pos+1].strftime('%d/%m/%Y')}): "
                  f"{sesudah['TTK']:.0f} TTK, {sesudah['KG']:.0f} KG" if pd.notna(sesudah['KG']) else
                  f"  Minggu sesudah ({df.index[pos+1].strftime('%d/%m/%Y')}): {sesudah['TTK']:.0f} TTK")
                change_ttk = sesudah['TTK'] - sebelum['TTK']
                pct_ttk = (change_ttk / sebelum['TTK'] * 100) if sebelum['TTK'] > 0 else 0
                p(f"  Perubahan TTK: {change_ttk:+.0f} ({pct_ttk:+.1f}%)")
else:
    p("  Semua minggu iklan aktif")

# --- F. REKOMENDASI ---
p("\n" + "-" * 65)
p("F. REKOMENDASI")
p("-" * 65)

recommendations = []

# 1. Informasi kunci
recommendations.append(f"1. ANGKA KUNCI: Biaya rata-rata Rp {avg_cost_per_ttk:,.0f} per resi (TTK)")
recommendations.append(f"   dan Rp {avg_cost_per_kg:,.0f} per KG.")
recommendations.append(f"   --> Jika profit per resi LEBIH BESAR dari Rp {avg_cost_per_ttk:,.0f}, iklan WORTH IT.")
recommendations.append(f"   --> Jika profit per resi LEBIH KECIL dari Rp {avg_cost_per_ttk:,.0f}, iklan TIDAK WORTH IT.")

# 2. Tren
if 'TURUN' in trend_cost_per_ttk['direction']:
    recommendations.append("2. [+] Cost per TTK MENURUN - iklan semakin efisien seiring waktu.")
elif 'NAIK' in trend_cost_per_ttk['direction']:
    recommendations.append("2. [!] Cost per TTK MENINGKAT - efisiensi iklan menurun.")
    recommendations.append("   --> Pertimbangkan: refresh creative, perbaiki targeting, A/B test.")
else:
    recommendations.append("2. Cost per TTK stabil.")

if 'NAIK' in trend_ttk['direction']:
    recommendations.append("3. [+] Tren TTK naik - iklan semakin efektif mendatangkan resi.")
elif 'TURUN' in trend_ttk['direction']:
    recommendations.append("3. [!] Tren TTK menurun - perlu refresh materi iklan/targeting.")
else:
    recommendations.append("3. Tren TTK stabil.")

if 'NAIK' in trend_kg['direction']:
    recommendations.append("4. [+] Tren KG naik - volume pengiriman meningkat.")
elif 'TURUN' in trend_kg['direction']:
    recommendations.append("4. [!] Tren KG menurun - volume pengiriman berkurang.")
else:
    recommendations.append("4. Tren KG stabil.")

# Data kosong warning
minggu_tanpa_ttk = df_aktif[df_aktif['TTK'].isna() | (df_aktif['TTK'] == 0)]
if len(minggu_tanpa_ttk) > 0:
    recommendations.append(f"\n   [!!] PERHATIAN: {len(minggu_tanpa_ttk)} minggu TIDAK memiliki data TTK.")
    recommendations.append("   Pastikan data TTK diisi lengkap untuk analisis yang akurat.")

for rec in recommendations:
    p(f"  {rec}")

p("\n" + "=" * 65)
p("           AKHIR LAPORAN")
p("=" * 65)

# Simpan laporan
report_path = OUTPUT_DIR / 'laporan_analisis_ads.txt'
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f"\n[SAVED] Laporan tersimpan di: {report_path}")

# ==========================================
# 6. VISUALISASI
# ==========================================
print("\n[5/5] Membuat visualisasi...")

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.size'] = 10

# === GRAFIK UTAMA (2x2) ===
fig, axes = plt.subplots(2, 2, figsize=(18, 12))
fig.suptitle('Analisis Meta Ads - Wahana Express\n(Spend vs TTK vs KG)',
             fontsize=16, fontweight='bold', y=0.98)

# Plot 1: TTK + KG vs Spending
ax1 = axes[0, 0]
color_ttk, color_kg, color_spend = '#2196F3', '#4CAF50', '#FF5722'
ax1_twin = ax1.twinx()

# Bar TTK
ax1.bar(df_ttk.index - pd.Timedelta(days=2), df_ttk['TTK'], width=4, alpha=0.7,
        color=color_ttk, label='TTK (Resi)', zorder=2)
# Bar KG (skala berbeda, tampilkan di bar kedua)
ax1.bar(df_kg.index + pd.Timedelta(days=2), df_kg['KG'], width=4, alpha=0.7,
        color=color_kg, label='KG', zorder=2)
# Line spending
ax1_twin.plot(df_aktif.index, df_aktif['Actual_Spend'] / 1_000_000,
              color=color_spend, linewidth=2, marker='o', markersize=4,
              label='Spend (Juta Rp)', zorder=3)

ax1.set_ylabel('TTK / KG', fontweight='bold')
ax1_twin.set_ylabel('Spending (Juta Rp)', color=color_spend, fontweight='bold')
ax1.set_title('TTK & KG vs Spending per Minggu', fontweight='bold')
ax1.tick_params(axis='x', rotation=45)
ax1.set_xticks(df_aktif.index)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

for mati_idx in minggu_mati.index:
    ax1.axvline(x=mati_idx, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax1.annotate('OFF', xy=(mati_idx, ax1.get_ylim()[1]*0.95),
                fontsize=7, color='red', ha='center', fontweight='bold')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=8)

# Plot 2: Cost per TTK
ax2 = axes[0, 1]
valid_cpt = df_ttk['Cost_per_TTK'].dropna()
if len(valid_cpt) > 0:
    colors_cpt = ['#4CAF50' if v <= avg_cost_per_ttk else '#FF9800' for v in valid_cpt]
    ax2.bar(valid_cpt.index, valid_cpt / 1000, width=5, color=colors_cpt, alpha=0.8)
    ax2.axhline(y=avg_cost_per_ttk / 1000, color='red', linestyle='--', linewidth=1.5,
                label=f'Rata-rata: Rp {avg_cost_per_ttk/1000:,.0f}K/resi')
    ax2.set_ylabel('Cost per TTK (Ribu Rp)', fontweight='bold')
    ax2.set_title('Biaya per Resi (Cost/TTK) per Minggu', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.set_xticks(valid_cpt.index)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

    if len(valid_cpt) >= 3:
        x_num = np.arange(len(valid_cpt))
        z = np.polyfit(x_num, valid_cpt.values / 1000, 1)
        p_trend = np.poly1d(z)
        ax2.plot(valid_cpt.index, p_trend(x_num), color='darkblue',
                 linestyle=':', linewidth=2, label=f'Tren ({trend_cost_per_ttk["direction"]})')
    ax2.legend(fontsize=9)

# Plot 3: Cost per KG
ax3 = axes[1, 0]
valid_cpk = df_kg['Cost_per_KG'].dropna()
if len(valid_cpk) > 0:
    colors_cpk = ['#4CAF50' if v <= avg_cost_per_kg else '#FF9800' for v in valid_cpk]
    ax3.bar(valid_cpk.index, valid_cpk / 1000, width=5, color=colors_cpk, alpha=0.8)
    ax3.axhline(y=avg_cost_per_kg / 1000, color='red', linestyle='--', linewidth=1.5,
                label=f'Rata-rata: Rp {avg_cost_per_kg/1000:,.0f}K/kg')
    ax3.set_ylabel('Cost per KG (Ribu Rp)', fontweight='bold')
    ax3.set_title('Biaya per KG per Minggu', fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    ax3.set_xticks(valid_cpk.index)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

    if len(valid_cpk) >= 3:
        x_num = np.arange(len(valid_cpk))
        z = np.polyfit(x_num, valid_cpk.values / 1000, 1)
        p_trend = np.poly1d(z)
        ax3.plot(valid_cpk.index, p_trend(x_num), color='darkblue',
                 linestyle=':', linewidth=2, label=f'Tren ({trend_cost_per_kg["direction"]})')
    ax3.legend(fontsize=9)

# Plot 4: Perbandingan bulanan (Cost/TTK dan Cost/KG)
ax4 = axes[1, 1]
monthly_valid = monthly[monthly['Cost_per_TTK'].notna() | monthly['Cost_per_KG'].notna()]
if len(monthly_valid) > 0:
    month_labels = [str(m) for m in monthly_valid.index]
    x_pos = np.arange(len(month_labels))
    width = 0.35

    cpt_vals = monthly_valid['Cost_per_TTK'].fillna(0) / 1000
    cpk_vals = monthly_valid['Cost_per_KG'].fillna(0) / 1000

    bars_cpt = ax4.bar(x_pos - width/2, cpt_vals, width, color='#2196F3', alpha=0.8, label='Cost/TTK (Ribu)')
    bars_cpk = ax4.bar(x_pos + width/2, cpk_vals, width, color='#4CAF50', alpha=0.8, label='Cost/KG (Ribu)')

    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(month_labels, rotation=45)
    ax4.set_ylabel('Biaya (Ribu Rp)', fontweight='bold')
    ax4.set_title('Cost/TTK vs Cost/KG per Bulan', fontweight='bold')
    ax4.legend(fontsize=9)

    for bar, val in zip(bars_cpt, cpt_vals):
        if val > 0:
            ax4.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:.0f}K', ha='center', va='bottom', fontsize=7, fontweight='bold')
    for bar, val in zip(bars_cpk, cpk_vals):
        if val > 0:
            ax4.text(bar.get_x() + bar.get_width()/2., val,
                    f'{val:.0f}K', ha='center', va='bottom', fontsize=7, fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.95])
chart_path = OUTPUT_DIR / 'grafik_analisis_ads.png'
plt.savefig(chart_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"[SAVED] Grafik tersimpan di: {chart_path}")

# === GRAFIK DETAIL ===
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
fig2.suptitle('Detail Engagement & Pengiriman', fontsize=14, fontweight='bold')

# Views & CTR
ax5 = axes2[0]
ax5_twin = ax5.twinx()
ax5.bar(df_aktif.index, df_aktif['Views'] / 1000, width=5, alpha=0.6,
        color='#9C27B0', label='Views (ribu)')
ax5_twin.plot(df_aktif.index, df_aktif['CTR'], color='#E91E63',
              linewidth=2, marker='s', markersize=4, label='CTR (%)')
ax5.set_ylabel('Views (ribu)', fontweight='bold')
ax5_twin.set_ylabel('CTR (%)', color='#E91E63', fontweight='bold')
ax5.set_title('Views & Click-Through Rate', fontweight='bold')
ax5.tick_params(axis='x', rotation=45)
ax5.set_xticks(df_aktif.index)
ax5.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
lines5a, labels5a = ax5.get_legend_handles_labels()
lines5b, labels5b = ax5_twin.get_legend_handles_labels()
ax5.legend(lines5a + lines5b, labels5a + labels5b, loc='upper right', fontsize=8)

# TTK vs KG scatter / correlation
ax6 = axes2[1]
merged = df_ttk[['TTK']].join(df_kg[['KG']], how='inner')
if len(merged) > 2:
    ax6.scatter(merged['TTK'], merged['KG'], color='#FF5722', alpha=0.7, s=60, edgecolors='white')
    # Trend line
    z = np.polyfit(merged['TTK'].values, merged['KG'].values, 1)
    p_fit = np.poly1d(z)
    x_line = np.linspace(merged['TTK'].min(), merged['TTK'].max(), 50)
    ax6.plot(x_line, p_fit(x_line), color='darkblue', linestyle='--', linewidth=1.5)
    corr = merged['TTK'].corr(merged['KG'])
    ax6.set_title(f'Korelasi TTK vs KG (r={corr:.2f})', fontweight='bold')
    ax6.set_xlabel('Jumlah TTK (Resi)', fontweight='bold')
    ax6.set_ylabel('Jumlah KG', fontweight='bold')
else:
    ax6.text(0.5, 0.5, 'Tidak cukup data\nuntuk korelasi TTK vs KG',
             ha='center', va='center', fontsize=12, transform=ax6.transAxes)
    ax6.set_title('Korelasi TTK vs KG', fontweight='bold')

plt.tight_layout()
chart2_path = OUTPUT_DIR / 'grafik_detail.png'
plt.savefig(chart2_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"[SAVED] Grafik detail tersimpan di: {chart2_path}")

# Export CSV
export_cols = ['Budget', 'Actual_Spend', 'Views', 'Viewers', 'Link_Clicks', 'TTK', 'KG', 'Iklan_Aktif']
export_cols = [c for c in export_cols if c in df.columns]
csv_path = OUTPUT_DIR / 'data_bersih.csv'
df[export_cols].to_csv(csv_path, encoding='utf-8-sig')
print(f"[SAVED] Data bersih tersimpan di: {csv_path}")

print("\n[DONE] Analisis selesai! Semua output di folder: analysis_output/")
