<template>
  <div class="page-layout">
    <ProfileNavBar />
    
    <div class="main-content">
      <div class="friends-page">
        <!-- Page Header -->
        <div class="page-header">
          <h1 class="page-title">MY FRIENDS</h1>
          <p class="page-subtitle">Stay connected with your network</p>

          <!-- Add Friend by Phone -->
          <div class="add-friend">
            <InputText
              v-model="addPhone"
              placeholder="Enter friend's Singapore phone (e.g. 9123 4567 or +65 9123 4567)"
              class="add-friend-input"
            />
            <Button
              :label="sending ? 'Sending...' : 'Add Friend'"
              :loading="sending"
              class="add-friend-btn"
              @click="sendFriendRequest"
            />
          </div>
        </div>

        <!-- Tabs: Friends and Pending Requests -->
        <TabView v-model:activeIndex="activeTab">
          <TabPanel header="My Friends">
            <!-- Friends Grid / Empty state -->
            <div v-if="loading" class="loading-state">
              Loading friends...
            </div>

            <div v-else-if="friends.length === 0" class="empty-state">
              <h3>No friends yet</h3>
              <p>Add friends using their Singapore phone number above.</p>
            </div>

            <div v-else class="friends-grid">
              <Card
                v-for="friend in friends"
                :key="friend.id"
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
                    <div class="friend-info">
                      <h3 class="friend-name">{{ friend.name }}</h3>
                      <p class="friend-role">{{ friend.role }}</p>
                      <p class="friend-company">{{ friend.company }}</p>
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
          </TabPanel>

          <TabPanel :header="pendingHeader">
            <div v-if="pendingLoading" class="loading-state">
              Loading pending requests...
            </div>

            <div v-else-if="pendingRequests.length === 0" class="empty-state">
              <h3>No pending requests</h3>
              <p>When someone adds you, you'll see it here to accept or reject.</p>
            </div>

            <div v-else class="friends-grid">
              <Card
                v-for="req in pendingRequests"
                :key="req.id"
                class="friend-card"
              >
                <template #content>
                  <div class="friend-content">
                    <!-- Requester Avatar -->
                    <div class="friend-avatar">
                      <Avatar
                        :image="req.fromUser.avatar"
                        :label="req.fromUser.initials"
                        size="large"
                        shape="circle"
                        class="avatar"
                      />
                    </div>

                    <!-- Request Info -->
                    <div class="friend-info">
                      <h3 class="friend-name">{{ req.fromUser.name }}</h3>
                      <p class="friend-company">{{ req.fromUser.phoneNumber }}</p>
                      <div class="friend-stats">
                        <span class="stat">
                          <i class="pi pi-clock"></i>
                          {{ req.createdAtDisplay || 'Pending' }}
                        </span>
                      </div>
                    </div>

                    <!-- Accept / Reject -->
                    <div class="friend-actions">
                      <Button
                        label="Accept"
                        icon="pi pi-check"
                        size="small"
                        severity="success"
                        :loading="isBusy(req.id)"
                        @click="acceptRequest(req)"
                        class="action-btn"
                      />
                      <Button
                        label="Reject"
                        icon="pi pi-times"
                        size="small"
                        severity="danger"
                        outlined
                        :loading="isBusy(req.id)"
                        @click="rejectRequest(req)"
                        class="action-btn"
                      />
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </TabPanel>
        </TabView>

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
    </div>
  </div>
</template>

<script>
import ProfileNavBar from "@/components/ProfileNavBar.vue";
import { ref, onMounted, watch, computed } from 'vue'
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Divider from 'primevue/divider'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import InputText from 'primevue/inputtext'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import { useToast } from 'primevue/usetoast'
import api from '@/services/api'

