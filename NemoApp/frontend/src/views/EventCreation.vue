<template>
  <div class="event-creation-container">
 
    
    <div class="main-content">
      <div class="form-container">
        <h1 class="page-title">Create New Event</h1>
        
        <Form
          :resolver="resolver"
          @submit="onFormSubmit"
          class="event-form"
        >
          <!-- Title -->
          <FormField
            v-slot="$field"
            name="title"
            initialValue=""
            class="form-field"
          >
            <label class="field-label">Event Title *</label>
            <InputText
              v-model="$field.value"
              type="text"
              placeholder="Enter event title"
              class="form-input"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
            >
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- Date and Time Row -->
          <div class="form-row">
            <!-- Date -->
            <FormField
              v-slot="$field"
              name="date"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Date *</label>
              <Calendar
                v-model="$field.value"
                placeholder="Select date"
                class="form-input"
                dateFormat="dd/mm/yy"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <!-- Start Time -->
            <FormField
              v-slot="$field"
              name="startTime"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Start Time *</label>
              <InputText
                v-model="$field.value"
                type="text"
                placeholder="HH:MM (24h)"
                class="form-input"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <!-- End Time -->
            <FormField
              v-slot="$field"
              name="endTime"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">End Time *</label>
              <InputText
                v-model="$field.value"
                type="text"
                placeholder="HH:MM (24h)"
                class="form-input"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>
          </div>

          <!-- Location -->
          <FormField
            v-slot="$field"
            name="location"
            initialValue=""
            class="form-field"
          >
            <label class="field-label">Location *</label>
            <InputText
              v-model="$field.value"
              type="text"
              placeholder="Enter event location"
              class="form-input"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
            >
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- Organiser -->
          <div class="form-row">
            <!-- Organiser -->
            <FormField
              v-slot="$field"
              name="organiser"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Organiser *</label>
              <InputText
                v-model="$field.value"
                type="text"
                placeholder="Enter organiser name"
                class="form-input"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            </div>

          <!-- Booking Slots and Price Row -->
          <div class="form-row">
            <!-- Number of Booking Slots -->
            <FormField
              v-slot="$field"
              name="bookingSlots"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Available Booking Slots *</label>
              <InputNumber
                v-model="$field.value"
                placeholder="Number of slots"
                class="form-input"
                :min="1"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <!-- Price -->
            <FormField
              v-slot="$field"
              name="price"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Price (SGD)</label>
              <InputNumber
                v-model="$field.value"
                placeholder="Event price"
                class="form-input"
                mode="currency"
                currency="SGD"
                :min="0"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>
          </div>

          <!-- Format, Type, and Region Row -->
          <div class="form-row">
            <!-- Format -->
            <FormField
              v-slot="$field"
              name="format"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Format *</label>
              <Select
                v-model="$field.value"
                :options="formatOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select format"
                class="form-input"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <!-- Venue Type (required when format=offline) -->
            <FormField
              v-slot="$field"
              name="venueType"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Venue Type</label>
              <Select
                v-model="$field.value"
                :options="venueOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Indoor / Outdoor / Both"
                class="form-input"
              />
              <small class="text-gray-500">Required when Format is Offline</small>
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <!-- Type -->
            <FormField
              v-slot="$field"
              name="type"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Type *</label>
              <Select
                v-model="$field.value"
                :options="typeOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select type"
                class="form-input"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>

            <!-- Region -->
            <FormField
              v-slot="$field"
              name="region"
              initialValue=""
              class="form-field flex-1"
            >
              <label class="field-label">Region *</label>
              <Select
                v-model="$field.value"
                :options="regionOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select region"
                class="form-input"
              />
              <Message
                v-if="$field?.invalid"
                severity="error"
                size="small"
                variant="simple"
              >
                {{ $field.error?.message }}
              </Message>
            </FormField>
          </div>

          <!-- Description -->
          <FormField
            v-slot="$field"
            name="description"
            initialValue=""
            class="form-field"
          >
            <label class="field-label">Description *</label>
            <Textarea
              v-model="$field.value"
              placeholder="Enter event description"
              class="form-input description-textarea"
              rows="4"
            />
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
            >
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- Image Upload -->
          <FormField
            v-slot="$field"
            name="image"
            initialValue=""
            class="form-field"
          >
            <label class="field-label">Event Image</label>
            <FileUpload
              mode="basic"
              accept="image/*"
              :maxFileSize="5000000"
              @select="onFileSelect"
              class="form-input"
              chooseLabel="Choose Image"
            />
            <small class="text-gray-500">Maximum file size: 5MB. Supported formats: JPG, PNG, GIF</small>
            <Message
              v-if="$field?.invalid"
              severity="error"
              size="small"
              variant="simple"
            >
              {{ $field.error?.message }}
            </Message>
          </FormField>

          <!-- Submit Buttons -->
          <div class="form-buttons">
            <Button
              type="button"
              label="Cancel"
              severity="secondary"
              class="cancel-btn"
              @click="handleCancel"
            />
            <Button
              type="submit"
              label="Create Event"
              class="create-btn"
            />
          </div>
        </Form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { zodResolver } from "@primevue/forms/resolvers/zod";
import { z } from "zod";
import { useToast } from "primevue/usetoast";
import { useRouter } from "vue-router";
import { Form, FormField } from "@primevue/forms";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Textarea from "primevue/textarea";
import Calendar from "primevue/calendar";
import Select from "primevue/select";
import FileUpload from "primevue/fileupload";
import Button from "primevue/button";
import Message from "primevue/message";
import { uploadFile } from "@/services/firebase";

