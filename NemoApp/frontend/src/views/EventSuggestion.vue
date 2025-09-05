<template>
  <div class="suggest-event-container">
    <div class="suggestion-form-box">
      <h1 class="form-title">Leave your suggestions below</h1>
      
      <form @submit.prevent="submitSuggestion" class="suggestion-form">
        <div class="textarea-container">
          <textarea
            v-model="suggestion"
            class="suggestion-textarea"
            placeholder="Type your suggestion here"
            rows="8"
            @focus="handleFocus"
            @blur="handleBlur"
          ></textarea>
        </div>
        
        <div class="button-container">
          <button 
            type="submit" 
            class="submit-btn"
            :disabled="!suggestion.trim()"
          >
            Submit Suggestion
          </button>
          <button 
            type="button" 
            class="clear-btn"
            @click="clearSuggestion"
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from "vue-router";


const toast = useToast();
const suggestion = ref('');
const isFocused = ref(false);
const router = useRouter();
 
const handleFocus = () => {
  isFocused.value = true;
};

const handleBlur = () => {
  isFocused.value = false;
};

const submitSuggestion = () => {
  if (!suggestion.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'Please enter a suggestion before submitting.',
      life: 3000
    });
    return;
  }

  // Here you would typically send the suggestion to your backend
  console.log('Suggestion submitted:', suggestion.value);
  
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Thank you for your suggestion! We appreciate your feedback.',
    life: 4000
  });
  
  // Clear the form after successful submission
  suggestion.value = '';
};

const clearSuggestion = () => {
  suggestion.value = '';
};
</script>

<style scoped>
.suggest-event-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f4f0 0%, #faf7f4 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.suggestion-form-box {
  background: #ffeedd;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  border: 1px solid #ffd4b3;
}

.form-title {
  color: #8b4513;
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 2rem;
  font-family: 'Poppins', sans-serif;
}

.suggestion-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.textarea-container {
  position: relative;
}

.suggestion-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid #ffcc99;
  border-radius: 12px;
  font-size: 1rem;
  font-family: 'Arial', sans-serif;
  line-height: 1.5;
  resize: vertical;
  min-height: 150px;
  background: white;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.suggestion-textarea::placeholder {
  color: #999;
  opacity: 1;
  font-style: italic;
}

.suggestion-textarea:focus {
  outline: none;
  border-color: #ff9966;
  box-shadow: 0 0 0 3px rgba(255, 153, 102, 0.2);
}

.suggestion-textarea:focus::placeholder {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.button-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.submit-btn {
  background: linear-gradient(135deg, #ff9966 0%, #ff7733 100%);
  color: white;
  border: none;
  padding: 0.875rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff7733 0%, #ff5500 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 119, 51, 0.3);
}

.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

.clear-btn {
  background: transparent;
  color: #8b4513;
  border: 2px solid #ff9966;
  padding: 0.875rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'Poppins', sans-serif;
}

.clear-btn:hover {
  background: #ff9966;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 153, 102, 0.3);
}

/* Responsive design */
@media (max-width: 768px) {
  .suggest-event-container {
    padding: 1rem;
  }
  
  .suggestion-form-box {
    padding: 2rem;
  }
  
  .form-title {
    font-size: 1.5rem;
  }
  
  .button-container {
    flex-direction: column;
    align-items: center;
  }
  
  .submit-btn,
  .clear-btn {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .suggestion-form-box {
    padding: 1.5rem;
  }
  
  .form-title {
    font-size: 1.25rem;
  }
}
</style>