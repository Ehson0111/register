<!--
  [VIEW] CalendarView — календарь задач/событий
  Маршрут: /manager/calendar | Сервис: services/calendarService.js
-->
<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Заголовок и навигация -->
    <div class="mb-8">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Календарь задач</h1>
          <p class="text-gray-600 mt-2">{{ currentDate }}</p>
        </div>
        <div class="flex items-center space-x-4">
          <div class="relative">
            <input
              v-model="searchQuery"
              @input="handleSearch"
              type="text"
              placeholder="Поиск задач..."
              class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            @click="showCreateModal = true"
            class="bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 transition-colors flex items-center"
          >
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Новая задача
          </button>
        </div>
      </div>

      <!-- Фильтры и статистика -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
        <div class="flex flex-wrap gap-2 mb-4">
          <button
            @click="loadAllTasks"
            :class="activeFilter === 'all' ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-300 text-slate-900 border-slate-400'"
            class="px-4 py-2 border rounded-lg text-sm font-medium transition-all"
          >
            Все задачи
          </button>
          <button
            @click="loadTodayTasks"
            :class="activeFilter === 'today' ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-300 text-slate-900 border-slate-400'"
            class="px-4 py-2 border rounded-lg text-sm font-medium transition-all"
          >
            Сегодня
          </button>
          <button
            @click="loadUpcomingTasks"
            :class="activeFilter === 'upcoming' ? 'bg-blue-600 text-white border-blue-500' : 'bg-slate-300 text-slate-900 border-slate-400'"
            class="px-4 py-2 border rounded-lg text-sm font-medium transition-all"
          >
            Предстоящие
          </button>
          <button
            @click="loadOverdueTasks"
            :class="activeFilter === 'overdue' ? 'bg-red-600 text-white border-red-500' : 'bg-slate-300 text-slate-900 border-slate-400'"
            class="px-4 py-2 border rounded-lg text-sm font-medium transition-all"
          >
            Просроченные
          </button>
          <div class="relative">
            <select
              v-model="priorityFilter"
              @change="handlePriorityFilter"
              class="pl-3 pr-8 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Все приоритеты</option>
              <option value="high">Высокий</option>
              <option value="medium">Средний</option>
              <option value="low">Низкий</option>
            </select>
          </div>
          <div class="relative">
            <select
              v-model="typeFilter"
              @change="handleTypeFilter"
              class="pl-3 pr-8 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Все типы</option>
              <option value="task">Задача</option>
              <option value="meeting">Встреча</option>
              <option value="reminder">Напоминание</option>
              <option value="deadline">Дедлайн</option>
            </select>
          </div>
        </div>

        <!-- Статистика -->
        <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-gray-900">{{ stats.total_tasks }}</div>
            <div class="text-sm text-gray-600">Всего задач</div>
          </div>
          <div class="bg-green-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-green-900">{{ stats.completed_tasks }}</div>
            <div class="text-sm text-green-600">Выполнено</div>
          </div>
          <div class="bg-yellow-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-yellow-900">{{ stats.high_priority_tasks }}</div>
            <div class="text-sm text-yellow-600">Высокий приоритет</div>
          </div>
          <div class="bg-red-50 p-4 rounded-lg">
            <div class="text-2xl font-bold text-red-900">{{ stats.overdue_tasks }}</div>
            <div class="text-sm text-red-600">Просрочено</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Основной контент в 2 колонки -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Левая колонка - Календарь -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <!-- Заголовок календаря -->
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900">{{ currentMonthYear }}</h2>
            <div class="flex items-center space-x-2">
              <button
                @click="prevMonth"
                class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Предыдущий месяц"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                @click="nextMonth"
                class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                title="Следующий месяц"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
              <button
                @click="loadCurrentMonth"
                class="p-2 hover:bg-gray-100 rounded-lg transition-colors text-sm text-gray-600"
                title="Текущий месяц"
              >
                Сегодня
              </button>
            </div>
          </div>

          <!-- Дни недели -->
          <div class="grid grid-cols-7 gap-2 mb-3">
            <div
              v-for="day in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']"
              :key="day"
              class="text-center font-medium text-gray-600 py-2"
            >
              {{ day }}
            </div>
          </div>

          <!-- Ячейки календаря -->
          <div class="grid grid-cols-7 gap-2">
            <div
              v-for="day in calendarDays"
              :key="day.date"
              class="min-h-32 border border-gray-200 rounded-lg p-2 transition-all duration-200"
              :class="{
                'bg-blue-50 border-blue-200': day.isToday,
                'bg-gray-50': !day.isCurrentMonth,
                'text-gray-400': !day.isCurrentMonth,
                'border-blue-300': day.hasTasks
              }"
            >
              <!-- Заголовок дня -->
              <div class="flex justify-between items-center mb-2">
                <div class="flex items-center">
                  <span 
                    class="font-medium text-sm w-6 h-6 flex items-center justify-center rounded-full"
                    :class="{
                      'bg-blue-600 text-white': day.isToday && day.isCurrentMonth,
                      'text-gray-900': !day.isToday && day.isCurrentMonth
                    }"
                  >
                    {{ day.day }}
                  </span>
                </div>
                <div class="flex items-center">
                  <span 
                    v-if="day.isToday" 
                    class="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded"
                  >
                    Сегодня
                  </span>
                  <!-- <span 
                    v-else-if="getTasksForDay(day.date).length > 0" 
                    class="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded"
                  >
                    {{ getTasksForDay(day.date).length }}
                  </span> -->
                  <span 
                        v-else-if="getTasksForDay(day.date).length > 0" 
                        class="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded font-medium"
                      >
                        {{ getTasksForDay(day.date).length }}
                      </span>
                </div>
              </div>

              <!-- Задачи дня -->
              <div class="space-y-1 max-h-20 overflow-y-auto pr-1">
                <div
                  v-for="task in getTasksForDay(day.date).slice(0, 3)"
                  :key="task.id"
                  @click.stop="openTaskDetails(task)"
                  :class="getTaskClasses(task)"
                  class="px-2 py-1.5 rounded text-xs cursor-pointer transition-all hover:opacity-90 group relative"
                >
                  <!-- Полоска приоритета -->
                  <div 
                    :class="getPriorityColor(task.priority)"
                    class="absolute left-0 top-0 bottom-0 w-1 rounded-l"
                  ></div>
                  
                  <div class="ml-1.5">
                    <!-- Название задачи -->
                    <div class="flex items-start justify-between">
                      <span
                        class="font-medium truncate block"
                        :class="{ 'line-through': task.completed }"
                      >
                        {{ task.title }}
                      </span>
                    </div>
                    
                    <!-- Время и место -->
                    <div v-if="task.time || task.location" class="mt-0.5 text-xs opacity-75">
                      <div class="flex items-center truncate">
                        <span v-if="task.time" class="truncate">
                          {{ formatTime(task.time) }}
                        </span>
                        <span v-if="task.location" class="ml-1 truncate">
                          • {{ task.location }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Показать больше задач -->
                <div 
                  v-if="getTasksForDay(day.date).length > 3"
                  @click.stop="openDayView(day)"
                  class="text-xs text-blue-600 hover:text-blue-800 cursor-pointer text-center py-1 hover:bg-blue-50 rounded"
                >
                  +{{ getTasksForDay(day.date).length - 3 }} ещё
                </div>
                
                <!-- Сообщение о пустом дне -->
                <div 
                  v-else-if="getTasksForDay(day.date).length === 0 && day.isCurrentMonth"
                  class="text-xs text-blue-400 text-center py-2"
                >
                  Нет задач
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Правая колонка - Список задач -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 h-full">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900">Список задач</h2>
            <span class="text-sm text-gray-500">{{ filteredTasks.length }} задач</span>
          </div>

          <!-- Статус загрузки -->
          <div v-if="loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="text-gray-600 mt-2">Загрузка задач...</p>
          </div>

          <!-- Список задач -->
          <div v-else class="space-y-4 max-h-[calc(100vh-300px)] overflow-y-auto pr-2">
            <div
              v-for="task in filteredTasks"
              :key="task.id"
              @click="openTaskDetails(task)"
              class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-sm transition-all duration-200 cursor-pointer group"
            >
              <div class="flex items-start justify-between">
                <!-- Контент задачи -->
                <div class="flex-1 min-w-0">
                  <!-- Заголовок и приоритет -->
                  <div class="flex items-center mb-2">
                    <div
                      :class="getPriorityBadge(task.priority)"
                      class="text-xs px-2 py-0.5 rounded mr-2"
                    >
                      {{ task.priority_display }}
                    </div>
                    <span v-if="task.is_overdue && !task.completed" class="text-xs px-2 py-0.5 bg-red-100 text-red-800 rounded">
                      Просрочено
                    </span>
                  </div>

                  <!-- Название и статус -->
                  <div class="flex items-center mb-2">
                    <input
                      type="checkbox"
                      :checked="task.completed"
                      @change.stop="toggleTaskComplete(task.id)"
                      class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mr-2"
                    />
                    <h3
                      class="font-medium text-gray-900 truncate"
                      :class="{ 'line-through text-gray-500': task.completed }"
                    >
                      {{ task.title }}
                    </h3>
                  </div>

                  <!-- Описание -->
                  <p v-if="task.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
                    {{ task.description }}
                  </p>

                  <!-- Мета-информация -->
                  <div class="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                    <div class="flex items-center">
                      <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {{ task.formatted_date }}
                    </div>
                    <div v-if="task.time" class="flex items-center">
                      <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {{ formatTime(task.time) }}
                    </div>
                    <div v-if="task.location" class="flex items-center">
                      <svg class="w-3.5 h-3.5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {{ task.location }}
                    </div>
                  </div>
                </div>

                <!-- Кнопки действий -->
                <div class="flex flex-col items-center space-y-2 ml-3">
                  <button
                    @click.stop="editTask(task)"
                    :title="'Редактировать: ' + task.title"
                    class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    @click.stop="deleteTask(task.id)"
                    :title="'Удалить: ' + task.title"
                    class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Пустой список -->
            <div v-if="filteredTasks.length === 0 && !loading" class="text-center py-12">
              <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p class="text-gray-500 mb-2">Задачи не найдены</p>
              <button
                @click="showCreateModal = true"
                class="text-blue-600 hover:text-blue-800 font-medium"
              >
                Создайте первую задачу
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно создания -->
    <TaskCreateModal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      @save="handleCreateTask"
    />

    <!-- Модальное окно редактирования -->
    <TaskEditModal
      v-if="showEditModal && selectedTask"
      :task="selectedTask"
      @close="closeEditModal"
      @save="handleUpdateTask"
    />

    <!-- Модальное окно деталей -->
    <TaskDetailModal
      v-if="showDetailModal && selectedTask"
      :task="selectedTask"
      @close="closeDetailModal"
      @edit="editTaskFromDetail"
      @toggle="toggleTaskComplete(selectedTask.id)"
      @delete="deleteTask(selectedTask.id)"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useAuthStore } from "../../store/auth";
