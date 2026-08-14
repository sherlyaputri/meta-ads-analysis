// ============================================
// app.js — Main Application Controller
// ============================================

const APP = {
    rawData: [],
    filterState: null,
    metrics: null,
};

document.addEventListener('DOMContentLoaded', () => {
    setChartDefaults();
    setupUpload();
});

// ---- Upload Setup ----

function setupUpload() {
    const dropzone = document.getElementById('upload-dropzone');
    const input = document.getElementById('upload-input');
    const reuploadBtn = document.getElementById('btn-reupload');

    if (!dropzone || !input) return;

    // Click to browse
    dropzone.addEventListener('click', () => input.click());

    // Drag & drop
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        const files = [...e.dataTransfer.files].filter(f => /\.xlsx?$/i.test(f.name));
        if (files.length > 0) handleFiles(files);
    });

    // File input change
    input.addEventListener('change', () => {
        const files = [...input.files];
        if (files.length > 0) handleFiles(files);
        input.value = '';
    });

    // Re-upload button
    if (reuploadBtn) {
        reuploadBtn.addEventListener('click', () => {
            showView('upload');
        });
    }
}

// ---- File Handling ----

async function handleFiles(files) {
    showLoading(true);
    try {
        let allRows = [];
        for (const file of files) {
            const rows = await parseExcelFile(file);
            // Tag source from filename
            const source = file.name.toLowerCase().includes('malaysia') ? 'malaysia' : 'indonesia';
            rows.forEach(r => { r.source = source; });
            allRows = allRows.concat(rows);
        }

        if (allRows.length === 0) {
            alert('Tidak ada data valid ditemukan dalam file yang di-upload.');
            showLoading(false);
            return;
        }

        APP.rawData = allRows;
        APP.filterState = initFilterState(allRows);

        // Render dashboard
        renderFilterDropdowns(APP.filterState);
        bindFilterEvents(APP.filterState, APP.rawData, onFilterChange);
        onFilterChange();
        showView('dashboard');

        // Show file info
        const infoEl = document.getElementById('file-info');
        if (infoEl) {
            infoEl.textContent = files.map(f => f.name).join(', ');
        }
    } catch (err) {
        console.error('Error processing file:', err);
        alert('Error membaca file: ' + err.message);
    }
    showLoading(false);
}

// ---- Filter Change Handler ----

function onFilterChange() {
    const sel = APP.filterState.selected;
    const filtered = applyFilters(APP.rawData, sel);
    
    const shouldExcludeKargo = sel.campaigns.length === 0 && sel.excludeKargo;
    const metrics = calculateMetrics(filtered, sel.period, shouldExcludeKargo);
    APP.metrics = metrics;

    if (!metrics) {
        document.getElementById('dashboard-content').style.display = 'none';
        document.getElementById('no-data-msg').style.display = 'block';
        return;
    }

    document.getElementById('dashboard-content').style.display = 'block';
    document.getElementById('no-data-msg').style.display = 'none';

    renderKPIs(metrics);
    destroyAllCharts();
    renderAllCharts(metrics);
    renderDetailTable(metrics);
    renderRecommendations(metrics);
    renderKargoSection(metrics);
}

// ---- KPI Cards ----

function renderKPIs(m) {
    setKPI('kpi-spend', formatRp(m.totalSpend), trendHTML(m.trendSpend));
    setKPI('kpi-ttk', formatNum(m.totalTTK), trendHTML(m.trendTTK));
    setKPI('kpi-kg', formatNum(m.totalKG), trendHTML(m.trendKG));
    setKPI('kpi-costttk', formatRpFull(m.avgCostPerTTK), trendHTML(m.trendCostPerTTK));
    setKPI('kpi-ctr', formatPct(m.ctr), trendHTML(m.trendCTR));
    setKPI('kpi-cvr', formatPct(m.cvr), '');

    // Period info
    const periodEl = document.getElementById('period-info');
    if (periodEl && m.dateMin && m.dateMax) {
        const fmt = d => d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
        periodEl.textContent = `${fmt(m.dateMin)} — ${fmt(m.dateMax)} (${m.totalWeeks} minggu)`;
    }
}

function setKPI(id, value, trendHtml) {
    const el = document.getElementById(id);
    if (!el) return;
    el.querySelector('.kpi-value').textContent = value;
    const trendEl = el.querySelector('.kpi-trend');
    if (trendEl) trendEl.innerHTML = trendHtml;

    // Animate entrance
    el.classList.remove('kpi-animate');
    void el.offsetWidth;
    el.classList.add('kpi-animate');
}

// ---- Detail Table ----

