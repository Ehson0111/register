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
          <div v-if="dealsLoading" class="text-sm text-gray-500">
            Загрузка сделок...
          </div>
          <div v-else-if="contactDeals.length === 0" class="text-sm text-gray-500">
            У этого контакта пока нет сделок.
          </div>
          <ul v-else class="divide-y divide-gray-100">
            <li
              v-for="deal in contactDeals"
              :key="deal.id"
              class="py-3 flex items-center justify-between"
            >
              <div>
                <button
                  class="text-sm font-medium text-blue-600 hover:underline"
                  @click="$router.push(`/manager/deals/${deal.id}`)"
                >
                  {{ deal.title }}
                </button>
                <p class="text-xs text-gray-500">
                  {{ deal.service_name }} · {{ deal.status_display }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-900">
                  {{ formatCurrency(deal.amount) }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ deal.expected_close_date ? formatDate(deal.expected_close_date) : 'Без даты' }}
                </p>
              </div>
            </li>
          </ul>
        </div>

        <!-- История изменений -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">История изменений</h2>
          <div v-if="auditLoading" class="text-sm text-gray-500">Загрузка истории...</div>
          <div v-else-if="auditTrail.length === 0" class="text-sm text-gray-500">
            По контакту пока нет зафиксированных изменений.
          </div>
          <ul v-else class="divide-y divide-gray-100">
            <li v-for="item in auditTrail" :key="item.id" class="py-3 flex items-start justify-between gap-4">
              <div>
                <p class="text-sm font-medium text-gray-900">{{ auditActionText(item.action) }}</p>
                <p class="text-xs text-gray-500">Кто: {{ item.actor || "system" }}</p>
              </div>
              <p class="text-xs text-gray-500 whitespace-nowrap">{{ formatDateTime(item.created_at) }}</p>
            </li>
          </ul>
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
            <button
              class="w-full text-left px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 rounded"
              @click="openCreateDeal"
            >
              Создать сделку
            </button>
            <button
              class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded"
              @click="sendEmailToContact"
            >
              Отправить email
            </button>
            <button
              class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded"
              @click="openEditContact"
            >
              Добавить заметку
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модалка создания/редактирования сделки для контакта -->
    <DealFormModal
      :show="showDealModal"
      :deal="null"
      :defaultContactId="contact?.id || null"
      @close="closeDealModal"
      @saved="handleDealSaved"
    />

    <!-- Модалка редактирования контакта (для заметок и пр.) -->
    <ContactFormModal
      :show="showContactModal"
      :contact="contact"
      @close="closeContactModal"
      @saved="handleContactSaved"
    />
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
import { useRoute, useRouter } from 'vue-router'
import contactService, { type Contact, type AuditTrailItem } from '../../services/contactService'
import dealService from '../../services/dealService'
import DealFormModal from './components/DealFormModal.vue'
import ContactFormModal from './components/ContactFormModal.vue'


const route = useRoute()
const router = useRouter()
const contact = ref<Contact | null>(null)
const loading = ref(true)
const contactDeals = ref<any[]>([])
const dealsLoading = ref(false)
const showDealModal = ref(false)
const showContactModal = ref(false)
const auditTrail = ref<AuditTrailItem[]>([])
const auditLoading = ref(false)

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

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('ru-RU')
}

const auditActionText = (action: string) => {
  const map: Record<string, string> = {
    contact_created: 'Контакт создан',
    contact_updated: 'Контакт изменен',
    contact_deleted: 'Контакт удален',
    deal_created: 'Создана сделка по контакту',
    deal_status_changed: 'Изменен статус сделки',
  }
  return map[action] || action
}

const formatCurrency = (amount: number) => {
  return contactService.formatCurrency(amount)
}

const loadContactDeals = async (contactId: number) => {
  try {
    dealsLoading.value = true
    contactDeals.value = await dealService.getDealsByContact(contactId)
  } catch (error) {
    console.error('Ошибка загрузки сделок контакта:', error)
  } finally {
    dealsLoading.value = false
  }
}

const loadAuditTrail = async (contactId: number) => {
  try {
    auditLoading.value = true
    // #region agent log
    fetch("http://127.0.0.1:7647/ingest/66103dc7-eaf0-4803-be05-aba9d5dec07c", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "ad25e9" },
      body: JSON.stringify({
        sessionId: "ad25e9",
        runId: "run3",
        hypothesisId: "H13",
        location: "ContactDetailView.vue:loadAuditTrail",
        message: "loading contact audit trail",
        data: { contactId },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
    // #endregion
    auditTrail.value = await contactService.getAuditTrail({
      entity_type: 'contact',
      entity_id: contactId,
    })
  } catch (error) {
    console.error('Ошибка загрузки истории:', error)
  } finally {
    auditLoading.value = false
  }
}

const openCreateDeal = () => {
  if (!contact.value) return
  showDealModal.value = true
}

const closeDealModal = () => {
  showDealModal.value = false
}

const handleDealSaved = async () => {
  closeDealModal()
  if (contact.value) {
    await loadContactDeals(contact.value.id)
    await loadAuditTrail(contact.value.id)
  }
}

const sendEmailToContact = () => {
  if (!contact.value) return
  router.push({
    name: 'ManagerMarketing',
    query: { recipientId: String(contact.value.id) }
  })
}

const openEditContact = () => {
  if (!contact.value) return
  showContactModal.value = true
}

const closeContactModal = () => {
  showContactModal.value = false
}

const handleContactSaved = async () => {
  closeContactModal()
  if (!contact.value) return
  try {
    const updated = await contactService.getContact(contact.value.id)
    contact.value = updated
    await loadAuditTrail(contact.value.id)
  } catch (error) {
    console.error('Ошибка обновления контакта:', error)
  }
}

onMounted(async () => {
  try {
    const contactId = parseInt(route.params.id as string)
    contact.value = await contactService.getContact(contactId)
    await loadContactDeals(contactId)
    await loadAuditTrail(contactId)
  } catch (error) {
    console.error('Ошибка загрузки контакта:', error)
  } finally {
    loading.value = false
  }
})
</script>