import calendarService from "../../services/calendarService";
import TaskCreateModal from "./components/TaskCreateModal.vue";
import TaskEditModal from "./components/TaskEditModal.vue";
import TaskDetailModal from "./components/TaskDetailModal.vue";

const authStore = useAuthStore();

// Состояние
const tasks = ref([]);
const filteredTasks = ref([]);
const loading = ref(false);
const stats = ref(null);
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showDetailModal = ref(false);
const selectedTask = ref(null);
const activeFilter = ref("all");
const searchQuery = ref("");
const priorityFilter = ref("");
const typeFilter = ref("");
const currentMonth = ref(new Date().getMonth());
const currentYear = ref(new Date().getFullYear());

// Вычисляемые свойства
const currentDate = computed(() => {
  return new Date().toLocaleDateString("ru-RU", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
});

const currentMonthYear = computed(() => {
  return new Date(currentYear.value, currentMonth.value).toLocaleDateString(
    "ru-RU",
    {
      month: "long",
      year: "numeric",
    }
  );
});

const calendarDays = computed(() => {
  const today = new Date();
  const year = currentYear.value;
  const month = currentMonth.value;

  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  const days = [];

  let firstDayOfWeek = firstDay.getDay();
  firstDayOfWeek = firstDayOfWeek === 0 ? 7 : firstDayOfWeek;

  const daysFromPrevMonth = firstDayOfWeek - 1;
  const prevMonthLastDay = new Date(year, month, 0).getDate();

  for (let i = daysFromPrevMonth; i > 0; i--) {
    const dayNumber = prevMonthLastDay - i + 1;
    const date = new Date(year, month - 1, dayNumber);
    days.push({
      date: formatDateForComparison(date),
      day: dayNumber,
      isCurrentMonth: false,
      isToday: false,
      hasTasks: getTasksForDay(formatDateForComparison(date)).length > 0,
    });
  }

  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i);
    days.push({
      date: formatDateForComparison(date),
      day: i,
      isCurrentMonth: true,
      isToday: date.toDateString() === today.toDateString(),
      hasTasks: getTasksForDay(formatDateForComparison(date)).length > 0,
    });
  }

  const totalCells = 42;
  const daysNeeded = totalCells - days.length;
  for (let i = 1; i <= daysNeeded; i++) {
    const date = new Date(year, month + 1, i);
    days.push({
      date: formatDateForComparison(date),
      day: i,
      isCurrentMonth: false,
      isToday: false,
      hasTasks: false,
    });
  }

  return days;
});

