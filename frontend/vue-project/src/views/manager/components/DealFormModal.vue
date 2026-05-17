<!-- frontend/src/views/manager/components/DealFormModal.vue -->
<template>
  <TransitionRoot appear :show="show" as="template">
    <Dialog as="div" @close="closeModal" class="relative z-10">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                {{ deal ? 'Редактировать сделку' : 'Новая сделка' }}
              </DialogTitle>

              <form @submit.prevent="handleSubmit">
                <div class="space-y-4 mb-6">
                  <!-- Название сделки -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Название сделки *
                    </label>
                    <input
                      v-model="formData.title"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      :class="{ 'border-red-300': errors.title }"
                      placeholder="Например: Разработка сайта для ООО Ромашка"
                    />
                    <p v-if="errors.title" class="text-red-600 text-sm mt-1">
                      {{ errors.title }}
                    </p>
                  </div>

                  <!-- Контакт и услуга -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Контакт *
                      </label>

                      <select
                        v-model="formData.contact"
                        required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        :class="{ 'border-red-300': errors.contact }"
                      >
                        <option value="">Выберите контакт</option>
                        <option v-for="contact in contacts" :key="contact.id" :value="contact.id">
                          {{ contact.first_name }} {{ contact.last_name }} - {{ contact.company }}
                        </option>
                      </select>
                      <p v-if="errors.contact" class="text-red-600 text-sm mt-1">
                        {{ errors.contact }}
                      </p>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Услуга *
                      </label>
                      <!-- {{formData.contact_name}} -->
                      <select
                        v-model="formData.service"
                        required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        :class="{ 'border-red-300': errors.service }"
                      >
                        <option value="">Выберите услугу</option>
                        <option v-for="service in services" :key="service.id" :value="service.id">
                          {{ service.name }} - {{ formatCurrency(Number(service.price)) }}
                        </option>
                      </select>
                      <p v-if="errors.service" class="text-red-600 text-sm mt-1">
                        {{ errors.service }}
                      </p>
                    </div>
                  </div>

                  <!-- Сумма и вероятность -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Сумма сделки *
                      </label>
                      <div class="relative">
                        <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">₽</span>
                        <input
                          v-model="formData.amount"
                          type="number"
                          step="0.01"
                          min="0"
                          required
                          class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                          :class="{ 'border-red-300': errors.amount }"
                          placeholder="0.00"
                        />
                      </div>
                      <p v-if="errors.amount" class="text-red-600 text-sm mt-1">
                        {{ errors.amount }}
                    </p>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Вероятность (%)
                      </label>
                      <input
                        v-model="formData.probability"
                        type="range"
                        min="0"
                        max="100"
                        step="5"
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <div class="flex justify-between text-sm text-gray-600 mt-1">
                        <span>0%</span>
                        <span class="font-medium">{{ formData.probability }}%</span>
                        <span>100%</span>
                      </div>
                    </div>
                  </div>

                  <!-- Статус, этап и дата закрытия -->
                  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Статус *
                      </label>
                      <select
                        v-model="formData.status"
                        required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option
                          v-for="status in dealStatusOptions"
                          :key="status.value"
                          :value="status.value"
                        >
                          {{ status.label }}
                        </option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Этап
                      </label>
                      <select
                        v-model="formData.stage"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option :value="null">Без этапа</option>
                        <option v-for="stage in stages" :key="stage.id" :value="stage.id">
                          {{ stage.name }}
                        </option>
                      </select>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Ожидаемая дата закрытия
                      </label>
                      <input
                        v-model="formData.expected_close_date"
                        type="date"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  <!-- Описание -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Описание
                    </label>
                    <textarea
                      v-model="formData.description"
                      rows="3"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Детальное описание сделки..."
                    />
                  </div>
                </div>

                <!-- Ошибки -->
                <div v-if="errors.general" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <p class="text-red-600 text-sm">{{ errors.general }}</p>
                </div>

                <!-- Кнопки -->
                <div class="flex justify-end space-x-3">
                  <button
                    type="button"
                    @click="closeModal"
                    class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    :disabled="loading"
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    :disabled="loading"
                  >
                    <span v-if="loading">Сохранение...</span>
                    <span v-else>{{ deal ? 'Обновить' : 'Создать' }}</span>
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'
import { useToast } from '../../../composables/useToast'
import dealService from '../../../services/dealService'
import contactService, { type Contact, type DealStage } from '../../../services/contactService'
import serviceService, { type Service } from '../../../services/serviceService'
import { DEAL_STATUS_OPTIONS } from '../../../constants/dealStatuses'

const dealStatusOptions = DEAL_STATUS_OPTIONS

interface Props {
  show: boolean
  deal?: any | null
  defaultContactId?: number | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  saved: []
}>()

const { showSuccess, showError } = useToast()

const formData = ref<any>({
  title: '',
  description: '',
  contact: 0,
  service: 0,
  amount: 0,
  probability: 50,
  status: 'new',
  stage: null,
  expected_close_date: ''
})

const contacts = ref<Contact[]>([])
const services = ref<Service[]>([])
const stages = ref<DealStage[]>([])
const errors = ref<Record<string, string>>({})
const loading = ref(false)

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

// Загрузка данных для выпадающих списков
const loadFormData = async () => {
  try {
    const [contactsData, servicesData] = await Promise.all([
      contactService.getContacts(),
      serviceService.getServices()
    ])
    stages.value = await dealService.getDealStages()

    // print(contactsData)
    contacts.value = contactsData
    services.value = servicesData

  } catch (error) {
    console.error('Ошибка загрузки данных формы:', error)
  }
}

// Сброс формы при открытии/закрытии
watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.deal) {
      // Заполняем форму данными сделки для редактирования
      formData.value = {
        ...props.deal,
        contact: props.deal.contact,
        service: props.deal.service,
        stage: props.deal.stage ?? null
      }
    } else {
      // Сбрасываем форму для создания и подставляем контакт, если передан
      resetForm()
      if (props.defaultContactId && props.defaultContactId > 0) {
        formData.value.contact = props.defaultContactId
      }
    }
  }
})

const resetForm = () => {
  formData.value = {
    title: '',
    description: '',
    contact: 0,
    service: 0,
    amount: 0,
    probability: 50,
    status: 'new',
    stage: null,
    expected_close_date: ''
  }
  errors.value = {}
}

const closeModal = () => {
  emit('close')
}

const validateForm = (): boolean => {
  errors.value = {}

  if (!formData.value.title.trim()) {
    errors.value.title = 'Название сделки обязательно'
  }

  if (!formData.value.contact) {
    errors.value.contact = 'Выберите контакт'
  }

  if (!formData.value.service) {
    errors.value.service = 'Выберите услугу'
  }

  if (!formData.value.amount || formData.value.amount <= 0) {
    errors.value.amount = 'Сумма должна быть больше 0'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    loading.value = true
    errors.value = {}

    if (props.deal) {
      // Редактирование существующей сделки
      await dealService.updateDeal(props.deal.id, formData.value)
      showSuccess('Сделка успешно обновлена')
    } else {
      // Создание новой сделки
      await dealService.createDeal(formData.value)
      showSuccess('Сделка успешно создана')
    }

    emit('saved')
  } catch (error: any) {
    console.error('Ошибка сохранения сделки:', error)
    
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else if (error.response?.data?.message) {
      errors.value.general = error.response.data.message
    } else {
      errors.value.general = 'Произошла ошибка при сохранении'
    }
    
    showError('Не удалось сохранить сделку')
  } finally {
    loading.value = false
  }
}

// Инициализация
onMounted(() => {
  loadFormData()
})
</script>