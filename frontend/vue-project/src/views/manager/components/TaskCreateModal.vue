<!-- frontend/src/views/manager/components/TaskCreateModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-md">
      <!-- Заголовок -->
      <div class="border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Новая задача</h3>
          <button 
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Форма -->
      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Основные поля -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Название *</label>
          <input
            v-model="formData.title"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Введите название задачи"
            required
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
          <textarea
            v-model="formData.description"
            rows="2"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="Описание задачи"
          ></textarea>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Дата *</label>
            <input
              v-model="formData.date"
              type="date"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Время *</label>
            <input
              v-model="formData.time"
              type="time"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Приоритет</label>
            <select
              v-model="formData.priority"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Тип задачи</label>
            <select
              v-model="formData.task_type"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="task">Задача</option>
              <option value="meeting">Встреча</option>
              <option value="reminder">Напоминание</option>
              <option value="deadline">Дедлайн</option>
            </select>
          </div>
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Место</label>
          <input
            v-model="formData.location"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Например: Офис, кабинет 301"
          >
        </div>
        
        <!-- Кнопки -->
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Отмена
          </button>
          <button
            type="submit"
            :disabled="!isFormValid || loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Создать
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['close', 'save'])

const loading = ref(false)
const formData = ref({
  title: '',
  description: '',
  date: new Date().toISOString().split('T')[0],
  time: '09:00',
  priority: 'medium',
  task_type: 'task',
  location: '',
  color: '#4CAF50'
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
  emit('save', { ...formData.value })
  loading.value = false
}
</script>