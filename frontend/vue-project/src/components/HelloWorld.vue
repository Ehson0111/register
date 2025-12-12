<!-- views/DashboardView.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
// import StatsOverview from '@/components/dashboard/StatsOverview.vue'
// import QuickActions from '@/components/dashboard/QuickActions.vue'
// import RecentActivity from '@/components/dashboard/RecentActivity.vue'
// import UpcomingTasks from '@/components/dashboard/UpcomingTasks.vue'

// Данные для статистики
const stats = ref([
  { title: 'Новые лиды', value: 12, change: '+2', icon: '👥', trend: 'up' },
  { title: 'Открытые сделки', value: 8, change: '+1', icon: '💰', trend: 'up' },
  { title: 'Задачи на сегодня', value: 5, change: '-3', icon: '✅', trend: 'down' },
  { title: 'Конверсия', value: '24%', change: '+3%', icon: '📈', trend: 'up' },
])

// Недавняя активность
const recentActivities = ref([
  { 
    id: 1, 
    type: 'lead', 
    message: 'Новый лид от Ивана Петрова', 
    time: '5 мин назад',
    user: 'Менеджер Алексей'
  },
  { 
    id: 2, 
    type: 'deal', 
    message: 'Сделка "Поставка офисной мебели" перешла на новый этап', 
    time: '1 час назад',
    user: 'Менеджер Мария'
  },
  { 
    id: 3, 
    type: 'task', 
    message: 'Задача "Позвонить клиенту" выполнена', 
    time: '2 часа назад',
    user: 'Вы'
  },
  { 
    id: 4, 
    type: 'meeting', 
    message: 'Встреча с ООО "ТехноПрофи" запланирована', 
    time: '3 часа назад',
    user: 'Менеджер Сергей'
  },
])

// Предстоящие задачи
const upcomingTasks = ref([
  { id: 1, title: 'Подготовить коммерческое предложение', time: '10:00', priority: 'high' },
  { id: 2, title: 'Звонок клиенту по сделке #245', time: '14:30', priority: 'medium' },
  { id: 3, title: 'Отправить договор на подпись', time: '16:00', priority: 'low' },
])

// Получение приветствия по времени суток
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Доброе утро'
  if (hour < 18) return 'Добрый день'
  return 'Добрый вечер'
}

const greeting = ref(getGreeting())

onMounted(() => {
  // Здесь будет загрузка данных с бэкенда
  console.log('Dashboard mounted')
})
</script>

<template>
  <main class="dashboard">
    <!-- Заголовок страницы -->
    <div class="dashboard__header">
      <div class="header-content">
        <h1 class="header-title">{{ greeting }}, команда! 👋</h1>
        <p class="header-subtitle">Обзор вашей деятельности за сегодня</p>
      </div>
      <div class="header-date">
        {{ new Date().toLocaleDateString('ru-RU', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        }) }}
      </div>
    </div>

    <!-- Основной контент -->
    <div class="dashboard__content">
      <!-- Блок статистики -->
      <section class="dashboard-section">
        <h2 class="section-title">Общая статистика</h2>
        <StatsOverview :stats="stats" />
      </section>

      <!-- Быстрые действия -->
      <section class="dashboard-section">
        <h2 class="section-title">Быстрые действия</h2>
        <QuickActions />
      </section>

      <!-- Двухколоночный layout -->
      <div class="dashboard__grid">
        <!-- Левая колонка: Активность -->
        <section class="dashboard-section">
          <h2 class="section-title">Недавняя активность</h2>
          <RecentActivity :activities="recentActivities" />
        </section>

        <!-- Правая колонка: Задачи -->
        <section class="dashboard-section">
          <div class="section-header">
            <h2 class="section-title">Предстоящие задачи</h2>
            <button class="add-task-btn">
              <span>+</span>
              Добавить
            </button>
          </div>
          <UpcomingTasks :tasks="upcomingTasks" />
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background: #f8fafc;
}

/* Заголовок */
.dashboard__header {
  display: flex;
  justify-content: between;
  align-items: flex-start;
  margin-bottom: 2rem;
  gap: 2rem;
}

.header-content {
  flex: 1;
}

.header-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.header-subtitle {
  color: #718096;
  font-size: 1.1rem;
  margin: 0;
}

.header-date {
  color: #a0aec0;
  font-size: 0.9rem;
  text-align: right;
  white-space: nowrap;
  padding-top: 0.25rem;
}

/* Основной контент */
.dashboard__content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-section {
  background: transparent;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
}

/* Двухколоночный layout */
.dashboard__grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: start;
}

.section-header {
  display: flex;
  justify-content: between;
  align-items: center;
  margin-bottom: 1rem;
}

.add-task-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.add-task-btn:hover {
  background: #3182ce;
}

.add-task-btn span {
  font-size: 1.2rem;
  font-weight: 300;
}

/* Адаптивность */
@media (max-width: 1024px) {
  .dashboard__grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .dashboard__header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-date {
    text-align: center;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .header-title {
    font-size: 1.5rem;
  }
  
  .dashboard__content {
    gap: 1.5rem;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 0.75rem;
  }
  
  .header-title {
    font-size: 1.25rem;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .add-task-btn {
    justify-content: center;
  }
}
</style>