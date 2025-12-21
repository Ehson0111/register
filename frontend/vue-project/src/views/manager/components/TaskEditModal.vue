<!-- frontend/src/views/manager/components/TaskEditModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-2xl max-h-[90vh] overflow-hidden">
      <div class="border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900">Редактирование задачи</h3>
          <button 
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      <div class="p-6 overflow-y-auto max-h-[70vh]">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Форма такая же как в TaskCreateModal, но с заполненными данными -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название *</label>
            <input
              v-model="formData.title"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
          </div>
          
          <!-- Остальные поля аналогично TaskCreateModal -->
          
          <!-- Дополнительные поля для редактирования -->
          <div class="flex items-center">
            <input
              v-model="formData.completed"
              type="checkbox"
              id="completed"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label for="completed" class="ml-2 text-sm text-gray-700">
              Задача выполнена
            </label>
          </div>
          
          <!-- Кнопки -->
          <div class="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              @click="$emit('close')"
              class="px-6 py-2.5 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              :disabled="!isFormValid || loading"
              class="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const formData = ref({
  title: '',
  description: '',
  date: '',
  time: '',
  priority: 'medium',
  task_type: 'task',
  location: '',
  color: '#4CAF50',
  completed: false
})

const isFormValid = computed(() => {
  return formData.value.title.trim() !== '' &&
         formData.value.date !== '' &&
         formData.value.time !== ''
})

const handleSubmit = () => {
  if (!isFormValid.value) {
    alert('Пожалуйста, заполните все обязательные поля')
    return
  }
  
  loading.value = true
  
  const taskData = {
    ...formData.value,
    id: props.task.id
  }
  
  emit('save', taskData)
  loading.value = false
}

onMounted(() => {
  // Заполняем форму данными задачи
  Object.assign(formData.value, {
    title: props.task.title || '',
    description: props.task.description || '',
    date: new Date(props.task.date).toISOString().split('T')[0],
    time: props.task.time ? props.task.time.substring(0, 5) : '09:00',
    priority: props.task.priority || 'medium',
    task_type: props.task.task_type || 'task',
    location: props.task.location || '',
    color: props.task.color || '#4CAF50',
    completed: props.task.completed || false
  })
})
</script>