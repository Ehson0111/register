<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-900">Чаты команды</h2>
      <button
        @click="openCreateRoomModal"
        class="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        <PlusIcon class="w-5 h-5" />
        Создать чат
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <section class="lg:col-span-1 bg-white rounded-lg border border-gray-200 shadow-sm">
        <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="font-semibold text-gray-900">Мои комнаты</h3>
          <button @click="loadRooms" class="text-sm text-blue-600 hover:text-blue-800">Обновить</button>
        </div>
        <div v-if="roomsLoading" class="p-4 text-sm text-gray-500">Загрузка комнат...</div>
        <div v-else-if="roomsError" class="p-4 text-sm text-red-600">{{ roomsError }}</div>
        <div v-else-if="rooms.length === 0" class="p-4 text-sm text-gray-500">Пока нет чатов.</div>
        <ul v-else class="divide-y divide-gray-100">
          <li
            v-for="room in rooms"
            :key="room.id"
            class="p-4 cursor-pointer hover:bg-gray-50"
            :class="selectedRoomId === room.id ? 'bg-blue-700/45 chat-room-selected' : ''"
            @click="selectRoom(room.id)"
          >
            <div class="flex items-center gap-2">
              <p class="font-medium text-gray-900 truncate">{{ room.title || ('Чат #' + room.id) }}</p>
              <span
                v-if="room.is_telegram"
                class="inline-flex items-center rounded-full bg-sky-100 text-sky-700 px-2 py-0.5 text-[11px] font-medium"
              >
                Telegram
              </span>
            </div>
            <p class="text-xs text-gray-500 mt-1 truncate">
              {{ room.last_message ? room.last_message.text : 'Без сообщений' }}
            </p>
            <div class="text-xs text-gray-400 mt-2 flex items-center justify-between">
              <span>Участников: {{ room.participants.length }}</span>
              <span>{{ formatDateTime(room.updated_at) }}</span>
            </div>
          </li>
        </ul>
      </section>

      <section class="lg:col-span-2 bg-white rounded-lg border border-gray-200 shadow-sm flex flex-col min-h-[560px]">
        <div class="px-4 py-3 border-b border-gray-200">
          <template v-if="selectedRoom">
            <div class="flex items-center gap-2">
              <h3 class="font-semibold text-gray-900">{{ selectedRoom.title || ('Чат #' + selectedRoom.id) }}</h3>
              <span
                v-if="selectedRoom.is_telegram"
                class="inline-flex items-center rounded-full bg-sky-100 text-sky-700 px-2 py-0.5 text-[11px] font-medium"
              >
                Telegram
              </span>
            </div>
            <p class="text-sm text-gray-500">
              {{ participantsPreview(selectedRoom) }}
              <template v-if="selectedRoom.is_telegram && selectedRoom.telegram_chat_id">
                · chat id: {{ selectedRoom.telegram_chat_id }}
              </template>
            </p>
            <div class="mt-2">
              <button
                @click="handleDeleteRoom"
                class="text-xs text-red-600 hover:text-red-800"
                :disabled="deletingRoom"
              >
                {{ deletingRoom ? 'Удаление...' : 'Удалить чат' }}
              </button>
            </div>
          </template>
          <template v-else>
            <h3 class="font-semibold text-gray-900">Выберите чат</h3>
            <p class="text-sm text-gray-500">Слева выберите комнату или создайте новую.</p>
          </template>
        </div>

        <div v-if="selectedRoomId" class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
          <div v-if="messagesLoading" class="text-sm text-gray-500">Загрузка сообщений...</div>
          <div v-else-if="messagesError" class="text-sm text-red-600">{{ messagesError }}</div>
          <div v-else-if="messages.length === 0" class="text-sm text-gray-500">Напишите первое сообщение.</div>
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="max-w-[80%] rounded-xl px-4 py-2 shadow-sm"
            :class="msg.sender_id === currentUserId ? 'ml-auto bg-blue-600 text-white' : 'bg-white text-gray-900'"
          >
            <p class="text-xs opacity-80 mb-1">
              {{ msg.sender_name }} · {{ formatDateTime(msg.created_at) }}
            </p>
            <p class="whitespace-pre-wrap break-words">{{ msg.text }}</p>
          </div>
        </div>
        <div v-else class="flex-1 flex items-center justify-center text-gray-400">Нет выбранной комнаты</div>

        <form
          v-if="selectedRoomId"
          @submit.prevent="submitMessage"
          class="p-4 border-t border-gray-200 bg-white flex items-end gap-3"
        >
          <textarea
            v-model="messageDraft"
            rows="2"
            placeholder="Введите сообщение..."
            class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
          <button
            type="submit"
            :disabled="sendingMessage || !messageDraft.trim()"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ sendingMessage ? 'Отправка...' : 'Отправить' }}
          </button>
        </form>
      </section>
    </div>

    <Teleport to="body">
      <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/30" @click="showCreateModal = false"></div>
        <div class="relative w-full max-w-xl bg-white rounded-xl shadow-lg border border-gray-200">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">Создать новый чат</h3>
          </div>
          <form @submit.prevent="submitCreateRoom" class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Название</label>
              <input
                v-model="newRoomTitle"
                type="text"
                placeholder="Например: Чат админов и менеджеров"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <p class="text-sm font-medium text-gray-700 mb-2">Участники (manager/admin)</p>
              <div v-if="staffLoading" class="text-sm text-gray-500">Загрузка пользователей...</div>
              <div v-else-if="staffError" class="text-sm text-red-600">{{ staffError }}</div>
              <div v-else class="max-h-56 overflow-auto border border-gray-200 rounded-lg divide-y divide-gray-100">
                <label
                  v-for="user in staffUsers"
                  :key="user.id"
                  class="flex items-center justify-between px-3 py-2 text-sm hover:bg-gray-50"
                >
                  <div class="flex items-center gap-2">
                    <input
                      type="checkbox"
                      :value="user.id"
                      v-model="selectedParticipantIds"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span class="text-gray-900">
                      {{ fullName(user) }} <span class="text-gray-500">({{ user.email }})</span>
                    </span>
                  </div>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-slate-300 text-slate-900">{{ roleLabel(user.role) }}</span>
                </label>
              </div>
            </div>

            <p v-if="createRoomError" class="text-sm text-red-600">{{ createRoomError }}</p>

            <div class="flex justify-end gap-3">
              <button type="button" @click="showCreateModal = false" class="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200">
                Отмена
              </button>
              <button
                type="submit"
                :disabled="creatingRoom"
                class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {{ creatingRoom ? 'Создание...' : 'Создать чат' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '../../store/auth.js'
import chatService, { type ChatMessage, type ChatRoom, type TeamUser } from '../../services/chatService'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id || 0)

const rooms = ref<ChatRoom[]>([])
const roomsLoading = ref(false)
const roomsError = ref('')
const selectedRoomId = ref<number | null>(null)

const messages = ref<ChatMessage[]>([])
const messagesLoading = ref(false)
const messagesError = ref('')
const messageDraft = ref('')
const sendingMessage = ref(false)

const showCreateModal = ref(false)
const newRoomTitle = ref('')
const staffUsers = ref<TeamUser[]>([])
const staffLoading = ref(false)
const staffError = ref('')
const selectedParticipantIds = ref<number[]>([])
const creatingRoom = ref(false)
const createRoomError = ref('')
const deletingRoom = ref(false)
const ROOMS_POLL_INTERVAL_MS = 3000
const MESSAGES_POLL_INTERVAL_MS = 1200
let roomsPollTimer: number | null = null
let messagesPollTimer: number | null = null

const selectedRoom = computed(() => rooms.value.find(r => r.id === selectedRoomId.value) || null)

function fullName(user: TeamUser): string {
  const name = `${user.first_name || ''} ${user.last_name || ''}`.trim()
  return name || user.email
}

function roleLabel(role: string): string {
  if (role === 'admin') return 'Админ'
  if (role === 'manager') return 'Менеджер'
  if (role === 'telegram_client') return 'Telegram клиент'
  return role
}

function formatDateTime(value: string): string {
  if (!value) return ''
  return new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function participantsPreview(room: ChatRoom): string {
  return room.participants.map(p => p.full_name || p.email || `ID ${p.user_id}`).join(', ')
}

async function loadRooms(options?: { silent?: boolean }) {
  const silent = !!options?.silent
  if (!silent) {
    roomsLoading.value = true
  }
  roomsError.value = ''
  try {
    rooms.value = await chatService.getRooms()
    const firstRoom = rooms.value[0]
    if (!selectedRoomId.value && firstRoom) {
      selectedRoomId.value = firstRoom.id
      await loadMessages(firstRoom.id)
    } else if (selectedRoomId.value && !rooms.value.some(r => r.id === selectedRoomId.value)) {
      selectedRoomId.value = null
      messages.value = []
    }
  } catch (e: any) {
    roomsError.value = e?.response?.data?.detail || e?.message || 'Не удалось загрузить комнаты'
    rooms.value = []
  } finally {
    if (!silent) {
      roomsLoading.value = false
    }
  }
}

async function selectRoom(roomId: number) {
  selectedRoomId.value = roomId
  await loadMessages(roomId)
}

async function loadMessages(roomId: number, options?: { silent?: boolean }) {
  const silent = !!options?.silent
  if (!silent) {
    messagesLoading.value = true
  }
  messagesError.value = ''
  try {
    messages.value = await chatService.getMessages(roomId)
  } catch (e: any) {
    messagesError.value = e?.response?.data?.detail || e?.message || 'Не удалось загрузить сообщения'
    messages.value = []
  } finally {
    if (!silent) {
      messagesLoading.value = false
    }
  }
}

async function submitMessage() {
  const roomId = selectedRoomId.value
  if (!roomId || !messageDraft.value.trim()) return
  sendingMessage.value = true
  messagesError.value = ''
  try {
    const created = await chatService.sendMessage(roomId, messageDraft.value.trim())
    messages.value.push(created)
    messageDraft.value = ''
    await loadRooms()
  } catch (e: any) {
    messagesError.value = e?.response?.data?.detail || e?.message || 'Не удалось отправить сообщение'
  } finally {
    sendingMessage.value = false
  }
}

async function handleDeleteRoom() {
  const roomId = selectedRoomId.value
  if (!roomId) return
  const ok = window.confirm('Удалить этот чат?')
  if (!ok) return
  deletingRoom.value = true
  try {
    await chatService.deleteRoom(roomId)
    selectedRoomId.value = null
    messages.value = []
    await loadRooms()
  } catch (e: any) {
    messagesError.value = e?.response?.data?.detail || e?.message || 'Не удалось удалить чат'
  } finally {
    deletingRoom.value = false
  }
}

async function pollRoomsTick() {
  await loadRooms({ silent: true })
}

async function pollMessagesTick() {
  if (!selectedRoomId.value) return
  await loadMessages(selectedRoomId.value, { silent: true })
}

async function refreshNow() {
  await pollRoomsTick()
  await pollMessagesTick()
}

function startPolling() {
  if (!roomsPollTimer) {
    roomsPollTimer = window.setInterval(() => {
      pollRoomsTick()
    }, ROOMS_POLL_INTERVAL_MS)
  }
  if (!messagesPollTimer) {
    messagesPollTimer = window.setInterval(() => {
      pollMessagesTick()
    }, MESSAGES_POLL_INTERVAL_MS)
  }
}

function stopPolling() {
  if (roomsPollTimer) {
    window.clearInterval(roomsPollTimer)
    roomsPollTimer = null
  }
  if (messagesPollTimer) {
    window.clearInterval(messagesPollTimer)
    messagesPollTimer = null
  }
}

async function loadStaffUsers() {
  staffLoading.value = true
  staffError.value = ''
  try {
    staffUsers.value = await chatService.getStaffUsers()
    const me = currentUserId.value
    selectedParticipantIds.value = me ? [me] : []
  } catch (e: any) {
    staffError.value = e?.response?.data?.detail || e?.message || 'Не удалось загрузить пользователей'
    staffUsers.value = []
  } finally {
    staffLoading.value = false
  }
}

async function openCreateRoomModal() {
  showCreateModal.value = true
  createRoomError.value = ''
  newRoomTitle.value = ''
  await loadStaffUsers()
}

async function submitCreateRoom() {
  createRoomError.value = ''
  const unique = Array.from(new Set(selectedParticipantIds.value))
  if (unique.length < 2) {
    createRoomError.value = 'Выберите минимум 2 участников (включая себя).'
    return
  }

  creatingRoom.value = true
  try {
    const participants = unique.map(id => {
      const user = staffUsers.value.find(u => u.id === id)
      return {
        user_id: id,
        role: (user?.role === 'admin' ? 'admin' : 'manager') as 'admin' | 'manager',
        email: user?.email || '',
        first_name: user?.first_name || '',
        last_name: user?.last_name || ''
      }
    })

    const room = await chatService.createRoom(newRoomTitle.value.trim(), participants)
    showCreateModal.value = false
    await loadRooms()
    await selectRoom(room.id)
  } catch (e: any) {
    createRoomError.value = e?.response?.data?.detail || e?.message || 'Не удалось создать чат'
  } finally {
    creatingRoom.value = false
  }
}

onMounted(async () => {
  await loadRooms()
  startPolling()
  window.addEventListener('focus', refreshNow)
  document.addEventListener('visibilitychange', refreshNow)
})

onUnmounted(() => {
  stopPolling()
  window.removeEventListener('focus', refreshNow)
  document.removeEventListener('visibilitychange', refreshNow)
})
</script>

<style scoped>
.chat-room-selected p,
.chat-room-selected span {
  color: rgba(255, 255, 255, 0.96) !important;
}
</style>
