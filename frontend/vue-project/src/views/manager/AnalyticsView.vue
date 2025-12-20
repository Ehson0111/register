<!-- frontend/src/views/manager/AnalyticsView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Аналитика и отчеты</h2>
      <div class="flex space-x-3">
        <select 
          v-model="selectedPeriod"
          class="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="week">За неделю</option>
          <option value="month">За месяц</option>
          <option value="quarter">За квартал</option>
          <option value="year">За год</option>
        </select>
        
        <button class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Экспорт отчета
        </button>
      </div>
    </div>

    <!-- Динамика продаж -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Динамика продаж</h3>
      <div class="h-80">
        <div class="flex items-end justify-between h-64 px-4 border-b border-l border-gray-200">
          <div 
            v-for="(item, index) in salesData"
            :key="index"
            class="flex flex-col items-center flex-1 mx-1"
          >
            <div 
              class="w-full bg-gradient-to-t from-blue-500 to-blue-600 rounded-t hover:from-blue-600 hover:to-blue-700 transition-all duration-300 cursor-pointer relative group"
              :style="{ height: (item.value / maxSalesValue) * 100 + '%', minHeight: '20px' }"
            >
              <div class="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                {{ item.value }} тыс. руб.
              </div>
            </div>
            <span class="text-xs text-gray-600 mt-2">{{ item.label }}</span>
          </div>
        </div>
        
        <!-- Линия сетки и значения -->
        <div class="flex justify-between text-xs text-gray-500 mt-2 px-4">
          <span>0</span>
          <span>{{ Math.round(maxSalesValue * 0.25) }}</span>
          <span>{{ Math.round(maxSalesValue * 0.5) }}</span>
          <span>{{ Math.round(maxSalesValue * 0.75) }}</span>
          <span>{{ maxSalesValue }}</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Статусы сделок -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Статусы сделок</h3>
        <div class="flex items-center justify-center">
          <div class="relative w-64 h-64">
            <!-- Внешний круг для прогресса -->
            <svg class="w-full h-full transform -rotate-90">
              <circle 
                v-for="(item, index) in dealsByStatus"
                :key="item.status"
                :cx="32"
                :cy="32"
                :r="30"
                fill="transparent"
                :stroke="item.color"
                :stroke-width="6"
                :stroke-dasharray="circumference"
                :stroke-dashoffset="getStrokeDashoffset(index)"
                class="transition-all duration-1000 ease-out"
              />
            </svg>
            
            <!-- Центральный текст -->
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <div class="text-2xl font-bold text-gray-900">{{ totalDeals }}</div>
              <div class="text-sm text-gray-600">Всего сделок</div>
            </div>
          </div>
        </div>
        
        <!-- Легенда -->
        <div class="mt-6 space-y-3">
          <div 
            v-for="item in dealsByStatus"
            :key="item.status"
            class="flex items-center justify-between"
          >
            <div class="flex items-center space-x-3">
              <div class="w-4 h-4 rounded-full" :style="{ backgroundColor: item.color }"></div>
              <span class="text-sm text-gray-700">{{ item.status }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-sm font-medium text-gray-900">{{ item.count }}</span>
              <span class="text-sm text-gray-500">({{ item.percentage }}%)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Эффективность менеджеров -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-6">Эффективность менеджеров</h3>
        <div class="space-y-6">
          <div 
            v-for="manager in managerPerformance"
            :key="manager.name"
            class="space-y-2"
          >
            <div class="flex justify-between items-center">
              <span class="text-sm font-medium text-gray-900">{{ manager.name }}</span>
              <span class="text-sm text-gray-600">{{ manager.deals }} сделок</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-3">
              <div 
                class="bg-gradient-to-r from-green-400 to-green-600 h-3 rounded-full transition-all duration-1000 ease-out"
                :style="{ width: manager.successRate + '%' }"
              ></div>
            </div>
            <div class="flex justify-between text-xs text-gray-500">
              <span>Успешность:</span>
              <span class="font-medium text-green-600">{{ manager.successRate }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ключевые метрики -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Ключевые метрики</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div class="text-center p-6 bg-blue-50 rounded-xl border border-blue-200">
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ metrics.conversionRate }}%</div>
          <div class="text-sm font-medium text-blue-900">Конверсия</div>
          <div class="text-xs text-blue-600 mt-1">+2.3% за месяц</div>
        </div>
        
        <div class="text-center p-6 bg-green-50 rounded-xl border border-green-200">
          <div class="text-3xl font-bold text-green-600 mb-2">{{ metrics.avgDealSize }}</div>
          <div class="text-sm font-medium text-green-900">Средний чек</div>
          <div class="text-xs text-green-600 mt-1">тыс. руб.</div>
        </div>
        
        <div class="text-center p-6 bg-purple-50 rounded-xl border border-purple-200">
          <div class="text-3xl font-bold text-purple-600 mb-2">{{ metrics.salesCycle }}</div>
          <div class="text-sm font-medium text-purple-900">Цикл продаж</div>
          <div class="text-xs text-purple-600 mt-1">дней</div>
        </div>
        
        <div class="text-center p-6 bg-orange-50 rounded-xl border border-orange-200">
          <div class="text-3xl font-bold text-orange-600 mb-2">{{ metrics.customerSatisfaction }}%</div>
          <div class="text-sm font-medium text-orange-900">Удовлетворенность</div>
          <div class="text-xs text-orange-600 mt-1">клиентов</div>
        </div>
      </div>
    </div>

    <!-- Воронка продаж -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Воронка продаж</h3>
      <div class="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
        <div 
          v-for="(stage, index) in salesFunnel"
          :key="stage.name"
          class="flex flex-col items-center text-center flex-1"
        >
          <div class="w-16 h-16 rounded-full flex items-center justify-center text-white font-bold mb-2"
               :class="getFunnelStageColor(index)">
            {{ stage.count }}
          </div>
          <div class="text-sm font-medium text-gray-900 mb-1">{{ stage.name }}</div>
          <div class="text-xs text-gray-500">{{ stage.percentage }}%</div>
          <div class="text-xs text-gray-400 mt-1">{{ stage.value }} тыс. руб.</div>
          
          <!-- Стрелка между этапами -->
          <div v-if="index < salesFunnel.length - 1" 
               class="hidden md:block absolute transform translate-x-16">
            <svg class="w-8 h-8 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const selectedPeriod = ref('month')

