<!-- frontend/src/views/manager/CalendarView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Календарь задач</h2>
        <p class="text-gray-600 mt-1">
          {{ currentDate }}
          <span v-if="loading" class="text-sm text-blue-600 ml-2">Загрузка...</span>
        </p>
      </div>
      <button 
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Новая задача
      </button>
    </div>

    <!-- Блок фильтров и статистики -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div class="flex space-x-4 mb-4">
        <button 
          @click="loadAllTasks"
          :class="activeFilter === 'all' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'"
          class="px-4 py-2 rounded-lg text-sm font-medium"
        >
          Все задачи
        </button>
        <button 
          @click="loadTodayTasks"
          :class="activeFilter === 'today' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'"
          class="px-4 py-2 rounded-lg text-sm font-medium"
        >
          Сегодня
        </button>
        <button 
          @click="loadUpcomingTasks"
          :class="activeFilter === 'upcoming' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'"
          class="px-4 py-2 rounded-lg text-sm font-medium"
        >
          Предстоящие
        </button>
        <button 
          @click="loadOverdueTasks"
          :class="activeFilter === 'overdue' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'"
          class="px-4 py-2 rounded-lg text-sm font-medium"
        >
          Просроченные
        </button>
      </div>

      <!-- Статистика -->
      <div v-if="stats" class="grid grid-cols-4 gap-4">
        <div class="bg-gray-50 p-3 rounded-lg">
          <div class="text-2xl font-bold text-gray-900">{{ stats.total_tasks }}</div>
          <div class="text-sm text-gray-600">Всего задач</div>
        </div>
        <div class="bg-green-50 p-3 rounded-lg">
          <div class="text-2xl font-bold text-green-900">{{ stats.completed_tasks }}</div>
          <div class="text-sm text-green-600">Выполнено</div>
        </div>
        <div class="bg-yellow-50 p-3 rounded-lg">
          <div class="text-2xl font-bold text-yellow-900">{{ stats.high_priority_tasks }}</div>
          <div class="text-sm text-yellow-600">Высокий приоритет</div>
        </div>
        <div class="bg-red-50 p-3 rounded-lg">
          <div class="text-2xl font-bold text-red-900">{{ stats.overdue_tasks }}</div>
          <div class="text-sm text-red-600">Просрочено</div>
        </div>
      </div>
    </div>

    <!-- Календарь -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-lg font-semibold">Календарь на {{ currentMonthYear }}</h3>
        <div class="flex space-x-2">
          <button @click="prevMonth" class="p-2 hover:bg-gray-100 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button @click="nextMonth" class="p-2 hover:bg-gray-100 rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Дни недели -->
      <div class="grid grid-cols-7 gap-4 mb-4">
        <div 
          v-for="day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']" 
          :key="day"
          class="text-center font-medium text-gray-600 py-2"
        >
          {{ day }}
        </div>
      </div>
      
      <!-- Ячейки календаря -->
      <div class="grid grid-cols-7 gap-4">
        <div 
          v-for="day in calendarDays" 
          :key="day.date"
          class="min-h-32 border border-gray-200 rounded-lg p-2 hover:bg-gray-50 transition-colors"
          :class="{
            'bg-blue-50': day.isToday,
            'text-gray-400': !day.isCurrentMonth,
            'border-blue-200': day.hasTasks
          }"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium">{{ day.day }}</span>
            <span 
              v-if="day.isToday"
              class="w-2 h-2 bg-blue-600 rounded-full"
            ></span>
          </div>
          
          <div class="space-y-1 max-h-20 overflow-y-auto">
            <div 
              v-for="task in getTasksForDay(day.date)"
              :key="task.id"
              class="text-xs p-2 rounded cursor-pointer transition-colors"
              :class="getTaskClasses(task)"
              @click="openTaskDetails(task)"
            >
              <div class="flex items-center justify-between">
                <div class="font-medium truncate flex-1">{{ task.title }}</div>
                <div class="flex items-center space-x-1">
                  <input 
                    type="checkbox" 
                    :checked="task.completed"
                    @click.stop="toggleTaskComplete(task.id)"
                    class="w-3 h-3"
                  />
                  <button 
                    @click.stop="deleteTask(task.id)"
                    class="text-gray-400 hover:text-red-500"
                  >
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div v-if="task.time" class="text-gray-600 text-xs mt-1">
                {{ formatTime(task.time) }}
                <span v-if="task.location" class="ml-2">📍 {{ task.location }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Список задач (альтернативный вид) -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-semibold mb-4">Список задач ({{ tasks.length }})</h3>
      <div class="space-y-3">
        <div 
          v-for="task in tasks" 
          :key="task.id"
          class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  :checked="task.completed"
                  @change="toggleTaskComplete(task.id)"
                  class="w-4 h-4"
                />
                <span class="font-medium" :class="{ 'line-through text-gray-500': task.completed }">
                  {{ task.title }}
                </span>
                <span :class="getPriorityBadge(task.priority)" class="text-xs px-2 py-1 rounded">
                  {{ task.priority_display }}
                </span>
                <span v-if="task.is_overdue" class="text-xs px-2 py-1 bg-red-100 text-red-800 rounded">
                  Просрочено
                </span>
              </div>
              <p class="text-gray-600 text-sm mt-1">{{ task.description }}</p>
              <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                <span>📅 {{ task.formatted_date }}</span>
                <span v-if="task.time">🕒 {{ formatTime(task.time) }}</span>
                <span v-if="task.location">📍 {{ task.location }}</span>
                <span>👤 {{ task.manager_id }}</span>
              </div>
            </div>
            <button 
              @click="deleteTask(task.id)"
              class="text-gray-400 hover:text-red-500 p-1"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания задачи -->
    <TaskModal 
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @save="handleCreateTask"
    />

    <!-- Модальное окно просмотра/редактирования задачи -->
    <TaskModal 
      v-if="showEditModal && selectedTask"
      :task="selectedTask"
      @close="showEditModal = false"
      @save="handleUpdateTask"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../store/auth'
import calendarService from '../../services/calendarService'
import TaskModal from './components/TaskModal.vue'

const authStore = useAuthStore()
const tasks = ref([])
const loading = ref(false)
const stats = ref(null)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedTask = ref(null)
const activeFilter = ref('all')

// Дата для календаря
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())

