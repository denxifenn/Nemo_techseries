<template>
  <ProfileNavBar />

  <div class="bookings-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">MY BOOKINGS</h1>
    </div>

    <!-- Bookings Grid -->
    <div class="bookings-grid">
      <Card 
        v-for="booking in bookings" 
        :key="booking.id"
        class="booking-card"
      >
        <template #content>
          <div class="booking-content">
            <!-- Profile Image -->
            <div class="booking-avatar">
              <Avatar 
                :image="booking.avatar" 
                :label="booking.initials"
                size="large"
                shape="circle"
                class="avatar"
              />
            </div>

            <!-- Booking Info -->
            <div class="booking-info">
              <h3 class="booking-name">{{ booking.name }}</h3>
              <p class="booking-role">{{ booking.role }}</p>
              <p class="booking-company">{{ booking.company }}</p>
              <div class="booking-stats">
                <span class="stat">
                  <i class="pi pi-users"></i>
                  {{ booking.mutualFriends }} mutual
                </span>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="booking-actions">
              <Button
                label="More Info"
                icon="pi pi-info-circle"
                size="small"
                @click="viewProfile(booking)"
                class="action-btn"
              />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Profile Dialog -->
    <Dialog 
      v-model:visible="showProfileDialog"
      :header="selectedBooking?.name"
      modal
      class="profile-dialog"
      :style="{ width: '600px' }"
    >
      <div v-if="selectedBooking" class="profile-details">
        <div class="profile-header">
          <Avatar 
            :image="selectedBooking.avatar" 
            :label="selectedBooking.initials"
            size="xlarge"
            shape="circle"
          />
          <div class="profile-basic-info">
            <h2>{{ selectedBooking.name }}</h2>
            <p class="role">{{ selectedBooking.role }}</p>
            <p class="company">{{ selectedBooking.company }}</p>
          </div>
        </div>

        <Divider />

        <div class="profile-sections">
          <div class="section">
            <h4><i class="pi pi-user"></i> About</h4>
            <p>{{ selectedBooking.bio }}</p>
          </div>

          <div class="section">
            <h4><i class="pi pi-heart"></i> Interests</h4>
            <div class="interests">
              <Tag 
                v-for="interest in selectedBooking.interests"
                :key="interest"
                :value="interest"
                severity="info"
                class="interest-tag"
              />
            </div>
          </div>

          <div class="section">
            <h4><i class="pi pi-users"></i> Network</h4>
            <p>{{ selectedBooking.mutualFriends }} mutual friends</p>
            <p>{{ selectedBooking.totalConnections }} total connections</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-actions">
          <Button
            label="Close"
            severity="secondary"
            @click="closeProfile"
            class="close-btn"
          />
        </div>
      </template>
    </Dialog>

    <!-- Toast for notifications -->
    <Toast ref="toast" />
  </div>
</template>

