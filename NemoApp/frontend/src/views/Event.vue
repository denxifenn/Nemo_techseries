<template>
  <div class="event-detail">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Loading event details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <h2>Error</h2>
      <p>{{ error }}</p>
      <button @click="$router.go(-1)" class="back-button">Go Back</button>
    </div>

    <!-- Event Content -->
    <div v-else-if="event">
      <!-- Hero Section with Image -->
      <div class="hero-section">
        <div class="hero-image-container">
          <img :src="event.image" :alt="event.title" class="hero-image">
          <div class="hero-overlay">
            <div class="hero-content">
              <h1 class="hero-title">{{ event.title }}</h1>
              <p class="hero-subtitle">{{ event.description }}</p>
            </div>
          </div>
        </div>
      </div>

    <!-- Main Content Container -->
    <div class="content-container">
      <div class="content-grid">
        <!-- Left Column - Event Information -->
        <div class="main-content">
          <!-- Event Meta Cards -->
          <div class="meta-cards">
            <div class="meta-card">
              <div class="meta-icon">
                 <span class="material-symbols-outlined">schedule</span>
              </div>
              <div class="meta-content">
                <span class="meta-label">Date & Time</span>
                <span class="meta-value">{{ event.date }}</span>
              </div>
            </div>

            <div class="meta-card">
              <div class="meta-icon">
                <span class="material-symbols-outlined">location_on</span>
              </div>
              <div class="meta-content">
                <span class="meta-label">Location</span>
                <span class="meta-value">{{ event.location }}</span>
              </div>
            </div>

            <div class="meta-card">
              <div class="meta-icon">
                 <span class="material-symbols-outlined">map</span>
              </div>
              <div class="meta-content">
                <span class="meta-label">Region</span>
                <span class="meta-value">{{ event.region }}</span>
              </div>
            </div>

            <div class="meta-card">
              <div class="meta-icon">
                 <span class="material-symbols-outlined">event_note</span>
              </div>
              <div class="meta-content">
                <span class="meta-label">Format</span>
                <span class="meta-value">{{ event.format }}</span>
              </div>
            </div>
          </div>

          <!-- Event Description -->
          <div class="description-section">
            <h2>About This Event</h2>
            <p class="event-description">{{ event.description }}</p>
            <p class="additional-info">
              Join us for this exciting event! Don't miss out on this amazing opportunity 
              to connect with fellow enthusiasts in the {{ event.region }} region.
            </p>
          </div>
        </div>

        <!-- Right Column - Booking & Info -->
        <div class="sidebar">
          <!-- Booking Card -->
          <div class="booking-card">
            <div class="price-section">
              <div class="price-label">Event Registration</div>
            </div>
            
            <Button 
              class="book-button" 
              @click="handleBooking"
              :loading="isBooking"
            >
              
              <span>Register Now</span>
            </Button>

            <!-- <div class="booking-info">
              <div class="info-item">
                <i class="pi pi-clock"></i>
              </div>
              <div class="info-item">
                <i class="pi pi-check-circle"></i>
              </div>
            </div> -->
          </div>

          <!-- Organizer Card -->
          <div class="organizer-card">
            <h3>Event Organiser</h3>
            <div class="organizer-info">
              <div class="organizer-avatar">
                <span class="material-symbols-outlined">person</span>
              </div>
              <div class="organizer-details">
                <h4>Sports Center Management</h4>
              </div>
            </div>
          </div>

          <!-- Additional Info Card
          <div class="info-card">
            <h3>Good to Know</h3>
            <div class="info-list">
              <div class="info-item">
                <i class="pi pi-info-circle"></i>
                <span>Bring your own equipment</span>
              </div>
              <div class="info-item">
                <i class="pi pi-shield"></i>
                <span>Safety measures in place</span>
              </div>
              <div class="info-item">
                <i class="pi pi-car"></i>
                <span>Parking available on-site</span>
              </div>
              <div class="info-item">
                <i class="pi pi-refresh"></i>
                <span>Flexible cancellation policy</span>
              </div>
            </div>
          </div> -->
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import Button from 'primevue/button';

