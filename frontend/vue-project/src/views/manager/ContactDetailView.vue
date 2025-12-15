<!-- frontend/src/views/manager/ContactDetailView.vue -->
<template>
  <div class="space-y-6" v-if="contact">
    <!-- Заголовок -->
    <div class="flex justify-between items-start">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">
          {{ contact.first_name }} {{ contact.last_name }}
        </h1>
        <p class="text-gray-600 mt-1">{{ contact.email }}</p>
      </div>
      <button 
        @click="$router.back()"
        class="text-gray-500 hover:text-gray-700 transition-colors"
      >
        ← Назад
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Основная информация -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Карточка информации -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Информация о контакте</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-500">Телефон</label>
              <p class="text-gray-900">{{ contact.phone || 'Не указан' }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Компания</label>
              <p class="text-gray-900">{{ contact.company || 'Не указана' }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Должность</label>
              <p class="text-gray-900">{{ contact.position || 'Не указана' }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-500">Статус</label>
              <span 
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                :class="getStatusClass(contact.status)"
              >
                {{ contact.status_display }}
              </span>
            </div>
            <div class="md:col-span-2">
              <label class="text-sm font-medium text-gray-500">Адрес</label>
              <p class="text-gray-900">{{ contact.address || 'Не указан' }}</p>
            </div>
            <div class="md:col-span-2">
              <label class="text-sm font-medium text-gray-500">Заметки</label>
              <p class="text-gray-900">{{ contact.notes || 'Нет заметок' }}</p>
            </div>
          </div>
        </div>

        <!-- Сделки контакта -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Сделки</h2>
          <p class="text-gray-500">Функционал сделок будет добавлен позже...</p>
        </div>
      </div>

      <!-- Боковая панель -->
      <div class="space-y-6">
        <!-- Статистика -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Статистика</h3>
          <div class="space-y-3">
            <div>
              <p class="text-sm text-gray-500">Активные сделки</p>
              <p class="text-2xl font-bold text-gray-900">{{ contact.active_deals_count || 0 }}</p>
            </div>
            <div>
              <p class="text-sm text-gray-500">Дата создания</p>
              <p class="text-gray-900">{{ formatDate(contact.created_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Действия -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Действия</h3>
          <div class="space-y-2">
            <button class="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded">
              Создать сделку
            </button>
            <button class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded">
              Отправить email
            </button>
            <button class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded">
              Добавить заметку
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="loading" class="text-center py-8">
    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
    <p class="text-gray-500 mt-2">Загрузка контакта...</p>
  </div>

  <div v-else class="text-center py-8">
    <p class="text-gray-500">Контакт не найден</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
// import contactService, { type Contact } from '../../../services/contactService'
import contactService, { type Contact } from '../../services/contactService'


const route = useRoute()
const contact = ref<Contact | null>(null)
const loading = ref(true)

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    lead: 'bg-yellow-100 text-yellow-800',
    client: 'bg-green-100 text-green-800',
    partner: 'bg-blue-100 text-blue-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

onMounted(async () => {
  try {
    const contactId = parseInt(route.params.id as string)
    contact.value = await contactService.getContact(contactId)
  } catch (error) {
    console.error('Ошибка загрузки контакта:', error)
  } finally {
    loading.value = false
  }
})
</script>