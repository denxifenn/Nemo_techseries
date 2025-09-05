<template>
  <div class="event-filter-sidebar" ref="sidebarRef">
    <div class="filter-header">
      <h2>Filter events</h2>
    </div>

    <!-- Search Input -->
    <div class="search-section">
      <span class="p-input-icon-left">
        <InputText
          v-model="filters.search"
          placeholder="Search events"
          class="w-full"
        />
      </span>
    </div>

    <!-- Date Range Section -->
    <div class="filter-section">
      <h4>Date Range</h4>
      <div class="date-range-group">
        <div class="date-input-group">
          <label for="startDate" class="date-label">From:</label>
          <Calendar
            id="startDate"
            v-model="filters.dateRange.start"
            placeholder="Start date"
            :showIcon="true"
            dateFormat="dd/mm/yy"
            class="w-full"
          />
        </div>
        <div class="date-input-group">
          <label for="endDate" class="date-label">To:</label>
          <Calendar
            id="endDate"
            v-model="filters.dateRange.end"
            placeholder="End date"
            :showIcon="true"
            dateFormat="dd/mm/yy"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <!-- Timing Section -->
    <div class="filter-section">
      <h4>Timing</h4>
      <div class="checkbox-group">
        <div class="field-checkbox">
          <Checkbox
            id="morning"
            v-model="filters.timing"
            value="morning"
          />
          <label for="morning">Morning (5 AM - 12 PM)</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="afternoon"
            v-model="filters.timing"
            value="afternoon"
          />
          <label for="afternoon">Afternoon (12 PM - 4 PM)</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="evening"
            v-model="filters.timing"
            value="evening"
          />
          <label for="evening">Evening (4 PM - 7 PM)</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="night"
            v-model="filters.timing"
            value="night"
          />
          <label for="night">Night (7 PM - 5 AM)</label>
        </div>
      </div>
    </div>

    <!-- Format Section -->
    <div class="filter-section">
      <h4>Format</h4>
      <div class="checkbox-group">
        <div class="field-checkbox">
          <Checkbox
            id="online"
            v-model="filters.format"
            value="online"
          />
          <label for="online">Online</label>
        </div>
        <div class="field-checkbox expandable-checkbox">
          <Checkbox
            id="offline"
            v-model="filters.format"
            value="offline"
          />
          <label for="offline" @click="toggleOfflineExpanded">Offline</label>
          <button
            class="expand-btn"
            @click="toggleOfflineExpanded"
            :class="{ expanded: offlineExpanded }"
          >
            <i class="pi pi-chevron-down"></i>
          </button>
        </div>
        <div v-if="offlineExpanded" class="sub-options">
          <div class="field-checkbox sub-checkbox">
            <Checkbox
              id="indoor"
              v-model="filters.format"
              value="indoor"
            />
            <label for="indoor">Indoor</label>
          </div>
          <div class="field-checkbox sub-checkbox">
            <Checkbox
              id="outdoor"
              v-model="filters.format"
              value="outdoor"
            />
            <label for="outdoor">Outdoor</label>
          </div>
        </div>
      </div>
    </div>

    <!-- Type Section -->
    <div class="filter-section">
      <h4>Type</h4>
      <div class="checkbox-group">
        <div class="field-checkbox">
          <Checkbox
            id="sports"
            v-model="filters.type"
            value="sports"
          />
          <label for="sports">Sports</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="arts"
            v-model="filters.type"
            value="arts"
          />
          <label for="arts">Arts</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="culture"
            v-model="filters.type"
            value="culture"
          />
          <label for="culture">Culture</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="music"
            v-model="filters.type"
            value="music"
          />
          <label for="music">Music</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="performance"
            v-model="filters.type"
            value="performance"
          />
          <label for="performance">Performance</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="workshop"
            v-model="filters.type"
            value="workshop"
          />
          <label for="workshop">Workshop</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="tours"
            v-model="filters.type"
            value="tours"
          />
          <label for="tours">Tours</label>
        </div>
      </div>
    </div>

    <!-- Region Section -->
    <div class="filter-section">
      <h4>Region</h4>
      <div class="checkbox-group">
        <div class="field-checkbox">
          <Checkbox
            id="North"
            v-model="filters.region"
            value="North"
          />
          <label for="North">North</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="South"
            v-model="filters.region"
            value="South"
          />
          <label for="South">South</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="East"
            v-model="filters.region"
            value="East"
          />
          <label for="East">East</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="West"
            v-model="filters.region"
            value="West"
          />
          <label for="West">West</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="Central"
            v-model="filters.region"
            value="Central"
          />
          <label for="Central">Central</label>
        </div>
      </div>
    </div>

    <!-- Price Section -->
