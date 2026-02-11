<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>
    <template v-else>
      <!-- Статистика -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 rounded-lg">
              <BriefcaseIcon class="w-6 h-6 text-blue-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Всего заявок</p>
              <p class="text-2xl font-bold text-gray-900">{{ dealsData?.total_deals ?? 0 }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center">
            <div class="p-2 bg-yellow-100 rounded-lg">
              <ClockIcon class="w-6 h-6 text-yellow-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">В работе</p>
              <p class="text-2xl font-bold text-gray-900">{{ activeCount }}</p>
            </div>
          </div>
        </div>
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 rounded-lg">
              <CheckCircleIcon class="w-6 h-6 text-green-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Завершённые</p>
              <p class="text-2xl font-bold text-gray-900">{{ closedCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Недавние заявки -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200">
        <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Недавние заявки</h3>
          <router-link to="/client/deals" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
            Все заявки →
          </router-link>
        </div>
        <div class="p-6">
          <div v-if="!recentDeals.length" class="text-center py-8 text-gray-500">
            Заявок пока нет.
            <router-link to="/client/services" class="text-blue-600 hover:underline ml-1">Оставить заявку</router-link>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="deal in recentDeals"
              :key="deal.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div class="flex-1">
                <p class="font-medium text-gray-900">{{ deal.title }}</p>
                <p class="text-sm text-gray-500">{{ deal.service_name }} · {{ formatCurrency(deal.amount) }}</p>
              </div>
              <span
                class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
                :class="getStatusClass(deal.status)"
              >
                {{ deal.status_display }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Быстрое действие -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <p class="text-gray-700 mb-3">Нужна новая услуга?</p>
        <router-link
          to="/client/services"
          class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
        >
          Оставить заявку
        </router-link>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { BriefcaseIcon, ClockIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import clientService, { type ClientDealsResponse, type ClientDeal } from '../../services/clientService'

const loading = ref(true)
const error = ref('')
const dealsData = ref<ClientDealsResponse | null>(null)

const recentDeals = computed(() => (dealsData.value?.deals ?? []).slice(0, 5))
const activeCount = computed(() =>
  (dealsData.value?.deals ?? []).filter((d) => !d.is_closed && d.status !== 'on_hold').length
)
const closedCount = computed(() => (dealsData.value?.deals ?? []).filter((d) => d.is_closed).length)

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(amount)
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    new: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    won: 'bg-green-100 text-green-800',
    lost: 'bg-red-100 text-red-800',
    on_hold: 'bg-gray-100 text-gray-800'
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    dealsData.value = await clientService.getDeals()
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
