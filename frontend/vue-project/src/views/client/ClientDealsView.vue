<!--
   ClientDealsView — список заявок клиента с фильтром по статусу
  Маршрут: /client/deals | API: clientService.getDeals(status?)
-->
<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <p class="text-gray-600">Всего заявок: {{ dealsData?.total_deals ?? 0 }}</p>
      <select
        v-model="dealStatusFilter"
        @change="loadDeals()"
        class="border border-gray-300 rounded-lg px-3 py-2 text-sm"
      >
        <option value="">Все статусы</option>
        <option value="new">Новая</option>
        <option value="in_progress">В работе</option>
        <option value="won">Выиграна</option>
        <option value="lost">Проиграна</option>
        <option value="on_hold">На паузе</option>
      </select>
    </div>
    <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">{{ error }}</div>
    <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div v-if="!dealsData?.deals?.length" class="text-center py-12 text-gray-500">
        Заявок нет. <router-link to="/client/services" class="text-blue-600">Оставить заявку</router-link>
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="deal in dealsData.deals"
          :key="deal.id"
          class="flex flex-wrap items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
        >
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900">{{ deal.title }}</p>
            <p class="text-sm text-gray-500">{{ deal.service_name }} · {{ formatCurrency(deal.amount) }}</p>
          </div>
          <span class="inline-flex px-2.5 py-1 rounded-full text-xs font-medium" :class="getStatusClass(deal.status)">
            {{ deal.status_display }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import clientService, { type ClientDealsResponse } from '../../services/clientService'

const loading = ref(true)
const error = ref('')
const dealsData = ref<ClientDealsResponse | null>(null)
const dealStatusFilter = ref('')

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

async function loadDeals() {
  loading.value = true
  error.value = ''
  try {
    dealsData.value = await clientService.getDeals(dealStatusFilter.value || undefined)
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить заявки'
  } finally {
    loading.value = false
  }
}

onMounted(loadDeals)
</script>
