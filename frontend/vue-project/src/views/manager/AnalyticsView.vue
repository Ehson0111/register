<template>
  <div class="analytics-view">
    <!-- Заголовок -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Аналитика CRM</h1>
      <p class="text-gray-600">Статистика и аналитика по контактам, сделкам и услугам</p>
    </div>

    <!-- Фильтры -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Период</label>
          <select v-model="selectedPeriod" @change="fetchAnalytics" 
                  class="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="30">Последние 30 дней</option>
            <option value="90">Последние 90 дней</option>
            <option value="365">Последний год</option>
          </select>
        </div>
        
        <button @click="fetchAnalytics" 
                class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors mt-6">
          Обновить
        </button>
        
        <div v-if="loading" class="ml-4">
          <span class="text-blue-600">Загрузка...</span>
        </div>
      </div>
    </div>

    <!-- Общая статистика -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <div v-for="stat in overviewStats" :key="stat.title" 
           class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">{{ stat.title }}</p>
            <p class="text-2xl font-bold text-gray-900 mt-2">{{ stat.value }}</p>
          </div>
          <div :class="stat.iconBg" class="p-3 rounded-lg">
            <component :is="stat.icon" :class="stat.iconColor" class="w-6 h-6" />
          </div>
        </div>
      </div>
    </div>

    <!-- Графики и диаграммы -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Сделки по статусам -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Сделки по статусам</h2>
        <div v-if="dealsByStatus.length > 0" class="space-y-4">
          <div v-for="deal in dealsByStatus" :key="deal.status" class="flex items-center">
            <div class="w-32 text-sm font-medium text-gray-700">
              {{ getStatusText(deal.status) }}
            </div>
            <div class="flex-1 ml-4">
              <div class="flex justify-between text-sm text-gray-600 mb-1">
                <span>{{ deal.count }} сделок</span>
                <span v-if="deal.total_amount">{{ contactService.formatCurrency(deal.total_amount) }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  :style="{ width: calculatePercentage(deal.count) + '%' }" 
                  :class="getStatusColor(deal.status, true)"
                  class="h-2 rounded-full transition-all duration-500"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500 text-center py-8">
          Нет данных о сделках
        </div>
      </div>

      <!-- Контакты по статусам -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Контакты по статусам</h2>
        <div v-if="contactsByStatus.length > 0" class="space-y-4">
          <div v-for="contact in contactsByStatus" :key="contact.status" class="flex items-center">
            <div class="w-32 text-sm font-medium text-gray-700">
              {{ getStatusText(contact.status) }}
            </div>
            <div class="flex-1 ml-4">
              <div class="text-sm text-gray-600 mb-1">
                {{ contact.count }} контактов
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div 
                  :style="{ width: calculatePercentage(contact.count, true) + '%' }" 
                  :class="getStatusColor(contact.status, true)"
                  class="h-2 rounded-full transition-all duration-500"
                ></div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500 text-center py-8">
          Нет данных о контактах
        </div>
      </div>
    </div>

    <!-- Топ контакты и услуги -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Топ контакты -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Топ контакты по сделкам</h2>
        <div v-if="topContacts.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Контакт
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сделок
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сумма
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Конверсия
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="contact in topContacts" :key="contact.id">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ contact.full_name }}</div>
                  <div class="text-sm text-gray-500">{{ contact.company || 'Без компании' }}</div>
                </td>
                <td class="px-4 py-3 text-gray-900">{{ contact.deal_count }}</td>
                <td class="px-4 py-3">
                  <span class="font-medium text-green-600">
                    {{ contactService.formatCurrency(contact.total_deal_amount) }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <div class="w-full bg-gray-200 rounded-full h-2 mr-2">
                      <div :style="{ width: contact.win_rate + '%' }" 
                           class="bg-green-500 h-2 rounded-full"></div>
                    </div>
                    <span class="text-sm text-gray-600">{{ contact.win_rate }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-gray-500 text-center py-8">
          Нет данных о контактах
        </div>
      </div>

      <!-- Топ услуги -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Топ услуги по доходу</h2>
        <div v-if="topServices.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Услуга
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Цена
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сделок
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Доход
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="service in topServices" :key="service.id">
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-900">{{ service.name }}</div>
                  <div class="text-sm text-gray-500 line-clamp-1">{{ service.description }}</div>
                </td>
                <td class="px-4 py-3 text-gray-900">{{ contactService.formatCurrency(service.price) }}</td>
                <td class="px-4 py-3">{{ service.deal_count }}</td>
                <td class="px-4 py-3">
                  <span class="font-medium text-green-600">
                    {{ contactService.formatCurrency(service.total_amount) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-gray-500 text-center py-8">
          Нет данных об услугах
        </div>
      </div>
    </div>

    <!-- График трендов -->
    <div class="bg-white rounded-lg shadow p-6 mb-8" v-if="timelineData.deals_timeline?.length > 0">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Динамика сделок за месяц</h2>
      <div class="h-80">
        <!-- Простая CSS-визуализация -->
        <div class="flex items-end h-64 space-x-2">
          <div v-for="(day, index) in timelineData.deals_timeline.slice(0, 15)" :key="index" 
               class="flex-1 flex flex-col items-center">
            <div class="w-full max-w-8 bg-blue-500 rounded-t" 
                 :style="{ height: (day.count / maxDealsCount) * 200 + 'px' }"></div>
            <div class="text-xs text-gray-500 mt-2">{{ formatDateShort(day.date) }}</div>
          </div>
        </div>
        <div class="flex justify-between mt-4 text-sm text-gray-600">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-blue-500 rounded mr-2"></div>
            Новые сделки
          </div>
          <div class="flex items-center">
            <div class="w-3 h-3 bg-green-500 rounded mr-2"></div>
            Выигранные сделки
          </div>
        </div>
      </div>
    </div>

    <!-- Анализ эффективности -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- По месяцам -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Эффективность по месяцам</h2>
        <div v-if="monthlyPerformance.length > 0" class="space-y-4">
          <div v-for="month in monthlyPerformance" :key="month.month" 
               class="border-b pb-3 last:border-b-0">
            <div class="flex justify-between items-center mb-1">
              <span class="font-medium">{{ getMonthName(month.month) }}</span>
              <span class="font-medium text-green-600">
                {{ contactService.formatCurrency(month.total_amount) }}
              </span>
            </div>
            <div class="flex justify-between text-sm text-gray-600">
              <span>{{ month.total_deals }} сделок</span>
              <span>Конверсия: {{ month.conversion_rate }}%</span>
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500 text-center py-8">
          Нет данных по месяцам
        </div>
      </div>

      <!-- По вероятности -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Анализ по вероятности</h2>
        <div v-if="probabilityAnalysis.length > 0" class="space-y-4">
          <div v-for="prob in probabilityAnalysis" :key="prob.range" 
               class="border-b pb-3 last:border-b-0">
            <div class="flex justify-between items-center mb-1">
              <span class="font-medium">Вероятность {{ prob.range }}</span>
              <span class="font-medium text-blue-600">{{ prob.total_deals }} сделок</span>
            </div>
            <div class="text-sm text-gray-600">
              Выиграно: {{ prob.won_deals }} ({{ prob.conversion_rate }}%)
            </div>
          </div>
        </div>
        <div v-else class="text-gray-500 text-center py-8">
          Нет данных по вероятности
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import contactService, { type AnalyticsOverview, type AnalyticsTimeline } from '../../services/contactService'
import {
  UserGroupIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

// Состояние
const loading = ref(false)
const selectedPeriod = ref('30')

// Данные
const overviewStats = ref<any[]>([])
const topContacts = ref<any[]>([])
const topServices = ref<any[]>([])
const dealsByStatus = ref<any[]>([])
const contactsByStatus = ref<any[]>([])
const timelineData = ref<AnalyticsTimeline>({
  deals_timeline: [],
  contacts_timeline: [],
  won_deals_timeline: []
})
const monthlyPerformance = ref<any[]>([])
const probabilityAnalysis = ref<any[]>([])

// Вычисляем максимальное количество сделок для графика
const maxDealsCount = computed(() => {
  if (!timelineData.value.deals_timeline?.length) return 1
  return Math.max(...timelineData.value.deals_timeline.map(d => d.count))
})

// Загрузка аналитики
const fetchAnalytics = async () => {
  loading.value = true
  try {
    const [overview, timeline, topContactsRes, topServicesRes, performance] = await Promise.all([
      contactService.getAnalyticsOverview(),
      contactService.getAnalyticsTimeline(selectedPeriod.value),
      contactService.getTopContacts(),
      contactService.getTopServices(),
      contactService.getDealPerformance()
    ])

    // Обновляем данные
    updateOverviewStats(overview)
    dealsByStatus.value = overview.deals_by_status || []
    contactsByStatus.value = overview.contacts_by_status || []
    topContacts.value = topContactsRes.by_deal_count.map((contact: any) => ({
      ...contact,
      win_rate: contactService.calculateWinRate(contact.won_deals, contact.deal_count)
    }))
    topServices.value = topServicesRes.by_revenue
    timelineData.value = timeline
    monthlyPerformance.value = performance.monthly_performance || []
    probabilityAnalysis.value = performance.probability_analysis || []
    
  } catch (error) {
    console.error('Ошибка загрузки аналитики:', error)
  } finally {
    loading.value = false
  }
}

// Обновление общей статистики
const updateOverviewStats = (data: AnalyticsOverview) => {
  overviewStats.value = [
    {
      title: 'Всего контактов',
      value: data.overview.total_contacts,
      icon: UserGroupIcon,
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600'
    },
    {
      title: 'Всего сделок',
      value: data.overview.total_deals,
      icon: CurrencyDollarIcon,
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600'
    },
    {
      title: 'Общий доход',
      value: contactService.formatCurrency(data.overview.total_revenue),
      icon: ArrowTrendingUpIcon,
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600'
    },
    {
      title: 'Конверсия',
      value: `${data.overview.conversion_rate}%`,
      icon: CheckCircleIcon,
      iconBg: 'bg-yellow-100',
      iconColor: 'text-yellow-600'
    }
  ]
}

// Вспомогательные функции
const formatDateShort = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short'
  })
}

const getMonthName = (month: number) => {
  const months = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ]
  return months[month - 1] || ''
}

const calculatePercentage = (count: number, isContacts: boolean = false) => {
  const total = isContacts 
    ? contactsByStatus.value.reduce((sum, item) => sum + item.count, 0)
    : dealsByStatus.value.reduce((sum, item) => sum + item.count, 0)
  return total > 0 ? Math.round((count / total) * 100) : 0
}

const getStatusText = (status: string) => {
  return contactService.getStatusText(status)
}

const getStatusColor = (status: string, isBg: boolean = false) => {
  const colors: Record<string, string> = {
    'new': isBg ? 'bg-blue-500' : 'text-blue-600',
    'in_progress': isBg ? 'bg-yellow-500' : 'text-yellow-600',
    'won': isBg ? 'bg-green-500' : 'text-green-600',
    'lost': isBg ? 'bg-red-500' : 'text-red-600',
    'on_hold': isBg ? 'bg-gray-500' : 'text-gray-600',
    'lead': isBg ? 'bg-purple-500' : 'text-purple-600',
    'client': isBg ? 'bg-green-500' : 'text-green-600',
    'partner': isBg ? 'bg-orange-500' : 'text-orange-600'
  }
  return colors[status] || (isBg ? 'bg-gray-500' : 'text-gray-600')
}

// Инициализация
onMounted(() => {
  fetchAnalytics()
})
</script>

<style scoped>
.analytics-view {
  max-width: 1400px;
  margin: 0 auto;
}
</style>