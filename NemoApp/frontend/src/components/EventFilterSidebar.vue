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

    <!-- Action Buttons -->
    <div class="filter-actions">
      <!-- <Button
        label="Apply"
        class="p-button-success apply-btn"
        @click="applyFilters"
      /> -->
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

export default {
  name: 'EventFilterSidebar',
  components: {
    InputText,
    Checkbox,
    Button
  },
  emits: ['filtersChanged'],
  setup(props, { emit }) {
    const sidebarRef = ref(null)
    const filters = ref({
      search: '',
      format: [],
      type: []
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
        format: [],
        type: []
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
}
</style>