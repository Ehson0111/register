<!-- frontend/src/views/manager/components/TaskModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-lg font-medium">
          {{ isEditMode ? 'Редактировать задачу' : 'Новая задача' }}
        </h3>
        <button 
          @click="$emit('close')"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Название *
          </label>
          <input 
            v-model="formData.title"
            type="text" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Введите название задачи"
            required
          >
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Описание
          </label>
          <textarea 
            v-model="formData.description"
            rows="3"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Описание задачи"
          ></textarea>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Дата *
            </label>
            <input 
              v-model="formData.date"
              type="date" 
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Время *
            </label>
            <input 
              v-model="formData.time"
              type="time" 
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Приоритет
            </label>
            <select 
              v-model="formData.priority"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Тип задачи
            </label>
            <select 
              v-model="formData.task_type"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="task">Задача</option>
              <option value="meeting">Встреча</option>
              <option value="reminder">Напоминание</option>
              <option value="deadline">Дедлайн</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Место
          </label>
          <input 
            v-model="formData.location"
            type="text" 
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Например: Офис, кабинет 301"
          >
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Цвет
          </label>
          <div class="flex space-x-2">
            <button 
              v-for="color in colorOptions"
              :key="color"
              type="button"
              @click="formData.color = color"
              class="w-8 h-8 rounded-full border-2"
              :class="[
                `bg-[${color}]`,
                formData.color === color ? 'border-blue-500' : 'border-gray-300'
              ]"
              :style="{ backgroundColor: color }"
              :title="color"
            ></button>
          </div>
        </div>

        <div v-if="isEditMode" class="flex items-center">
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
            :disabled="!isFormValid"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {{ isEditMode ? 'Сохранить' : 'Создать' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  task: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const isEditMode = computed(() => !!props.task)

const formData = ref({
  title: '',
  description: '',
  date: new Date().toISOString().split('T')[0],
  time: '09:00',
  priority: 'medium',
  task_type: 'task',
  location: '',
  color: '#4CAF50',
  completed: false
})

const colorOptions = [
  '#4CAF50', // green
  '#2196F3', // blue
  '#FF9800', // orange
  '#F44336', // red
  '#9C27B0', // purple
  '#795548', // brown
  '#607D8B'  // blue gray
]

const isFormValid = computed(() => {
  return formData.value.title.trim() !== '' && 
         formData.value.date !== '' && 
         formData.value.time !== ''
})

function handleSubmit() {
  if (!isFormValid.value) {
    alert('Пожалуйста, заполните все обязательные поля')
    return
  }
  
  emit('save', { ...formData.value })
}

onMounted(() => {
  if (props.task) {
    // Копируем данные задачи для редактирования
    formData.value = {
      ...props.task,
      // Убедимся, что дата в правильном формате
      date: new Date(props.task.date).toISOString().split('T')[0],
      // Если время null, установим значение по умолчанию
      time: props.task.time || '09:00'
    }
  }
})
</script>