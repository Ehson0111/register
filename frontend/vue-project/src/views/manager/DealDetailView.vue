<!-- frontend/src/views/manager/DealDetailView.vue -->
<template>


  <div class="space-y-6" v-if="dealdetail">
    <!-- Заголовок и навигация -->
    <div class="flex justify-between items-start">
      <!-- <div -->
      <div>
        <button
          @click="$router.back()"
          class="flex items-center text-gray-500 hover:text-gray-700 mb-4 transition-colors"
        >
          <ArrowLeftIcon class="w-5 h-5 mr-2" />
          Назад к списку сделок
        </button>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ dealdetail?.title }}
        </h1>
        <p class="text-gray-600 text-lg">{{ dealdetail?.description }}</p>
      </div>

      <div class="flex space-x-3">
        <button
          v-if="canIssueInvoice"
          @click="issueInvoice"
          :disabled="invoiceLoading || issuingInvoice || !!invoice"
          class="px-6 py-3 bg-violet-600 text-white rounded-lg hover:bg-violet-700 flex items-center transition-colors disabled:opacity-60"
        >
          <DocumentTextIcon class="w-5 h-5 mr-2" />
          <span>{{ issuingInvoice ? 'Выставление...' : invoice ? 'Счет выставлен' : 'Выставить счет' }}</span>
        </button>
        <!-- показываем если сделка не закрытаа-->
        <button
          v-if="!dealdetail?.is_closed"
          @click="changeDealStatus('won')"
          class="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center transition-colors"
        >
          <CheckIcon class="w-5 h-5" />
          <span>Выиграть сделку</span>
        </button>

        <button
          v-if="!dealdetail?.is_closed"
          @click="changeDealStatus('lost')"
          class="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2 transition-colors"
        >
          <XMarkIcon class="w-5 h-5" />
          <span>Проиграть сделку</span>
        </button>

        <button
          @click.stop="editDeal(dealdetail)"
          class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2 transition-colors"
        >
          <PencilIcon class="w-5 h-5" />
          <span>Редактировать</span>
        </button>
      </div>
    </div>

    <!-- Основная информация lg:grid-cols-3 - на больших экранах (≥1024px): 3 колонки-->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Левая колонка - детали сделки -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Карточка основной информации -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">
            Основная информация
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block font-medium text-gray-500 mb-1"
                  >Контакт</label
                >
                <div class="flex items-center space-x-3">
                  <div
                    class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center"
                  >
                    <span class="text-blue-600 font-medium text-sm">
                      {{ getInitials(dealdetail?.contact_name || "") }}
                    </span>
                  </div>

                  <span class="text-lg font-medium text-gray-900">{{
                    dealdetail?.contact_name
                  }}</span>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-500 mb-1"
                  >Услуга</label
                >
                <p class="text-lg text-gray-900">
                  {{ dealdetail?.service_name }}
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-500 mb-1"
                  >Статус</label
                >
                <span
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                  :class="getStatusClass(dealdetail?.status || '')"
                >
                  {{ dealdetail?.status_display }}
                </span>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-500 mb-1"
                  >Сумма сделки</label
                >
                <p class="text-2xl font-bold text-gray-900">
                  {{ formatCurrency(parseFloat(dealdetail?.amount || "0")) }}
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-500 mb-1"
                  >Вероятность успеха</label
                >
                <div class="flex items-center space-x-3">
                  <div class="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      class="h-3 rounded-full transition-all duration-500"
                      :class="getProbabilityColor(dealdetail?.probability || 0)"
                      :style="{ width: `${dealdetail?.probability || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-lg font-medium text-gray-900 min-w-12">
                    {{ dealdetail?.probability }}%
                  </span>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-500 mb-1"
                  >Дней в работе</label
                >
                <p class="text-lg text-gray-900">
                  {{ dealdetail?.days_open }} дней
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Даты и временные метки -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-6">
            Временная шкала
          </h2>

          <div class="space-y-10">
            <div
              class="flex justify-between items-center py-3 border-b border-gray-100"
            >
              <span class="text-gray-600">Дата создания</span>
              <span class="font-medium text-gray-900">{{
                formatDate(dealdetail?.created_at || "")
              }}</span>
            </div>

            <div
              class="flex justify-between items-center py-3 border-b border-gray-100"
            >
              <span class="text-gray-600">Последнее обновление</span>
              <span class="font-medium text-gray-900">{{
                formatDate(dealdetail?.updated_at || "")
              }}</span>
            </div>
            <div
              v-if="dealdetail?.expected_close_date"
              class="flex justify-between items-center py-3 border-b border-gray-100"
            >
              <span class="text-gray-600">Ожидаемая дата закрытия</span>
              <span class="font-medium text-gray-900">{{
                formatDate(dealdetail.expected_close_date)
              }}</span>
            </div>
            <div
              v-if="dealdetail?.actual_close_date"
              class="flex justify-between items-center py-3"
            >
              <span class="text-gray-600">Фактическая дата закрытия</span>
              <span class="font-medium text-gray-900">{{
                formatDate(dealdetail.actual_close_date)
              }}</span>
            </div>
          </div>
        </div>

        <!-- Описание -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">
            Описание сделки
          </h2>
          <p
            class="text-gray-700 leading-relaxed"
            v-if="dealdetail?.description"
          >
            {{ dealdetail.description }}
          </p>
          <p class="text-gray-500 italic" v-else>Описание отсутствует</p>
        </div>

        <!-- История изменений -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-semibold text-gray-900 mb-4">История изменений</h2>
          <div v-if="auditLoading" class="text-sm text-gray-500">Загрузка истории...</div>
          <div v-else-if="auditTrail.length === 0" class="text-sm text-gray-500">
            По этой сделке пока нет записей в истории.
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
 

      <!-- Правая колонка - действия и статистика -->
      <div class="space-y-6">
        <!-- Статус сделки -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            Статус сделки
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Текущий статус:</span>
              <span
                class="font-medium"
                :class="getStatusTextColor(dealdetail?.status || '')"
              >
                {{ dealdetail?.status_display }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Состояние:</span>
              <span
                class="font-medium"
                :class="
                  dealdetail?.is_closed ? 'text-red-600' : 'text-green-600'
                "
              >
                {{ dealdetail?.is_closed ? "Закрыта" : "Активна" }}
              </span>
            </div>
          </div>
        </div>

        <!-- Быстрые действия -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            Быстрые действия
          </h3>
          <div class="space-y-2">
            <button
              v-if="canIssueInvoice"
              @click="issueInvoice"
              :disabled="invoiceLoading || issuingInvoice || !!invoice"
              class="w-full flex items-center space-x-3 px-4 py-3 text-violet-700 bg-violet-50 hover:bg-violet-100 rounded-lg transition-colors disabled:opacity-60"
            >
              <DocumentTextIcon class="w-5 h-5" />
              <span>{{ issuingInvoice ? "Выставление счета..." : invoice ? "Счет уже создан" : "Выставить счет" }}</span>
            </button>
            <button
              v-if="!dealdetail?.is_closed"
              @click="changeDealStatus('won')"
              class="w-full flex items-center space-x-3 px-4 py-3 text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
            >
              <CheckCircleIcon class="w-5 h-5" />
              <span>Отметить как выигранную</span>
            </button>
            <button
              v-if="!dealdetail?.is_closed"
              @click="changeDealStatus('lost')"
              class="w-full flex items-center space-x-3 px-4 py-3 text-red-700 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
            >
              <XCircleIcon class="w-5 h-5" />
              <span>Отметить как проигранную</span>
            </button>
            <button
              @click="editDeal(dealdetail)"
              class="w-full flex items-center space-x-3 px-4 py-3 text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
            >
              <PencilSquareIcon class="w-5 h-5" />
              <span>Редактировать сделку</span>
            </button>
            <button
              @click="openMarketingForDeal"
              class="w-full flex items-center space-x-3 px-4 py-3 text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
            >
              <DocumentTextIcon class="w-5 h-5" />
              <span>Создать коммерческое предложение</span>
            </button>
            <button
              @click="openMarketingForDeal"
              class="w-full flex items-center space-x-3 px-4 py-3 text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <EnvelopeIcon class="w-5 h-5" />
              <span>Отправить email</span>
            </button>
          </div>
        </div>

        <div v-if="dealdetail?.status === 'won'" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            Счет и оплата
          </h3>
          <div v-if="invoiceLoading" class="text-sm text-gray-500">Загрузка счета...</div>
          <div v-else-if="!invoice" class="space-y-3">
            <p class="text-sm text-gray-600">По этой успешно закрытой сделке счет еще не выставлен.</p>
            <button
              @click="issueInvoice"
              :disabled="issuingInvoice"
              class="w-full px-4 py-3 bg-violet-600 text-white rounded-lg hover:bg-violet-700 transition-colors disabled:opacity-60"
            >
              {{ issuingInvoice ? "Выставление..." : "Выставить счет в 1С" }}
            </button>
          </div>
          <div v-else class="space-y-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-500">Номер счета</p>
                <p class="font-semibold text-gray-900">{{ invoice.onec_invoice_number || invoice.invoice_number }}</p>
              </div>
              <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium" :class="invoiceStatusClass(invoice.status)">
                {{ invoiceStatusText(invoice.status) }}
              </span>
            </div>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-600">Сумма</span>
                <span class="text-gray-900 font-medium">{{ formatCurrency(Number(invoice.amount || 0)) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Контрагент 1С</span>
                <span class="text-gray-900 font-medium">{{ invoice.onec_document_id || "Ожидает номер из 1С" }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Синхронизация 1С</span>
                <span class="font-medium" :class="syncStatusTextClass(invoice.onec_sync_status)">
                  {{ syncStatusText(invoice.onec_sync_status) }}
                </span>
              </div>
              <div v-if="invoice.onec_payment_document_id" class="flex justify-between">
                <span class="text-gray-600">Документ оплаты 1С</span>
                <span class="text-gray-900 font-medium">{{ invoice.onec_payment_document_id }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Отправка ссылки клиенту</span>
                <span class="font-medium" :class="syncStatusTextClass(invoice.crm_sync_status)">
                  {{ syncStatusText(invoice.crm_sync_status) }}
                </span>
              </div>
            </div>

            <div v-if="invoice.payment_url" class="space-y-2">
              <p class="text-sm text-gray-500 break-all">{{ invoice.payment_url }}</p>
              <a
                :href="invoice.payment_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center justify-center w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Открыть ссылку на оплату
              </a>
            </div>

            <button
              v-if="invoice.onec_sync_status === 'error'"
              @click="retryInvoiceSync"
              :disabled="retryingInvoice"
              class="w-full px-4 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors disabled:opacity-60"
            >
              {{ retryingInvoice ? "Повтор..." : "Повторить синхронизацию с 1С" }}
            </button>

            <p v-if="invoice.last_onec_error" class="text-xs text-red-600">
              Ошибка 1С: {{ invoice.last_onec_error }}
            </p>
            <p v-if="invoice.next_retry_at" class="text-xs text-amber-600">
              Следующая автопопытка: {{ formatDateTime(invoice.next_retry_at) }}
            </p>
            <p v-if="invoice.last_crm_error" class="text-xs text-red-600">
              Ошибка CRM: {{ invoice.last_crm_error }}
            </p>
          </div>
        </div>

        <!-- Прогресс сделки -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">
            Прогресс сделки
          </h3>
          <div class="space-y-4">
            <div
              v-for="stage in dealStages"
              :key="stage.status"
              class="flex items-center space-x-3"
            >
              <div
                class="w-3 h-3 rounded-full border-2"
                :class="getStageDotClass(stage.status)"
              ></div>
              <span class="text-sm" :class="getStageTextClass(stage.status)">
                {{ stage.label }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="text-center py-12">
      <div
        class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"
      ></div>
      <p class="text-gray-500 mt-4 text-lg">Загрузка данных сделки...</p>
    </div>

    <!-- Ошибка -->
    <div v-if="!loading && !dealdetail" class="text-center py-12">
      <ExclamationTriangleIcon class="w-16 h-16 text-red-400 mx-auto mb-4" />
      <h3 class="text-xl font-semibold text-gray-900 mb-2">
        Сделка не найдена
      </h3>
      <p class="text-gray-500 mb-6">
        Запрошенная сделка не существует или была удалена
      </p>
      <button
        @click="$router.back()"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Вернуться назад
      </button>
    </div>
  
  
  <DealFormModal
      :show="showCreateModal"
      :deal="editingDeal"
      @close="closeModal"
      @saved="handleDealSaved"
    />

  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useToast } from "../../composables/useToast";
import dealService from "../../services/dealService";
import contactService, { type AuditTrailItem } from "../../services/contactService";
import paymentService, { type DealInvoice } from "../../services/paymentService";

import DealFormModal from './components/DealFormModal.vue'

import {
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon,
  PencilIcon,
  CheckCircleIcon,
  XCircleIcon,
  PencilSquareIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  ExclamationTriangleIcon,
} from "@heroicons/vue/24/outline";


const editingDeal = ref<any | null>(null)
const showCreateModal=ref(false)


const route = useRoute();
const router = useRouter();
const { showSuccess, showError } = useToast();
const deals = ref<any[]>([])

const dealdetail = ref<any | null>(null);
const loading = ref(true);
const invoice = ref<DealInvoice | null>(null)
const invoiceLoading = ref(false)
const issuingInvoice = ref(false)
const retryingInvoice = ref(false)
const auditTrail = ref<AuditTrailItem[]>([]);
const auditLoading = ref(false);
const closeModal = () => {
  showCreateModal.value = false
  editingDeal.value = null
}

const handleDealSaved = () => {
  closeModal()
  loadDeals()
}
const searchQuery = ref('')
const statusFilter = ref('')
const serviceFilter = ref('')

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

    loadDeal()

  } catch (error) {
    console.error('Ошибка загрузки сделок:', error)
    showError('Не удалось загрузить сделки')
  } finally {
    loading.value = false
  }
}
// Ини
// Стадии сделки
const dealStages = [
  { status: "new", label: "Новая заявка" },
  { status: "in_progress", label: "В работе" },
  { status: "won", label: "Успешно закрыта" },
  { status: "lost", label: "Закрыта неудачно" },
];

// Вспомогательные функции
//фио Пример: "John Doe" → "JD", "Мария Иванова" → "МИ"


const getInitials = (fullName: string) => {
  if (!fullName) return "??";
  return fullName
    .split(" ")
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase()
    .slice(0, 2);
};

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    new: "bg-blue-100 text-blue-800",
    in_progress: "bg-orange-100 text-orange-800",
    won: "bg-green-100 text-green-800",
    lost: "bg-red-100 text-red-800",
    on_hold: "bg-slate-300 text-slate-900",
  };
  return classes[status] || "bg-slate-300 text-slate-900";
};

const getStatusTextColor = (status: string) => {
  const colors: Record<string, string> = {
    new: "text-blue-600",
    in_progress: "text-orange-600",
    won: "text-green-600",
    lost: "text-red-600",
    on_hold: "text-slate-200",
  };
  return colors[status] || "text-slate-200";
};

const invoiceStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: "Черновик",
    waiting: "Ожидает оплаты",
    paid: "Оплачен",
    cancelled: "Отменен",
  }
  return texts[status] || status
}

const invoiceStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    draft: "bg-slate-100 text-slate-700",
    waiting: "bg-blue-100 text-blue-800",
    paid: "bg-green-100 text-green-800",
    cancelled: "bg-red-100 text-red-800",
  }
  return classes[status] || "bg-slate-100 text-slate-700"
}

const syncStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: "В процессе",
    synced: "Готово",
    error: "Ошибка",
  }
  return texts[status] || status
}

const syncStatusTextClass = (status: string) => {
  const classes: Record<string, string> = {
    pending: "text-amber-600",
    synced: "text-green-600",
    error: "text-red-600",
  }
  return classes[status] || "text-gray-600"
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 80) return "bg-green-500";
  if (probability >= 50) return "bg-yellow-500";
  return "bg-red-500";
};

const getStageDotClass = (stageStatus: string) => {
  const currentStatus = dealdetail.value?.status;
  const statusOrder = ["new", "in_progress", "won", "lost"];

  const currentIndex = statusOrder.indexOf(currentStatus || "");
  const stageIndex = statusOrder.indexOf(stageStatus);

  if (stageIndex < currentIndex) {
    return "bg-green-500 border-green-500"; // Пройдено
  } else if (stageIndex === currentIndex) {
    return "bg-blue-500 border-blue-500"; // Текущее
  } else {
    return "bg-gray-300 border-gray-300"; // Будущее
  }
};

