// ============================================
// filters.js — Filter System
// Multi-select location + Flatpickr date range
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
        },
        _flatpickrStart: null,
        _flatpickrEnd: null,
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

    // Location filter (multi-select)
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
    // Multi-select campaign
    renderCampaignMultiSelect(state.availableCampaigns, state.selected.campaigns);

    // Multi-select location
    renderLocationMultiSelect(state.availableLocations, state.selected.locations);

    const periodSel = document.getElementById('filter-period');
    if (periodSel) periodSel.value = state.selected.period;
    // Initialize Flatpickr date pickers
    initDatePickers(state);
}

/**
 * Render multi-select location dropdown options.
 */
function renderLocationMultiSelect(locations, selectedLocs) {
    const container = document.getElementById('ms-options-location');
    if (!container) return;

    container.innerHTML = '';
    locations.forEach(loc => {
        const isChecked = selectedLocs.includes(loc);
        const item = document.createElement('label');
        item.className = 'ms-option' + (isChecked ? ' checked' : '');
        item.innerHTML = `
            <input type="checkbox" value="${loc}" ${isChecked ? 'checked' : ''}>
            <span class="ms-checkbox"></span>
            <span class="ms-option-text">${loc}</span>
        `;
        container.appendChild(item);
    });
}

/**
 * Update the trigger display for multi-select.
 */
function updateMultiSelectTrigger(selectedLocs) {
    const trigger = document.getElementById('ms-trigger-location');
    if (!trigger) return;

    const placeholder = trigger.querySelector('.multi-select-placeholder');
    if (!placeholder) return;

    if (selectedLocs.length === 0) {
        placeholder.textContent = 'Semua Lokasi';
        placeholder.classList.remove('has-selection');
        trigger.title = 'Semua Lokasi';
    } else if (selectedLocs.length === 1) {
        placeholder.textContent = selectedLocs[0];
        placeholder.classList.add('has-selection');
        trigger.title = selectedLocs[0];
    } else if (selectedLocs.length <= 3) {
        placeholder.textContent = selectedLocs.join(', ');
        placeholder.classList.add('has-selection');
        trigger.title = selectedLocs.join(', ');
    } else {
        placeholder.textContent = `${selectedLocs.length} lokasi dipilih`;
        placeholder.classList.add('has-selection');
        trigger.title = selectedLocs.join(', ');
    }
}

/**
 * Read currently checked locations from multi-select DOM.
 */


function readSelectedCampaigns() {
    const checkboxes = document.querySelectorAll('#ms-options-campaign input[type="checkbox"]:checked');
    return [...checkboxes].map(cb => cb.value);
}

function updateMultiSelectTriggerCampaign(selectedCams) {
    const trigger = document.getElementById('ms-trigger-campaign');
    if (!trigger) return;
    const placeholder = trigger.querySelector('.multi-select-placeholder');
    if (!placeholder) return;

    if (selectedCams.length === 0) {
        placeholder.textContent = 'Semua Campaign';
        placeholder.classList.remove('has-selection');
        trigger.title = 'Semua Campaign';
    } else if (selectedCams.length === 1) {
        placeholder.textContent = selectedCams[0];
        placeholder.classList.add('has-selection');
        trigger.title = selectedCams[0];
    } else if (selectedCams.length <= 2) {
        placeholder.textContent = selectedCams.join(', ');
        placeholder.classList.add('has-selection');
        trigger.title = selectedCams.join(', ');
    } else {
        placeholder.textContent = `${selectedCams.length} campaign dipilih`;
        placeholder.classList.add('has-selection');
        trigger.title = selectedCams.join(', ');
    }
}

function renderCampaignMultiSelect(campaigns, selectedCams) {
    const container = document.getElementById('ms-options-campaign');
    if (!container) return;
    container.innerHTML = '';
    campaigns.forEach(cam => {
        const isChecked = selectedCams.includes(cam);
        const item = document.createElement('label');
        item.className = 'ms-option' + (isChecked ? ' checked' : '');
        item.innerHTML = `
            <input type="checkbox" value="${cam}" ${isChecked ? 'checked' : ''}>
            <span class="ms-checkbox"></span>
            <span class="ms-option-text">${cam}</span>
        `;
        container.appendChild(item);
    });
}

