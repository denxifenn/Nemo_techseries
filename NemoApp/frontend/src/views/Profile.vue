<template>
  <div class="profile-page">
    <!-- Profile Header -->
    <Card class="profile-header-card">
      <template #content>
        <div class="profile-header">
          <div class="avatar-section">
            <Avatar 
              :image="user.avatar" 
              :label="user.initials"
              size="xlarge"
              shape="circle"
              class="profile-avatar"
            />
            <div 
              class="status-indicator"
              :class="user.isOnline ? 'online' : 'offline'"
            ></div>
            <Button
              icon="pi pi-camera"
              severity="secondary"
              rounded
              class="camera-btn"
              @click="changePhoto"
            />
          </div>
          
          <div class="profile-basic-info">
            <div class="name-section">
              <h1>{{ user.name }}</h1>
              <Tag 
                :value="user.isOnline ? 'Online' : 'Offline'"
                :severity="user.isOnline ? 'success' : 'secondary'"
                class="status-tag"
              />
            </div>
            <p class="role">{{ user.role }}</p>
            <p class="company">{{ user.company }}</p>
            <div class="quick-actions">
              <Button
                label="Edit Profile"
                icon="pi pi-pencil"
                @click="editProfile"
                class="action-btn"
              />
              <Button
                label="Share Profile"
                icon="pi pi-share-alt"
                severity="secondary"
                @click="shareProfile"
                class="action-btn"
              />
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Profile Information Tabs -->
    <TabView class="profile-tabs">
      <!-- Personal Information Tab -->
      <TabPanel header="Personal Info">
        <div class="info-grid">
          <Card class="info-card">
            <template #title>
              <i class="pi pi-user"></i> Basic Information
            </template>
            <template #content>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">Full Name:</span>
                  <span class="value">{{ user.name }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Age:</span>
                  <span class="value">{{ user.age }} years old</span>
                </div>
                <div class="info-item">
                  <span class="label">Phone Number:</span>
                  <span class="value">{{ user.phoneNumber }}</span>
                  <Button
                    icon="pi pi-phone"
                    severity="success"
                    size="small"
                    rounded
                  
                    class="contact-btn"
                  />
                </div>
               
                <div class="info-item">
                  <span class="label">Nationality:</span>
                  <span class="value">{{ user.nationality }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Languages:</span>
                  <span class="value">{{ user.languages.join(', ') }}</span>
                </div>
              </div>
            </template>
          </Card>

          <Card class="info-card">
            <template #content>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">Nearest MRT:</span>
                  <span class="value">{{ user.nearestMRT }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Home Country:</span>
                  <span class="value">{{ user.homeCountry }}</span>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </TabPanel>

      <!-- Work Information Tab -->
      <TabPanel header="Work Info">
        <div class="info-grid">
          <Card class="info-card">
            <template #title>
              <i class="pi pi-briefcase"></i> Employment Details
            </template>
            <template #content>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">Job Title:</span>
                  <span class="value">{{ user.role }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Company:</span>
                  <span class="value">{{ user.company }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Work Experience:</span>
                  <span class="value">{{ user.experience }} years</span>
                </div>
                </div>
            </template>
          </Card>

          <Card class="info-card">
            <template #title>
              <i class="pi pi-clock"></i> Work Schedule
            </template>
            <template #content>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">Working Days:</span>
                  <span class="value">{{ user.workingDays }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Working Hours:</span>
                  <span class="value">{{ user.workingHours }}</span>
                </div>
                <div class="info-item">
                  <span class="label">Rest Day:</span>
                  <span class="value">{{ user.restDay }}</span>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </TabPanel>

      <!-- Emergency Contact Tab -->
      <TabPanel header="Emergency Contact">
        <Card class="info-card">
          <template #title>
            <i class="pi pi-exclamation-triangle"></i> Emergency Information
          </template>
          <template #content>
            <div class="info-list">
              <div class="info-item">
                <span class="label">Emergency Contact Name:</span>
                <span class="value">{{ user.emergencyContact.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">Relationship:</span>
                <span class="value">{{ user.emergencyContact.relationship }}</span>
              </div>
              <div class="info-item">
                <span class="label">Phone Number:</span>
                <span class="value">{{ user.emergencyContact.phoneCensored }}</span>
              
              </div>
              <div class="info-item">
                <span class="label">Location:</span>
                <span class="value">{{ user.emergencyContact.location }}</span>
              </div>
            </div>
            
            <Divider />
            
            <div class="emergency-services">
              <h4>Singapore Emergency Services</h4>
              <div class="emergency-numbers">
                <Button
                  label="Police: 999"
                  icon="pi pi-shield"
                  severity="danger"
                  @click="callPolice"
                  class="emergency-btn"
                />
                <Button
                  label="Ambulance: 995"
                  icon="pi pi-plus"
                  severity="danger"
                  @click="callAmbulance"
                  class="emergency-btn"
                />
                <Button
                  label="Fire: 995"
                  icon="pi pi-exclamation-triangle"
                  severity="danger"
                  @click="callFire"
                  class="emergency-btn"
                />
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>

      <!-- Interests & Skills Tab -->
      <TabPanel header="Interests & Skills">
        <div class="info-grid">
          <Card class="info-card">
            <template #title>
              <i class="pi pi-heart"></i> Interests & Hobbies
            </template>
            <template #content>
              <div class="interests-section">
                <Tag 
                  v-for="interest in user.interests"
                  :key="interest"
                  :value="interest"
                  severity="info"
                  class="interest-tag"
                />
              </div>
            </template>
          </Card>

          <Card class="info-card">
            <template #title>
              <i class="pi pi-star"></i> Skills & Certifications
            </template>
            <template #content>
              <div class="skills-section">
                <div class="skill-item" v-for="skill in user.skills" :key="skill.name">
                  <span class="skill-name">{{ skill.name }}</span>
                  <ProgressBar :value="skill.level" class="skill-bar" />
                </div>
              </div>
            </template>
          </Card>
        </div>
      </TabPanel>
    </TabView>

    <!-- Toast for notifications -->
    <Toast ref="toast" />
  </div>
</template>

<script>
import { ref } from 'vue'
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Divider from 'primevue/divider'
import ProgressBar from 'primevue/progressbar'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

export default {
  name: 'ProfilePage',
  components: {
    Card,
    Avatar,
    Button,
    Tag,
    TabView,
    TabPanel,
    Divider,
    ProgressBar,
    Toast
  },
  setup() {
    const toast = useToast()

    // Sample user profile data
    const user = ref({
      name: 'Maria Santos',
      age: 28,
      phoneNumber: '+65 9123 4567',
      role: 'Domestic Helper',
      company: 'Private Household',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b602?w=150&h=150&fit=crop&crop=face',
      initials: 'MS',
      isOnline: true,
      nationality: 'Filipino',
      languages: ['Filipino', 'English', 'Basic Mandarin'],
      nearestMRT: 'Toa Payoh MRT',
      homeCountry: 'Philippines',
      experience: 6,
      workPermitNumber: 'WP1234567A',
      permitExpiry: '15 Dec 2025',
      employerContact: '+65 9876 5432',
      workingDays: 'Monday to Saturday',
      workingHours: '7:00 AM - 8:00 PM',
      restDay: 'Sunday',
      salaryRange: '$650 - $800',
      emergencyContact: {
        name: 'Rosa Santos',
        relationship: 'Sister',
        phone: '+63 917 123 4567',
        location: 'Manila, Philippines'
      },
      interests: ['Cooking', 'Childcare', 'Filipino Culture', 'K-Drama', 'Shopping'],
      skills: [
        { name: 'Childcare', level: 90 },
        { name: 'Cooking', level: 85 },
        { name: 'Housekeeping', level: 95 },
        { name: 'English Communication', level: 75 },
        { name: 'Basic Mandarin', level: 40 }
      ]
    })

    const changePhoto = () => {
      toast.add({
        severity: 'info',
        summary: 'Photo Update',
        detail: 'Photo upload feature coming soon',
        life: 3000
      })
    }

    const editProfile = () => {
      toast.add({
        severity: 'info',
        summary: 'Edit Profile',
        detail: 'Opening profile editor',
        life: 3000
      })
    }

    const shareProfile = () => {
      toast.add({
        severity: 'success',
        summary: 'Profile Shared',
        detail: 'Profile link copied to clipboard',
        life: 3000
      })
    }


   const callEmergency = () => {
      toast.add({
        severity: 'warn',
        summary: 'Emergency Contact',
        detail: `Calling ${user.value.emergencyContact.name}`,
        life: 3000
      })
    }

    const callPolice = () => {
      toast.add({
        severity: 'error',
        summary: 'Emergency',
        detail: 'Calling Police: 999',
        life: 5000
      })
    }

    const callAmbulance = () => {
      toast.add({
        severity: 'error',
        summary: 'Emergency',
        detail: 'Calling Ambulance: 995',
        life: 5000
      })
    }

    const callFire = () => {
      toast.add({
        severity: 'error',
        summary: 'Emergency',
        detail: 'Calling Fire Service: 995',
        life: 5000
      })
    }

    return {
      user,
      changePhoto,
      editProfile,
      shareProfile,
      callEmergency,
      callPolice,
      callAmbulance,
      callFire
    }
  }
}
</script>

<style scoped>
.profile-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.profile-header-card {
  margin-bottom: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem;
}

.avatar-section {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.profile-avatar {
  border: 4px solid var(--surface-border);
  margin-bottom: 1rem;
}

.status-indicator {
  position: absolute;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 3px solid white;
  top: 10px;
  right: 10px;
}

.status-indicator.online {
  background-color: #22c55e;
}

.status-indicator.offline {
  background-color: #6b7280;
}

.camera-btn {
  margin-top: 0.5rem;
}

.profile-basic-info {
  flex: 1;
}

.name-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.profile-basic-info h1 {
  font-size: 2rem;
  color: var(--text-color);
  margin: 0;
}

.status-tag {
  font-size: 0.875rem;
}

.role {
  color: var(--primary-color);
  font-weight: 600;
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
}

.company {
  color: var(--text-color-secondary);
  margin-bottom: 1.5rem;
}

.quick-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  min-width: 120px;
}

.profile-tabs {
  margin-top: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.info-card {
  height: fit-content;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--surface-border);
}

.info-item:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: var(--text-color);
  min-width: 140px;
}

.value {
  flex: 1;
  text-align: right;
  color: var(--text-color-secondary);
  margin-right: 1rem;
}

.contact-btn {
  margin-left: 0.5rem;
}

.interests-section {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.interest-tag {
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
}

.skills-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.skill-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skill-name {
  font-weight: 600;
  color: var(--text-color);
}

.skill-bar {
  height: 8px;
}

.emergency-services {
  margin-top: 2rem;
}

.emergency-services h4 {
  color: var(--text-color);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.emergency-numbers {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.emergency-btn {
  flex: 1;
  min-width: 150px;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 1rem;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .name-section {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .quick-actions {
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .value {
    text-align: left;
    margin-right: 0;
  }
  
  .emergency-numbers {
    flex-direction: column;
  }
}
</style>