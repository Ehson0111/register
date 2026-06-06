<!--
  [VIEW] ServicesView — каталог услуг компании (CRUD)
  Маршрут: /manager/services | Модалка: ServiceFormModal.vue
-->
<template>
  <div class="space-y-6">
    <!-- Заголовок и кнопки -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Услуги</h1>
        <p class="text-gray-600 mt-1">Управление услугами и ценами</p>
      </div>
      <button 
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
      >
        <PlusIcon class="w-5 h-5" />
        <span>Добавить услугу</span>
      </button>
    </div>

    <!-- Статистика -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-blue-100 rounded-lg">
            <CogIcon class="w-6 h-6 text-blue-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Всего услуг</p>
            <p class="text-2xl font-bold text-gray-900">{{ services.length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-green-100 rounded-lg">
            <CheckCircleIcon class="w-6 h-6 text-green-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Активные услуги</p>
            <p class="text-2xl font-bold text-gray-900">{{ activeServicesCount }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-purple-100 rounded-lg">
            <CurrencyDollarIcon class="w-6 h-6 text-purple-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Средняя цена</p>
            <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(averagePrice) }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="flex items-center">
          <div class="p-2 bg-orange-100 rounded-lg">
            <BriefcaseIcon class="w-6 h-6 text-orange-600" />
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-600">Активные сделки</p>
            <p class="text-2xl font-bold text-gray-900">{{ totalActiveDeals }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <!-- Поиск -->
        <div class="flex-1">
          <div class="relative">
            <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Поиск по названию услуги..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="handleSearch"
            />
          </div>
        </div>
        
        <!-- Фильтр по статусу -->
        <select
          v-model="statusFilter"
          @change="loadServices"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Все статусы</option>
          <option value="active">Активные</option>
          <option value="inactive">Неактивные</option>
        </select>
      </div>
    </div>

    <!-- Таблица услуг -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <!-- Заголовок таблицы -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Все услуги ({{ services.length }})
          </h3>
          <div class="flex items-center space-x-4">
            <button
              @click="loadServices"
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
        <p class="text-gray-500 mt-2">Загрузка услуг...</p>
      </div>

      <!-- Состояние пустого списка -->
      <div v-else-if="services.length === 0" class="p-8 text-center">
        <CogIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Услуги не найдены</h3>
        <p class="text-gray-500 mb-4">Начните с добавления первой услуги</p>
        <button
          @click="showCreateModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Добавить услугу
        </button>
      </div>

      <!-- Таблица -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Услуга
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Описание
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Цена
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Длительность
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Статус
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Активные сделки
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Дата создания
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="service in services" 
              :key="service.id"
              class="hover:bg-gray-50 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                    <CogIcon class="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ service.name }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 max-w-xs truncate">
                  {{ service.description || 'Нет описания' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ formatCurrency(parseFloat(service.price)) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ service.duration_days }} дней
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="service.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ service.is_active ? 'Активна' : 'Неактивна' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ service.active_deals_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(service.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button
                    @click="editService(service)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Редактировать"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="toggleServiceStatus(service)"
                    class="text-orange-600 hover:text-orange-900 transition-colors"
                    :title="service.is_active ? 'Деактивировать' : 'Активировать'"
                  >
                    <PowerIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click="deleteService(service)"
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
    <ServiceFormModal
      :show="showCreateModal"
      :service="editingService"
      @close="closeModal"
      @saved="handleServiceSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from '../../../src/composables/useToast'
import serviceService, { type Service } from '../../../src/services/serviceService'
import ServiceFormModal from './components/ServiceFormModal.vue'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  CogIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  BriefcaseIcon,
  PencilIcon,
  PowerIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const { showSuccess, showError } = useToast()
const route = useRoute()

// Состояние
const services = ref<Service[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const showCreateModal = ref(false)
const editingService = ref<Service | null>(null)

// Computed свойства
const activeServicesCount = computed(() => {
  return services.value.filter(service => service.is_active).length
})

const averagePrice = computed(() => {
  if (services.value.length === 0) return 0
  const total = services.value.reduce((sum, service) => sum + parseFloat(service.price), 0)
  return total / services.value.length
})

const totalActiveDeals = computed(() => {
  return services.value.reduce((sum, service) => sum + (service.active_deals_count || 0), 0)
})

// Загрузка услуг
const loadServices = async () => {
  try {
    loading.value = true
    services.value = await serviceService.getServices()
  } catch (error) {
    console.error('Ошибка загрузки услуг:', error)
    showError('Не удалось загрузить услуги')
  } finally {
    loading.value = false
  }
}

// Поиск с задержкой
let searchTimeout: NodeJS.Timeout
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadServices()
  }, 500)
}

// Вспомогательные функции
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

// Действия с услугами
const editService = (service: Service) => {
  editingService.value = service
  showCreateModal.value = true
}

const deleteService = async (service: Service) => {
  if (!confirm(`Удалить услугу "${service.name}"?`)) {
    return
  }

  try {
    await serviceService.deleteService(service.id)
    showSuccess('Услуга успешно удалена')
    loadServices()
  } catch (error) {
    console.error('Ошибка удаления услуги:', error)
    showError('Не удалось удалить услугу')
  }
}

const toggleServiceStatus = async (service: Service) => {
  const newStatus = !service.is_active
  const action = newStatus ? 'активирована' : 'деактивирована'

  if (!confirm(`${newStatus ? 'Активировать' : 'Деактивировать'} услугу "${service.name}"?`)) {
    return
  }

  try {
    await serviceService.updateService(service.id, { is_active: newStatus })
    showSuccess(`Услуга успешно ${action}`)
    loadServices()
  } catch (error) {
    console.error('Ошибка изменения статуса:', error)
    showError('Не удалось изменить статус услуги')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingService.value = null
}

const handleServiceSaved = () => {
  closeModal()
  loadServices()
}

const openServiceFromQuery = async () => {
  const rawId = route.query.id
  if (!rawId) return

  const serviceId = Number(rawId)
  if (!Number.isFinite(serviceId)) return

  let service = services.value.find((item) => item.id === serviceId)
  if (!service) {
    try {
      service = await serviceService.getService(serviceId)
    } catch {
      return
    }
  }

  editingService.value = service
  showCreateModal.value = true
}

// Инициализация
onMounted(async () => {
  await loadServices()
  await openServiceFromQuery()
})

watch(() => route.query.id, () => {
  openServiceFromQuery()
})
</script>