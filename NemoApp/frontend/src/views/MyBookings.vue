<template>
  <ProfileNavBar />

  <div class="my-bookings-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">MY BOOKINGS</h1>
      <!-- <p class="page-subtitle"></p> -->
    </div>

    <!-- Friends Grid -->
    <div class="friends-grid">
      <Card 
        v-for="event in bookings" 
        :key="event.id"
        class="friend-card"
      >
        <template #content>
          <div class="friend-content">
            <!-- Profile Image -->
            <div class="friend-avatar">
              <Avatar 
                :image="friend.avatar" 
                :label="friend.initials"
                size="large"
                shape="circle"
                class="avatar"
              />
              
            </div>

            <!-- Friend Info -->
            <div class="event-info">
              <h3 class="event-name">{{ event.name }}</h3>
              <p class="event-role">{{ event.role }}</p>
              <p class="friend-company">{{ event.company }}</p>
              <div class="friend-stats">
                <span class="stat">
                  <i class="pi pi-users"></i>
                  {{ friend.mutualFriends }} mutual
                </span>
               
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="friend-actions">
              <Button
                label="Message"
                icon="pi pi-comments"
                severity="secondary"
                size="small"
                @click="sendMessage(friend)"
                class="action-btn"
              />
              <Button
                label="More Info"
                icon="pi pi-info-circle"
                size="small"
                @click="viewProfile(friend)"
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
      :header="selectedFriend?.name"
      modal
      class="profile-dialog"
      :style="{ width: '600px' }"
    >
      <div v-if="selectedFriend" class="profile-details">
        <div class="profile-header">
          <Avatar 
            :image="selectedFriend.avatar" 
            :label="selectedFriend.initials"
            size="xlarge"
            shape="circle"
          />
          <div class="profile-basic-info">
            <h2>{{ selectedFriend.name }}</h2>
            <p class="role">{{ selectedFriend.role }}</p>
            <p class="company">{{ selectedFriend.company }}</p>
          
          </div>
        </div>

        <Divider />

        <div class="profile-sections">
          <div class="section">
            <h4><i class="pi pi-user"></i> About</h4>
            <p>{{ selectedFriend.bio }}</p>
          </div>

        <div class="section">
            <h4><i class="pi pi-heart"></i> Interests</h4>
            <div class="interests">
              <Tag 
                v-for="interest in selectedFriend.interests"
                :key="interest"
                :value="interest"
                severity="info"
                class="interest-tag"
              />
            </div>
          </div>

          <div class="section">
            <h4><i class="pi pi-users"></i> Network</h4>
            <p>{{ selectedFriend.mutualFriends }} mutual friends</p>
            <p>{{ selectedFriend.totalConnections }} total connections</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-actions">
          <Button
            label="Send Message"
            icon="pi pi-comments"
            @click="sendMessage(selectedFriend)"
            class="close-btn"
          />
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
    const selectedFriend = ref(null)

    // Sample friends data - Migrant workers in Singapore
    const friends = ref([
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
        Interests: ['Cricket', 'Tamil Movies', 'Cooking'],
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
        experience: 4,
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
        experience: 2,
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
        experience: 12,
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
        bio: 'Reliable security guard from Philippines. Ensuring safety and security for Singaporean communities.',
        interests: ['Basketball', 'Filipino Movies', 'Reading'],
        totalConnections: 41
      }
    ])

    const viewProfile = (friend) => {
      selectedFriend.value = friend
      showProfileDialog.value = true
    }

    const closeProfile = () => {
      showProfileDialog.value = false
      selectedFriend.value = null
    }

    const sendMessage = (friend) => {
      toast.add({
        severity: 'info',
        summary: 'Message',
        detail: `Opening chat with ${friend.name}`,
        life: 3000
      })
      // Here you would typically navigate to a messaging interface
      // or open a chat component
    }

    return {
      friends,
      showProfileDialog,
      selectedFriend,
      viewProfile,
      closeProfile,
      sendMessage,
      toast
    }
  }
}
</script>

<style scoped>
.friends-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 2.5rem;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: var(--text-color-secondary);
  font-size: 1.1rem;
}

.friends-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 5rem;
}

.friend-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color:  #FFC67B;
  border-radius: 12px;
}

.friend-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(230, 93, 2, 0.973);
}

.friend-content {
  padding: 1rem;
}

.friend-avatar {
  position: relative;
  text-align: center;
  margin-bottom: 1rem;
}

.avatar {
  border: 3px solid var(--surface-border);
}

.status-indicator {
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid white;
  bottom: 0;
  right: calc(50% - 35px);
}


.friend-info {
  text-align: center;
  margin-bottom: 1.5rem;
  
}

.friend-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--text-color);
}

.friend-role {
  color: var(--primary-color);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.friend-company {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.friend-stats {
  display: flex;
  justify-content: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.friend-actions {
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
  width: 600px;
  padding: 1rem 0;
  background-color: rgb(255, 146, 78);
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
  color: var(--text-color);
}

.profile-basic-info .role {
  color: var(--primary-color);
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.profile-basic-info .company {
  color: var(--text-color-secondary);
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
  color: var(--text-color);
  margin-bottom: 0.75rem;
  font-weight: 600;
}

.section p {
  color: var(--text-color-secondary);
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

.close-btn{
  background-color: #ec6212; 
  color: rgb(0, 0, 0);
}
.close-btn:hover {
  background-color: #c4808c; 
}

@media (max-width: 768px) {
  .friends-page {
    padding: 1rem;
  }
  
  .friends-grid {
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