export default {
  name: 'EventDetail',
  components: {
    Button
  },
  props: {
    eventId: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      isBooking: false,
      event: null,
      loading: true,
      error: null
    }
  },
  watch: {
    eventId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.fetchEventData(newId)
        }
      }
    }
  },
  methods: {
    async handleBooking() {
      this.isBooking = true;
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        this.$emit('book-event', this.event);

        // Show success message (you can replace this with a toast notification)
        alert('Successfully registered for the event!');
      } catch (error) {
        console.error('Booking failed:', error);
        alert('Registration failed. Please try again.');
      } finally {
        this.isBooking = false;
      }
    },

    async fetchEventData(eventId) {
      this.loading = true;
      this.error = null;

      try {
        // Mock data - in a real app, this would be an API call
        const mockEvents = [
          {
            id: 1,
            title: 'Basketball Tournament',
            date: 'Oct 15, 2025',
            location: 'Sports Center',
            description: 'Annual basketball tournament for all skill levels.',
            format: 'indoor',
            type: 'sports',
            region: 'North',
            image: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80'
          },
          {
            id: 2,
            title: 'Art Exhibition',
            date: 'Oct 20, 2025',
            location: 'Gallery Downtown',
            description: 'Unique art exhibition featuring local artists.',
            format: 'indoor',
            type: 'arts',
            region: 'South',
            image: 'https://images.unsplash.com/photo-1518998053901-5348d3961a04?q=80&w=1074&auto=format&fit=crop'
          },
          {
            id: 3,
            title: 'Virtual Cooking Class',
            date: 'Oct 18, 2024',
            location: 'Online',
            description: 'Learn to cook traditional dishes from home.',
            format: 'online',
            type: 'workshop',
            region: 'North',
            image: 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?q=80&w=1170&auto=format&fit=crop'
          },
          {
            id: 4,
            title: 'Outdoor Yoga',
            date: 'Oct 22, 2025',
            location: 'Central Park',
            description: 'Morning yoga session in the park.',
            format: 'outdoor',
            type: 'sports',
            region: 'Central',
            image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=250&fit=crop'
          },
          {
            id: 5,
            title: 'Music Festival',
            date: 'Oct 25, 2025',
            location: 'City Park',
            description: 'Two-day music festival featuring various artists.',
            format: 'outdoor',
            type: 'music',
            region: 'West',
            image: 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=400&h=250&fit=crop'
          },
          {
            id: 6,
            title: 'Tech Webinar',
            date: 'Oct 30, 2025',
            location: 'Online',
            description: 'Learn about the latest technology trends.',
            format: 'online',
            type: 'workshop',
            region: 'East',
            image: 'https://images.unsplash.com/photo-1550622824-c11e494a4b65?q=80&w=1173&auto=format&fit=crop'
          },
          {
            id: 7,
            title: 'Jazz Night Live',
            date: 'Nov 5, 2025',
            location: 'Blue Note Jazz Club',
            description: 'An evening of smooth jazz with local and international artists.',
            format: 'indoor',
            type: 'music',
            region: 'Central',
            image: 'https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400&h=250&fit=crop'
          },
          {
            id: 8,
            title: 'Modern Dance Performance',
            date: 'Nov 8, 2025',
            location: 'City Theater',
            description: 'Contemporary dance showcase featuring innovative choreography.',
            format: 'indoor',
            type: 'performance',
            region: 'West',
            image: 'https://images.unsplash.com/photo-1499439398383-cfcbab21207d?q=80&w=1176&auto=format&fit=crop'
          },
          {
            id: 9,
            title: 'Digital Photography Workshop',
            date: 'Nov 12, 2025',
            location: 'Community Center',
            description: 'Hands-on workshop covering composition, lighting, and editing techniques.',
            format: 'indoor',
            type: 'workshop',
            region: 'North',
            image: 'https://images.unsplash.com/photo-1548502499-ef49e8cf98d4?q=80&w=1170&auto=format&fit=crop'
          },
          {
            id: 10,
            title: 'Historic City Walking Tour',
            date: 'Nov 15, 2025',
            location: 'Old Town Square',
            description: 'Explore the city\'s rich history with a knowledgeable local guide.',
            format: 'outdoor',
            type: 'tours',
            region: 'Central',
            image: 'https://images.unsplash.com/photo-1654738366489-8e50a99e0469?q=80&w=1176&auto=format&fit=crop'
          },
          {
            id: 11,
            title: 'Beach Volleyball Championship',
            date: 'Nov 18, 2024',
            location: 'Sunny Beach Resort',
            description: 'Annual beach volleyball tournament with teams from across the region.',
            format: 'outdoor',
            type: 'sports',
            region: 'South',
            image: 'https://images.unsplash.com/photo-1592656094267-764a45160876?q=80&w=1170&auto=format&fit=crop'
          },
          {
            id: 12,
            title: 'International Food Festival',
            date: 'Nov 22, 2024',
            location: 'Riverside Park',
            description: 'Celebrate global cuisines with food stalls, cooking demonstrations, and cultural performances.',
            format: 'outdoor',
            type: 'culture',
            region: 'East',
            image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=250&fit=crop'
          }
        ];

        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 500));

        const event = mockEvents.find(e => e.id === parseInt(eventId));

        if (event) {
          this.event = event;
        } else {
          this.error = 'Event not found';
        }
      } catch (error) {
        console.error('Error fetching event data:', error);
        this.error = 'Failed to load event data';
      } finally {
        this.loading = false;
      }
    }
  },

}
</script>

