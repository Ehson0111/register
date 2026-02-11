<!-- frontend/src/views/manager/MarketingView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Маркетинг и рассылки</h2>
      <button
        @click="openCreateModal()"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        + Новая рассылка
      </button>
    </div>

    <!-- Загрузка / Ошибка -->
    <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>

    <template v-else>
      <!-- Статистика -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Общая статистика</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Всего рассылок</span>
              <span class="font-semibold">{{ stats.total_campaigns }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Получателей</span>
              <span class="font-semibold">{{ stats.total_recipients }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">Доставлено</span>
              <span class="font-semibold text-green-600">{{ stats.total_sent }}</span>
            </div>
            <div class="flex justify-between items-center" v-if="stats.total_recipients > 0">
              <span class="text-gray-600">% доставки</span>
              <span class="font-semibold text-blue-600">{{ deliveryRate }}%</span>
            </div>
          </div>
        </div>

        <!-- Рассылки -->
        <div class="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Рассылки</h3>
          <div class="space-y-4">
            <div
              v-for="campaign in campaigns"
              :key="campaign.id"
              class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="flex-1">
                <h4 class="font-medium text-gray-900">{{ campaign.name }}</h4>
                <p class="text-sm text-gray-600">
                  {{ campaign.recipient_count }} получателей · {{ campaign.status_display }}
                </p>
              </div>
              <div class="text-right">
                <div class="text-sm font-medium text-gray-900">{{ campaign.delivery_rate }}%</div>
                <div class="w-24 bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-500 h-2 rounded-full"
                    :style="{ width: Math.min(campaign.delivery_rate, 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
            <p v-if="campaigns.length === 0" class="text-sm text-gray-500">Пока нет рассылок.</p>
          </div>
        </div>
      </div>

      <!-- Шаблоны писем -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Шаблоны писем</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="template in templates"
            :key="template.id"
            class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
          >
            <h4 class="font-medium text-gray-900 mb-2">{{ template.name }}</h4>
            <p class="text-sm text-gray-600 mb-3">{{ template.description || '—' }}</p>
            <div class="flex space-x-2">
              <button
                @click="useTemplate(template)"
                class="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Использовать
              </button>
            </div>
          </div>
          <p v-if="templates.length === 0" class="text-sm text-gray-500 col-span-full">Нет шаблонов.</p>
        </div>
      </div>
    </template>

    <!-- Модальное окно: новая рассылка -->
    <Teleport to="body">
      <div
        v-if="showCreateCampaign"
        class="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="modal-title"
        role="dialog"
        aria-modal="true"
      >
        <div class="flex min-h-screen items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/30" aria-hidden="true" @click="showCreateCampaign = false"></div>
          <div class="relative bg-white rounded-xl shadow-lg max-w-lg w-full p-6">
            <h3 id="modal-title" class="text-lg font-semibold text-gray-900 mb-4">Новая рассылка</h3>

            <!-- Режим: по шаблону / быстрое сообщение -->
            <div class="flex gap-4 mb-4 border-b border-gray-200">
              <button
                :class="[
                  'pb-2 text-sm font-medium border-b-2 transition-colors',
                  campaignMode === 'template'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                ]"
                @click="campaignMode = 'template'"
              >
                По шаблону
              </button>
              <button
                :class="[
                  'pb-2 text-sm font-medium border-b-2 transition-colors',
                  campaignMode === 'quick'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                ]"
                @click="campaignMode = 'quick'"
              >
                Быстрое сообщение
              </button>
            </div>

            <form @submit.prevent="submitCampaign" class="space-y-4">
              <!-- По шаблону -->
              <template v-if="campaignMode === 'template'">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Шаблон *</label>
                  <select
                    v-model="form.template_id"
                    required
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Выберите шаблон</option>
                    <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Тема письма</label>
                  <input
                    v-model="form.subject"
                    type="text"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Тема"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Текст (опционально)</label>
                  <textarea
                    v-model="form.content"
                    rows="3"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Оставьте пустым, чтобы использовать текст шаблона"
                  ></textarea>
                </div>
              </template>

              <!-- Быстрое сообщение -->
              <template v-else>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Тема *</label>
                  <input
                    v-model="quickForm.subject"
                    type="text"
                    required
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Тема письма"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Текст сообщения *</label>
                  <textarea
                    v-model="quickForm.message"
                    rows="4"
                    required
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Текст письма"
                  ></textarea>
                </div>
              </template>

              <!-- Общие поля -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Получатели (контакты) *</label>
                <select
                  v-model="form.recipient_ids"
                  multiple
                  required
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500 min-h-[120px]"
                >
                  <option v-for="c in contacts" :key="c.id" :value="c.id">
                    {{ c.full_name || c.first_name + ' ' + c.last_name }} — {{ c.email }}
                  </option>
                </select>
                <p class="text-xs text-gray-500 mt-1">Удерживайте Ctrl (Cmd), чтобы выбрать несколько.</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Название рассылки</label>
                <input
                  v-model="form.campaign_name"
                  type="text"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Например: Декабрьская акция"
                />
              </div>

              <div class="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  @click="showCreateCampaign = false"
                  class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  :disabled="submitLoading"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {{ submitLoading ? 'Отправка...' : 'Отправить' }}
                </button>
              </div>
              <p v-if="submitError" class="text-sm text-red-600">{{ submitError }}</p>
            </form>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import marketingService, {
  type Campaign,
  type CampaignStats,
  type MarketingTemplate
} from '../../services/marketingService'
import contactService, { type Contact } from '../../services/contactService'

