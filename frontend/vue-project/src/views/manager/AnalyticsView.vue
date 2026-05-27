<!--
  [VIEW] AnalyticsView — графики и аналитика (Chart.js / vue-chartjs)
  Маршрут: /manager/analytics
-->
<template>
  <div class="analytics-view">
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Аналитика CRM</h1>
      <p class="text-gray-600">Статистика и аналитика по контактам, сделкам и услугам</p>
    </div>

    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex flex-wrap items-center gap-4">
        <button
          @click="fetchAnalytics"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Обновить
        </button>
        <div v-if="loading">
          <span class="text-blue-600">Загрузка...</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      <div v-for="stat in overviewStats" :key="stat.title" class="bg-white rounded-lg shadow p-6">
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

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
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
        <div v-else class="text-gray-500 text-center py-8">Нет данных о сделках</div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Контакты по статусам</h2>
        <div v-if="contactsByStatus.length > 0" class="space-y-4">
          <div v-for="contact in contactsByStatus" :key="contact.status" class="flex items-center">
            <div class="w-32 text-sm font-medium text-gray-700">
              {{ getStatusText(contact.status) }}
            </div>
            <div class="flex-1 ml-4">
              <div class="text-sm text-gray-600 mb-1">{{ contact.count }} контактов</div>
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
        <div v-else class="text-gray-500 text-center py-8">Нет данных о контактах</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Топ контакты по сделкам</h2>
        <div v-if="topContacts.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Контакт</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сделок</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сумма</th>
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
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-gray-500 text-center py-8">Нет данных о контактах</div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Топ услуги по доходу</h2>
        <div v-if="topServices.length > 0" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Услуга</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Цена</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Сделок</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Доход</th>
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
        <div v-else class="text-gray-500 text-center py-8">Нет данных об услугах</div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Эффективность по месяцам</h2>
      <div v-if="monthlyPerformance.length > 0" class="space-y-4">
        <div v-for="month in monthlyPerformance" :key="month.month" class="border-b pb-3 last:border-b-0">
          <div class="flex justify-between items-center mb-1">
            <span class="font-medium">{{ getMonthName(month.month) }}</span>
            <span class="font-medium text-green-600">
              {{ contactService.formatCurrency(month.total_amount) }}
            </span>
          </div>
          <div class="text-sm text-gray-600">{{ month.total_deals }} сделок</div>
        </div>
      </div>
      <div v-else class="text-gray-500 text-center py-8">Нет данных по месяцам</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import contactService, { type AnalyticsOverview } from '../../services/contactService'
import { getDealStatusLabel } from '../../constants/dealStatuses'
import {
  UserGroupIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/vue/24/outline'

const loading = ref(false)

const overviewStats = ref<any[]>([])
const topContacts = ref<any[]>([])
const topServices = ref<any[]>([])
const dealsByStatus = ref<any[]>([])
const contactsByStatus = ref<any[]>([])
const monthlyPerformance = ref<any[]>([])

const fetchAnalytics = async () => {
  loading.value = true
  try {
    const [overview, topContactsRes, topServicesRes, performance] = await Promise.all([
      contactService.getAnalyticsOverview(),
      contactService.getTopContacts(),
      contactService.getTopServices(),
      contactService.getDealPerformance(),
    ])

    updateOverviewStats(overview)
    dealsByStatus.value = overview.deals_by_status || []
    contactsByStatus.value = overview.contacts_by_status || []
    topContacts.value = topContactsRes.by_deal_count
    topServices.value = topServicesRes.by_revenue
    monthlyPerformance.value = performance.monthly_performance || []
  } catch (error) {
    console.error('Ошибка загрузки аналитики:', error)
  } finally {
    loading.value = false
  }
}

const updateOverviewStats = (data: AnalyticsOverview) => {
  overviewStats.value = [
    {
      title: 'Всего контактов',
      value: data.overview.total_contacts,
      icon: UserGroupIcon,
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
    },
    {
      title: 'Всего сделок',
      value: data.overview.total_deals,
      icon: CurrencyDollarIcon,
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
    },
    {
      title: 'Общий доход',
      value: contactService.formatCurrency(data.overview.total_revenue),
      icon: ArrowTrendingUpIcon,
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
    },
  ]
}

const getMonthName = (month: number) => {
  const months = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
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
  const dealLabel = getDealStatusLabel(status)
  if (dealLabel !== status) return dealLabel
  return contactService.getStatusText(status)
}

const getStatusColor = (status: string, isBg: boolean = false) => {
  const colors: Record<string, string> = {
    new: isBg ? 'bg-blue-500' : 'text-blue-600',
    in_progress: isBg ? 'bg-yellow-500' : 'text-yellow-600',
    won: isBg ? 'bg-green-500' : 'text-green-600',
    lost: isBg ? 'bg-red-500' : 'text-red-600',
    on_hold: isBg ? 'bg-gray-500' : 'text-gray-600',
    lead: isBg ? 'bg-purple-500' : 'text-purple-600',
    client: isBg ? 'bg-green-500' : 'text-green-600',
    partner: isBg ? 'bg-orange-500' : 'text-orange-600',
  }
  return colors[status] || (isBg ? 'bg-gray-500' : 'text-gray-600')
}

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