const toast = useToast();
const router = useRouter();

// Form validation schema
const resolver = zodResolver(
  z.object({
    title: z.string().min(1, { message: "Event title is required." }),
    // PrimeVue Calendar returns Date object
    date: z.any().refine((v) => v instanceof Date, { message: "Event date is required." }),
    // Times are free-typed strings to allow manual input
    startTime: z.string().regex(/^\d{1,2}:\d{2}$/, { message: "Start time must be HH:MM (24h)" }),
    endTime: z.string().regex(/^\d{1,2}:\d{2}$/, { message: "End time must be HH:MM (24h)" }),
    location: z.string().min(1, { message: "Location is required." }),
    organiser: z.string().min(1, { message: "Organiser name is required." }),
    bookingSlots: z.number().min(1, { message: "At least 1 booking slot is required." }),
    price: z.number().min(0, { message: "Price must be ≥ 0" }),
    description: z.string().min(10, { message: "Description must be at least 10 characters." }),
    format: z.string().min(1, { message: "Format is required." }),
    venueType: z.string().optional(), // Required only when format=offline (validated on submit)
    type: z.string().min(1, { message: "Type is required." }),
    region: z.string().min(1, { message: "Region is required." }),
    image: z.any().optional(),
  })
);


const formatOptions = [
  { label: "Offline", value: "offline" },
  { label: "Online", value: "online" },
];

const typeOptions = [
  { label: "Sports", value: "sports" },
  { label: "Arts", value: "arts" },
  { label: "Culture", value: "culture" },
  { label: "Music", value: "music" },
  { label: "Performance", value: "performance" },
  { label: "Workshop", value: "workshop" },
  { label: "Other", value: "other" }
];

const regionOptions = [
  { label: "North", value: "north" },
  { label: "South", value: "south" },
  { label: "East", value: "east" },
  { label: "West", value: "west" },
  { label: "Central", value: "central" }
];

const venueOptions = [
  { label: "Indoor", value: "indoor" },
  { label: "Outdoor", value: "outdoor" },
  { label: "Both", value: "both" },
];

const selectedImage = ref(null);

// Handle file selection
const onFileSelect = (event) => {
  selectedImage.value = event.files[0];
};

// Handle form submission
const onFormSubmit = async (formData) => {
  // Helper: format Date -> YYYY-MM-DD
  const fmtDate = (d) => {
    try {
      const yyyy = d.getFullYear();
      const mm = String(d.getMonth() + 1).padStart(2, "0");
      const dd = String(d.getDate()).padStart(2, "0");
      return `${yyyy}-${mm}-${dd}`;
    } catch {
      return "";
    }
  };
  // Helper: normalize "H:MM" -> "HH:MM"
  const toHHMM = (s) => {
    const [h, m] = String(s || "").split(":");
    const hh = String(parseInt(h || "0", 10)).padStart(2, "0");
    const mm = String(parseInt(m || "0", 10)).padStart(2, "0");
    return `${hh}:${mm}`;
  };

  try {
    // Validate conditional venue requirement
    if (formData.format === "offline" && !formData.venueType) {
      toast.add({ severity: "error", summary: "Validation", detail: "Venue Type is required when Format is Offline", life: 3000 });
      return;
    }

    // Upload image if selected
    let imageUrl = "";
    if (selectedImage.value) {
      const file = selectedImage.value;
      const safeName = (file.name || `event_${Date.now()}.jpg`).replace(/[^\w.\-]+/g, "_");
      const path = `events/${Date.now()}_${safeName}`;
      imageUrl = await uploadFile(path, file);
    }

    // Compose backend payload
    const payload = {
      title: formData.title,
      description: formData.description,
      format: formData.format,
      venueType: formData.format === "offline" ? (formData.venueType || "") : null,
      type: formData.type,
      region: formData.region,
      organiser: formData.organiser,
      location: formData.location,
      date: fmtDate(formData.date),
      startTime: toHHMM(formData.startTime),
      endTime: toHHMM(formData.endTime),
      price: typeof formData.price === "number" ? formData.price : 0,
      maxParticipants: formData.bookingSlots,
      imageUrl,
    };

    // Submit to backend
    const resp = await (await import("@/services/api")).default.post("/api/admin/events", payload);
    if (resp?.data?.success) {
      toast.add({ severity: "success", summary: "Event Created", detail: "Event created successfully", life: 3000 });
      router.push({ name: "Discover" });
    } else {
      throw new Error(resp?.data?.error || "Unknown error");
    }
  } catch (error) {
    console.error("Create event failed", error);
    const msg = error?.response?.data?.error || error?.message || "Failed to create event. Please try again.";
    toast.add({ severity: "error", summary: "Error", detail: msg, life: 4000 });
  }
};

// Handle cancel action
const handleCancel = () => {
  router.go(-1); // Go back to previous page
};
</script>

<style scoped>
.event-creation-container {
  min-height: 100vh;
  background: #ffc67b;
;
}

.main-content {
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.form-container {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
}

.page-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
}

.event-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.flex-1 {
  flex: 1;
}

.field-label {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #3b82f6;
  outline: none;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.description-textarea {
  resize: vertical;
  min-height: 100px;
}

.form-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.cancel-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #4b5563;
}

.create-btn {
  background: #ec6212;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.create-btn:hover {
  background: #2563eb;
}

/* Responsive design */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
  
  .form-container {
    padding: 1.5rem;
  }
  
  .form-row {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .form-buttons {
    flex-direction: column-reverse;
  }
}
</style>