const getStageTextClass = (stageStatus: string) => {
  const currentStatus = dealdetail.value?.status;
  const statusOrder = ["new", "in_progress", "won", "lost"];

  const currentIndex = statusOrder.indexOf(currentStatus || "");
  const stageIndex = statusOrder.indexOf(stageStatus);

  if (stageIndex < currentIndex) {
    return "text-green-600 font-medium"; // Пройдено
  } else if (stageIndex === currentIndex) {
    return "text-blue-600 font-bold"; // Текущее
  } else {
    return "text-gray-500"; // Будущее
  }
};

const formatCurrency = (amount: number) => {  
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    minimumFractionDigits: 0,
  }).format(amount);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString("ru-RU");
};

const canIssueInvoice = computed(() => dealdetail.value?.status === "won")

const auditActionText = (action: string) => {
  const map: Record<string, string> = {
    deal_created: "Сделка создана",
    deal_status_changed: "Изменен статус сделки",
    contact_updated: "Изменен связанный контакт",
  };
  return map[action] || action;
};

// Действия со сделкой
const changeDealStatus = async (status: "won" | "lost") => {
  
  if (!dealdetail.value) return;

  const statusNames = {
    won: "выиграна",
    lost: "проиграна",
  };

  if (
    !confirm(
      `Вы уверены, что хотите отметить сделку "${dealdetail.value.title}" как ${statusNames[status]}?`
    )
  ) {
    return;
  }

  try {
    await dealService.changeDealStatus(dealdetail.value.id, status);
    showSuccess(`Сделка успешно отмечена как ${statusNames[status]}`);
    // Перезагружаем данные
    loadDeal();
    loadAuditTrail(dealdetail.value.id);
  } catch (error) {
    console.error("Ошибка изменения статуса:", error);
    showError("Не удалось изменить статус сделки");
  }
};

