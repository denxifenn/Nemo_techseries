<template>
  <div class="profile-layout">
    <!-- Sidebar -->
    <ProfileNavBar />

    <div class="profile-page">
      <!-- Profile Header -->
      <div class="profile-header">
        <div class="avatar-section">
          <Avatar
            :image="user.avatar"
            :label="user.initials"
            size="xlarge"
            shape="square"
            class="profile-avatar"
          />

          <Button
            icon="pi pi-camera"
            label="Edit Profile Pic"
            severity="secondary"
            class="camera-btn"
            @click="changePhoto"
          />
        </div>

        <div class="profile-basic-info">
          <div class="name-section">
            <h1>{{ user.name }}</h1>
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
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Profile Information Tabs -->
  <TabView class="profile-tabs">
    <!-- Personal Information Tab -->
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

    <!-- Toast for notifications -->
    <Toast ref="toast" />
  </TabView>
</template>

<script>
import ProfileNavBar from "@/components/ProfileNavBar.vue";
import profilePic from "@/assets/profilepic.jpg";
import { ref } from "vue";
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

    // Sample user profile data
    const user = ref({
      name: "Lee Kian Yee",
      age: 28,
      phoneNumber: "+65 9123 4567",
      role: "Construction Worker",
      company: "ABC Construction Pte Ltd",
      avatar: profilePic,
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
      toast.add({
        severity: "info",
        summary: "Edit Profile",
        detail: "Opening profile editor",
        life: 3000,
      });
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
      changePhoto,
      editProfile,
      shareProfile,
      callEmergency,
      callPolice,
      callAmbulance,
      callFire,
    };
  },
};
</script>

<style scoped>
.profile-page {
  margin-left: 50px; /* same as sidebar width */
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
  margin-right: 1px;
  flex-direction: column;
}

.profile-avatar {
  margin-right: 1rem;
  width: 300px;
  height: 300px;
  background-color: var(--surface-200);
  border: 4px solid var(--surface-border);
  margin-bottom: 1rem;
}

.camera-btn {
  border-radius: 8px; /* slightly rounded corners */
  padding: 0.5rem 1rem; /* control size */
  font-weight: 600; /* thicker text */
  margin-left: 50px;
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
  margin-left: 242px;
  margin-top: 2rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 4rem;
  margin-top: 1rem;
}

.info-list {
  margin-right: 1px;
  width: 1850px;
  background-color: #ffc67b;
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
    gap: 2rem;
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
