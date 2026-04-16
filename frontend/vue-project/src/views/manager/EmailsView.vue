<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Почта</h1>
        <p class="text-gray-600 mt-1">Полноценная почта: просмотр всех писем, папки и отправка сообщений</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="showCompose = true"
          class="px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-black"
        >
          Написать
        </button>
        <button
          @click="syncMailbox"
          :disabled="syncing"
          class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {{ syncing ? "Синхронизация..." : "Синхронизировать" }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-[240px_minmax(320px,420px)_1fr] gap-6">
      <aside class="bg-white border border-gray-200 rounded-xl p-4 space-y-2">
        <button
          v-for="folder in folders"
          :key="folder.id"
          @click="selectFolder(folder.id)"
          class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-left transition-colors"
          :class="activeFolder === folder.id ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-50 text-gray-700'"
        >
          <span>{{ folder.label }}</span>
          <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">
            {{ folder.count }}
          </span>
        </button>
      </aside>

      <section class="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div class="p-4 border-b border-gray-200">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по теме, отправителю, тексту..."
            class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            @input="loadMessages"
          />
        </div>

        <div class="max-h-[70vh] overflow-y-auto">
          <button
            v-for="message in messages"
            :key="message.id"
            @click="openMessage(message.id)"
            class="w-full text-left px-4 py-4 border-b border-gray-100 hover:bg-gray-50"
            :class="{ 'bg-blue-50': selectedMessage?.id === message.id }"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="font-medium text-gray-900 truncate">
                  {{ message.subject || "Без темы" }}
                </p>
                <p class="text-sm text-gray-500 truncate">
                  {{ message.sender_email || message.recipients || "-" }}
                </p>
                <p class="text-sm text-gray-700 mt-1 line-clamp-2">
                  {{ message.preview || "Без текста" }}
                </p>
              </div>
              <div class="flex flex-col items-end gap-1">
                <span class="text-xs text-gray-500 whitespace-nowrap">{{ formatDate(message.date) }}</span>
                <span v-if="message.is_important" class="text-[11px] px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">
                  Important
                </span>
              </div>
            </div>
          </button>

          <div v-if="!loading && messages.length === 0" class="px-4 py-10 text-sm text-gray-400 text-center">
            Писем в этой папке пока нет
          </div>
          <div v-if="loading" class="px-4 py-10 text-sm text-gray-500 text-center">Загрузка писем...</div>
        </div>
      </section>

      <section class="bg-white border border-gray-200 rounded-xl overflow-hidden min-h-[70vh]">
        <div v-if="selectedMessage" class="h-full flex flex-col">
          <header class="p-5 border-b border-gray-200">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">{{ selectedMessage.subject || "Без темы" }}</h2>
                <p class="text-sm text-gray-500 mt-2">
                  От: {{ selectedMessage.sender_email || "-" }}
                </p>
                <p class="text-sm text-gray-500">
                  Кому: {{ selectedMessage.recipients || "-" }}
                </p>
                <p v-if="selectedMessage.cc" class="text-sm text-gray-500">
                  Копия: {{ selectedMessage.cc }}
                </p>
              </div>
              <span class="text-sm text-gray-500 whitespace-nowrap">{{ formatDateTime(selectedMessage.date) }}</span>
            </div>
          </header>

          <div class="p-5 overflow-y-auto whitespace-pre-wrap text-sm text-gray-800 flex-1">
            {{ selectedMessage.body_text || "Пустое письмо" }}
          </div>

          <div class="p-4 border-t border-gray-200 flex justify-end">
            <button
              @click="replyToSelected"
              class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
            >
              Ответить
            </button>
          </div>
        </div>

        <div v-else class="h-full flex items-center justify-center text-sm text-gray-400">
          Выберите письмо слева
        </div>
      </section>
    </div>

    <div v-if="showCompose" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div class="w-full max-w-2xl bg-white rounded-xl shadow-xl p-5 space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Новое письмо</h3>
          <button @click="closeCompose" class="text-sm text-gray-500 hover:text-gray-700">Закрыть</button>
        </div>

        <div class="grid grid-cols-1 gap-3">
          <input v-model="compose.to" type="text" placeholder="Кому" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="compose.cc" type="text" placeholder="Копия" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <input v-model="compose.subject" type="text" placeholder="Тема" class="px-3 py-2 border border-gray-300 rounded-lg" />
          <textarea
            v-model="compose.body"
            rows="10"
            placeholder="Текст письма..."
            class="px-3 py-2 border border-gray-300 rounded-lg"
          />
        </div>

        <div class="flex justify-end gap-2">
          <button @click="closeCompose" class="px-4 py-2 rounded-lg border border-gray-300">Отмена</button>
          <button
            @click="sendMail"
            :disabled="sending"
            class="px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-black disabled:opacity-60"
          >
            {{ sending ? "Отправка..." : "Отправить" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import applicationsService, {
  type MailDetail,
  type MailFolderCounts,
  type MailItem,
} from "../../services/applications"
import { useToast } from "../../composables/useToast"

type FolderId = "all" | "inbox" | "sent" | "important" | "trash"

const { showSuccess, showError } = useToast()
const loading = ref(false)
const syncing = ref(false)
const sending = ref(false)
const activeFolder = ref<FolderId>("all")
const searchQuery = ref("")
const folderCounts = ref<MailFolderCounts>({
  all: 0,
  inbox: 0,
  sent: 0,
  important: 0,
  trash: 0,
})
const messages = ref<MailItem[]>([])
const selectedMessage = ref<MailDetail | null>(null)
const showCompose = ref(false)

const compose = ref({
  to: "",
  cc: "",
  subject: "",
  body: "",
})

const folders = computed(() => [
  { id: "all" as FolderId, label: "All", count: folderCounts.value.all },
  { id: "inbox" as FolderId, label: "Inbox", count: folderCounts.value.inbox },
  { id: "sent" as FolderId, label: "Sent", count: folderCounts.value.sent },
  { id: "important" as FolderId, label: "Important", count: folderCounts.value.important },
  { id: "trash" as FolderId, label: "Trash", count: folderCounts.value.trash },
])

const loadFolderCounts = async () => {
  folderCounts.value = await applicationsService.getMailFolders()
}

const loadMessages = async () => {
  try {
    loading.value = true
    messages.value = await applicationsService.getMailMessages({
      folder: activeFolder.value,
      search: searchQuery.value.trim() || undefined,
    })
    if (messages.value.length > 0) {
      const currentExists = selectedMessage.value && messages.value.some((item) => item.id === selectedMessage.value?.id)
      if (!currentExists) {
        await openMessage(messages.value[0].id)
      }
    } else {
      selectedMessage.value = null
    }
  } catch (error) {
    console.error("Ошибка загрузки писем", error)
    showError("Не удалось загрузить письма")
  } finally {
    loading.value = false
  }
}

const openMessage = async (id: number) => {
  try {
    selectedMessage.value = await applicationsService.getMailMessage(id)
  } catch (error) {
    console.error("Ошибка загрузки письма", error)
    showError("Не удалось открыть письмо")
  }
}

const syncMailbox = async () => {
  try {
    syncing.value = true
    const result = await applicationsService.syncMailbox()
    await Promise.all([loadFolderCounts(), loadMessages()])
    showSuccess(`Почта синхронизирована: ${result.synced} писем`)
  } catch (error) {
    console.error("Ошибка синхронизации", error)
    showError("Не удалось синхронизировать почту")
  } finally {
    syncing.value = false
  }
}

const selectFolder = async (folder: FolderId) => {
  activeFolder.value = folder
  await loadMessages()
}

const closeCompose = () => {
  showCompose.value = false
  compose.value = { to: "", cc: "", subject: "", body: "" }
}

const sendMail = async () => {
  if (!compose.value.to.trim() || !compose.value.subject.trim()) {
    showError("Укажите получателя и тему")
    return
  }

  try {
    sending.value = true
    const sent = await applicationsService.sendMail({
      to: compose.value.to.trim(),
      cc: compose.value.cc.trim(),
      subject: compose.value.subject.trim(),
      body: compose.value.body,
    })
    closeCompose()
    await Promise.all([loadFolderCounts(), loadMessages()])
    selectedMessage.value = sent
    showSuccess("Письмо отправлено")
  } catch (error) {
    console.error("Ошибка отправки", error)
    showError("Не удалось отправить письмо")
  } finally {
    sending.value = false
  }
}

const replyToSelected = () => {
  if (!selectedMessage.value) return
  compose.value = {
    to: selectedMessage.value.sender_email || "",
    cc: "",
    subject: selectedMessage.value.subject ? `Re: ${selectedMessage.value.subject}` : "Re:",
    body: `\n\n---\n${selectedMessage.value.body_text || ""}`,
  }
  showCompose.value = true
}

const formatDate = (date: string) =>
  new Date(date).toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" })

const formatDateTime = (date: string) => new Date(date).toLocaleString("ru-RU")

onMounted(async () => {
  await Promise.all([loadFolderCounts(), loadMessages()])
})
</script>
