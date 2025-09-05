<template>
  <div class="event-filter-sidebar" ref="sidebarRef">
    <div class="filter-header">
      <h3>Filter events</h3>
    </div>

    <!-- Search Input -->
    <div class="search-section">
      <span class="p-input-icon-left">
        <i class="pi pi-search" />
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
            id="indoor"
            v-model="filters.format"
            value="indoor"
          />
          <label for="indoor">Indoor</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="outdoor"
            v-model="filters.format"
            value="outdoor"
          />
          <label for="outdoor">Outdoor</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="online"
            v-model="filters.format"
            value="online"
          />
          <label for="online">Online</label>
        </div>
        <div class="field-checkbox">
          <Checkbox
            id="offline"
            v-model="filters.format"
            value="offline"
          />
          <label for="offline">Offline</label>
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
    const filters = ref({
      search: '',
      dateRange: {
        start: null,
        end: null
      },
      timing: [],
      format: [],
      type: [],
      region: []
    })

    // Watch for changes and emit to parent
    watch(
      filters,
      (newFilters) => {
        emit('filtersChanged', { ...newFilters })
      },
      { deep: true }
    )

    const applyFilters = () => {
      // Emit current filters to parent component
      emit('filtersChanged', { ...filters.value })
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
        region: []
      }
    }

    return {
      sidebarRef,
      filters,
      applyFilters,
      resetFilters
    }
  }
}
</script>

<style scoped>
.event-filter-sidebar {
  width: 100%;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  padding: 10px;
  height: auto;
  overflow-y: auto;
  position: sticky;
  align-self: flex-start;
}

.filter-header {
  margin-bottom: 20px;
}

.filter-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.search-section {
  margin-bottom: 30px;
}

.filter-section {
  margin-bottom: 30px;
}

.filter-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 15px 0;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
}

.field-checkbox label {
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
}

/* Date Range Styles */
.date-range-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.date-input-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.apply-btn {
  flex: 1;
  background-color: #22c55e !important;
  border-color: #22c55e !important;
}

.reset-btn {
  flex: 1;
  color: #6b7280 !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .event-filter-sidebar {
    width: 100%;
    height: auto;
    position: relative;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }
  
  .date-range-group {
    gap: 12px;
  }
}
</style>