function renderDetailTable(metrics) {
    const tbody = document.getElementById('detail-table-body');
    if (!tbody) return;

    const sorted = [...metrics.locationData].sort((a, b) => (a.costPerTTK || Infinity) - (b.costPerTTK || Infinity));
    const q = metrics.quadrant;

    tbody.innerHTML = sorted.map(loc => {
        let statusClass = '';
        let statusText = '';
        if (q.stars.includes(loc.location)) { statusClass = 'status-star'; statusText = '⭐ Bintang'; }
        else if (q.leaky.includes(loc.location)) { statusClass = 'status-warn'; statusText = '⚠️ Bocor CS'; }
        else if (q.poorContent.includes(loc.location)) { statusClass = 'status-info'; statusText = '📝 Konten'; }
        else { statusClass = 'status-neutral'; statusText = '—'; }

        return `<tr>
            <td class="td-location">${loc.location}</td>
            <td class="td-number">${formatRp(loc.totalSpend)}</td>
            <td class="td-number">${formatNum(loc.totalTTK)}</td>
            <td class="td-number">${formatNum(loc.totalKG)}</td>
            <td class="td-number">${loc.costPerTTK != null ? formatRpFull(loc.costPerTTK) : '-'}</td>
            <td class="td-number">${loc.ctr != null ? formatPct(loc.ctr) : '-'}</td>
            <td class="td-number">${loc.cvr != null ? formatPct(loc.cvr) : '-'}</td>
            <td class="td-status"><span class="${statusClass}">${statusText}</span></td>
        </tr>`;
    }).join('');

    // Make table sortable
    setupTableSort();
}

function setupTableSort() {
    document.querySelectorAll('#detail-table th[data-sort]').forEach(th => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const tbody = document.getElementById('detail-table-body');
            const rows = [...tbody.querySelectorAll('tr')];
            const col = th.cellIndex;
            const asc = th.dataset.dir !== 'asc';
            th.dataset.dir = asc ? 'asc' : 'desc';

            rows.sort((a, b) => {
                let va = a.cells[col].textContent.replace(/[^\d.-]/g, '');
                let vb = b.cells[col].textContent.replace(/[^\d.-]/g, '');
                va = parseFloat(va) || 0;
                vb = parseFloat(vb) || 0;
                return asc ? va - vb : vb - va;
            });

            rows.forEach(r => tbody.appendChild(r));

            // Update sort indicators
            document.querySelectorAll('#detail-table th[data-sort]').forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
            th.classList.add(asc ? 'sort-asc' : 'sort-desc');
        });
    });
}

// ---- Recommendations ----

function renderRecommendations(metrics) {
    const el = document.getElementById('recommendations');
    if (!el || !metrics.recommendations) return;

    if (metrics.recommendations.length === 0) {
        el.innerHTML = '<div class="rec-card rec-neutral"><span class="rec-icon">✅</span> Semua lokasi berkinerja merata, pertahankan strategi.</div>';
        return;
    }

    el.innerHTML = metrics.recommendations.map(r => {
        const icon = r.type === 'success' ? '🟢' : r.type === 'warning' ? '🟡' : '🔴';
        return `<div class="rec-card rec-${r.type}">
            <span class="rec-icon">${icon}</span>
            <strong>${r.location}:</strong> ${r.text}
        </div>`;
    }).join('');
}

// ---- Kargo Section ----

function renderKargoSection(metrics) {
    const el = document.getElementById('kargo-section');
    if (!el) return;

    if (!metrics.kargoStats) {
        el.style.display = 'none';
        return;
    }

    el.style.display = 'block';
    const k = metrics.kargoStats;
    el.innerHTML = `
        <h3 class="section-title">📦 Data Kargo (Dipisahkan)</h3>
        <div class="kargo-grid">
            <div class="kargo-item"><span class="kargo-label">Spend</span><span class="kargo-val">${formatRp(k.spend)}</span></div>
            <div class="kargo-item"><span class="kargo-label">TTK</span><span class="kargo-val">${formatNum(k.ttk)}</span></div>
            <div class="kargo-item"><span class="kargo-label">KG</span><span class="kargo-val">${formatNum(k.kg)}</span></div>
            <div class="kargo-item"><span class="kargo-label">Cost/TTK</span><span class="kargo-val">${k.ttk > 0 ? formatRpFull(k.spend / k.ttk) : '-'}</span></div>
            <div class="kargo-item kargo-locs"><span class="kargo-label">Lokasi</span><span class="kargo-val">${k.locations.join(', ')}</span></div>
        </div>
    `;
}

// ---- View Switching ----

function showView(view) {
    document.getElementById('view-upload').style.display = view === 'upload' ? 'flex' : 'none';
    document.getElementById('view-dashboard').style.display = view === 'dashboard' ? 'block' : 'none';
}

function showLoading(show) {
    const el = document.getElementById('loading-overlay');
    if (el) el.style.display = show ? 'flex' : 'none';
}