function filterCampaignOptions(searchText) {
    const query = searchText.toLowerCase().trim();
    const options = document.querySelectorAll('#ms-options-campaign .ms-option');
    options.forEach(opt => {
        const text = opt.querySelector('.ms-option-text')?.textContent.toLowerCase() || '';
        opt.classList.toggle('hidden', query !== '' && !text.includes(query));
    });
}

function readSelectedLocations() {
    const checkboxes = document.querySelectorAll('#ms-options-location input[type="checkbox"]:checked');
    return [...checkboxes].map(cb => cb.value);
}

/**
 * Read current filter selections from the DOM.
 */
function readFilters(filterState) {
    const sel = { ...filterState.selected };

    sel.campaigns = readSelectedCampaigns();

    // Multi-select locations
    sel.locations = readSelectedLocations();

    // Date range from Flatpickr
    if (filterState._flatpickrStart && filterState._flatpickrStart.selectedDates.length > 0) {
        sel.dateStart = filterState._flatpickrStart.selectedDates[0];
    }
    if (filterState._flatpickrEnd && filterState._flatpickrEnd.selectedDates.length > 0) {
        sel.dateEnd = filterState._flatpickrEnd.selectedDates[0];
    }
    const periodVal = document.getElementById('filter-period')?.value;
    if (periodVal) sel.period = periodVal;

    return sel;
}



/**
 * Initialize Flatpickr date pickers.
 */
function initDatePickers(state) {
    const startInput = document.getElementById('filter-date-start');
    const endInput = document.getElementById('filter-date-end');
    if (!startInput || !endInput) return;

    const fpConfig = {
        dateFormat: 'd/m/Y',
        minDate: state.dateRange.min,
        maxDate: state.dateRange.max,
        disableMobile: true,
        locale: {
            firstDayOfWeek: 1,
            weekdays: {
                shorthand: ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'],
                longhand: ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'],
            },
            months: {
                shorthand: ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'],
                longhand: ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'],
            },
        },
    };

    state._flatpickrStart = flatpickr(startInput, {
        ...fpConfig,
        defaultDate: state.dateRange.min,
    });

    state._flatpickrEnd = flatpickr(endInput, {
        ...fpConfig,
        defaultDate: state.dateRange.max,
    });
}

/**
 * Update the location multi-select options based on the selected campaign.
 */
function updateLocationMultiSelect(filterState, rawData) {
    const selCams = filterState.selected.campaigns;

    let validLocations;
    if (selCams.length > 0) {
        const camData = rawData.filter(r => selCams.includes(r.campaign));
        validLocations = [...new Set(camData.map(r => r.location))].sort();
    } else {
        validLocations = filterState.availableLocations;
    }

    // Keep only currently selected locations that are still valid
    const currentSelected = filterState.selected.locations.filter(l => validLocations.includes(l));
    filterState.selected.locations = currentSelected;

    // Re-render options
    renderLocationMultiSelect(validLocations, currentSelected);
    updateMultiSelectTrigger(currentSelected);
}

/**
 * Bind filter events. Calls onChange() whenever any filter changes.
 */
