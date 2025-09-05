<script>
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Card from 'primevue/card'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import EventFilterSidebar from '../components/EventFilterSidebar.vue'

export default {
  name: 'Discover',
  components: {
    Button,
    Tag,
    Card,
    EventFilterSidebar
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

    // Sample events data - replace with your API call
    const events = ref([
      {
        id: 1,
        title: 'Basketball Tournament',
        date: 'Oct 15, 2025',
        startTime: '2:00 PM',
        endTime: '6:00 PM',
        location: 'MPC@Khatib',
        organiser: 'Active Sports Club',
        status: 'active',
        bookingSlots: 50,
        description: 'Annual basketball tournament for all skill levels.',
        format: 'indoor',
        type: 'sports',
        region: 'North',
        price: 35,
        image: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=250&fit=crop'
      },
      {
        id: 2,
        title: 'Art Exhibition',
        date: 'Oct 20, 2025',
        startTime: '10:00 AM',
        endTime: '5:00 PM',
        location: 'National Gallery',
        organiser: 'Art Society',
        status: 'active',
        bookingSlots: 100,
        description: 'Unique art exhibition featuring local artists.',
        format: 'indoor',
        type: 'arts',
        region: 'South',
        price: 0,
        image: 'https://images.unsplash.com/photo-1518998053901-5348d3961a04?q=80&w=1074&auto=format&fit=crop'
      },
      {
        id: 3,
        title: 'Virtual Cooking Class',
        date: 'Sept 18, 2025',
        startTime: '6:00 PM',
        endTime: '8:00 PM',
        location: 'Online',
        organiser: 'Culinary Institute',
        status: 'active',
        bookingSlots: 30,
        description: 'Learn to cook traditional dishes from home.',
        format: 'online',
        type: 'workshop',
        region: 'North',
        price: 50,
        image: 'https://images.unsplash.com/photo-1544325718-488a5064cfeb?q=80&w=1172&auto=format&fit=crop'
      },
      {
        id: 4,
        title: 'Outdoor Yoga',
        date: 'Sept 16, 2025',
        startTime: '8:00 AM',
        endTime: '9:30 AM',
        location: 'Bishan Park',
        organiser: 'Wellness Center',
        status: 'active',
        bookingSlots: 25,
        description: 'Morning yoga session in the park.',
        format: 'outdoor',
        type: 'sports',
        region: 'Central',
        price: 0,
        image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=250&fit=crop'
      },
      {
        id: 5,
        title: 'Music Festival',
        date: 'Sept 29, 2025',
        startTime: '7:00 PM',
        endTime: '11:00 PM',
        location: 'Sentosa',
        organiser: 'Music Events Co.',
        status: 'active',
        bookingSlots: 200,
        description: 'Two-day music festival featuring various artists.',
        format: 'outdoor',
        type: 'music',
        region: 'South',
        price: 120,
        image: 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=400&h=250&fit=crop'
      },
      {
        id: 6,
        title: 'Tech Webinar',
        date: 'Oct 12, 2025',
        startTime: '3:00 PM',
        endTime: '4:30 PM',
        location: 'Online',
        organiser: 'Tech Hub',
        status: 'active',
        bookingSlots: 150,
        description: 'Learn about the latest technology trends.',
        format: 'online',
        type: 'workshop',
        region: 'East',
        price: 0,
        image: 'https://images.unsplash.com/photo-1550622824-c11e494a4b65?q=80&w=1173&auto=format&fit=crop'
      },
      {
        id: 7,
        title: 'Jazz Night Live',
        date: 'Nov 1, 2025',
        startTime: '8:00 PM',
        endTime: '11:00 PM',
        location: 'Blue Note Jazz Club',
        organiser: 'Jazz Society',
        status: 'active',
        bookingSlots: 80,
        description: 'An evening of smooth jazz with local and international artists.',
        format: 'indoor',
        type: 'music',
        region: 'Central',
        price: 80,
        image: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=250&fit=crop'
      },
      {
        id: 8,
        title: 'Modern Dance Performance',
        date: 'Nov 8, 2025',
        startTime: '7:30 PM',
        endTime: '9:30 PM',
        location: 'City Theater',
        organiser: 'Dance Collective',
        status: 'active',
        bookingSlots: 120,
        description: 'Contemporary dance showcase featuring innovative choreography.',
        format: 'indoor',
        type: 'performance',
        region: 'West',
        price: 35,
        image: 'https://images.unsplash.com/photo-1499439398383-cfcbab21207d?q=80&w=1176&auto=format&fit=crop'
      },
      {
        id: 9,
        title: 'Digital Photography Workshop',
        date: 'Nov 12, 2024',
        startTime: '10:00 AM',
        endTime: '4:00 PM',
        location: 'Woodlands CC',
        organiser: 'Photo Academy',
        status: 'active',
        bookingSlots: 25,
        description: 'Hands-on workshop covering composition, lighting, and editing techniques.',
        format: 'indoor',
        type: 'workshop',
        region: 'North',
        price: 50,
        image: 'https://images.unsplash.com/photo-1548502499-ef49e8cf98d4?q=80&w=1170&auto=format&fit=crop'
      },
      {
        id: 10,
        title: 'Heritage Walking Tour',
        date: 'Nov 15, 2025',
        startTime: '9:00 AM',
        endTime: '12:00 PM',
        location: 'Changi',
        organiser: 'Heritage Tours',
        status: 'active',
        bookingSlots: 40,
        description: 'Explore the city\'s rich heritage with a knowledgeable local guide.',
        format: 'outdoor',
        type: 'tours',
        region: 'East',
        price: 75,
        image: 'https://images.unsplash.com/photo-1654738366489-8e50a99e0469?q=80&w=1176&auto=format&fit=crop'
      },
      {
        id: 11,
        title: 'Beach Volleyball Championship',
        date: 'Nov 17, 2025',
        startTime: '8:00 AM',
        endTime: '6:00 PM',
        location: 'Palawan Beach',
        organiser: 'Volleyball Association',
        status: 'active',
        bookingSlots: 200,
        description: 'Annual beach volleyball tournament.',
        format: 'outdoor',
        type: 'sports',
        region: 'South',
        price: 0,
        image: 'https://images.unsplash.com/photo-1592656094267-764a45160876?q=80&w=1170&auto=format&fit=crop'
      },
      {
        id: 12,
        title: 'International Food Festival',
        date: 'Nov 22, 2025',
        startTime: '11:00 AM',
        endTime: '9:00 PM',
        location: 'Riverside Park',
        organiser: 'Culinary Events Co.',
        status: 'active',
        bookingSlots: 300,
        description: 'Celebrate global cuisines with food stalls, cooking demonstrations, and cultural performances.',
        format: 'outdoor',
        type: 'culture',
        region: 'East',
        price: 150,
        image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=250&fit=crop'
      }
    ])

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
          const timeStr = event.startTime
          const [time, period] = timeStr.split(' ')
          const [hours, minutes] = time.split(':').map(Number)
          let hour24 = hours
          if (period === 'PM' && hours !== 12) hour24 += 12
          if (period === 'AM' && hours === 12) hour24 = 0

          let timingCategory = ''
          if (hour24 >= 5 && hour24 < 12) timingCategory = 'morning'
          else if (hour24 >= 12 && hour24 < 16) timingCategory = 'afternoon'
          else if (hour24 >= 16 && hour24 < 19) timingCategory = 'evening'
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

          // If offline is selected, include both indoor and outdoor
          if (isOfflineSelected && !isIndoorSelected && !isOutdoorSelected) {
            return event.format === 'indoor' || event.format === 'outdoor'
          }

          // If specific formats are selected, match them exactly
          if (isIndoorSelected && event.format === 'indoor') return true
          if (isOutdoorSelected && event.format === 'outdoor') return true
          if (selectedFormats.includes('online') && event.format === 'online') return true

          // If offline + indoor are selected, show only indoor
          if (isOfflineSelected && isIndoorSelected && !isOutdoorSelected) {
            return event.format === 'indoor'
          }

          // If offline + outdoor are selected, show only outdoor
          if (isOfflineSelected && isOutdoorSelected && !isIndoorSelected) {
            return event.format === 'outdoor'
          }

          // If offline + indoor + outdoor are selected, show both
          if (isOfflineSelected && isIndoorSelected && isOutdoorSelected) {
            return event.format === 'indoor' || event.format === 'outdoor'
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
        filtered = filtered.filter(event =>
          currentFilters.value.region.includes(event.region)
        )
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

    return {
      componentName,
      searchTerm,
      heroRef,
      eventsGridRef,
      currentFilters,
      events,
      filteredEvents,
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
        <div class="events-grid" ref="eventsGridRef">
          <div 
            v-for="event in filteredEvents" 
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
                  <!-- <span class="event-organiser">👤 {{ event.organiser }}</span> -->
                  <!-- <span class="event-slots">🎫 {{ event.bookingSlots }}</span> -->
                  <!-- <span class="event-price">{{ event.price === 0 ? '🆓 Free' : `💰 $${event.price}` }}</span> -->
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

.events-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
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