<!-- frontend/src/views/manager/ContactsView.vue -->
<template>
  <div class="space-y-6">
    <!-- Заголовок и кнопки -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Контакты</h1>
        <p class="text-gray-600 mt-1">Управление клиентами и партнерами</p>
      </div>
      <button 
        @click="showCreateModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
      >
        <PlusIcon class="w-5 h-5" />
        <span>Добавить контакт</span>
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
              placeholder="Поиск по имени, email или компании..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              @input="handleSearch"
            />
          </div>
        </div>
        
        <!-- Фильтр по статусу -->
        <select
          v-model="statusFilter"
          @change="loadContacts"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Все статусы</option>
          <option value="lead">Lead</option>
          <option value="client">Client</option>
          <option value="partner">Partner</option>
        </select>
      </div>
    </div>

    <!-- Таблица контактов -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <!-- Заголовок таблицы -->
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">
            Все контакты ({{ contacts.length }})
          </h3>
          <div class="flex items-center space-x-4">
            <button
              @click="loadContacts"
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
        <p class="text-gray-500 mt-2">Загрузка контактов...</p>
      </div>

      <!-- Состояние пустого списка -->
      <div v-else-if="contacts.length === 0" class="p-8 text-center">
        <UsersIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Контакты не найдены</h3>
        <p class="text-gray-500 mb-4">Начните с добавления первого контакта</p>
        <button
          @click="showCreateModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          + Добавить контакт
        </button>
      </div>

      <!-- Таблица -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Контакт
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Компания
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Телефон
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
              v-for="contact in contacts" 
              :key="contact.id"
              class="hover:bg-gray-50 transition-colors cursor-pointer"
              @click="$router.push(`/manager/contacts/${contact.id}`)"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                    <span class="text-blue-600 font-medium text-sm">
                      {{ getInitials(contact.first_name, contact.last_name) }}
                    </span>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">
                      {{ contact.first_name }} {{ contact.last_name }}
                    </div>
                    <div class="text-sm text-gray-500">{{ contact.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ contact.company || '-' }}</div>
                <div class="text-sm text-gray-500">{{ contact.position || '-' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ contact.phone || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  :class="getStatusClass(contact.status)"
                >
                  {{ contact.status_display }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ contact.active_deals_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(contact.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button
                    @click.stop="editContact(contact)"
                    class="text-blue-600 hover:text-blue-900 transition-colors"
                    title="Редактировать"
                  >
                    <PencilIcon class="w-4 h-4" />
                  </button>
                  <button
                    @click.stop="deleteContact(contact)"
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
    <ContactFormModal
      :show="showCreateModal"
      :contact="editingContact"
      @close="closeModal"
      @saved="handleContactSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// import { useToast } from '../../../composables/useToast'
import {useToast} from '../../../src/composables/useToast'
import contactService, { type Contact } from '../../../src/services/contactService'
import ContactFormModal from './components/ContactFormModal.vue'
import {
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  UsersIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const { showSuccess, showError } = useToast()

// Состояние
const contacts = ref<Contact[]>([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const showCreateModal = ref(false)
const editingContact = ref<Contact | null>(null)

// Загрузка контактов
const loadContacts = async () => {
  try {
    loading.value = true
    const params: any = {}
    
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }

    contacts.value = await contactService.getContacts(params)
  } catch (error) {
    console.error('Ошибка загрузки контактов:', error)
    showError('Не удалось загрузить контакты')
  } finally {
    loading.value = false
  }
}

// Поиск с задержкой
let searchTimeout: NodeJS.Timeout
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadContacts()
  }, 500)
}

// Вспомогательные функции
const getInitials = (firstName: string, lastName: string) => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

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

// Действия с контактами
const editContact = (contact: Contact) => {
  editingContact.value = contact
  showCreateModal.value = true
}

const deleteContact = async (contact: Contact) => {
  if (!confirm(`Удалить контакт ${contact.first_name} ${contact.last_name}?`)) {
    return
  }

  try {
    await contactService.deleteContact(contact.id)
    showSuccess('Контакт успешно удален')
    loadContacts()
  } catch (error) {
    console.error('Ошибка удаления контакта:', error)
    showError('Не удалось удалить контакт')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingContact.value = null
}

const handleContactSaved = () => {
  closeModal()
  loadContacts()
}

// Инициализация
onMounted(() => {
  loadContacts()
})
</script>