<!-- frontend/src/views/manager/components/ContactFormModal.vue -->
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
                {{ contact ? 'Редактировать контакт' : 'Добавить контакт' }}
              </DialogTitle>

              <form @submit.prevent="handleSubmit">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <!-- Имя -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Имя *
                    </label>
                    <input
                      v-model="formData.first_name"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      :class="{ 'border-red-300': errors.first_name }"
                    />
                    <p v-if="errors.first_name" class="text-red-600 text-sm mt-1">
                      {{ errors.first_name }}
                    </p>
                  </div>

                  <!-- Фамилия -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Фамилия *
                    </label>
                    <input
                      v-model="formData.last_name"
                      type="text"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      :class="{ 'border-red-300': errors.last_name }"
                    />
                    <p v-if="errors.last_name" class="text-red-600 text-sm mt-1">
                      {{ errors.last_name }}
                    </p>
                  </div>

                  <!-- Email -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Email *
                    </label>
                    <input
                      v-model="formData.email"
                      type="email"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      :class="{ 'border-red-300': errors.email }"
                    />
                    <p v-if="errors.email" class="text-red-600 text-sm mt-1">
                      {{ errors.email }}
                    </p>
                  </div>

                  <!-- Телефон -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Телефон
                    </label>
                    <input
                      v-model="formData.phone"
                      type="tel"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <!-- Компания -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Компания
                    </label>
                    <input
                      v-model="formData.company"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <!-- Должность -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Должность
                    </label>
                    <input
                      v-model="formData.position"
                      type="text"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <!-- Статус -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                      Статус *
                    </label>
                    <select
                      v-model="formData.status"
                      required
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      :class="{ 'border-red-300': errors.status }"
                    >
                      <option value="lead">Lead</option>
                      <option value="client">Client</option>
                      <option value="partner">Partner</option>
                    </select>
                    <p v-if="errors.status" class="text-red-600 text-sm mt-1">
                      {{ errors.status }}
                    </p>
                  </div>
                </div>

                <!-- Адрес -->
                <div class="mb-4">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Адрес 
                  </label>
                  <textarea
                    v-model="formData.address"
                    rows="2"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <!-- Заметки -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-1">
                    Заметки
                  </label>
                  <textarea
                    v-model="formData.notes"
                    rows="3"
                    class="w-full px-3 py-2 border border-gray-300 arounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
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
                    <span v-else>{{ contact ? 'Обновить' : 'Создать' }}</span>
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
import { ref, watch, computed } from 'vue'
import {
  TransitionRoot,
  TransitionChild,
  Dialog,
  DialogPanel,
  DialogTitle,
} from '@headlessui/vue'
import { useToast } from '../../../../src/composables/useToast'
import contactService, { type Contact, type CreateContactData } from '../../../services/contactService'

interface Props {
  show: boolean
  contact?: Contact | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  saved: []
}>()

const { showSuccess, showError } = useToast()

const formData = ref<CreateContactData>({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  company: '',
  position: '',
  status: 'lead',
  address: '',
  notes: ''
})

const errors = ref<Record<string, string>>({})
const loading = ref(false)

// Сброс формы при открытии/закрытии
watch(() => props.show, (newVal) => {
  if (newVal && props.contact) {
    // Заполняем форму данными контакта для редактирования
    formData.value = { ...props.contact }

    console.log("xcv",formData.value.address)
  } else if (!newVal) {
    // Сбрасываем форму при закрытии
    resetForm()
  }
})

const resetForm = () => {
  formData.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    company: '',
    position: '',
    status: 'lead',
    address: '',
    notes: ''
  }
  errors.value = {}
}

const closeModal = () => {
  emit('close')
}

const validateForm = (): boolean => {
  errors.value = {}

  if (!formData.value.first_name.trim()) {
    errors.value.first_name = 'Имя обязательно'
  }

  if (!formData.value.last_name.trim()) {
    errors.value.last_name = 'Фамилия обязательна'
  }

  if (!formData.value.email.trim()) {
    errors.value.email = 'Email обязателен'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email)) {
    errors.value.email = 'Введите корректный email'
  }

  if (!formData.value.status || !formData.value.status.trim()) {
    errors.value.status = 'Статус обязателен'
  }

  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    loading.value = true
    errors.value = {}

    if (props.contact) {
      // Редактирование существующего контакта
      await contactService.updateContact(props.contact.id, formData.value)
      showSuccess('Контакт успешно обновлен')
    } else {
      // Создание нового контакта
      await contactService.createContact(formData.value)
      showSuccess('Контакт успешно создан')
    }

    emit('saved')
  } catch (error: any) {
    console.error('Ошибка сохранения контакта:', error)
    
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else if (error.response?.data?.message) {
      errors.value.general = error.response.data.message
    } else {
      errors.value.general = 'Произошла ошибка при сохранении'
    }
    
    showError('Не удалось сохранить контакт')
  } finally {
    loading.value = false
  }
}
</script>