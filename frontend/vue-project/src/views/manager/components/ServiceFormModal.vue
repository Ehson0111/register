<!-- frontend/src/views/manager/components/ServiceFormModal.vue -->
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
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                {{ service ? 'Редактировать услугу' : 'Новая услуга' }}
              </DialogTitle>

              <form @submit.prevent="handleSubmit">
                <div class="space-y-4 mb-6">
                  <!-- Название услуги -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Название услуги *
                    </label>
                    <input
                      v-model="formData.name"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      :class="{ 'border-red-300': errors.name }"
                      placeholder="Например: Разработка веб-сайта"
                    />
                    <p v-if="errors.name" class="text-red-600 text-sm mt-1">
                      {{ errors.name }}
                    </p>
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
                      placeholder="Подробное описание услуги..."
                    />
                  </div>

                  <!-- Цена и длительность -->
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Цена (₽) *
                      </label>
                      <input
                        v-model="formData.price"
                        type="number"
                        step="0.01"
                        min="0"
                        required
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        :class="{ 'border-red-300': errors.price }"
                      />
                      <p v-if="errors.price" class="text-red-600 text-sm mt-1">
                        {{ errors.price }}
                      </p>
                    </div>

                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">
                        Длительность (дни)
                      </label>
                      <input
                        v-model="formData.duration_days"
                        type="number"
                        min="1"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  <!-- Статус -->
                  <div>
                    <label class="flex items-center">
                      <input
                        v-model="formData.is_active"
                        type="checkbox"
                        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <span class="ml-2 text-sm text-gray-700">Услуга активна</span>
                    </label>
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
                    <span v-else>{{ service ? 'Обновить' : 'Создать' }}</span>
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
import { ref, watch } from 'vue'
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'
import { useToast } from '../../../../src/composables/useToast'
import serviceService, { type Service, type CreateServiceData } from '../../../../src/services/serviceService'

interface Props {
  show: boolean
  service?: Service | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  saved: []
}>()

const { showSuccess, showError } = useToast()

const formData = ref<CreateServiceData>({
  name: '',
  description: '',
  price: 0,
  duration_days: 30,
  is_active: true
})

const errors = ref<Record<string, string>>({})
const loading = ref(false)

// Сброс формы при открытии/закрытии
watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.service) {
      formData.value = { ...props.service }
    } else {
      resetForm()
    }
  }
})

const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    price: 0,
    duration_days: 30,
    is_active: true
  }
  errors.value = {}
}

const closeModal = () => {
  emit('close')
}

const validateForm = (): boolean => {
  errors.value = {}

  if (!formData.value.name.trim()) {
    errors.value.name = 'Название услуги обязательно'
  }

  if (!formData.value.price || formData.value.price <= 0) {
    errors.value.price = 'Цена должна быть больше 0'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    loading.value = true
    errors.value = {}

    if (props.service) {
      await serviceService.updateService(props.service.id, formData.value)
      showSuccess('Услуга успешно обновлена')
    } else {
      await serviceService.createService(formData.value)
      showSuccess('Услуга успешно создана')
    }

    emit('saved')
  } catch (error: any) {
    console.error('Ошибка сохранения услуги:', error)
    
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else if (error.response?.data?.message) {
      errors.value.general = error.response.data.message
    } else {
      errors.value.general = 'Произошла ошибка при сохранении'
    }
    
    showError('Не удалось сохранить услугу')
  } finally {
    loading.value = false
  }
}
</script>