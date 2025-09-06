<template>
  <div class="profile-layout">
    <!-- Sidebar -->
    <ProfileNavBar />

    <div class="profile-page">
      <!-- Profile Header -->
      <div class="profile-header">
        <div class="profile-basic-info">
          <div class="name-and-avatar">
            <div class="avatar-container">
              <div class="avatar-wrapper">
                <Avatar
                  :image="user.avatar"
                  :label="user.initials"
                  size="large"
                  shape="circle"
                  class="profile-avatar"
                />
              </div>
              <Button
                icon="pi pi-camera"
                class="change-photo-btn"
                label="Change Photo"
                size="small"
                @click="changePhoto"
                rounded
              />
            </div>
            <div class="name-section">
              <h2 class="user-name">{{ user.name }}</h2>
              <p class="user-role">{{ user.role }}</p>
              <p class="user-company">{{ user.company }}</p>
            </div>
          </div>

            <!-- Profile Information Tabs -->
            <TabView class="profile-tabs" :activeIndex="0">
        
        <TabPanel header="Personal Information">
          <div class="info-grid">
            <Card class="info-card1">
              <template #content class="info-box">
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
                  </div>

                  <div class="info-item">
                    <span class="label">Nationality:</span>
                    <span class="value">{{ user.nationality }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Languages:</span>
                    <span class="value">{{ user.languages.join(", ") }}</span>
                  </div>
                </div>
                <div class="info-list">
                  <div class="info-item">
                    <span class="label">Home Country:</span>
                    <span class="value">{{ user.homeCountry }}</span>
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

        <!-- Interests & Skills Tab -->
        <TabPanel header="Interests & Skills">
          <div class="info-grid">
            <Card class="info-card">
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
                  <div
                    class="skill-item"
                    v-for="skill in user.skills"
                    :key="skill.name"
                  >
                    <span class="skill-name">{{ skill.name }}</span>
                    <ProgressBar :value="skill.level" class="skill-bar" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </TabPanel>
      </TabView>

        </div>
        </div>
      </div>

      <!-- Sticky Edit Profile Button -->
      <div class="sticky-edit-btn">
        <Button
          label="Edit Profile"
          icon="pi pi-pencil"
          @click="editProfile"
          class="edit-profile-sticky-btn"
        />
      </div>

    <!-- Toast for notifications -->
    <Toast ref="toast" />
  </div>
</template>

<script>
import ProfileNavBar from "@/components/ProfileNavBar.vue";
import profilePic from "@/assets/profilepic.jpg";
import { ref, onMounted } from "vue";
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import Button from "primevue/button";
import Tag from "primevue/tag";
import TabView from "primevue/tabview";
import TabPanel from "primevue/tabpanel";
import Divider from "primevue/divider";
import ProgressBar from "primevue/progressbar";
import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";
import { useRouter } from "vue-router";


export default {
  name: "ProfilePage",
  components: {
    ProfileNavBar,
    Card,
    Avatar,
    Button,
    Tag,
    TabView,
    TabPanel,
    Divider,
    ProgressBar,
    Toast,
  },
  setup() {
    const toast = useToast();
    const router = useRouter();

    onMounted(() => {
      // Component mounted successfully
    });

    // Layout improvements completed

    // Sample user profile data
    const user = ref({
      name: "Lee Kian Yee",
      age: 28,
      phoneNumber: "+65 9123 4567",
      role: "Construction Worker",
      company: "ABC Construction Pte Ltd",
      avatar: profilePic,
      initials: "LK",
      nationality: "Chinese",
      languages: ["Basic English", "Mandarin"],
      homeCountry: "Philippines",
      restDay: "Saturday, Sunday",
      interests: [
        "Cooking",
        "Childcare",
        "Filipino Culture",
        "K-Drama",
        "Shopping",
      ],
      skills: [
        { name: "Childcare", level: 90 },
        { name: "Cooking", level: 85 },
        { name: "Housekeeping", level: 95 },
        { name: "English Communication", level: 75 },
        { name: "Basic Mandarin", level: 40 },
      ],
    });


    const changePhoto = () => {
      toast.add({
        severity: "info",
        summary: "Photo Update",
        detail: "Photo upload feature coming soon",
        life: 3000,
      });
    };

    const editProfile = () => {
      router.push({name: 'EditProfile' })
    };

    const shareProfile = () => {
      toast.add({
        severity: "success",
        summary: "Profile Shared",
        detail: "Profile link copied to clipboard",
        life: 3000,
      });
    };

    const callEmergency = () => {
      toast.add({
        severity: "warn",
        summary: "Emergency Contact",
        detail: `Calling ${user.value.emergencyContact.name}`,
        life: 3000,
      });
    };

    const callPolice = () => {
      toast.add({
        severity: "error",
        summary: "Emergency",
        detail: "Calling Police: 999",
        life: 5000,
      });
    };

    const callAmbulance = () => {
      toast.add({
        severity: "error",
        summary: "Emergency",
        detail: "Calling Ambulance: 995",
        life: 5000,
      });
    };

    const callFire = () => {
      toast.add({
        severity: "error",
        summary: "Emergency",
        detail: "Calling Fire Service: 995",
        life: 5000,
      });
    };

    return {
      user,
      router,
      changePhoto,
      editProfile,
      shareProfile,
    };
  },
};
</script>

<style scoped>
.profile-layout {
  display: flex;
  min-height: 100vh; 
}

/* Sidebar (ProfileNavBar) */
.profile-layout > *:first-child {
  width: 250px;      
  flex-shrink: 0;      
}

.profile-page {
  flex: 1;
  padding: 2rem;
  margin-left: 250px;
  max-width: 100%;
}

.profile-header-card {
  background: linear-gradient(90deg, #f8faff, #fef9f5);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
  margin-bottom: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
  margin-top: 3rem;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.change-photo-btn {
  background: white;
  border: 1px solid #ddd;
  color: #555;
  font-size: 0.8rem;
  padding: 0.4rem 0.8rem;
}

.user-name {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.user-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.5rem 2rem;
  margin-bottom: 1rem;
}
.user-role {
  color: #3b82f6;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.user-company {
  color: #718096;
  margin: 0 0 1.5rem 0;
  font-size: 0.9rem;
}

.edit-btn {
  min-width: 100px;
}

.camera-btn {
  border-radius: 8px; 
  padding: 0.5rem 1rem; 
  font-weight: 600;
  align-self: flex-start;
  margin-top: 0.5rem;
}

.profile-basic-info {
  flex: 1;
}

.user-info-stack {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.name-and-avatar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.name-section {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.profile-basic-info h1 {
  font-size: 2rem;
  color: var(--text-color);
  margin: 0;
}

.status-tag {
  font-size: 0.875rem;
}


.profile-tabs {
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 4rem;
  margin-top: 1rem;
}

.info-list {
  margin-right: 1px;
  width: 100%;
  max-width: 100%;
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

@media (max-width: 1024px) {
  .profile-avatar {
    width: 250px;
    height: 250px;
  }

  .profile-basic-info h1 {
    font-size: 1.8rem;
  }

  .info-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 3rem;
  }
}

@media (max-width: 768px) {
  .profile-layout {
    flex-direction: column;
  }

  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
    padding: 1rem 0.5rem;
  }

  .avatar-section {
    align-items: center;
  }

  .profile-avatar {
    width: 120px;
    height: 120px;
  }

  .change-photo-btn {
    margin-top: 0.5rem;
    align-self: center;
  }

  .name-and-avatar {
    justify-content: center;
  }

  .name-section {
    flex-direction: column;
    gap: 0.5rem;
  }

  .profile-basic-info h1 {
    font-size: 1.5rem;
  }

  .user-details {
    margin-bottom: 1rem;
  }

  .role, .company, .age, .phone {
    font-size: 0.9rem;
  }

  .quick-actions {
    justify-content: center;
  }

  .action-btn {
    min-width: 10px;
    font-size: 0.9rem;
  }

  .profile-tabs {
    margin-left: 0;
    margin-top: 1rem;
  }

  .profile-layout > *:first-child {
    width: 100%;
  }

  .profile-page {
    padding: 1rem 0.5rem;
    margin-left: 0;
  }

  .info-grid {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.5rem 0;
  }

  .value {
    text-align: left;
    margin-right: 0;
  }

  .emergency-numbers {
    flex-direction: column;
  }

  .interest-tag {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
}

@media (max-width: 480px) {
  .profile-page {
    padding: 0.5rem;
  }

  .profile-header {
    gap: 1rem;
    padding: 0.5rem;
  }

  .profile-avatar {
    width: 60px;
    height: 60px;
  }

  .change-photo-btn {
    font-size: 0.7rem;
    padding: 0.3rem 0.6rem;
  }

  .profile-basic-info h1 {
    font-size: 1.3rem;
  }

  .user-details {
    margin-bottom: 0.5rem;
  }

  .role, .company, .age, .phone {
    font-size: 0.85rem;
    margin-bottom: 0.2rem;
  }

  .action-btn {
    min-width: 80px;
    font-size: 0.8rem;
    padding: 0.5rem 0.75rem;
  }

  .info-grid {
    gap: 1rem;
  }

  .info-item {
    padding: 0.4rem 0;
  }

  .label {
    min-width: 120px;
    font-size: 0.9rem;
  }

  .value {
    font-size: 0.9rem;
  }

  .interest-tag {
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
  }

  .skills-section {
    gap: 1rem;
  }

  .skill-item {
    gap: 0.3rem;
  }

  .skill-name {
    font-size: 0.9rem;
  }
}

/* Sticky Edit Profile Button */
.sticky-edit-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
}

.edit-profile-sticky-btn {
  background: #3b82f6;
  border: none;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all 0.3s ease;
}

.edit-profile-sticky-btn:hover {
  background: #2563eb;
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4);
  transform: translateY(-2px);
}

.edit-profile-sticky-btn:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
}
</style>
