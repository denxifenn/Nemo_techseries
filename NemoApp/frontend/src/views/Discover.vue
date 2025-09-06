<script>
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Card from 'primevue/card'
import Paginator from 'primevue/paginator'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EventFilterSidebar from '../components/EventFilterSidebar.vue'
import api from '../services/api'

export default {
  name: 'Discover',
  components: {
    Button,
    Tag,
    Card,
    EventFilterSidebar,
    Paginator
  },
  setup() {
    const componentName = ref('Discover')
    const searchTerm = ref('')
    const heroRef = ref(null)
    const eventsGridRef = ref(null)
    const router = useRouter()
    
    const currentFilters = ref({
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

    // Events fetched from backend
    const events = ref([])
    const loading = ref(false)
    const error = ref(null)

    const placeholderImage = '/src/assets/workers_background.jpg'

    async function fetchEvents() {
      loading.value = true
      error.value = null
      try {
        const resp = await api.get('/api/events', { limit: 50 })
        const list = Array.isArray(resp.data?.events) ? resp.data.events : []
        events.value = list.map(e => ({
          id: e.id,
          title: e.title,
          description: e.description,
          date: e.date,
          startTime: e.startTime,
          endTime: e.endTime,
          location: e.location,
          organiser: e.organiser,
          // Represent offline subtypes by venueType for filtering UI that shows indoor/outdoor
          format: e.format === 'offline' ? (e.venueType || 'offline') : 'online',
          type: e.type,
          region: e.region,
          price: e.price ?? 0,
          bookingSlots: e.maxParticipants ?? 0,
          image: e.imageUrl && String(e.imageUrl).trim() ? e.imageUrl : placeholderImage,
        }))
      } catch (err) {
        console.error('Failed to load events', err)
        error.value = err?.message || String(err)
        events.value = []
      } finally {
        loading.value = false
      }
    }

    onMounted(fetchEvents)

    const handleFiltersChange = (filters) => {
      console.log('Discover: Received filters:', filters)
      currentFilters.value = filters
    }

    const handleHeroSearch = () => {
      // Update the filter sidebar search when hero search is used
      currentFilters.value.search = searchTerm.value
    }

    const handleSignUp = (eventId) => {
      // Navigate to the event page with the event ID
      router.push({ name: 'Event', params: { eventId: eventId } })
    }

    const filteredEvents = computed(() => {
      let filtered = [...events.value]

      // Combine hero search and filter sidebar search
      const combinedSearch = searchTerm.value || currentFilters.value.search

      // Filter by search term
      if (combinedSearch) {
        const search = combinedSearch.toLowerCase()
        filtered = filtered.filter(event =>
          event.title.toLowerCase().includes(search) ||
          event.description.toLowerCase().includes(search) ||
          event.location.toLowerCase().includes(search)
        )
      }

      // Filter by date range
      if (currentFilters.value.dateRange.start || currentFilters.value.dateRange.end) {
        filtered = filtered.filter(event => {
          const eventDate = new Date(event.date)
          const start = currentFilters.value.dateRange.start ? new Date(currentFilters.value.dateRange.start) : null
          const end = currentFilters.value.dateRange.end ? new Date(currentFilters.value.dateRange.end) : null

          if (start && end) {
            return eventDate >= start && eventDate <= end
          } else if (start) {
            return eventDate >= start
          } else if (end) {
            return eventDate <= end
          }
          return true
        })
      }

      // Filter by timing
      if (currentFilters.value.timing.length > 0) {
        filtered = filtered.filter(event => {
          const timeStr = String(event.startTime || '')
          let hour24 = 0
          if (timeStr.includes('AM') || timeStr.includes('PM')) {
            const [time, period] = timeStr.split(' ')
            const [hours] = time.split(':').map(Number)
            hour24 = hours
            if (period === 'PM' && hours !== 12) hour24 += 12
            if (period === 'AM' && hours === 12) hour24 = 0
          } else if (timeStr.includes(':')) {
            const [hours] = timeStr.split(':').map(Number)
            hour24 = isNaN(hours) ? 0 : hours
          }

          let timingCategory = ''
          if (hour24 >= 6 && hour24 <= 11) timingCategory = 'morning'
          else if (hour24 >= 12 && hour24 <= 17) timingCategory = 'afternoon'
          else if (hour24 >= 18 && hour24 <= 21) timingCategory = 'evening'
          else timingCategory = 'night'

          return currentFilters.value.timing.includes(timingCategory)
        })
      }

      // Filter by format
      if (currentFilters.value.format.length > 0) {
        filtered = filtered.filter(event => {
          const selectedFormats = currentFilters.value.format
          const isOfflineSelected = selectedFormats.includes('offline')
          const isIndoorSelected = selectedFormats.includes('indoor')
          const isOutdoorSelected = selectedFormats.includes('outdoor')

          const isOnline = event.format === 'online'
          const isIndoor = event.format === 'indoor'
          const isOutdoor = event.format === 'outdoor'
          const isBoth = event.format === 'both'

          // Online filter
          if (selectedFormats.includes('online') && isOnline) return true

          // If offline is selected without specific sub-options, allow indoor, outdoor, both
          if (isOfflineSelected && !isIndoorSelected && !isOutdoorSelected) {
            return isIndoor || isOutdoor || isBoth
          }

          // If specific formats are selected, include 'both' as matching either
          if (isIndoorSelected && (isIndoor || isBoth)) return true
          if (isOutdoorSelected && (isOutdoor || isBoth)) return true

          // If offline + indoor + outdoor are selected, include all offline variants
          if (isOfflineSelected && isIndoorSelected && isOutdoorSelected) {
            return isIndoor || isOutdoor || isBoth
          }

          return false
        })
      }

      // Filter by type
      if (currentFilters.value.type.length > 0) {
        filtered = filtered.filter(event =>
          currentFilters.value.type.includes(event.type)
        )
      }

      // Filter by region
      if (currentFilters.value.region.length > 0) {
        const selected = currentFilters.value.region.map(r => String(r).toLowerCase())
        filtered = filtered.filter(event => selected.includes(String(event.region).toLowerCase()))
      }

      // Filter by price range
      if (currentFilters.value.priceRange[0] > 0 || currentFilters.value.priceRange[1] < 500) {
        filtered = filtered.filter(event => {
          const eventPrice = event.price
          return eventPrice >= currentFilters.value.priceRange[0] && eventPrice <= currentFilters.value.priceRange[1]
        })
      }

      return filtered
    })

    const first = ref(0)
    const rows = ref(12)

    const onPageChange = (e) => {
      first.value = e.first
      rows.value = e.rows
      try { eventsGridRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' }) } catch {}
    }

    const pagedEvents = computed(() => {
      return filteredEvents.value.slice(first.value, first.value + rows.value)
    })

    return {
      componentName,
      searchTerm,
      heroRef,
      eventsGridRef,
      currentFilters,
      events,
      filteredEvents,
      pagedEvents,
      first,
      rows,
      onPageChange,
      handleFiltersChange,
      handleHeroSearch,
      handleSignUp
    }
  }
}
</script>

<template>
  <div class="discover-page">
    <!-- Main Content -->
    <div class="main-content">
      <!-- Hero Section -->
      <section class="hero" ref="heroRef">
        <div class="hero-content">
          <h1>Explore Events</h1>
          <p>Find and register for the most exciting events happening near you</p>

          <div class="search-bar">
            <input
              type="text"
              placeholder="Search events..."
              v-model="searchTerm"
              @keyup.enter="handleHeroSearch"
              class="search-input"
            >
            <button @click="handleHeroSearch">Search</button>
          </div>
        </div>
      </section>

      <!-- Events Section -->
      <section class="events-section">
        <div class="events-header">
          <h2>Discover Events</h2>
          <p class="results-count">
            {{ filteredEvents.length }} events found
          </p>
        </div>

        <!-- Events Grid -->
      <div class="events-layout">
        <!-- Filter Sidebar -->
        <aside class="sidebar">
          <EventFilterSidebar @filtersChanged="handleFiltersChange" />
        </aside>

        <!-- Events content column (grid + pagination) -->
        <div class="events-content">
          <div class="events-grid" ref="eventsGridRef">
            <div
              v-for="event in pagedEvents"
              :key="event.id"
              class="event-card"
            >
              <Card>
                <template #header>
                  <div class="event-image">
                    <img :src="event.image" :alt="event.title" />
                  </div>
                </template>
                <template #title>{{ event.title }}</template>
                <template #subtitle>
                  <div class="event-meta">
                    <span class="event-date">{{ event.date }} at {{ event.startTime }} - {{ event.endTime }}</span>
                    <span class="event-location"><span class="material-symbols-outlined">location_on</span> {{ event.location }}</span>
                    <span class="event-organiser"><span class="material-symbols-outlined">person</span> {{ event.organiser }}</span>
                    <span class="event-slots"><span class="material-symbols-outlined">confirmation_number</span>  {{ event.bookingSlots }}</span>
                    <span class="event-price"><span class="material-symbols-outlined">attach_money</span>  {{ event.price }}</span>
                  </div>
                </template>
                <template #content>
                  <p class="event-description">{{ event.description }}</p>
                  <div class="event-tags">
                    <Tag :value="event.format" severity="secondary" class="format-tag" />
                    <Tag :value="event.type" severity="secondary" class="format-tag" />
                    <Tag :value="event.region" severity="secondary" class="format-tag" />
                  </div>
                </template>
                <template #footer>
                  <Button
                    label="Sign Up"
                    class="p-button-primary signup-btn"
                    icon="pi pi-calendar-plus"
                    @click="handleSignUp(event.id)"
                  />
                </template>
              </Card>
            </div>
          </div>

          <div class="events-pagination">
            <Paginator
              :first="first"
              :rows="rows"
              :totalRecords="filteredEvents.length"
              :rowsPerPageOptions="[6,12,24,48]"
              @page="onPageChange"
            />
          </div>
        </div>
      </div>

        <!-- No Results Message -->
        <div v-if="filteredEvents.length === 0" class="no-results">
          <h3>No events found</h3>
          <p>Try adjusting your search criteria or filters to find more events.</p>
        </div>
      </section>
    </div>
  </div>

</template>

<style scoped>
.discover-page {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}

/* Hero section */
.hero {
  background: #EC7600;
  padding: 60px 20px;
  text-align: center;
  color: white;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero h1 {
  font-size: 3.2em;
  margin-bottom: 20px;
  font-weight: 700;
}

.hero p {
  font-size: 1.3em;
  margin-bottom: 40px;
  opacity: 0.95;
}

.search-bar {
  background: white;
  padding: 15px 25px;
  border-radius: 50px;
  display: flex;
  max-width: 500px;
  margin: 0 auto 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.search-bar input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1.1em;
  color: #333;
  background: transparent;
}

.search-bar .search-input {
  color: #333; /* Ensure search text is visible */
}

.search-bar button {
  background: #FFC67B;
  border: none;
  padding: 8px 20px;
  border-radius: 25px;
  color: #333;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s ease;
}

.search-bar button:hover {
  background: #FFB85C;
}

/* Events Section */
.events-section {
  padding: 40px 20px;
  background-color: #f9fafb;
}

.events-header {
  max-width: 1200px;
  margin: 0 auto 30px;
}

.events-header h2 {
  font-size: 2.5em;
  color: #111827;
  margin-bottom: 10px;
  font-weight: 700;
}

.results-count {
  color: #6b7280;
  font-size: 1.1em;
  margin: 0;
}

.events-layout {
  display: flex;
  gap: 20px;
  /* max-width: 1200px; */
  margin: 0 auto;
  align-items: flex-start;
}

.sidebar {
  flex: 0 0 280px; /* increased width for better layout */
  top: 25px;
  position: sticky;
  align-self: flex-start;
  height: fit-content;
  max-height: calc(100vh - 100px); /* Adjust based on header height */
  overflow-y: auto;
}

.events-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.events-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.events-pagination {
  margin-top: 16px;
}

.events-pagination :deep(.p-paginator) {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.event-card {
  width: 100%;
  transition: transform 0.2s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.event-card:hover {
  transform: translateY(-2px);
}

.event-card :deep(.p-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.event-card :deep(.p-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.event-card :deep(.p-card-content) {
  flex: 1;
}

.event-image {
  height: 200px;
  overflow: hidden;
  border-radius: 6px 6px 0 0;
}

.event-image img {
  width: 100%;
  object-fit: cover;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.9em;
  color: #6b7280;
}

.event-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-date {
  font-weight: 600;
}

.event-location {
  color: #9ca3af;
}

.event-description {
  color: #4b5563;
  line-height: 1.6;
  margin: 10px 0;
}

.event-tags {
  display: flex;
  gap: 8px;
  margin-top: 15px;
}

.format-tag {
  background-color: lightblue !important;
}

.signup-btn {
  width: 100%;
  background-color: #EC7600 !important;
  border-color: #EC7600 !important;
  font-weight: 600;
}

.signup-btn:hover {
  background-color: #d97706 !important;
  border-color: #d97706 !important;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
  max-width: 600px;
  margin: 0 auto;
}

.no-results h3 {
  font-size: 1.8em;
  color: #374151;
  margin-bottom: 10px;
}

.no-results p {
  color: #6b7280;
  font-size: 1.1em;
}

/* Material Symbols */
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-variation-settings:
  'FILL' 0,
  'wght' 400,
  'GRAD' 0,
  'opsz' 24;
  font-size: 1rem;
}

/* Responsive design */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
  }
  
  .events-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5em;
  }
  
  .hero p {
    font-size: 1.1em;
  }
  
  .events-header h2 {
    font-size: 2em;
  }
  
  .events-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 480px) {
  .hero {
    padding: 40px 20px;
  }
  
  .hero h1 {
    font-size: 2em;
  }
  
  .search-bar {
    padding: 12px 20px;
  }
  
  .events-section {
    padding: 30px 15px;
  }
}
</style>