<template>
  <div class="event-detail">
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
              Join us for this exciting {{ event.type }} event! Whether you're a beginner or experienced participant, 
              this {{ event.format }} event welcomes all skill levels. Don't miss out on this amazing opportunity 
              to connect with fellow enthusiasts in the {{ event.region }} region.
            </p>
          </div>

          <!-- Event Highlights -->
          <!-- <div class="highlights-section">
            <h3>Event Highlights</h3>
            <div class="highlights-grid">
              <div class="highlight-item">
                <i class="pi pi-users"></i>
                <span>All Skill Levels Welcome</span>
              </div>
              <div class="highlight-item">
                <i class="pi pi-trophy"></i>
                <span>Competitive Tournament</span>
              </div>
              <div class="highlight-item">
                <i class="pi pi-heart"></i>
                <span>Community Building</span>
              </div>
              <div class="highlight-item">
                <i class="pi pi-star"></i>
                <span>Professional Organization</span>
              </div>
            </div>
          </div> -->
        </div>

        <!-- Right Column - Booking & Info -->
        <div class="sidebar">
          <!-- Booking Card -->
          <div class="booking-card">
            <div class="price-section">
              <div class="price-label">Event Registration</div>
              <div class="price-value">Free Event</div>
            </div>
            
            <Button 
              class="book-button" 
              @click="handleBooking"
              :loading="isBooking"
            >
              <i class="pi pi-ticket"></i>
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
            <h3>Event Organizer</h3>
            <div class="organizer-info">
              <img src="https://via.placeholder.com/60x60/ff6b35/white?text=ORG" alt="Organizer" class="organizer-avatar">
              <div class="organizer-details">
                <h4>Sports Center Management</h4>
                <p>Professional event organizers with 10+ years of experience</p>
              </div>
            </div>
            <!-- <Button class="contact-button" outlined>
              <i class="pi pi-envelope"></i>
              <span>Contact Organizer</span>
            </Button> -->
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
      required: false,
      default: 1
    }
  },
  data() {
    return {
      isBooking: false,
      event: {
        id: 1,
        title: 'Basketball Tournament',
        date: 'Oct 15, 2024',
        location: 'Sports Center',
        description: 'Annual basketball tournament for all skill levels.',
        format: 'Indoor',
        type: 'Sports',
        region: 'North',
        image: 'https://images.unsplash.com/photo-1546519638-68e109498ffc?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2340&q=80'
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
    
    fetchEventData(eventId) {
      // In a real app, you would fetch event data from an API
      console.log('Fetching event data for ID:', eventId);
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

/* Highlights Section */
/* .highlights-section {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
} */

/* .highlights-section h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 24px;
}

.highlights-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
} */

/* .highlight-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.highlight-item:hover {
  background: #fff5f0;
  transform: translateX(4px);
}

.highlight-item i {
  color: #ff6b35;
  font-size: 1.1rem;
}

.highlight-item span {
  font-weight: 500;
  color: #333;
} */

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

/* .contact-button {
  width: 100%;
  border-color: #ff6b35 !important;
  color: #ff6b35 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 8px !important;
} */

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