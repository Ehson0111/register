// useToast.js 

//система уведомлений 
import { ref, computed } from 'vue'

// Global toast state
const toastState = ref({
  show: false,
  message: '',
  type: 'info',
  duration: 5000
})

export function useToast() {
  const showToastMessage = (message, type = 'info', duration = 5000) => {
    toastState.value = {
      show: true,
      message,
      type,
      duration
    }
  }

  const hideToast = () => {
    toastState.value.show = false
  }

  const showSuccess = (message, duration = 5000) => showToastMessage(message, 'success', duration) //ShowSuccess('успешно')
  const showError = (message, duration = 5000) => showToastMessage(message, 'error', duration)
  const showWarning = (message, duration = 5000) => showToastMessage(message, 'warning', duration)
  const showInfo = (message, duration = 5000) => showToastMessage(message, 'info', duration)

  // Computed properties for reactive access
  const showToast = computed(() => toastState.value.show)
  const toastMessage = computed(() => toastState.value.message)
  const toastType = computed(() => toastState.value.type)

  return {
    // State (reactive)
    showToast,    // состояние: показывать?
    toastMessage,  // состояние: текст
    toastType,// состояние: тип

    // Actions
    showToast: showToastMessage,
    hideToast,
    showSuccess, // действие: показать успех
    showError,
    showWarning,
    showInfo
  }
}