const showCreateCampaign = ref(false)
const loading = ref(true)
const error = ref('')
const stats = ref<CampaignStats>({
  total_campaigns: 0,
  total_recipients: 0,
  total_sent: 0,
  recent_campaigns: 0,
  recent_recipients: 0,
  recent_sent: 0,
  by_type: { individual: 0, bulk: 0 },
  by_status: { draft: 0, sent: 0, sending: 0, failed: 0 }
})
const campaigns = ref<Campaign[]>([])
const templates = ref<MarketingTemplate[]>([])
const contacts = ref<Contact[]>([])

const campaignMode = ref<'template' | 'quick'>('template')
const form = ref({
  template_id: '' as number | '',
  subject: '',
  content: '',
  recipient_ids: [] as number[],
  campaign_name: ''
})
const quickForm = ref({
  subject: '',
  message: ''
})
const submitLoading = ref(false)
const submitError = ref('')

const deliveryRate = computed(() => {
  const s = stats.value
  if (s.total_recipients === 0) return 0
  return Math.round((s.total_sent / s.total_recipients) * 100)
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [statsRes, campaignsRes, templatesRes, contactsRes] = await Promise.all([
      marketingService.getCampaignStats(),
      marketingService.getCampaigns(),
      marketingService.getTemplates(),
      contactService.getContacts().catch(() => [])
    ])
    stats.value = statsRes
    campaigns.value = campaignsRes
    templates.value = templatesRes
    contacts.value = contactsRes
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || 'Не удалось загрузить данные'
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  campaignMode.value = 'template'
  form.value = { template_id: '', subject: '', content: '', recipient_ids: [], campaign_name: '' }
  quickForm.value = { subject: '', message: '' }
  submitError.value = ''
  showCreateCampaign.value = true
}

function useTemplate(template: MarketingTemplate) {
  form.value.template_id = template.id
  form.value.subject = template.subject || ''
  form.value.content = template.content || ''
  campaignMode.value = 'template'
  form.value.recipient_ids = []
  form.value.campaign_name = ''
  submitError.value = ''
  showCreateCampaign.value = true
}

async function submitCampaign() {
  submitError.value = ''
  const recipientIds = form.value.recipient_ids
  if (!recipientIds.length) {
    submitError.value = 'Выберите хотя бы одного получателя'
    return
  }

  submitLoading.value = true
  try {
    if (campaignMode.value === 'quick') {
      await marketingService.sendQuickMessage({
        message: quickForm.value.message,
        subject: quickForm.value.subject,
        recipient_ids: recipientIds,
        campaign_name: form.value.campaign_name || undefined
      })
    } else {
      const templateId = form.value.template_id
      if (!templateId) {
        submitError.value = 'Выберите шаблон'
        return
      }
      await marketingService.sendCampaign({
        template_id: Number(templateId),
        subject: form.value.subject || undefined,
        content: form.value.content || undefined,
        recipient_ids: recipientIds,
        campaign_name: form.value.campaign_name || undefined
      })
    }
    showCreateCampaign.value = false
    await loadData()
  } catch (e: any) {
    submitError.value = e.response?.data?.error || e.response?.data?.recipient_ids?.[0] || e.message || 'Ошибка отправки'
  } finally {
    submitLoading.value = false
  }
}

onMounted(loadData)
</script>
