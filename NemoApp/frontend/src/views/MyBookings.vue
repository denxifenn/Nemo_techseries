<template>
  <ProfileNavBar />

  <div class="bookings-page">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">MY BOOKINGS</h1>
      <p class="page-subtitle">Events you've signed up for!</p>
    </div>

    <!-- Bookings Grid -->
    <div class="bookings-grid">
      <div v-for="event in bookings" :key="event.id" class="event-card">
        <Card>
          <template #header>
            <div class="event-image">
              <img :src="event.image" :alt="event.title" />
            </div>
          </template>
          <template #title>{{ event.title }}</template>
          <template #subtitle>
            <div class="event-meta">
              <span class="event-date"
                >{{ event.date }} at {{ event.startTime }} -
                {{ event.endTime }}</span
              >
              <span class="event-location">📍 {{ event.location }}</span>
              <span class="event-organiser">👤 {{ event.organiser }}</span>
              <span class="event-slots">🎫 {{ event.bookingSlots }} slots</span>
              <span class="event-price">{{
                event.price === 0 ? "🆓 Free" : `💰 $${event.price}`
              }}</span>
            </div>
          </template>
          <template #content>
            <p class="event-description">{{ event.description }}</p>
            <div class="event-tags">
              <Tag
                :value="event.format"
                severity="secondary"
                class="format-tag"
              />
              <Tag
                :value="event.type"
                severity="secondary"
                class="format-tag"
              />
              <Tag
                :value="event.region"
                severity="secondary"
                class="format-tag"
              />
            </div>
          </template>
          <template #footer>
            <!-- Action Buttons -->
            <div class="booking-actions">
              <Button
                label="Cancel Booking"
                size="small"
                @click="cancelBooking(event.id)"
                class="cancel-booking-btn"
              />
              <Button
                label="More Info"
                icon="pi pi-info-circle"
                size="small"
                @click="router.push({ name: 'Event', params: { eventId: event.eventId } })"
                class="action-btn"
              />
            </div>
          </template>
        </Card>
      </div>
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
import { ref, onMounted } from "vue";
import Card from "primevue/card";
import Avatar from "primevue/avatar";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import Divider from "primevue/divider";
import Tag from "primevue/tag";
import Toast from "primevue/toast";
import { useToast } from "primevue/usetoast";
import { useRouter } from "vue-router";
import api from "@/services/api";

export default {
  name: "MyBookingsPage",
  components: {
    ProfileNavBar,
    Card,
    Avatar,
    Button,
    Dialog,
    Divider,
    Tag,
    Toast,
  },
  setup() {
    const toast = useToast();
    const router = useRouter();
    const showProfileDialog = ref(false);
    const selectedBooking = ref(null);

    const bookings = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const placeholderImage = "/src/assets/workers_background.jpg";

    function closeProfile() {
      showProfileDialog.value = false;
    }

    async function loadBookings() {
      loading.value = true;
      error.value = null;
      try {
        const resp = await api.get("/api/bookings/my", { filter: "current" });
        const list = Array.isArray(resp.data?.bookings) ? resp.data.bookings : [];
        bookings.value = list.map(b => {
          const ev = b.event || {};
          return {
            // booking id is used for cancel endpoint
            id: b.id,                 // bookingId (used by cancel)
            eventId: ev.id || b.eventId || "", // for "More Info" navigation
            title: ev.title || "Event",
            date: ev.date || "",
            startTime: ev.startTime || ev.time || "",
            endTime: "", // not provided in summary; leave blank
            location: ev.location || "",
            organiser: ev.organiser || "",
            bookingSlots: 0, // not part of summary; omit from UI logic
            description: "",
            format: ev.format || "",
            type: ev.type || ev.category || "",
            region: ev.region || "",
            price: ev.price ?? 0,
            image: placeholderImage
          };
        });
      } catch (e) {
        console.error("Failed to load bookings", e);
        error.value = e?.message || "Failed to load bookings";
        bookings.value = [];
      } finally {
        loading.value = false;
      }
    }

    async function cancelBooking(bookingId) {
      try {
        await api.del(`/api/bookings/${bookingId}`);
        // Remove locally
        bookings.value = bookings.value.filter(b => b.id !== bookingId);
        toast.add({
          severity: "warn",
          summary: "Booking Cancelled",
          detail: "Your booking has been cancelled",
          life: 3000
        });
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || "Failed to cancel booking";
        toast.add({ severity: "error", summary: "Cancel Booking", detail: msg, life: 3000 });
      }
    }

    onMounted(() => {
      loadBookings();
    });

    return {
      bookings,
      showProfileDialog,
      selectedBooking,
      router,
      closeProfile,
      cancelBooking,
      toast,
      loading,
      error
    };
  },
};
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

.page-title {
  font-size: 2.5rem;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: white;
  font-size: 1.1rem;
}

.bookings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.booking-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color: #ffffff;
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

.cancel-booking-btn {
  background-color: #e63b0777;
  color: white;
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