// Методы
const formatDateForComparison = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

const getTasksForDay = (date) => {
  return tasks.value
    .filter((task) => {
      const taskDate = formatDateForComparison(new Date(task.date));
      return taskDate === date;
    })
    .sort((a, b) => a.time?.localeCompare(b.time || "") || 0);
};

const getTaskClasses = (task) => {
  const baseClass = "relative overflow-hidden ";
  if (task.completed) {
    return baseClass + "bg-gray-100 text-gray-500";
  }

  return baseClass + "bg-white text-gray-900 border border-gray-200";
};

const getPriorityColor = (priority) => {
  const colorMap = {
    high: "bg-red-500",
    medium: "bg-yellow-500",
    low: "bg-green-500",
  };
  return colorMap[priority] || "bg-gray-400";
};

const getPriorityBadge = (priority) => {
  const badgeMap = {
    high: "bg-red-100 text-red-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-green-100 text-green-800",
  };
  return badgeMap[priority] || "bg-slate-300 text-slate-900";
};

const formatTime = (time) => {
  if (!time) return "";
  const [hours, minutes] = time.split(":");
  return `${hours}:${minutes}`;
};

const openDayView = (day) => {
  // Фильтруем задачи для выбранного дня
  const dayTasks = getTasksForDay(day.date);
  
  // Устанавливаем фильтр на этот день
  selectedTask.value = null;
  filteredTasks.value = dayTasks;
  
  // Прокручиваем к списку задач
  const taskList = document.querySelector('.lg\\:col-span-1');
  if (taskList) {
    taskList.scrollIntoView({ behavior: "smooth" });
  }
};

