<script>
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Card from 'primevue/card'
import { ref, computed, onMounted } from 'vue'
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
    
    const currentFilters = ref({
      search: '',
      format: [],
      type: []
    })

    // Sample events data - replace with your API call
    const events = ref([
      {
        id: 1,
        title: 'Basketball Tournament',
        date: 'Oct 15, 2024',
        location: 'Sports Center',
        description: 'Annual basketball tournament for all skill levels.',
        format: 'indoor',
        type: 'sports',
        image: 'https://via.placeholder.com/300x200'
      },
      {
        id: 2,
        title: 'Art Exhibition',
        date: 'Oct 20, 2024',
        location: 'Gallery Downtown',
        description: 'Contemporary art exhibition featuring local artists.',
        format: 'indoor',
        type: 'arts',
        image: 'https://via.placeholder.com/300x200'
      },
      {
        id: 3,
        title: 'Virtual Cooking Class',
        date: 'Oct 18, 2024',
        location: 'Online',
        description: 'Learn to cook traditional dishes from home.',
        format: 'online',
        type: 'culture',
        image: 'https://via.placeholder.com/300x200'
      },
      {
        id: 4,
        title: 'Outdoor Yoga',
        date: 'Oct 22, 2024',
        location: 'Central Park',
        description: 'Morning yoga session in the park.',
        format: 'outdoor',
        type: 'sports',
        image: 'https://via.placeholder.com/300x200'
      },
      {
        id: 5,
        title: 'Music Festival',
        date: 'Oct 25, 2024',
        location: 'City Park',
        description: 'Three-day music festival featuring various artists.',
        format: 'outdoor',
        type: 'arts',
        image: 'https://via.placeholder.com/300x200'
      },
      {
        id: 6,
        title: 'Tech Webinar',
        date: 'Oct 30, 2024',
        location: 'Online',
        description: 'Learn about the latest technology trends.',
        format: 'online',
        type: 'culture',
        image: 'https://via.placeholder.com/300x200'
      }
    ])

    const handleFiltersChange = (filters) => {
      currentFilters.value = filters
    }

    const handleHeroSearch = () => {
      // Update the filter sidebar search when hero search is used
      currentFilters.value.search = searchTerm.value
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

      // Filter by format
      if (currentFilters.value.format.length > 0) {
        filtered = filtered.filter(event =>
          currentFilters.value.format.includes(event.format)
        )
      }

      // Filter by type
      if (currentFilters.value.type.length > 0) {
        filtered = filtered.filter(event =>
          currentFilters.value.type.includes(event.type)
        )
      }

      return filtered
    })

    return {
      componentName,
      searchTerm,
      heroRef,
      currentFilters,
      events,
      filteredEvents,
      handleFiltersChange,
      handleHeroSearch
    }

    onMounted(() => {
      if (heroRef.value) {
        console.log('Hero height:', heroRef.value.offsetHeight)
      }
    })
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
        <div class="events-grid">
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
                  <span class="event-date">{{ event.date }}</span>
                  <span class="event-location">📍 {{ event.location }}</span>
                </div>
              </template>
              <template #content>
                <p class="event-description">{{ event.description }}</p>
                <div class="event-tags">
                  <Tag :value="event.format" severity="info" class="format-tag" />
                  <Tag :value="event.type" severity="success" class="type-tag" />
                </div>
              </template>
              <template #footer>
                <Button 
                  label="Sign Up" 
                  class="p-button-primary signup-btn" 
                  icon="pi pi-calendar-plus"
                />
              </template>
            </Card>
          </div>
        </div>

        <!-- No Results Message -->
        <div v-if="filteredEvents.length === 0" class="no-results">
          <h3>No events found</h3>
          <p>Try adjusting your search criteria or filters to find more events.</p>
        </div>
      </section>

      <!-- Filter Sidebar -->
      <EventFilterSidebar @filtersChanged="handleFiltersChange" />
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
  margin-left: 280px; /* Match sidebar width */
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

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  max-width: 1200px;
  margin: 0 auto;
}

.event-card {
  height: fit-content;
  transition: transform 0.2s ease;
}

.event-card:hover {
  transform: translateY(-2px);
}

.event-image {
  height: 200px;
  overflow: hidden;
  border-radius: 6px 6px 0 0;
}

.event-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.9em;
  color: #6b7280;
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
  background-color: #3b82f6 !important;
}

.type-tag {
  background-color: #10b981 !important;
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