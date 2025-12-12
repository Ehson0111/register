<!-- frontend/src/views/manager/CalendarView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Календарь задач</h2>
      <button 
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        + Новая задача
      </button>
    </div>

    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div class="grid grid-cols-7 gap-4 mb-6">
        <div 
          v-for="day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']" 
          :key="day"
          class="text-center font-medium text-gray-600 py-2"
        >
          {{ day }}
        </div>
      </div>
      
      <div class="grid grid-cols-7 gap-4">
        <div 
          v-for="day in calendarDays" 
          :key="day.date"
          class="min-h-24 border border-gray-200 rounded-lg p-2 hover:bg-gray-50 transition-colors"
          :class="{
            'bg-blue-50': day.isToday,
            'text-gray-400': !day.isCurrentMonth
          }"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium">{{ day.day }}</span>
            <span 
              v-if="day.isToday"
              class="w-2 h-2 bg-blue-600 rounded-full"
            ></span>
          </div>
          
          <div class="space-y-1">
            <div 
              v-for="task in getTasksForDay(day.date)"
              :key="task.id"
              class="text-xs p-1 rounded cursor-pointer"
              :class="getTaskColor(task.priority)"
              @click="openTask(task)"
            >
              <div class="font-medium truncate">{{ task.title }}</div>
              <div class="text-gray-600">{{ formatTime(task.time) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания задачи -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium mb-4">Новая задача</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название *</label>
            <input 
              v-model="newTask.title"
              type="text" 
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Введите название задачи"
              required
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Описание</label>
            <textarea 
              v-model="newTask.description"
              rows="3"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Описание задачи"
            ></textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Дата *</label>
              <input 
                v-model="newTask.date"
                type="date" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Время *</label>
              <input 
                v-model="newTask.time"
                type="time" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Приоритет</label>
            <select 
              v-model="newTask.priority"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Низкий</option>
              <option value="medium">Средний</option>
              <option value="high">Высокий</option>
            </select>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button 
            @click="showCreateModal = false"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Отмена
          </button>
          <button 
            @click="createTask"
            :disabled="!isFormValid"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Создать
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Task {
  id: number
  title: string
  description: string
  date: string
  time: string
  priority: 'low' | 'medium' | 'high'
  completed: boolean
}

const showCreateModal = ref(false)
const tasks = ref<Task[]>([])

const newTask = ref({
  title: '',
  description: '',
  date: new Date().toISOString().split('T')[0],
  time: '09:00',
  priority: 'medium' as 'low' | 'medium' | 'high'
})

// ИСПРАВЛЕННАЯ генерация календаря
const calendarDays = computed(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()
  
  // Первый день месяца
  const firstDay = new Date(year, month, 1)
  // Последний день месяца
  const lastDay = new Date(year, month + 1, 0)
  
  const days = []
  
  // День недели первого дня месяца (0 - воскресенье, 6 - суббота)
  let firstDayOfWeek = firstDay.getDay()
  // Преобразуем к формату: 1 - понедельник, 7 - воскресенье
  firstDayOfWeek = firstDayOfWeek === 0 ? 7 : firstDayOfWeek
  
  // Количество дней предыдущего месяца для показа
  const daysFromPrevMonth = firstDayOfWeek - 1
  
  // Добавляем дни предыдущего месяца
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = daysFromPrevMonth; i > 0; i--) {
    const dayNumber = prevMonthLastDay - i + 1
    const date = new Date(year, month - 1, dayNumber)
    days.push({
      date: formatDateForComparison(date),
      day: dayNumber,
      isCurrentMonth: false,
      isToday: false
    })
  }
  
  // Добавляем дни текущего месяца
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i)
    days.push({
      date: formatDateForComparison(date),
      day: i,
      isCurrentMonth: true,
      isToday: date.toDateString() === today.toDateString()
    })
  }
  
  // Добавляем дни следующего месяца чтобы получить ровно 42 ячейки
  const totalCells = 42
  const daysNeeded = totalCells - days.length
  for (let i = 1; i <= daysNeeded; i++) {
    const date = new Date(year, month + 1, i)
    days.push({
      date: formatDateForComparison(date),
      day: i,
      isCurrentMonth: false,
      isToday: false
    })
  }
  
  return days
})

// ИСПРАВЛЕННЫЙ метод для сравнения дат
const getTasksForDay = (date: string) => {
  return tasks.value
    .filter(task => {
      // Приводим обе даты к одному формату для сравнения
      const taskDate = formatDateForComparison(new Date(task.date))
      const cellDate = formatDateForComparison(new Date(date))
      return taskDate === cellDate
    })
    .sort((a, b) => a.time.localeCompare(b.time))
}

// Универсальная функция для форматирования дат в YYYY-MM-DD
const formatDateForComparison = (date: Date): string => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Валидация формы
const isFormValid = computed(() => {
  return newTask.value.title.trim() !== '' && 
         newTask.value.date !== '' && 
         newTask.value.time !== ''
})

const getTaskColor = (priority: string) => {
  const colors = {
    low: 'bg-green-100 border border-green-200',
    medium: 'bg-yellow-100 border border-yellow-200',
    high: 'bg-red-100 border border-red-200'
  }
  return colors[priority] || 'bg-gray-100'
}

const formatTime = (time: string) => {
  const [hours, minutes] = time.split(':')
  return `${hours}:${minutes}`
}

const createTask = () => {
  if (!isFormValid.value) {
    alert('Пожалуйста, заполните все обязательные поля')
    return
  }

  // ИСПРАВЛЕНИЕ: Форматируем дату задачи для единообразия
  const taskDate = formatDateForComparison(new Date(newTask.value.date))
  
  const task: Task = {
    id: Date.now(),
    ...newTask.value,
    date: taskDate, // Используем отформатированную дату
    completed: false
  }
  
  tasks.value.push(task)
  showCreateModal.value = false
  
  // Сброс формы
  newTask.value = {
    title: '',
    description: '',
    date: new Date().toISOString().split('T')[0],
    time: '09:00',
    priority: 'medium'
  }
  
  // Для отладки
  console.log('Создана задача:', task)
  console.log('Все задачи:', tasks.value)
}

const openTask = (task: Task) => {
  console.log('Opening task:', task)
  alert(`Задача: ${task.title}\nДата: ${task.date}\nВремя: ${formatTime(task.time)}\nОписание: ${task.description}`)
}

// Для отладки - выводим информацию о календаре
const debugCalendar = () => {
  console.log('Отладочная информация календаря:')
  calendarDays.value.forEach((day, index) => {
    console.log(`Ячейка ${index}: число ${day.day}, дата ${day.date}, текущий месяц: ${day.isCurrentMonth}`)
  })
}

onMounted(() => {
  // Загрузка тестовых данных с ОТФОРМАТИРОВАННЫМИ датами
  const today = formatDateForComparison(new Date())
  
  tasks.value = [
    {
      id: 1,
      title: 'Встреча с клиентом',
      description: 'Обсуждение нового проекта',
      date: today,
      time: '10:00',
      priority: 'high',
      completed: false
    },
    {
      id: 2,
      title: 'Подготовка отчета',
      description: 'Еженедельный отчет по продажам',
      date: today,
      time: '14:30',
      priority: 'medium',
      completed: false
    }
  ]
  
  // Выводим отладочную информацию
  debugCalendar()
})
</script>