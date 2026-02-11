<template>
  <div class="space-y-8">
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Доступные услуги</h3>
      </div>
      <div class="p-6">
        <div v-if="loadingServices" class="text-center py-8 text-gray-500">Загрузка...</div>
        <div v-else-if="!services.length" class="text-center py-8 text-gray-500">Нет доступных услуг.</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="s in services"
            :key="s.id"
            class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <p class="font-medium text-gray-900">{{ s.name }}</p>
            <p class="text-sm text-gray-600 mt-1">{{ formatCurrency(s.price) }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Оставить заявку на услугу</h3>
      <form @submit.prevent="submitRequest" class="space-y-4 max-w-xl">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Услуга *</label>
          <select
            v-model="requestForm.service_id"
            required
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Выберите услугу</option>
            <option v-for="s in services" :key="s.id" :value="s.id">{{ s.name }} — {{ formatCurrency(s.price) }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Комментарий</label>
          <textarea
            v-model="requestForm.message"
            rows="3"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Опишите задачу или пожелания"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Желаемый бюджет (₽)</label>
          <input
            v-model.number="requestForm.budget"
            type="number"
            min="0"
            step="1"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="По умолчанию — цена услуги"
          >
        </div>
        <p v-if="requestError" class="text-sm text-red-600">{{ requestError }}</p>
        <button
          type="submit"
          :disabled="requestLoading || !requestForm.service_id"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
        >
          {{ requestLoading ? 'Отправка...' : 'Отправить заявку' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import clientService, { type ClientServiceOption } from '../../services/clientService'

const router = useRouter()
const services = ref<ClientServiceOption[]>([])
const loadingServices = ref(true)
const requestForm = ref({ service_id: '' as number | '', message: '', budget: undefined as number | undefined })
const requestLoading = ref(false)
const requestError = ref('')

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(amount)
}

async function loadServices() {
  loadingServices.value = true
  try {
    services.value = await clientService.getServices()
  } catch {
    services.value = []
  } finally {
    loadingServices.value = false
  }
}

async function submitRequest() {
  const serviceId = requestForm.value.service_id
  if (!serviceId) return
  requestError.value = ''
  requestLoading.value = true
  try {
    await clientService.createRequest({
      service_id: Number(serviceId),
      message: requestForm.value.message || undefined,
      budget: requestForm.value.budget
    })
    requestForm.value = { service_id: '', message: '', budget: undefined }
    await router.push('/client/deals')
  } catch (e: any) {
    requestError.value = e.response?.data?.error || e.message || 'Ошибка отправки заявки'
  } finally {
    requestLoading.value = false
  }
}

onMounted(loadServices)
</script>