// Загрузка данных
const loadAllTasks = async () => {
  try {
    loading.value = true;
    activeFilter.value = "all";
    const response = await calendarService.getTasks();
    tasks.value = Array.isArray(response) ? response : [];
    applyFilters();
  } catch (error) {
    console.error("Ошибка загрузки задач:", error);
    showError("Не удалось загрузить задачи");
  } finally {
    loading.value = false;
  }
};

const loadTodayTasks = async () => {
  try {
    loading.value = true;
    activeFilter.value = "today";
    const response = await calendarService.getTodayTasks();
    tasks.value = Array.isArray(response) ? response : [];
    applyFilters();
  } catch (error) {
    console.error("Ошибка загрузки задач на сегодня:", error);
    showError("Не удалось загрузить задачи на сегодня");
  } finally {
    loading.value = false;
  }
};

const loadUpcomingTasks = async () => {
  try {
    loading.value = true;
    activeFilter.value = "upcoming";
    const response = await calendarService.getUpcomingTasks();
    tasks.value = Array.isArray(response) ? response : [];
    applyFilters();
  } catch (error) {
    console.error("Ошибка загрузки предстоящих задач:", error);
    showError("Не удалось загрузить предстоящие задачи");
  } finally {
    loading.value = false;
  }
};

const loadOverdueTasks = async () => {
  try {
    loading.value = true;
    activeFilter.value = "overdue";
    const response = await calendarService.getOverdueTasks();
    tasks.value = Array.isArray(response) ? response : [];
    applyFilters();
  } catch (error) {
    console.error("Ошибка загрузки просроченных задач:", error);
    showError("Не удалось загрузить просроченные задачи");
  } finally {
    loading.value = false;
  }
};

const loadStats = async () => {
  try {
    const response = await calendarService.getStats();
    stats.value = response;
  } catch (error) {
    console.error("Ошибка загрузки статистики:", error);
  }
};

const loadTasksForMonth = async () => {
  try {
    const response = await calendarService.getTasksByMonth(
      currentYear.value,
      currentMonth.value + 1
    );
    tasks.value = Array.isArray(response) ? response : [];
    applyFilters();
  } catch (error) {
    console.error("Ошибка загрузки задач за месяц:", error);
    showError("Не удалось загрузить задачи за месяц");
  }
};

const loadCurrentMonth = () => {
  const today = new Date();
  currentMonth.value = today.getMonth();
  currentYear.value = today.getFullYear();
  loadTasksForMonth();
};

// Фильтрация
const applyFilters = () => {
  let result = [...tasks.value];

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(
      (task) =>
        task.title.toLowerCase().includes(query) ||
        (task.description && task.description.toLowerCase().includes(query)) ||
        (task.location && task.location.toLowerCase().includes(query))
    );
  }

  if (priorityFilter.value) {
    result = result.filter((task) => task.priority === priorityFilter.value);
  }

  if (typeFilter.value) {
    result = result.filter((task) => task.task_type === typeFilter.value);
  }

  filteredTasks.value = result;
};

const handleSearch = () => {
  applyFilters();
};

const handlePriorityFilter = () => {
  applyFilters();
};

