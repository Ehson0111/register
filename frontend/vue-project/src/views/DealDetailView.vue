<!-- frontend/src/views/manager/DealDetailView.vue -->
<template>
  <div class="space-y-6" v-if="deal">
    <!-- Заголовок -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ deal.title }}</h1>
        <p class="text-gray-600 mt-1">{{ deal.description }}</p>
      </div>
      <div class="flex space-x-3">
        <button 
          @click="$router.back()"
          class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          ← Назад
        </button>
        <button 
          v-if="!deal.is_closed"
          @click="changeDealStatus('won')"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Выиграть
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Основная информация -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Карточка информации -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Информация о сделке</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-500">Контакт</label>
              <p class="text-gray-900">{{ deal.contact_name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Услуга</label>
              <p class="text-gray-900">{{ deal.service_name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Сумма</label>
              <p class="text-xl font-bold text-gray-900">{{ formatCurrency(parseFloat(deal.amount)) }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Вероятность</label>
              <div class="flex items-center">
                <div class="w-full bg-gray-200 rounded-full h-2 mr-2">
                  <div 
                    class="h-2 rounded-full"
                    :class="getProbabilityColor(deal.probability)"
                    :style="{ width: `${deal.probability}%` }"
                  ></div>
                </div>
                <span class="text-sm text-gray-600">{{ deal.probability }}%</span>
              </div>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Статус</label>
              <span 
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusClass(deal.status)"
              >
                {{ deal.status_display }}
              </span>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Дней в работе</label>
              <p class="text-gray-900">{{ deal.days_open }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Ожидаемая дата закрытия</label>
              <p class="text-gray-900">{{ deal.expected_close_date ? formatDate(deal.expected_close_date) : 'Не указана' }}</p>
            </div>
            <div v-if="deal.actual_close_date">
              <label class="text-sm font-medium text-gray-500">Фактическая дата закрытия</label>
              <p class="text-gray-900">{{ formatDate(deal.actual_close_date) }}</p>
            </div>
          </div>
        </div>

        <!-- Описание -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Описание</h2>
          <p class="text-gray-700" v-if="deal.description">{{ deal.description }}</p>
          <p class="text-gray-500" v-else>Описание отсутствует</p>
        </div>
      </div>

      <!-- Боковая панель -->
      <div class="space-y-6">
        <!-- Статистика -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Детали</h3>
          <div class="space-y-3">
            <div>
              <p class="text-sm text-gray-500">Дата создания</p>
              <p class="text-gray-900">{{ formatDate(deal.created_at) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Последнее обновление</p>
              <p class="text-gray-900">{{ formatDate(deal.updated_at) }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Статус сделки</p>
              <p class="text-gray-900">{{ deal.is_closed ? 'Закрыта' : 'Открыта' }}</p>
            </div>
          </div>
        </div>

        <!-- Быстрые действия -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Действия</h3>
          <div class="space-y-2">
            <button 
              v-if="!deal.is_closed"
              @click="changeDealStatus('won')"
              class="w-full text-left px-3 py-2 text-sm text-green-600 hover:bg-green-50 rounded flex items-center"
            >
              <CheckIcon class="w-4 h-4 mr-2" />
              Выиграть сделку
            </button>
            <button 
              v-if="!deal.is_closed"
              @click="changeDealStatus('lost')"
              class="w-full text-left px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded flex items-center"
            >
              <XMarkIcon class="w-4 h-4 mr-2" />
              Проиграть сделку
            </button>
            <button class="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded flex items-center">
              <PencilIcon class="w-4 h-4 mr-2" />
              Редактировать
            </button>
            <button class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded flex items-center">
              <DocumentTextIcon class="w-4 h-4 mr-2" />
              Создать предложение
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="text-center py-8">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
    <p class="text-gray-500 mt-2">Загрузка сделки...</p>
  </div>

  <div v-else class="text-center py-8">
    <p class="text-gray-500">Сделка не найдена</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from '../../src/composables/useToast'
import dealService, { type Deal } from '../services/dealService'
import {
  CheckIcon,
  XMarkIcon,
  PencilIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const { showSuccess, showError } = useToast()

const deal = ref<Deal | null>(null)
const loading = ref(true)

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    new: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-orange-100 text-orange-800',
    won: 'bg-green-100 text-green-800',
    lost: 'bg-red-100 text-red-800',
    on_hold: 'bg-gray-100 text-gray-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 80) return 'bg-green-500'
  if (probability >= 50) return 'bg-yellow-500'
  return 'bg-red-500'
}

const changeDealStatus = async (status: string) => {
  if (!deal.value) return

  const statusNames: Record<string, string> = {
    won: 'выиграна',
    lost: 'проиграна'
  }

  if (!confirm(`Отметить сделку "${deal.value.title}" как ${statusNames[status]}?`)) {
    return
  }

  try {
    await dealService.changeDealStatus(deal.value.id, status)
    showSuccess(`Сделка отмечена как ${statusNames[status]}`)
    // Перезагружаем данные сделки
    loadDeal()
  } catch (error) {
    console.error('Ошибка изменения статуса:', error)
    showError('Не удалось изменить статус сделки')
  }
}

const loadDeal = async () => {
  try {
    const dealId = parseInt(route.params.id as string)
    deal.value = await dealService.getDeal(dealId)
  } catch (error) {
    console.error('Ошибка загрузки сделки:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDeal()
})
</script>