<style scoped>
.event-detail {
  min-height: 100vh;
  background-color: #fafafa;
}

/* Hero Section */
.hero-section {
  position: relative;
  height: 500px;
  overflow: hidden;
}

.hero-image-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.hero-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.3) 0%,
    rgba(0, 0, 0, 0.5) 70%,
    rgba(0, 0, 0, 0.7) 100%
  );
  display: flex;
  align-items: flex-end;
  padding: 60px;
}

.hero-content {
  color: white;
  max-width: 800px;
}

.event-badge {
  display: inline-block;
  background-color: #ff6b35;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: 0.5px;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  line-height: 1.5;
}

/* Content Container */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 60px;
}

/* Main Content */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* Meta Cards */
.meta-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.meta-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.meta-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.meta-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #ff6b35, #ff8c42);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
}

.meta-content {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 4px;
}

.meta-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

/* Description Section */
.description-section {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.description-section h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
}

.event-description {
  font-size: 1.1rem;
  line-height: 1.7;
  color: #555;
  margin-bottom: 16px;
}

.additional-info {
  font-size: 1rem;
  line-height: 1.6;
  color: #666;
}

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Booking Card */
.booking-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
  position: sticky;
  top: 20px;
}

.price-section {
  text-align: center;
  margin-bottom: 24px;
}

.price-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 8px;
}

.price-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #ff6b35;
}

.book-button {
  width: 100%;
  background: linear-gradient(135deg, #ff6b35, #ff8c42) !important;
  border: none !important;
  padding: 16px !important;
  font-size: 1.1rem !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
}

.book-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3) !important;
}

.booking-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Organizer Card */
.organizer-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.organizer-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
}

.organizer-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.organizer-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid #ff6b35;
  background: linear-gradient(135deg, #ff6b35, #ff8c42);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
}

.organizer-details h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.organizer-details p {
  font-size: 0.875rem;
  color: #666;
  line-height: 1.4;
}

/* Info Card */
.info-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.info-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 16px;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.9rem;
  color: #555;
}

.info-item i {
  color: #ff6b35;
  font-size: 1rem;
}

/* GOOGLE */
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-variation-settings:
  'FILL' 0,
  'wght' 400,
  'GRAD' 0,
  'opsz' 24;
}

/* Loading and Error States */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff6b35;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
  gap: 20px;
}

.error-container h2 {
  color: #ff6b35;
  font-size: 2rem;
  margin: 0;
}

.error-container p {
  color: #666;
  font-size: 1.1rem;
  margin: 0;
}

.back-button {
  background: linear-gradient(135deg, #ff6b35, #ff8c42);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: 40px;
  }
  
  .sidebar {
    order: -1;
  }
  
  .booking-card {
    position: static;
  }
}

@media (max-width: 768px) {
  .hero-overlay {
    padding: 30px 20px;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.1rem;
  }
  
  .content-container {
    padding: 40px 15px;
  }
  
  .meta-cards {
    grid-template-columns: 1fr;
  }
  
  .highlights-grid {
    grid-template-columns: 1fr;
  }
  
  .description-section,
  .highlights-section,
  .booking-card,
  .organizer-card,
  .info-card {
    padding: 24px;
  }
}
</style>