const handleTypeFilter = () => {
  applyFilters();
};

  // Операции с задачами
  const handleCreateTask = async (taskData) => {
    try {
      loading.value = true;
      const newTask = await calendarService.createTask({
        ...taskData,
        task_type: taskData.task_type || "task",
        is_recurring: false,
        recurrence_rule: "",
      });

      tasks.value = [newTask, ...tasks.value];
      await loadStats();
      showCreateModal.value = false;
      applyFilters();
      showSuccess("Задача успешно создана!");
    } catch (error) {
      console.error("Ошибка создания задачи:", error);
      showError(
        `Ошибка создания задачи: ${error.response?.data?.error || error.message}`
      );
    } finally {
      loading.value = false;
    }
  };

const editTask = (task) => {
  selectedTask.value = { ...task };
  showEditModal.value = true;
};

const handleUpdateTask = async (updatedTaskData) => {
  try {
    loading.value = true;
    const response = await calendarService.updateTask(
      updatedTaskData.id,
      updatedTaskData
    );

    const updatedTask = response.data || updatedTaskData;
    const index = tasks.value.findIndex((t) => t.id === updatedTaskData.id);
    if (index !== -1) {
      tasks.value[index] = updatedTask;
    }

    showEditModal.value = false;
    selectedTask.value = null;
    await loadStats();
    applyFilters();
    showSuccess("Задача успешно обновлена!");
  } catch (error) {
    console.error("Ошибка обновления задачи:", error);
    showError(
      `Ошибка обновления задачи: ${
        error.response?.data?.error || error.message
      }`
    );
  } finally {
    loading.value = false;
  }
};

const deleteTask = async (taskId) => {
  if (
    !confirm(
      "Вы уверены, что хотите удалить эту задачу? Это действие нельзя отменить."
    )
  ) {
    return;
  }

  try {
    loading.value = true;
    await calendarService.deleteTask(taskId);
    tasks.value = tasks.value.filter((task) => task.id !== taskId);
    await loadStats();
    applyFilters();
    showSuccess("Задача успешно удалена!");
  } catch (error) {
    console.error("Ошибка удаления задачи:", error);
    showError(
      `Ошибка удаления задачи: ${error.response?.data?.error || error.message}`
    );
  } finally {
    loading.value = false;
  }
};

const toggleTaskComplete = async (taskId) => {
  try {
    const updatedTask = await calendarService.toggleTaskComplete(taskId);
    const index = tasks.value.findIndex((t) => t.id === taskId);
    if (index !== -1) {
      tasks.value[index] = updatedTask;
    }
    await loadStats();
    applyFilters();
    showSuccess("Статус задачи обновлён!");
  } catch (error) {
    console.error("Ошибка обновления статуса задачи:", error);
    showError("Не удалось обновить статус задачи");
  }
};

const openTaskDetails = (task) => {
  selectedTask.value = { ...task };
  showDetailModal.value = true;
};

const editTaskFromDetail = () => {
  if (selectedTask.value) {
    showDetailModal.value = false;
    editTask(selectedTask.value);
  }
};

const closeEditModal = () => {
  showEditModal.value = false;
  selectedTask.value = null;
};

const closeDetailModal = () => {
  showDetailModal.value = false;
  selectedTask.value = null;
};

const quickCreateTask = (date) => {
  const defaultTime = new Date();
  defaultTime.setHours(9, 0, 0);

  selectedTask.value = {
    title: "",
    description: "",
    date: date,
    time: defaultTime.toTimeString().slice(0, 5),
    priority: "medium",
    task_type: "task",
    location: "",
    color: "#4CAF50",
  };

  showCreateModal.value = true;
};

const prevMonth = () => {
  currentMonth.value -= 1;
  if (currentMonth.value < 0) {
    currentMonth.value = 11;
    currentYear.value -= 1;
  }
  loadTasksForMonth();
};

const nextMonth = () => {
  currentMonth.value += 1;
  if (currentMonth.value > 11) {
    currentMonth.value = 0;
    currentYear.value += 1;
  }
  loadTasksForMonth();
};

// Вспомогательные функции
const showSuccess = (message) => {
  alert(message);
};

const showError = (message) => {
  alert(message);
};

// Наблюдатели
watch([priorityFilter, typeFilter, searchQuery], applyFilters);

// Инициализация
onMounted(async () => {

  if (!authStore.isAuthenticated) {
    showError("Вы не авторизованы. Пожалуйста, войдите в систему.");
    return;
  }

  await Promise.all([loadAllTasks(), loadStats()]);
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.transition-all {
  transition: all 0.2s ease-in-out;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>