// Вычисляемые свойства
const currentDate = computed(() => {
  return new Date().toLocaleDateString('ru-RU', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

const currentMonthYear = computed(() => {
  return new Date(currentYear.value, currentMonth.value).toLocaleDateString('ru-RU', {
    month: 'long',
    year: 'numeric'
  })
})

// Генерация дней календаря (ваш существующий код)
const calendarDays = computed(() => {
  // ... ваш существующий код генерации календаря
})

// Загрузка данных
async function loadAllTasks() {
  try {
    loading.value = true
    activeFilter.value = 'all'
    const response = await calendarService.getTasks()
    tasks.value = response
    console.log('Загружены все задачи:', tasks.value.length)
  } catch (error) {
    console.error('Ошибка загрузки задач:', error)
    alert('Ошибка загрузки задач')
  } finally {
    loading.value = false
  }
}

async function loadTodayTasks() {
  try {
    loading.value = true
    activeFilter.value = 'today'
    const response = await calendarService.getTodayTasks()
    tasks.value = response
  } catch (error) {
    console.error('Ошибка загрузки задач на сегодня:', error)
  } finally {
    loading.value = false
  }
}

async function loadUpcomingTasks() {
  try {
    loading.value = true
    activeFilter.value = 'upcoming'
    const response = await calendarService.getUpcomingTasks()
    tasks.value = response
  } catch (error) {
    console.error('Ошибка загрузки предстоящих задач:', error)
  } finally {
    loading.value = false
  }
}

async function loadOverdueTasks() {
  try {
    loading.value = true
    activeFilter.value = 'overdue'
    const response = await calendarService.getOverdueTasks()
    tasks.value = response
  } catch (error) {
    console.error('Ошибка загрузки просроченных задач:', error)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    const response = await calendarService.getStats()
    stats.value = response
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

// Создание задачи
async function handleCreateTask(taskData) {
  try {
    const newTask = await calendarService.createTask({
      ...taskData,
      task_type: taskData.task_type || 'task',
      is_recurring: false,
      recurrence_rule: ''
    })
    
    // Обновляем список задач
    tasks.value = [newTask, ...tasks.value]
    await loadStats() // Обновляем статистику
    showCreateModal.value = false
    
    alert('Задача успешно создана!')
  } catch (error) {
    console.error('Ошибка создания задачи:', error)
    alert('Ошибка создания задачи: ' + (error.response?.data?.error || error.message))
  }
}

// Обновление задачи
async function handleUpdateTask(updatedTask) {
  try {
    await calendarService.updateTask(updatedTask.id, updatedTask)
    
    // Обновляем задачу в списке
    const index = tasks.value.findIndex(t => t.id === updatedTask.id)
    if (index !== -1) {
      tasks.value[index] = updatedTask
    }
    
    showEditModal.value = false
    selectedTask.value = null
    
    alert('Задача успешно обновлена!')
  } catch (error) {
    console.error('Ошибка обновления задачи:', error)
    alert('Ошибка обновления задачи')
  }
}

// Переключение статуса выполнения
async function toggleTaskComplete(taskId) {
  try {
    const updatedTask = await calendarService.toggleTaskComplete(taskId)
    
    // Обновляем задачу в списке
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      tasks.value[index] = updatedTask
    }
    
    await loadStats() // Обновляем статистику
  } catch (error) {
    console.error('Ошибка обновления статуса задачи:', error)
  }
}

// Удаление задачи
async function deleteTask(taskId) {
  if (!confirm('Вы уверены, что хотите удалить эту задачу?')) return
  
  try {
    await calendarService.deleteTask(taskId)
    
    // Удаляем задачу из списка
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    
    await loadStats() // Обновляем статистику
    alert('Задача удалена')
  } catch (error) {
    console.error('Ошибка удаления задачи:', error)
    alert('Ошибка удаления задачи')
  }
}

// Получение задач для дня
function getTasksForDay(date) {
  return tasks.value.filter(task => {
    const taskDate = new Date(task.date).toISOString().split('T')[0]
    return taskDate === date
  })
}

// Классы для задач
function getTaskClasses(task) {
  const baseClass = 'border-l-4 '
  if (task.completed) {
    return baseClass + 'bg-gray-100 border-gray-400'
  }
  
  const colorMap = {
    high: 'bg-red-50 border-red-400',
    medium: 'bg-yellow-50 border-yellow-400',
    low: 'bg-green-50 border-green-400'
  }
  
  return baseClass + (colorMap[task.priority] || 'bg-gray-50 border-gray-300')
}

// Бейдж приоритета
function getPriorityBadge(priority) {
  const badgeMap = {
    high: 'bg-red-100 text-red-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800'
  }
  return badgeMap[priority] || 'bg-gray-100 text-gray-800'
}

// Форматирование времени
function formatTime(time) {
  if (!time) return ''
  const [hours, minutes] = time.split(':')
  return `${hours}:${minutes}`
}

// Открыть детали задачи
function openTaskDetails(task) {
  selectedTask.value = { ...task }
  showEditModal.value = true
}

// Навигация по месяцам
function prevMonth() {
  currentMonth.value -= 1
  if (currentMonth.value < 0) {
    currentMonth.value = 11
    currentYear.value -= 1
  }
  loadTasksForMonth()
}

function nextMonth() {
  currentMonth.value += 1
  if (currentMonth.value > 11) {
    currentMonth.value = 0
    currentYear.value += 1
  }
  loadTasksForMonth()
}

async function loadTasksForMonth() {
  try {
    const response = await calendarService.getTasksByMonth(
      currentYear.value,
      currentMonth.value + 1
    )
    tasks.value = response
  } catch (error) {
    console.error('Ошибка загрузки задач за месяц:', error)
  }
}

// Инициализация
onMounted(async () => {
  console.log('CalendarView mounted, user:', authStore.user)
  
  if (!authStore.isAuthenticated) {
    alert('Вы не авторизованы')
    return
  }
  
  await Promise.all([
    loadAllTasks(),
    loadStats()
  ])
})
</script>

<style scoped>
/* Стили для скролла в ячейках календаря */
.max-h-20 {
  max-height: 5rem;
}

/* Анимации */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>