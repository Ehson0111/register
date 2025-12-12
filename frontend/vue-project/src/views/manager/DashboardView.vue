<!-- frontend/src/views/manager/DashboardView.vue -->
<template>
  <div class="space-y-6">
    <!-- Статистика -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <UsersIcon class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Всего контактов</p>
            <p class="text-2xl font-bold text-gray-900"> {{ stats.totalContacts }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <BriefcaseIcon class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Активные сделки</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.activeDeals }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <CurrencyDollarIcon class="w-6 h-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Общий оборот</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(stats.totalRevenue) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div class="flex items-center">
          <div class="p-2 bg-orange-100 rounded-lg">
            <ChartBarIcon class="w-6 h-6 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Успешность</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.successRate }}%</p>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Недавние сделки -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Недавние сделки</h3>
        </div>
        <div class="p-6">
          <div v-if="recentDeals.length === 0" class="text-center py-8">
            <BriefcaseIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">Нет активных сделок</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="deal in recentDeals"
              :key="deal.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="flex-1">
                <p class="font-medium text-gray-900">{{ deal.title }}</p>
                <p class="text-sm text-gray-500">{{ deal.contact_name }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold text-gray-900">{{ formatCurrency(parseFloat(deal.amount)) }}</p>
                <span
                  class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="getStatusColor(deal.status_color)"
                >
                  {{ deal.status_display }}
                </span>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <router-link
              to="/manager/deals"
              class="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              Все сделки →
            </router-link>
          </div>
        </div>
      </div>

      <!-- Последние контакты -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">Последние контакты</h3>
        </div>
        <div class="p-6">
          <div v-if="recentContacts.length === 0" class="text-center py-8">
            <UsersIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">Нет контактов</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="contact in recentContacts"
              :key="contact.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span class="text-blue-600 font-medium text-sm">
                    {{ getInitials(contact.first_name, contact.last_name) }}
                  </span>
                </div>
                <div>
                  <p class="font-medium text-gray-900">
                    {{ contact.first_name }} {{ contact.last_name }}
                  </p>
                  <p class="text-sm text-gray-500">{{ contact.company }}</p>
                </div>
              </div>
              <span
                class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                :class="getContactStatusColor(contact.status)"
              >
                {{ contact.status_display }}
              </span>
            </div>
          </div>
          <div class="mt-4">
            <router-link
              to="/manager/contacts"
              class="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              Все контакты →
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  UsersIcon,
  BriefcaseIcon,
  CurrencyDollarIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'
import contactService, { type Contact } from '../../services/contactService'
import dealService, { type Deal } from '../../services/dealService'

const stats = ref({
  totalContacts: 0,
  activeDeals: 0,
  totalRevenue: 0,
  successRate: 0
})

const recentDeals = ref<Deal[]>([])
const recentContacts = ref<Contact[]>([])

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

const getStatusColor = (color: string) => {
  const colors: Record<string, string> = {
    green: 'bg-green-100 text-green-800',
    orange: 'bg-orange-100 text-orange-800',
    blue: 'bg-blue-100 text-blue-800',
    red: 'bg-red-100 text-red-800',
    gray: 'bg-gray-100 text-gray-800'
  }
  return colors[color] || colors.gray
}

const getContactStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    lead: 'bg-yellow-100 text-yellow-800',
    client: 'bg-green-100 text-green-800',
    partner: 'bg-blue-100 text-blue-800'
  }
  return colors[status] || colors.lead
}

const getInitials = (firstName: string, lastName: string) => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

const loadDashboardData = async () => {
  try {
    // Загружаем контакты
    const contacts = await contactService.getContacts()
    
    stats.value.totalContacts = 2
    recentContacts.value = contacts.slice(0, 5)
    console.log("контакты"+JSON.stringify( contacts,null,2))
    console.log("контакты"+contacts.length)

    // Загружаем сделки
    const deals = await dealService.getDeals()
    const activeDeals = deals.filter(deal => !deal.is_closed)
    const wonDeals = deals.filter(deal => deal.status === 'won')
    
    stats.value.activeDeals = activeDeals.length
    stats.value.totalRevenue = wonDeals.reduce((sum, deal) => sum + parseFloat(deal.amount), 0)
    stats.value.successRate = deals.length > 0 ? Math.round((wonDeals.length / deals.length) * 100) : 0
    
    recentDeals.value = deals.slice(0, 5)
  } catch (error) {
    console.error('Ошибка загрузки дашборда:', error)
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>