export default {
  name: 'MyFriendsPage',
  components: {
    ProfileNavBar,
    Card,
    Avatar,
    Button,
    Dialog,
    Divider,
    Tag,
    Toast,
    InputText,
    TabView,
    TabPanel
  },
  setup() {
    const toast = useToast()
    const showProfileDialog = ref(false)
    const selectedFriend = ref(null)

    const friends = ref([])
    const loading = ref(false)

    const addPhone = ref('')
    const sending = ref(false)

    // Tabs & pending requests state
    const activeTab = ref(0)
    const pendingRequests = ref([])
    const pendingLoading = ref(false)
    const hasLoadedPending = ref(false)
    const actionBusy = ref({})

    const pendingCount = computed(() => pendingRequests.value.length)
    const pendingHeader = computed(() => pendingCount.value ? `Pending Requests (${pendingCount.value})` : 'Pending Requests')

    function isBusy(id) {
      return !!actionBusy.value[id]
    }
    function setBusy(id, val) {
      actionBusy.value = { ...actionBusy.value, [id]: !!val }
    }

    const placeholderAvatar = 'https://via.placeholder.com/150?text=Friend'

    function computeInitials(fullName) {
      const parts = String(fullName || '').trim().split(/\s+/)
      const first = parts[0]?.[0] || ''
      const last = parts.length > 1 ? parts[parts.length - 1]?.[0] : ''
      return (first + last).toUpperCase() || 'U'
    }

    async function loadFriends() {
      loading.value = true
      try {
        const resp = await api.get('/api/friends')
        const list = Array.isArray(resp.data?.friends) ? resp.data.friends : []
        friends.value = list.map(f => ({
          id: f.id,
          name: f.name || 'Friend',
          avatar: (f.profilePicture && String(f.profilePicture).trim()) ? f.profilePicture : placeholderAvatar,
          initials: computeInitials(f.name || 'Friend'),
          // defaults to satisfy existing UI
          role: '',
          company: '',
          mutualFriends: 0,
          friendsSince: '',
          bio: '',
          interests: [],
          totalConnections: 0
        }))
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to load friends'
        toast.add({ severity: 'error', summary: 'Friends', detail: msg, life: 3000 })
        friends.value = []
      } finally {
        loading.value = false
      }
    }

    async function sendFriendRequest() {
      const phone = (addPhone.value || '').trim()
      if (!phone) {
        toast.add({ severity: 'warn', summary: 'Add Friend', detail: 'Enter a phone number', life: 2500 })
        return
      }
      sending.value = true
      try {
        await api.post('/api/friends/request', { phoneNumber: phone })
        toast.add({ severity: 'success', summary: 'Friend Request', detail: 'Request sent', life: 2500 })
        addPhone.value = ''
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to send request'
        toast.add({ severity: 'error', summary: 'Friend Request', detail: msg, life: 3500 })
      } finally {
        sending.value = false
      }
    }

    async function loadPending() {
      pendingLoading.value = true
      try {
        const resp = await api.get('/api/friends/pending')
        const list = Array.isArray(resp.data?.requests) ? resp.data.requests : []
        pendingRequests.value = list.map(r => {
          const u = r.fromUser || {}
          const name = u.name || 'User'
          const avatar = (u.profilePicture && String(u.profilePicture).trim()) ? u.profilePicture : placeholderAvatar
          let displayTime = ''
          try {
            if (r.createdAt) {
              const dt = new Date(r.createdAt)
              if (!isNaN(dt.getTime())) {
                displayTime = dt.toLocaleString()
              }
            }
          } catch (_) { /* ignore */ }
          return {
            id: r.id,
            fromUser: {
              uid: u.uid || '',
              name,
              phoneNumber: u.phoneNumber || '',
              avatar,
              initials: computeInitials(name)
            },
            createdAt: r.createdAt || null,
            createdAtDisplay: displayTime
          }
        })
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to load pending requests'
        toast.add({ severity: 'error', summary: 'Pending Requests', detail: msg, life: 3000 })
        pendingRequests.value = []
      } finally {
        pendingLoading.value = false
      }
    }

    watch(activeTab, (i) => {
      if (i === 1 && !hasLoadedPending.value) {
        hasLoadedPending.value = true
        loadPending()
      }
    })

    async function acceptRequest(req) {
      if (!req?.id) return
      setBusy(req.id, true)
      try {
        await api.put(`/api/friends/request/${req.id}`, { action: 'accept' })
        // Remove from pending and refresh friends
        pendingRequests.value = pendingRequests.value.filter(r => r.id !== req.id)
        toast.add({ severity: 'success', summary: 'Friend Request', detail: 'Friend request accepted', life: 2500 })
        loadFriends()
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to accept request'
        toast.add({ severity: 'error', summary: 'Friend Request', detail: msg, life: 3500 })
      } finally {
        setBusy(req.id, false)
      }
    }

    async function rejectRequest(req) {
      if (!req?.id) return
      setBusy(req.id, true)
      try {
        await api.put(`/api/friends/request/${req.id}`, { action: 'reject' })
        pendingRequests.value = pendingRequests.value.filter(r => r.id !== req.id)
        toast.add({ severity: 'success', summary: 'Friend Request', detail: 'Friend request rejected', life: 2500 })
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to reject request'
        toast.add({ severity: 'error', summary: 'Friend Request', detail: msg, life: 3500 })
      } finally {
        setBusy(req.id, false)
      }
    }

    onMounted(() => {
      loadFriends()
    })

    const viewProfile = (friend) => {
      selectedFriend.value = friend
      showProfileDialog.value = true
    }

    const closeProfile = () => {
      showProfileDialog.value = false
      selectedFriend.value = null
    }

    return {
      friends,
      loading,
      addPhone,
      sending,
      // tabs
      activeTab,
      // pending
      pendingRequests,
      pendingLoading,
      pendingHeader,
      pendingCount,
      isBusy,
      acceptRequest,
      rejectRequest,
      // dialog/profile
      showProfileDialog,
      selectedFriend,
      viewProfile,
      closeProfile,
      // actions
      sendFriendRequest,
      toast
    }
  }
}
</script>

<style scoped>
.page-layout {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 250px; /* Account for fixed sidebar width */
  min-height: 100vh;
}

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
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: white;
  font-size: 1.1rem;
}

/* Add Friend input row */
.add-friend {
  margin: 1rem auto 0;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
  max-width: 640px;
}

.add-friend-input {
  flex: 1;
}

.add-friend-btn {
  background-color: #EC7600 !important;
  border-color: #EC7600 !important;
  color: #fff !important;
  font-weight: 600;
}

/* Loading / Empty states */
.loading-state,
.empty-state {
  text-align: center;
  color: #ffffff;
  padding: 2rem 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #ffffff;
}

.empty-state p {
  margin: 0;
  color: #f1f5f9;
}

.friends-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.friend-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background-color: #ffffff;
  border-radius: 20px;
}

.friend-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(230, 93, 2, 0.3);
}

.friend-content {
  padding: 1rem;
}

.friend-avatar {
  text-align: center;
  margin-bottom: 1rem;
}

.avatar {
  border: 3px solid #fff;
}

.friend-info {
  text-align: center;
  margin-bottom: 1.5rem;
}

.friend-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #333;
}

.friend-role {
  color: #ff7733;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.friend-company {
  color: #666;
  margin-bottom: 1rem;
}

.friend-stats {
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

/* Responsive design */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0; /* No sidebar margin on mobile */
  }
  
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

@media (max-width: 480px) {
  .page-title {
    font-size: 2rem;
  }
  
  .friends-page {
    padding: 0.5rem;
  }
}
</style>