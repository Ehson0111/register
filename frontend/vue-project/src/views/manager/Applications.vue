<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Заявки</h1>
        <p class="text-gray-600 mt-1">
          Заявки с Яндекс Форм. Одобрение создаёт контакт и новую сделку.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <a
          href="https://forms.yandex.ru/u/69aeaa09eb6146cd4fd99c6b"
          target="_blank"
          rel="noopener noreferrer"
          class="px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
        >
          Открыть форму
        </a>
        <button
          @click="syncFromMail"
          class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
          :disabled="syncing"
        >
          {{ syncing ? "Синхронизация..." : "Забрать из почты" }}
        </button>
      </div>
    </div>

    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <input
          v-model="searchQuery"
          type="text"
          class="px-3 py-2 border border-gray-300 rounded-lg"
          placeholder="Поиск по теме/описанию..."
          @input="loadApplications"
        />
        <select
          v-model="statusFilter"
          class="px-3 py-2 border border-gray-300 rounded-lg"
          @change="applyFilters"
        >
          <option value="all">Все</option>
          <option value="new">Новые</option>
          <option value="approved">Одобрены</option>
          <option value="rejected">Отклонены</option>
          <option value="processed">Обработаны</option>
        </select>
        <button
          @click="loadApplications"
          class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
          :disabled="loading"
        >
          Обновить
        </button>
      </div>
    </div>

    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h3 class="text-lg font-medium text-gray-900">
          Список заявок ({{ filteredApplications.length }})
        </h3>
      </div>

      <div v-if="loading" class="p-8 text-center text-gray-500">Загрузка заявок...</div>

      <div v-else-if="filteredApplications.length === 0" class="p-8 text-center text-gray-500">
        Заявки не найдены
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs text-gray-500 uppercase">Заявка</th>
              <th class="px-6 py-3 text-left text-xs text-gray-500 uppercase">Контакт</th>
              <th class="px-6 py-3 text-left text-xs text-gray-500 uppercase">Услуга</th>
              <th class="px-6 py-3 text-left text-xs text-gray-500 uppercase">Сумма</th>
              <th class="px-6 py-3 text-left text-xs text-gray-500 uppercase">Статус</th>
              <th class="px-6 py-3 text-right text-xs text-gray-500 uppercase">Действия</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="item in filteredApplications" :key="item.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ item.subject || "Без темы" }}</div>
                <div class="text-xs text-gray-500">{{ formatDate(item.date) }}</div>
                <div class="text-xs text-gray-500 mt-1 line-clamp-2">
                  {{ item.text || "Текст отсутствует" }}
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-700">
                <div>{{ parseApplication(item).email || "-" }}</div>
                <div class="text-xs text-gray-500">{{ parseApplication(item).phone || "-" }}</div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-700">
                {{ parseApplication(item).serviceName || "-" }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-700">
                {{ parseApplication(item).amount ? formatCurrency(parseApplication(item).amount) : "-" }}
              </td>
              <td class="px-6 py-4">
                <span class="inline-flex px-2 py-1 rounded-full text-xs font-medium" :class="statusClass(item)">
                  {{ statusText(item) }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="inline-flex gap-2">
                  <button
                    @click="openApprove(item)"
                    class="px-3 py-1.5 text-xs rounded bg-green-600 text-white hover:bg-green-700 disabled:opacity-50"
                    :disabled="isLocked(item)"
                  >
                    Одобрить
                  </button>
                  <button
                    @click="reject(item)"
                    class="px-3 py-1.5 text-xs rounded bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
                    :disabled="isLocked(item)"
                  >
                    Отклонить
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="approvalDraft" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 space-y-4">
        <h3 class="text-lg font-semibold text-gray-900">Одобрение заявки #{{ approvalDraft.id }}</h3>
        <p class="text-sm text-gray-500">
          Перед подтверждением можно подправить данные, которые пойдут в контакт и сделку.
        </p>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input v-model="approvalDraft.firstName" type="text" placeholder="Имя" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="approvalDraft.lastName" type="text" placeholder="Фамилия" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="approvalDraft.email" type="email" placeholder="Email" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="approvalDraft.phone" type="text" placeholder="Телефон" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="approvalDraft.serviceName" type="text" placeholder="Услуга" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model.number="approvalDraft.amount" type="number" placeholder="Сумма" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="approvalDraft.expectedCloseDate" type="date" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="approvalDraft.title" type="text" placeholder="Название сделки" class="px-3 py-2 border border-gray-300 rounded-lg" />
        </div>
        <textarea
          v-model="approvalDraft.description"
          rows="4"
          placeholder="Описание"
          class="w-full px-3 py-2 border border-gray-300 rounded-lg"
        />
        <div class="flex justify-end gap-2">
          <button @click="approvalDraft = null" class="px-4 py-2 rounded-lg border border-gray-300">Отмена</button>
          <button
            @click="confirmApprove"
            :disabled="approving"
            class="px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-60"
          >
            {{ approving ? "Создаю..." : "Подтвердить одобрение" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useToast } from "../../composables/useToast";
import applicationsService, { type ApplicationItem } from "../../services/applications";
import contactService from "../../services/contactService";
import serviceService from "../../services/serviceService";
import { useAuthStore } from "../../store/auth";

type Decision = "approved" | "rejected";
type Draft = {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  serviceName: string;
  amount: number;
  expectedCloseDate: string;
  title: string;
  description: string;
};

const { showSuccess, showError, showWarning } = useToast();
const authStore = useAuthStore();
const loading = ref(false);
const syncing = ref(false);
const approving = ref(false);
const allApplications = ref<ApplicationItem[]>([]);
const searchQuery = ref("");
const statusFilter = ref("all");
const approvalDraft = ref<Draft | null>(null);
const decisionMap = ref<Record<number, Decision>>({});

const DECISIONS_KEY = "application_decisions_v1";

const debugLog = (hypothesisId: string, location: string, message: string, data: Record<string, unknown>) => {
  // #region agent log
  fetch("http://127.0.0.1:7647/ingest/66103dc7-eaf0-4803-be05-aba9d5dec07c", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "ad25e9" },
    body: JSON.stringify({
      sessionId: "ad25e9",
      runId: "run2",
      hypothesisId,
      location,
      message,
      data,
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion
};

const parseApplication = (item: ApplicationItem) => {
  const text = item.text || "";
  const read = (label: string) => {
    const m = text.match(new RegExp(`${label}:\\s*(.+)`, "i"));
    return m?.[1]?.trim() || "";
  };
  const subjectDeal = item.subject.replace(/^Новая заявка:\s*/i, "").trim();
  return {
    phone: read("Контакт"),
    serviceName: read("Услуга"),
    amount: Number((read("Сумма сделки") || "0").replace(/[^\d.]/g, "")) || 0,
    email: read("Почта"),
    expectedCloseDate: read("Ожидаемая дата закрытия"),
    description: (() => {
      const m = text.match(/Описание:\s*([\s\S]*)/i);
      if (!m) return "";
      return (m[1] || "").split("Это письмо содержит ответы")[0].trim();
    })(),
    title: read("Название сделки") || subjectDeal || "Заявка с сайта",
  };
};

const loadDecisions = () => {
  try {
    decisionMap.value = JSON.parse(localStorage.getItem(DECISIONS_KEY) || "{}");
  } catch {
    decisionMap.value = {};
  }
};

const saveDecisions = () => {
  localStorage.setItem(DECISIONS_KEY, JSON.stringify(decisionMap.value));
};

const isLocked = (item: ApplicationItem) => {
  return item.is_processed || !!decisionMap.value[item.id];
};

const statusText = (item: ApplicationItem) => {
  const decision = decisionMap.value[item.id];
  if (decision === "approved") return "Одобрена";
  if (decision === "rejected") return "Отклонена";
  if (item.is_processed) return "Обработана";
  return "Новая";
};

const statusClass = (item: ApplicationItem) => {
  const decision = decisionMap.value[item.id];
  if (decision === "approved") return "bg-green-100 text-green-700";
  if (decision === "rejected") return "bg-red-100 text-red-700";
  if (item.is_processed) return "bg-gray-100 text-gray-700";
  return "bg-blue-100 text-blue-700";
};

const filteredApplications = computed(() => {
  let list = allApplications.value;
  const query = searchQuery.value.trim().toLowerCase();
  if (query) {
    list = list.filter((a) =>
      `${a.subject} ${a.text}`.toLowerCase().includes(query)
    );
  }
  if (statusFilter.value === "new") return list.filter((a) => !isLocked(a));
  if (statusFilter.value === "approved") return list.filter((a) => decisionMap.value[a.id] === "approved");
  if (statusFilter.value === "rejected") return list.filter((a) => decisionMap.value[a.id] === "rejected");
  if (statusFilter.value === "processed") return list.filter((a) => a.is_processed);
  return list;
});

const loadApplications = async () => {
  try {
    loading.value = true;
    const params = searchQuery.value ? { search: searchQuery.value } : undefined;
    debugLog("H6", "Applications.vue:loadApplications", "load start", {
      search: searchQuery.value,
      statusFilter: statusFilter.value,
    });
    allApplications.value = await applicationsService.getApplications(params);
    debugLog("H6", "Applications.vue:loadApplications", "load success", {
      loaded: allApplications.value.length,
      filtered: filteredApplications.value.length,
    });
  } catch (error) {
    console.error("Ошибка загрузки заявок", error);
    debugLog("H7", "Applications.vue:loadApplications", "load error", {
      errorName: (error as any)?.name || "unknown",
      errorMessage: (error as any)?.message || "unknown",
      responseStatus: (error as any)?.response?.status ?? null,
    });
    showError("Не удалось загрузить заявки");
  } finally {
    loading.value = false;
  }
};

const applyFilters = () => {
  // filtering is reactive via computed
};

const syncFromMail = async () => {
  try {
    syncing.value = true;
    const result = await applicationsService.fetchFromMail();
    showSuccess(`Синхронизация завершена: новых ${result.new}, дубликатов ${result.duplicates}`);
    await loadApplications();
  } catch (error) {
    console.error("Ошибка синхронизации", error);
    showError("Не удалось получить письма из почты");
  } finally {
    syncing.value = false;
  }
};

const openApprove = (item: ApplicationItem) => {
  const parsed = parseApplication(item);
  const email = parsed.email || `lead-${item.id}@example.com`;
  approvalDraft.value = {
    id: item.id,
    firstName: "Новый",
    lastName: "Клиент",
    email,
    phone: parsed.phone || "",
    serviceName: parsed.serviceName || "",
    amount: parsed.amount || 0,
    expectedCloseDate: parsed.expectedCloseDate || "",
    title: parsed.title || "Заявка с сайта",
    description: parsed.description || item.text || "",
  };
};

const ensureContactId = async (draft: Draft): Promise<number> => {
  try {
    debugLog("H8", "Applications.vue:ensureContactId", "createContact start", {
      hasEmail: !!draft.email,
      hasPhone: !!draft.phone,
    });
    const created = await contactService.createContact({
      first_name: draft.firstName || "Новый",
      last_name: draft.lastName || "Клиент",
      email: draft.email,
      phone: draft.phone || "",
      company: "",
      status: "lead",
      position: "",
      address: "",
      notes: "Создано из заявки",
    });
    debugLog("H8", "Applications.vue:ensureContactId", "createContact success", {
      contactId: created?.contact?.id ?? null,
    });
    return created.contact.id;
  } catch (error) {
    debugLog("H8", "Applications.vue:ensureContactId", "createContact failed, searching existing", {
      status: (error as any)?.response?.status ?? null,
      message: (error as any)?.message || "unknown",
    });
    const contacts = await contactService.getContacts({ search: draft.email });
    const existing = contacts.find((c) => c.email?.toLowerCase() === draft.email.toLowerCase());
    debugLog("H8", "Applications.vue:ensureContactId", "search existing contact result", {
      found: !!existing,
      contactId: existing?.id ?? null,
    });
    if (!existing) throw error;
    return existing.id;
  }
};

const resolveServiceId = async (serviceName: string): Promise<number> => {
  debugLog("H9", "Applications.vue:resolveServiceId", "load services for resolve", {
    requestedService: serviceName || "",
  });
  const services = await serviceService.getServicesForSelect();
  if (!services.length) {
    debugLog("H9", "Applications.vue:resolveServiceId", "no services available", {});
    throw new Error("Нет доступных услуг для создания сделки");
  }
  const byName = services.find((s: any) => (s.name || "").toLowerCase() === serviceName.toLowerCase());
  debugLog("H9", "Applications.vue:resolveServiceId", "service resolved", {
    total: services.length,
    matchedByName: !!byName,
    selectedId: byName?.id || services[0].id,
  });
  return byName?.id || services[0].id;
};

const confirmApprove = async () => {
  if (!approvalDraft.value) return;
  const draft = approvalDraft.value;
  if (!draft.email) {
    showWarning("Укажи email клиента перед одобрением");
    return;
  }
  try {
    approving.value = true;
    debugLog("H10", "Applications.vue:confirmApprove", "approve flow start", {
      appId: draft.id,
      hasEmail: !!draft.email,
      amount: draft.amount,
    });
    const contactId = await ensureContactId(draft);
    const serviceId = await resolveServiceId(draft.serviceName);

    debugLog("H10", "Applications.vue:confirmApprove", "createDeal start", {
      contactId,
      serviceId,
      expectedCloseDate: draft.expectedCloseDate || null,
    });
    await contactService.createDeal({
      title: draft.title || "Новая заявка",
      description: draft.description || "",
      contact: contactId,
      service: serviceId,
      amount: draft.amount > 0 ? draft.amount : 1,
      probability: 10,
      status: "new",
      expected_close_date: draft.expectedCloseDate || undefined,
    });
    debugLog("H10", "Applications.vue:confirmApprove", "createDeal success", {});

    debugLog("H11", "Applications.vue:confirmApprove", "markProcessed start", {
      appId: draft.id,
    });
    await applicationsService.markProcessed(draft.id, true, {
      actor: authStore.userName || "manager",
      action: "approved",
    });
    debugLog("H11", "Applications.vue:confirmApprove", "markProcessed success", {
      appId: draft.id,
    });
    decisionMap.value[draft.id] = "approved";
    saveDecisions();
    approvalDraft.value = null;
    await loadApplications();
    showSuccess("Заявка одобрена: контакт и сделка созданы");
  } catch (error) {
    console.error("Ошибка одобрения заявки", error);
    debugLog("H12", "Applications.vue:confirmApprove", "approve flow failed", {
      status: (error as any)?.response?.status ?? null,
      message: (error as any)?.message || "unknown",
      data: (error as any)?.response?.data || null,
    });
    showError("Не удалось одобрить заявку");
  } finally {
    approving.value = false;
  }
};

const reject = async (item: ApplicationItem) => {
  if (!confirm("Отклонить заявку?")) return;
  try {
    await applicationsService.markProcessed(item.id, true, {
      actor: authStore.userName || "manager",
      action: "rejected",
    });
    decisionMap.value[item.id] = "rejected";
    saveDecisions();
    await loadApplications();
    showSuccess("Заявка отклонена");
  } catch (error) {
    console.error("Ошибка отклонения заявки", error);
    showError("Не удалось отклонить заявку");
  }
};

const formatDate = (date: string) => new Date(date).toLocaleString("ru-RU");
const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(amount);

onMounted(async () => {
  loadDecisions();
  await loadApplications();
});
</script>