<script>
import ProfileNavBar from "@/components/ProfileNavBar.vue";
import { ref } from 'vue'
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Divider from 'primevue/divider'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'MyBookingsPage',
  components: {
    ProfileNavBar,
    Card,
    Avatar,
    Button,
    Dialog,
    Divider,
    Tag,
    Toast
  },
  setup() {
    const toast = useToast()
    const showProfileDialog = ref(false)
    const selectedBooking = ref(null)

    // Sample bookings data - Fixed the variable name and structure
    const bookings = ref([
      {
        id: 1,
        name: 'Maria Santos',
        role: 'Domestic Helper',
        company: 'Private Household',
        avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b602?w=150&h=150&fit=crop&crop=face',
        initials: 'MS',
        mutualFriends: 12,
        friendsSince: '2021',
        bio: 'Caring domestic helper from Philippines. Love taking care of families and helping with household needs.',
        interests: ['Cooking', 'Childcare', 'Filipino Culture'],
        totalConnections: 45
      },
      {
        id: 2,
        name: 'Ravi Kumar',
        role: 'Construction Worker',
        company: 'Build-Tech Construction Pte Ltd',
        avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
        initials: 'RK',
        mutualFriends: 8,
        friendsSince: '2020',
        bio: 'Experienced construction worker from India. Specialized in building infrastructure and helping Singapore grow.',
        interests: ['Cricket', 'Tamil Movies', 'Cooking'],
        totalConnections: 62
      },
      {
        id: 3,
        name: 'Siti Aminah',
        role: 'Factory Worker',
        company: 'Metro Electronics Pte Ltd',
        avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
        initials: 'SA',
        mutualFriends: 15,
        friendsSince: '2022',
        bio: 'Dedicated factory worker from Indonesia. Working hard to support family back home while learning new skills.',
        interests: ['Badminton', 'Indonesian Food', 'Learning English'],
        totalConnections: 38
      },
      {
        id: 4,
        name: 'Zhang Wei',
        role: 'Kitchen Helper',
        company: 'Golden Dragon Restaurant',
        avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
        initials: 'ZW',
        mutualFriends: 6,
        friendsSince: '2023',
        bio: 'Hardworking kitchen helper from China. Learning Singaporean cuisine and saving money for family.',
        interests: ['Cooking', 'Table Tennis', 'Chinese Opera'],
        totalConnections: 28
      },
      {
        id: 5,
        name: 'Kumari Devi',
        role: 'Cleaner',
        company: 'CleanPro Services Pte Ltd',
        avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face',
        initials: 'KD',
        mutualFriends: 20,
        friendsSince: '2019',
        bio: 'Experienced cleaner from Bangladesh. Takes pride in keeping Singapore clean and beautiful.',
        interests: ['Bengali Music', 'Gardening', 'Community Service'],
        totalConnections: 54
      },
      {
        id: 6,
        name: 'Jose Reyes',
        role: 'Security Guard',
        company: 'SecureGuard Services Pte Ltd',
        avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
        initials: 'JR',
        mutualFriends: 9,
        friendsSince: '2023',
        bio: 'Reliable security guard from Philippines. Ensuring safety and security for Singaporean communities.',
        interests: ['Basketball', 'Filipino Movies', 'Reading'],
        totalConnections: 41
      }
    ])

    const viewProfile = (booking) => {
      selectedBooking.value = booking
      showProfileDialog.value = true
    }

    const closeProfile = () => {
      showProfileDialog.value = false
      selectedBooking.value = null
    }

    return {
      bookings,
      showProfileDialog,
      selectedBooking,
      viewProfile,
      closeProfile,
      toast
    }
  }
}
</script>

<style scoped>
.bookings-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  margin-bottom: 100px;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

/* .page-title {
  font-size: 2.5rem;
  color: #ff7733;
  margin-bottom: 0.5rem;
} */

.page-subtitle {
  color: #666;
  font-size: 1.1rem;
}

.bookings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.booking-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color: #FFC67B;
  border-radius: 20px;
}

.booking-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(230, 93, 2, 0.3);
}

.booking-content {
  padding: 1rem;
}

.booking-avatar {
  text-align: center;
  margin-bottom: 1rem;
}

.avatar {
  border: 3px solid #fff;
}

.booking-info {
  text-align: center;
  margin-bottom: 1.5rem;
}

.booking-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #333;
}

.booking-role {
  color: #ff7733;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.booking-company {
  color: #666;
  margin-bottom: 1rem;
}

.booking-stats {
  display: flex;
  justify-content: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.booking-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.action-btn {
  flex: 1;
}

.profile-dialog {
  border-radius: 12px;
}

.profile-details {
  padding: 1rem 0;
  background-color: #fff;
  border-radius: 8px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.profile-basic-info h2 {
  margin-bottom: 0.5rem;
  color: #333;
}

.profile-basic-info .role {
  color: #ff7733;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.profile-basic-info .company {
  color: #666;
  margin-bottom: 0.75rem;
}

.profile-sections {
  display: grid;
  gap: 1.5rem;
}

.section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.section p {
  color: #666;
  line-height: 1.6;
}

.interests {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.interest-tag {
  font-size: 0.875rem;
}

.dialog-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.close-btn {
  background-color: #ec6212;
  color: white;
}

.close-btn:hover {
  background-color: #c4511d;
}

@media (max-width: 768px) {
  .bookings-page {
    padding: 1rem;
  }
  
  .bookings-grid {
    grid-template-columns: 1fr;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .dialog-actions {
    flex-direction: column;
  }
}
</style>