const salesData = ref([
  { label: 'Янв', value: 120 },
  { label: 'Фев', value: 150 },
  { label: 'Мар', value: 180 },
  { label: 'Апр', value: 200 },
  { label: 'Май', value: 240 },
  { label: 'Июн', value: 220 },
  { label: 'Июл', value: 260 },
  { label: 'Авг', value: 280 },
  { label: 'Сен', value: 300 },
  { label: 'Окт', value: 320 },
  { label: 'Ноя', value: 310 },
  { label: 'Дек', value: 350 }
])

const dealsByStatus = ref([
  { status: 'Новые', count: 12, color: '#3B82F6', percentage: 25 },
  { status: 'В работе', count: 8, color: '#F59E0B', percentage: 17 },
  { status: 'Успешные', count: 25, color: '#10B981', percentage: 52 },
  { status: 'Отмененные', count: 3, color: '#EF4444', percentage: 6 }
])

const managerPerformance = ref([
  { name: 'Иван Петров', deals: 23, successRate: 78 },
  { name: 'Мария Сидорова', deals: 19, successRate: 85 },
  { name: 'Алексей Козлов', deals: 15, successRate: 65 },
  { name: 'Елена Новикова', deals: 21, successRate: 72 }
])

const metrics = ref({
  conversionRate: 23,
  avgDealSize: 45,
  salesCycle: 14,
  customerSatisfaction: 94
})

const salesFunnel = ref([
  { name: 'Лиды', count: 1000, percentage: 100, value: 0 },
  { name: 'Квалификация', count: 600, percentage: 60, value: 0 },
  { name: 'Предложение', count: 300, percentage: 30, value: 13500 },
  { name: 'Переговоры', count: 150, percentage: 15, value: 6750 },
  { name: 'Закрытые', count: 90, percentage: 9, value: 4050 }
])

// Вычисляемые свойства
const maxSalesValue = computed(() => {
  return Math.max(...salesData.value.map(item => item.value))
})

const totalDeals = computed(() => {
  return dealsByStatus.value.reduce((sum, item) => sum + item.count, 0)
})

const circumference = computed(() => {
  return 2 * Math.PI * 30 // 2 * π * radius
})

const getStrokeDashoffset = (index: number) => {
  const previousPercentage = dealsByStatus.value
    .slice(0, index)
    .reduce((sum, item) => sum + item.percentage, 0)
  
  return circumference.value * (1 - previousPercentage / 100)
}

const getFunnelStageColor = (index: number) => {
  const colors = [
    'bg-blue-500',
    'bg-blue-400',
    'bg-green-500',
    'bg-green-400',
    'bg-green-600'
  ]
  return colors[index] || 'bg-gray-500'
}
</script>

<style scoped>
/* Анимация для графиков */
.bg-gradient-to-r {
  background-size: 200% 100%;
  background-position: 100% 0;
}

.bg-gradient-to-r {
  animation: fillAnimation 2s ease-out forwards;
}

@keyframes fillAnimation {
  from {
    background-position: 100% 0;
  }
  to {
    background-position: 0 0;
  }
}
</style>