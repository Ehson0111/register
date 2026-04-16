<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Emails</h1>
        <p class="text-gray-600 mt-1">Входящие заявки из почты и внутренняя переписка команды</p>
      </div>
      <button
        @click="syncFromMail"
        :disabled="syncing"
        class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
      >
        {{ syncing ? "Синхронизация..." : "Обновить входящие" }}
      </button>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <section class="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <header class="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 class="font-semibold text-gray-900">Входящие (формы)</h2>
          <span class="text-sm text-gray-500">{{ inbox.length }}</span>
        </header>
        <div class="max-h-[65vh] overflow-y-auto">
          <article v-for="email in inbox" :key="email.id" class="px-5 py-4 border-b border-gray-100">
            <p class="font-medium text-gray-900">{{ email.subject || "Без темы" }}</p>
            <p class="text-sm text-gray-500">{{ email.sender_email || "-" }} · {{ formatDate(email.date) }}</p>
            <p class="text-sm text-gray-700 mt-2 whitespace-pre-wrap">{{ (email.text || "").slice(0, 240) }}</p>
          </article>
          <p v-if="!loading && inbox.length === 0" class="px-5 py-8 text-sm text-gray-400 text-center">Писем пока нет</p>
        </div>
      </section>

      <section class="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <header class="px-5 py-4 border-b border-gray-200">
          <h2 class="font-semibold text-gray-900">Внутренние emails</h2>
          <p class="text-sm text-gray-500 mt-1">Локальная внутренняя переписка менеджеров</p>
        </header>

        <div class="p-5 border-b border-gray-100 space-y-3">
          <input
            v-model="draft.subject"
            type="text"
            placeholder="Тема"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
          <textarea
            v-model="draft.body"
            rows="4"
            placeholder="Текст внутреннего email..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg"
          />
          <div class="flex justify-end">
            <button @click="sendInternal" class="px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-black">
              Отправить
            </button>
          </div>
        </div>

        <div class="max-h-[45vh] overflow-y-auto">
          <article v-for="item in internalEmails" :key="item.id" class="px-5 py-4 border-b border-gray-100">
            <p class="font-medium text-gray-900">{{ item.subject }}</p>
            <p class="text-xs text-gray-500">{{ item.author }} · {{ formatDate(item.createdAt) }}</p>
            <p class="text-sm text-gray-700 mt-2 whitespace-pre-wrap">{{ item.body }}</p>
          </article>
          <p v-if="internalEmails.length === 0" class="px-5 py-8 text-sm text-gray-400 text-center">
            Внутренних писем пока нет
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue"
import applicationsService, { type ApplicationItem } from "../../services/applications"
import { useToast } from "../../composables/useToast"
import { useAuthStore } from "../../store/auth"

type InternalEmail = {
  id: string
  subject: string
  body: string
  author: string
  createdAt: string
}

const INTERNAL_EMAILS_KEY = "manager_internal_emails_v1"

const authStore = useAuthStore()
const { showSuccess, showError } = useToast()
const loading = ref(false)
const syncing = ref(false)
const inbox = ref<ApplicationItem[]>([])
const internalEmails = ref<InternalEmail[]>([])

const draft = ref({
  subject: "",
  body: "",
})

const loadInbox = async () => {
  try {
    loading.value = true
    inbox.value = await applicationsService.getApplications()
  } catch (error) {
    console.error("Ошибка загрузки писем", error)
    showError("Не удалось загрузить входящие письма")
  } finally {
    loading.value = false
  }
}

const syncFromMail = async () => {
  try {
    syncing.value = true
    await applicationsService.fetchFromMail()
    await loadInbox()
    showSuccess("Входящие письма обновлены")
  } catch (error) {
    console.error("Ошибка синхронизации", error)
    showError("Не удалось синхронизировать почту")
  } finally {
    syncing.value = false
  }
}

const loadInternal = () => {
  try {
    internalEmails.value = JSON.parse(localStorage.getItem(INTERNAL_EMAILS_KEY) || "[]")
  } catch {
    internalEmails.value = []
  }
}

const persistInternal = () => {
  localStorage.setItem(INTERNAL_EMAILS_KEY, JSON.stringify(internalEmails.value))
}

const sendInternal = () => {
  if (!draft.value.subject.trim() || !draft.value.body.trim()) {
    showError("Заполните тему и текст")
    return
  }
  internalEmails.value = [
    {
      id: `${Date.now()}`,
      subject: draft.value.subject.trim(),
      body: draft.value.body.trim(),
      author: authStore.userName || "manager",
      createdAt: new Date().toISOString(),
    },
    ...internalEmails.value,
  ]
  persistInternal()
  draft.value.subject = ""
  draft.value.body = ""
  showSuccess("Внутренний email отправлен")
}

const formatDate = (date: string) => new Date(date).toLocaleString("ru-RU")

onMounted(async () => {
  loadInternal()
  await loadInbox()
})
</script>
