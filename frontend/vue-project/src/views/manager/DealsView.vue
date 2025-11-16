<!-- frontend/src/views/manager/DealsView.vue -->
<template>
  <div class="space-y-6">
    <!-- Заголовок и кнопки -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Сделки</h1>
        <p class="text-gray-600 mt-1">Управление коммерческими предложениями</p>
      </div>
      <button 
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
      >
        <PlusIcon class="w-5 h-5" />
        <span>Новая сделка</span>
      </button>
    </div>

    <!-- Фильтры и поиск -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Поиск -->
        <div class="flex-1">
          <div class="relative">
            <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск по названию сделки или контакту..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="handleSearch"
            />
          </div>
        </div>
        
        <!-- Фильтр по статусу -->
        <select
          v-model="statusFilter"
          @change="loadDeals"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Все статусы</option>
          <option value="new">New</option>
          <option value="in_progress">In Progress</option>
          <option value="won">Won</option>
          <option value="lost">Lost</option>
          <option value="on_hold">On Hold</option>
        </select>

        <!-- Фильтр по услуге -->
        <select
          v-model="serviceFilter"
          @change="loadDeals"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Все услуги</option>
          <option v-for="service in services" :key="service.id" :value="service.id">
            {{ service.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Статистика сделок -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div 
        v-for="status in dealStatuses" 
        :key="status.value"
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 cursor-pointer hover:shadow-md transition-shadow"
        :class="{ 'ring-2 ring-blue-500': statusFilter === status.value }"
        @click="toggleStatusFilter(status.value)"
      >
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-600">{{ status.label }}</span>
          <span class="text-lg font-bold" :class="status.color">
            {{ getStatusCount(status.value) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Таблица сделок -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <!-- Заголовок таблицы -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Все сделки ({{ deals.length }})
          </h3>
          <div class="flex items-center space-x-4">
            <button
              @click="loadDeals"
              class="text-gray-500 hover:text-gray-700 transition-colors"
              :disabled="loading"
            >
              <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': loading }" />
            </button>
          </div>
        </div>
      </div>

      <!-- Состояние загрузки -->
      <div v-if="loading" class="p-8 text-center">
        <div class="flex justify-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <p class="text-gray-500 mt-2">Загрузка сделок...</p>
      </div>

      <!-- Состояние пустого списка -->
      <div v-else-if="deals.length === 0" class="p-8 text-center">
        <BriefcaseIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Сделки не найдены</h3>
        <p class="text-gray-500 mb-4">Начните с создания первой сделки</p>
        <button
          @click="showCreateModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Новая сделка
        </button>
      </div>

      <!-- Таблица -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Сделка
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Контакт
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Услуга
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Сумма
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Вероятность
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Дата закрытия
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="deal in deals" 
              :key="deal.id"
              class="hover:bg-gray-50 transition-colors cursor-pointer"
              @click="$router.push(`/manager/deals/${deal.id}`)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <BriefcaseIcon class="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ deal.title }}
                    </div>
                    <div class="text-sm text-gray-500">
                      {{ formatDate(deal.created_at) }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ deal.contact_name }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ deal.service_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ formatCurrency(parseFloat(deal.amount)) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-full bg-gray-200 rounded-full h-2 mr-2">
                    <div 
                      class="h-2 rounded-full transition-all"
                      :class="getProbabilityColor(deal.probability)"
                      :style="{ width: `${deal.probability}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-gray-600">{{ deal.probability }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusClass(deal.status)"
                >
                  {{ deal.status_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ deal.expected_close_date ? formatDate(deal.expected_close_date) : '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button
                    v-if="!deal.is_closed"
                    @click.stop="changeDealStatus(deal, 'won')"
                    class="text-green-600 hover:text-green-900 transition-colors"
                    title="Выиграть сделку"
                  >
                    <CheckIcon class="w-4 h-4" />
                  </button>
                  <button
                    v-if="!deal.is_closed"
                    @click.stop="changeDealStatus(deal, 'lost')"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Проиграть сделку"
                  >
                    <XMarkIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click.stop="editDeal(deal)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Редактировать"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click.stop="deleteDeal(deal)"
                    class="text-red-600 hover:text-red-900 transition-colors"
                    title="Удалить"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модальное окно создания/редактирования -->
    <DealFormModal
      :show="showCreateModal"
      :deal="editingDeal"
      @close="closeModal"
      @saved="handleDealSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '../../composables/useToast'
import dealService, { type Deal } from '../../services/dealService'
import serviceService, { type Service } from '../../services/serviceService'
// import DealFormModal from 'components/DealFormModal.vue'
import DealFormModal from './components/DealFormModal.vue'

import {
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  BriefcaseIcon,
  PencilIcon,
  TrashIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const { showSuccess, showError } = useToast()

// Состояние
const deals = ref<Deal[]>([])
const services = ref<Service[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const serviceFilter = ref('')
const showCreateModal = ref(false)
const editingDeal = ref<Deal | null>(null)

// Статусы сделок
const dealStatuses = [
  { value: 'new', label: 'Новые', color: 'text-blue-600' },
  { value: 'in_progress', label: 'В работе', color: 'text-orange-600' },
  { value: 'won', label: 'Выиграны', color: 'text-green-600' },
  { value: 'lost', label: 'Проиграны', color: 'text-red-600' },
  { value: 'on_hold', label: 'На паузе', color: 'text-gray-600' }
]

// Загрузка данных
const loadDeals = async () => {
  try {
    loading.value = true
    const params: any = {}
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    if (serviceFilter.value) {
      params.service = serviceFilter.value
    }

    deals.value = await dealService.getDeals(params)
  } catch (error) {
    console.error('Ошибка загрузки сделок:', error)
    showError('Не удалось загрузить сделки')
  } finally {
    loading.value = false
  }
}

const loadServices = async () => {
  try {
    services.value = await serviceService.getServices()
  } catch (error) {
    console.error('Ошибка загрузки услуг:', error)
  }
}

// Поиск с задержкой
let searchTimeout: NodeJS.Timeout
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadDeals()
  }, 500)
}

// Вспомогательные функции
const getStatusCount = (status: string) => {
  return deals.value.filter(deal => deal.status === status).length
}

const toggleStatusFilter = (status: string) => {
  statusFilter.value = statusFilter.value === status ? '' : status
  loadDeals()
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

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

// Действия со сделками
const editDeal = (deal: Deal) => {
  editingDeal.value = deal
  showCreateModal.value = true
}

const deleteDeal = async (deal: Deal) => {
  if (!confirm(`Удалить сделку "${deal.title}"?`)) {
    return
  }

  try {
    await dealService.deleteDeal(deal.id)
    showSuccess('Сделка успешно удалена')
    loadDeals()
  } catch (error) {
    console.error('Ошибка удаления сделки:', error)
    showError('Не удалось удалить сделку')
  }
}

const changeDealStatus = async (deal: Deal, status: string) => {
  const statusNames: Record<string, string> = {
    won: 'выиграна',
    lost: 'проиграна'
  }

  if (!confirm(`Отметить сделку "${deal.title}" как ${statusNames[status]}?`)) {
    return
  }

  try {
    await dealService.changeDealStatus(deal.id, status)
    showSuccess(`Сделка отмечена как ${statusNames[status]}`)
    loadDeals()
  } catch (error) {
    console.error('Ошибка изменения статуса:', error)
    showError('Не удалось изменить статус сделки')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingDeal.value = null
}

const handleDealSaved = () => {
  closeModal()
  loadDeals()
}

// Инициализация
onMounted(() => {
  loadDeals()
  loadServices()
})
</script>