<div class="filter-section">
  <h4>Price</h4>
  <div class="price-range-container">
    <div class="price-inputs">
      <InputText
        v-model.number="filters.priceRange[0]"
        type="number"
        class="price-input"
        :min="0"
        :max="500"
      />
      <span class="price-separator">–</span>
      <InputText
        v-model.number="filters.priceRange[1]"
        type="number"
        class="price-input"
        :min="0"
        :max="500"
      />
    </div>

    <div class="dual-range-slider">
      <div class="slider-track">
        <div
          class="slider-range"
          :style="{
            left: (filters.priceRange[0] / 500) * 100 + '%',
            width: ((filters.priceRange[1] - filters.priceRange[0]) / 500) * 100 + '%'
          }"
        ></div>
        <input
          type="range"
          class="slider-thumb slider-min"
          v-model="filters.priceRange[0]"
          :min="0"
          :max="500"
          step="10"
          @input="handleMinChange"
        />
        <input
          type="range"
          class="slider-thumb slider-max"
          v-model="filters.priceRange[1]"
          :min="0"
          :max="500"
          step="10"
          @input="handleMaxChange"
        />
      </div>
    </div>
  </div>
</div>

    <!-- Action Buttons -->
    <div class="filter-actions">
      <Button
        label="Reset"
        class="p-button-text reset-btn"
        @click="resetFilters"
      />
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import InputText from 'primevue/inputtext'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Calendar from 'primevue/calendar'

export default {
  name: 'EventFilterSidebar',
  components: {
    InputText,
    Checkbox,
    Button,
    Calendar
  },
  emits: ['filtersChanged'],
  setup(props, { emit }) {
    const sidebarRef = ref(null)
    const offlineExpanded = ref(false)
    const filters = ref({
      search: '',
      dateRange: {
        start: null,
        end: null
      },
      timing: [],
      format: [],
      type: [],
      region: [],
      priceRange: [0, 500]
    })

    // Watch for changes and emit to parent
    watch(
      filters,
      (newFilters) => {
        console.log('EventFilterSidebar: Filters changed:', newFilters)
        emit('filtersChanged', { ...newFilters })
      },
      { deep: true }
    )

    const applyFilters = () => {
      // Emit current filters to parent component
      emit('filtersChanged', { ...filters.value })
    }

    const toggleOfflineExpanded = () => {
      offlineExpanded.value = !offlineExpanded.value
    }

    const handleMinChange = () => {
      if (filters.value.priceRange[0] > filters.value.priceRange[1] - 10) {
        filters.value.priceRange[0] = filters.value.priceRange[1] - 10
      }
    }

    const handleMaxChange = () => {
      if (filters.value.priceRange[1] < filters.value.priceRange[0] + 10) {
        filters.value.priceRange[1] = filters.value.priceRange[0] + 10
      }
    }

    const resetFilters = () => {
      filters.value = {
        search: '',
        dateRange: {
          start: null,
          end: null
        },
        timing: [],
        format: [],
        type: [],
        region: [],
        priceRange: [0, 500]
      }
      offlineExpanded.value = false
    }

    return {
      sidebarRef,
      offlineExpanded,
      filters,
      applyFilters,
      resetFilters,
      toggleOfflineExpanded,
      handleMinChange,
      handleMaxChange
    }
  }
}
</script>

<style scoped>
.event-filter-sidebar {
  width: 100%;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  padding: 15px 12px;
  height: auto;
  overflow-y: auto;
  position: sticky;
  align-self: flex-start;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: left; /* Ensure left alignment for entire sidebar */
}

.filter-header {
  margin-bottom: 25px;
  text-align: left; /* Changed from center to left */
}

.filter-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  letter-spacing: -0.025em;
  text-align: left; /* Explicit left alignment */
}

.search-section {
  margin-bottom: 25px;
}

.search-section .p-input-icon-left {
  width: 100%;
}

.search-section .p-inputtext {
  width: 100% !important;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #d1d5db;
  font-size: 14px;
  transition: border-color 0.2s ease;
  text-align: left; /* Left align input text */
}

.search-section .p-inputtext:focus {
  border-color: #EC7600;
  box-shadow: 0 0 0 2px rgba(236, 118, 0, 0.1);
}

.filter-section {
  margin-bottom: 25px;
  text-align: left; /* Ensure section content is left aligned */
}

.filter-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  justify-content: flex-start; /* Left align section headers */
  gap: 8px;
  text-align: left;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-start; /* Left align checkbox group */
}

.field-checkbox {
  display: flex;
  align-items: center; /* Changed from flex-start to center for better checkbox alignment */
  justify-content: flex-start; /* Explicit left alignment */
  gap: 10px;
  padding: 6px 8px 6px 4px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
  width: 100%; /* Ensure full width */
  text-align: left;
}

.field-checkbox:hover {
  background-color: #f9fafb;
}

.field-checkbox label {
  font-size: 14px;
  color: #4b5563;
  cursor: pointer;
  line-height: 1.4;
  margin: 0;
  flex: 1;
  text-align: left; /* Explicit left alignment for labels */
  white-space: nowrap; /* Prevent text wrapping that might affect alignment */
}

