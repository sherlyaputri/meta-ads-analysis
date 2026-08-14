// ============================================
// filters.js — Filter System
// ============================================

/**
 * Initialize filter state from raw data.
 */
function initFilterState(data) {
    const campaigns = [...new Set(data.map(r => r.campaign))].sort();
    const locations = [...new Set(data.map(r => r.location))].sort();
    const dates = data.map(r => r.date).filter(Boolean);
    const minDate = new Date(Math.min(...dates));
    const maxDate = new Date(Math.max(...dates));

    return {
        availableCampaigns: campaigns,
        availableLocations: locations,
        dateRange: { min: minDate, max: maxDate },
        selected: {
            campaigns: [],      // empty = all
            locations: [],      // empty = all
            period: 'weekly',   // weekly | monthly | yearly
            dateStart: minDate,
            dateEnd: maxDate,
            excludeKargo: true,
        },
    };
}

/**
 * Apply current filters to raw data → return filtered subset.
 */
function applyFilters(data, sel) {
    let filtered = data;

    // Campaign filter
    if (sel.campaigns.length > 0) {
        filtered = filtered.filter(r => sel.campaigns.includes(r.campaign));
    }

    // Location filter
    if (sel.locations.length > 0) {
        filtered = filtered.filter(r => sel.locations.includes(r.location));
    }

    // Date range
    if (sel.dateStart) filtered = filtered.filter(r => r.date >= sel.dateStart);
    if (sel.dateEnd) filtered = filtered.filter(r => r.date <= sel.dateEnd);

    return filtered;
}

/**
 * Populate filter dropdowns from available values.
 */
function renderFilterDropdowns(state) {
    // Campaign
    const camSel = document.getElementById('filter-campaign');
    if (camSel) {
        camSel.innerHTML = '<option value="">Semua Campaign</option>';
        state.availableCampaigns.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            camSel.appendChild(opt);
        });
    }

    // Location
    const locSel = document.getElementById('filter-location');
    if (locSel) {
        locSel.innerHTML = '<option value="">Semua Lokasi</option>';
        state.availableLocations.forEach(l => {
            const opt = document.createElement('option');
            opt.value = l;
            opt.textContent = l;
            locSel.appendChild(opt);
        });
    }

    // Date range display
    const rangeEl = document.getElementById('filter-date-range');
    if (rangeEl) {
        const fmt = d => `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
        rangeEl.textContent = `${fmt(state.dateRange.min)} — ${fmt(state.dateRange.max)}`;
    }

    // Period default
    setActivePeriod(state.selected.period);
}

/**
 * Read current filter selections from the DOM.
 */
function readFilters(filterState) {
    const sel = { ...filterState.selected };

    const camVal = document.getElementById('filter-campaign')?.value;
    sel.campaigns = camVal ? [camVal] : [];

    const locVal = document.getElementById('filter-location')?.value;
    sel.locations = locVal ? [locVal] : [];

    // Period is set via pill toggle click
    // DateStart/DateEnd stay as initialized unless changed

    return sel;
}

/**
 * Highlight the active period pill.
 */
function setActivePeriod(period) {
    document.querySelectorAll('.period-pill').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.period === period);
    });
}

/**
 * Update the location dropdown options based on the selected campaign.
 */
function updateLocationDropdown(filterState, rawData) {
    const selCam = filterState.selected.campaigns[0];
    const locSel = document.getElementById('filter-location');
    if (!locSel) return;

    // Preserve currently selected location (if any)
    const currentLoc = locSel.value;

    let validLocations;
    if (selCam) {
        // If a campaign is selected, only show locations that have data for this campaign
        const camData = rawData.filter(r => r.campaign === selCam);
        validLocations = [...new Set(camData.map(r => r.location))].sort();
    } else {
        // Otherwise show all available locations
        validLocations = filterState.availableLocations;
    }

    // Rebuild options
    locSel.innerHTML = '<option value="">Semua Lokasi</option>';
    validLocations.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l;
        opt.textContent = l;
        locSel.appendChild(opt);
    });

    // Restore previous selection if it's still valid
    if (validLocations.includes(currentLoc)) {
        locSel.value = currentLoc;
    } else {
        // If the previously selected location is no longer valid, clear it
        locSel.value = "";
        filterState.selected.locations = [];
    }
}

/**
 * Bind filter events. Calls onChange() whenever any filter changes.
 */
function bindFilterEvents(filterState, rawData, onChange) {
    // Campaign dropdown
    const camEl = document.getElementById('filter-campaign');
    if (camEl) {
        camEl.addEventListener('change', () => {
            filterState.selected = readFilters(filterState);
            updateLocationDropdown(filterState, rawData);
            // Need to read again in case location was cleared
            filterState.selected = readFilters(filterState);
            onChange();
        });
    }

    // Location dropdown
    const locEl = document.getElementById('filter-location');
    if (locEl) {
        locEl.addEventListener('change', () => {
            filterState.selected = readFilters(filterState);
            onChange();
        });
    }

    // Period pills
    document.querySelectorAll('.period-pill').forEach(btn => {
        btn.addEventListener('click', () => {
            filterState.selected.period = btn.dataset.period;
            setActivePeriod(btn.dataset.period);
            onChange();
        });
    });
}
