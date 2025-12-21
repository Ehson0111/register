<!-- frontend/src/views/manager/components/TaskDetailModal.vue -->
<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-lg">
      <div class="border-b border-gray-200 px-6 py-4">
        <div class="flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900">Детали задачи</h3>
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
      
      <div class="p-6">
        <div class="space-y-6">
          <!-- Основная информация -->
          <div>
            <h4 class="text-lg font-medium text-gray-900 mb-2">{{ task.title }}</h4>
            <p v-if="task.description" class="text-gray-600 mb-4">{{ task.description }}</p>
            
            <!-- Мета информация -->
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div class="text-gray-500">Дата:</div>
                <div class="font-medium">{{ task.formatted_date }}</div>
              </div>
              <div>
                <div class="text-gray-500">Время:</div>
                <div class="font-medium">{{ formatTime(task.time) }}</div>
              </div>
              <div>
                <div class="text-gray-500">Приоритет:</div>
                <div :class="getPriorityClass(task.priority)" class="font-medium">
                  {{ task.priority_display }}
                </div>
              </div>
              <div>
                <div class="text-gray-500">Тип:</div>
                <div class="font-medium">{{ task.task_type_display }}</div>
              </div>
              <div v-if="task.location">
                <div class="text-gray-500">Место:</div>
                <div class="font-medium">{{ task.location }}</div>
              </div>
              <div>
                <div class="text-gray-500">Статус:</div>
                <div :class="task.completed ? 'text-green-600' : 'text-yellow-600'" class="font-medium">
                  {{ task.completed ? 'Выполнена' : 'В работе' }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Дополнительная информация -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h5 class="text-sm font-medium text-gray-700 mb-2">Дополнительно</h5>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">ID менеджера:</span>
                <span class="font-medium">{{ task.manager_id }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Создана:</span>
                <span class="font-medium">{{ formatDateTime(task.created_at) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Обновлена:</span>
                <span class="font-medium">{{ formatDateTime(task.updated_at) }}</span>
              </div>
              <div v-if="task.is_overdue && !task.completed" class="text-red-600 font-medium">
                ⚠️ Задача просрочена
              </div>
            </div>
          </div>
          
          <!-- Кнопки действий -->
          <div class="flex justify-end space-x-3 pt-4 border-t">
            <button
              @click="$emit('toggle')"
              :class="task.completed ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' : 'bg-green-100 text-green-700 hover:bg-green-200'"
              class="px-4 py-2 rounded-lg font-medium transition-colors"
            >
              {{ task.completed ? 'Отметить невыполненной' : 'Отметить выполненной' }}
            </button>
            <button
              @click="$emit('edit')"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Редактировать
            </button>
            <button
              @click="$emit('delete')"
              class="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors font-medium"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  task: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'edit', 'toggle', 'delete'])

const formatTime = (time) => {
  if (!time) return 'Не указано'
  return time.substring(0, 5)
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return ''
  const date = new Date(dateTime)
  return date.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getPriorityClass = (priority) => {
  const classes = {
    high: 'text-red-600',
    medium: 'text-yellow-600',
    low: 'text-green-600'
  }
  return classes[priority] || 'text-gray-600'
}
</script>