const loadAuditTrail = async (dealId: number) => {
  try {
    auditLoading.value = true;
    // #region agent log
    fetch("http://127.0.0.1:7647/ingest/66103dc7-eaf0-4803-be05-aba9d5dec07c", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "ad25e9" },
      body: JSON.stringify({
        sessionId: "ad25e9",
        runId: "run3",
        hypothesisId: "H14",
        location: "DealDetailView.vue:loadAuditTrail",
        message: "loading deal audit trail",
        data: { dealId },
        timestamp: Date.now(),
      }),
    }).catch(() => {});
    // #endregion
    auditTrail.value = await contactService.getAuditTrail({
      entity_type: "deal",
      entity_id: dealId,
    });
  } catch (error) {
    console.error("Ошибка загрузки истории сделки:", error);
  } finally {
    auditLoading.value = false;
  }
};

const editDeal = (deal: any | null) => {
  if (!deal) return
  editingDeal.value = deal
  showCreateModal.value = true
};

const loadInvoice = async (dealId: number) => {
  try {
    invoiceLoading.value = true
    invoice.value = await paymentService.getDealInvoice(dealId)
  } catch (error) {
    console.error("Ошибка загрузки счета:", error)
  } finally {
    invoiceLoading.value = false
  }
}

const issueInvoice = async () => {
  if (!dealdetail.value) return
  try {
    issuingInvoice.value = true
    invoice.value = await paymentService.createInvoiceFromDeal(dealdetail.value.id)
    if (invoice.value.crm_sync_status === "error") {
      showSuccess("Счет создан и зарегистрирован в 1С, но отправка ссылки клиенту требует проверки")
    } else {
      showSuccess("Счет успешно выставлен, ссылка на оплату отправлена клиенту")
    }
  } catch (error: any) {
    console.error("Ошибка выставления счета:", error)
    const message = error?.response?.data?.detail || "Не удалось выставить счет"
    showError(message)
    if (error?.response?.data?.invoice) {
      invoice.value = error.response.data.invoice
    }
  } finally {
    issuingInvoice.value = false
  }
}