/* Checkbox alignment adjustments */
.field-checkbox .p-checkbox {
  align-self: flex-start; /* Align checkbox to top-left */
  margin-top: 2px; /* Fine-tune vertical alignment */
}

/* Date Range Styles */
.date-range-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start; /* Left align date inputs */
}

.date-input-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  align-items: flex-start; /* Left align date input elements */
}

.date-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
  margin-bottom: 4px;
  text-align: left; /* Left align date labels */
}

.date-input-group .p-calendar {
  width: 100%;
}

.date-input-group .p-inputtext {
  width: 100% !important;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  font-size: 14px;
  transition: border-color 0.2s ease;
  text-align: left; /* Left align date input text */
}

.date-input-group .p-inputtext:focus {
  border-color: #EC7600;
  box-shadow: 0 0 0 2px rgba(236, 118, 0, 0.1);
}

.filter-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
  align-items: stretch; /* Stretch button to full width */
}

.filter-actions .p-button {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  text-align: center; /* Center text in buttons */
}

.reset-btn {
  background-color: #f3f4f6 !important;
  border-color: #d1d5db !important;
  color: #374151 !important;
}

.reset-btn:hover {
  background-color: #e5e7eb !important;
  border-color: #9ca3af !important;
}

/* Custom scrollbar */
.event-filter-sidebar::-webkit-scrollbar {
  width: 6px;
}

.event-filter-sidebar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.event-filter-sidebar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.event-filter-sidebar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Expandable section styles */
.expandable-checkbox {
  position: relative;
}

.expand-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.expand-btn:hover {
  background-color: #f3f4f6;
  color: #374151;
}

.expand-btn.expanded {
  transform: translateY(-50%) rotate(180deg);
}

.sub-options {
  margin-left: 20px;
  margin-top: 8px;
  padding-left: 16px;
  border-left: 2px solid #e5e7eb;
  animation: slideDown 0.3s ease-out;
  text-align: left; /* Left align sub-options */
}

.sub-checkbox {
  padding: 6px 8px;
  margin-bottom: 4px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
  text-align: left; /* Left align sub-checkbox items */
}

.sub-checkbox:hover {
  background-color: #f9fafb;
}

/* Price Section Styles */
.price-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.price-type-toggles {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.price-slider-container {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  animation: slideIn 0.3s ease-out;
}

.price-range-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.price-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.price-values {
  font-size: 14px;
  font-weight: 700;
  color: #EC7600;
  background: #FEF3E2;
  padding: 4px 8px;
  border-radius: 4px;
}

/* Dual Range Slider */
.dual-range-slider {
  position: relative;
  margin-top: 10px;
}

.slider-track {
  position: relative;
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
}

.slider-range {
  position: absolute;
  height: 100%;
  background: #2d2d4d; /* dark navy bar */
  border-radius: 2px;
  top: 0;
  pointer-events: none;
}

.slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  background: transparent;
  cursor: pointer;
  border: none;
  outline: none;
  position: absolute;
  width: 100%;
  height: 4px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.slider-thumb::-webkit-slider-track {
  background: transparent;
  border: none;
  height: 4px;
}

.slider-thumb::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  background: #2d2d4d;
  border-radius: 2px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
  pointer-events: all;
}

.slider-thumb::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.slider-thumb::-moz-range-track {
  background: transparent;
  border: none;
  height: 4px;
}

.slider-thumb::-moz-range-thumb {
  width: 16px;
  height: 16px;
  background: #2d2d4d;
  border-radius: 2px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  border: none;
  transition: transform 0.2s ease;
}

.slider-thumb::-moz-range-thumb:hover {
  transform: scale(1.1);
}

.slider-min {
  z-index: 3;
}

.slider-max {
  z-index: 4;
}

/* Price Input Fields */
.price-inputs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.price-input-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.price-input-group label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.price-range-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.price-input {
  flex: 1;
  text-align: center;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  background: #fff;
}

.price-input:focus {
  border-color: #1f1f3d;
  box-shadow: 0 0 0 2px rgba(31, 31, 61, 0.1);
  outline: none;
}

.price-separator {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 4px;
}

/* Price Presets */
.price-presets {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-top: 16px;
}

.preset-btn {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  color: #6b7280;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.preset-btn:hover {
  border-color: #EC7600;
  color: #EC7600;
  background: #FEF3E2;
}

.preset-btn.active {
  background: #EC7600;
  border-color: #EC7600;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(236, 118, 0, 0.2);
}

@keyframes slideIn {
  from {
    opacity: 0;
    max-height: 0;
    padding-top: 0;
    padding-bottom: 0;
  }
  to {
    opacity: 1;
    max-height: 400px;
    padding-top: 16px;
    padding-bottom: 16px;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .event-filter-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
    padding: 16px;
    text-align: left; /* Maintain left alignment on mobile */
  }

  .date-range-group {
    gap: 12px;
  }

  .filter-actions {
    flex-direction: row;
    gap: 10px;
  }

  .filter-actions .p-button {
    flex: 1;
  }
}
</style>