function bindFilterEvents(filterState, rawData, onChange) {

    // Helper to bind a generic multi-select
    function bindMultiSelectEvents(type, readFunc, updateTriggerFunc, updateCascadeFunc) {
        const trigger = document.getElementById(`ms-trigger-${type}`);
        const dropdown = document.getElementById(`ms-dropdown-${type}`);
        const multiSelect = document.getElementById(`multi-select-${type}`);
        const optionsContainer = document.getElementById(`ms-options-${type}`);
        const searchInput = document.getElementById(`ms-search-${type}`);
        const selectAllBtn = document.getElementById(`ms-select-all-${type}`);
        const clearAllBtn = document.getElementById(`ms-clear-all-${type}`);
        const filterOptions = type === 'location' ? filterLocationOptions : filterCampaignOptions;

        if (trigger && dropdown) {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const isOpen = dropdown.classList.contains('open');
                dropdown.classList.toggle('open', !isOpen);
                multiSelect?.classList.toggle('open', !isOpen);
                if (!isOpen && searchInput) { 
                    searchInput.value = ''; filterOptions(''); searchInput.focus(); 
                }
            });
            document.addEventListener('click', (e) => {
                if (!multiSelect?.contains(e.target)) {
                    dropdown.classList.remove('open');
                    multiSelect?.classList.remove('open');
                }
            });
        }

        if (optionsContainer) {
            optionsContainer.addEventListener('change', (e) => {
                if (e.target.type === 'checkbox') {
                    const label = e.target.closest('.ms-option');
                    if (label) label.classList.toggle('checked', e.target.checked);
                    
                    if (type === 'campaign') {
                        filterState.selected.campaigns = readFunc();
                        updateTriggerFunc(filterState.selected.campaigns);
                        if (updateCascadeFunc) updateCascadeFunc(filterState, rawData);
                    } else {
                        filterState.selected.locations = readFunc();
                        updateTriggerFunc(filterState.selected.locations);
                    }
                    onChange();
                }
            });
        }

        if (searchInput) {
            searchInput.addEventListener('input', (e) => filterOptions(e.target.value));
            searchInput.addEventListener('click', (e) => e.stopPropagation());
        }

        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const checkboxes = document.querySelectorAll(`#ms-options-${type} input[type="checkbox"]`);
                checkboxes.forEach(cb => {
                    if (!cb.closest('.ms-option').classList.contains('hidden')) {
                        cb.checked = true;
                        cb.closest('.ms-option').classList.add('checked');
                    }
                });
                
                if (type === 'campaign') {
                    filterState.selected.campaigns = readFunc();
                    updateTriggerFunc(filterState.selected.campaigns);
                    if (updateCascadeFunc) updateCascadeFunc(filterState, rawData);
                } else {
                    filterState.selected.locations = readFunc();
                    updateTriggerFunc(filterState.selected.locations);
                }
                onChange();
            });
        }

        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const checkboxes = document.querySelectorAll(`#ms-options-${type} input[type="checkbox"]`);
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    cb.closest('.ms-option').classList.remove('checked');
                });
                
                if (type === 'campaign') {
                    filterState.selected.campaigns = [];
                    updateTriggerFunc([]);
                    if (updateCascadeFunc) updateCascadeFunc(filterState, rawData);
                } else {
                    filterState.selected.locations = [];
                    updateTriggerFunc([]);
                }
                onChange();
            });
        }
    }

    bindMultiSelectEvents('campaign', readSelectedCampaigns, updateMultiSelectTriggerCampaign, updateLocationMultiSelect);


    bindMultiSelectEvents('location', readSelectedLocations, updateMultiSelectTrigger, null);

    // Flatpickr date change events
    if (filterState._flatpickrStart) {
        filterState._flatpickrStart.config.onChange.push((selectedDates) => {
            if (selectedDates.length > 0) {
                filterState.selected.dateStart = selectedDates[0];
                onChange();
            }
        });
    }
    if (filterState._flatpickrEnd) {
        filterState._flatpickrEnd.config.onChange.push((selectedDates) => {
            if (selectedDates.length > 0) {
                filterState.selected.dateEnd = selectedDates[0];
                onChange();
            }
        });
    }

    // Period select
    const periodSel = document.getElementById('filter-period');
    if (periodSel) {
        periodSel.addEventListener('change', () => {
            filterState.selected.period = periodSel.value;
            onChange();
        });
    }
}

/**
 * Filter location options in multi-select by search text.
 */
function filterLocationOptions(searchText) {
    const query = searchText.toLowerCase().trim();
    const options = document.querySelectorAll('#ms-options-location .ms-option');
    options.forEach(opt => {
        const text = opt.querySelector('.ms-option-text')?.textContent.toLowerCase() || '';
        opt.classList.toggle('hidden', query !== '' && !text.includes(query));
    });
}