const retryInvoiceSync = async () => {
  if (!invoice.value) return
  try {
    retryingInvoice.value = true
    invoice.value = await paymentService.retryInvoiceSync(invoice.value.id)
    showSuccess("Синхронизация счета с 1С повторена")
  } catch (error: any) {
    console.error("Ошибка повторной синхронизации:", error)
    showError(error?.response?.data?.detail || "Не удалось повторить синхронизацию")
    if (error?.response?.data?.invoice) {
      invoice.value = error.response.data.invoice
    }
  } finally {
    retryingInvoice.value = false
  }
}

const openMarketingForDeal = () => {
  if (!dealdetail.value) return
  router.push({
    name: 'ManagerMarketing',
    query: { recipientId: String(dealdetail.value.contact) }
  })
};

// Загрузка данных
const loadDeal = async () => {
  try {
    loading.value = true;
    const dealId = parseInt(route.params.id as string);
    console.log("Загрузка сделки ID:", dealId);
    dealdetail.value = await dealService.getDeal(dealId);
    console.log("Загруженная сделка:", dealdetail.value);
    await loadAuditTrail(dealId);
    await loadInvoice(dealId);
  } catch (error) {
    console.error("Ошибка загрузки сделки:", error);
    showError("Не удалось загрузить данные сделки");
  } finally {
    loading.value = false;
  }
};

// Инициализация
onMounted(() => {
  loadDeals();
  loadDeal();
});
</script>

<style scoped>
/* Дополнительные стили для плавных анимаций */
.transition-colors {
  transition: all 0.2s ease-in-out;
}

/* Стили для прогресс-бара */
.progress-bar {
  transition: width 0.5s ease-in-out;
}
</style>