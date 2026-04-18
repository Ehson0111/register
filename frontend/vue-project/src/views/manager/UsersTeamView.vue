<template>
  <div class="space-y-6">
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Добавить пользователя</h2>
      <p class="text-sm text-gray-500 mb-4">
        <template v-if="isAdmin">
          Администратор может создавать менеджеров и клиентов. Учётная запись сразу активна, вход — по email и паролю.
        </template>
        <template v-else>
          Менеджер может добавлять только клиентов. Новых менеджеров создаёт администратор.
        </template>
      </p>
      <form class="grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="handleCreate">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Имя пользователя</label>
          <input
            v-model="form.username"
            type="text"
            required
            minlength="3"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Имя</label>
          <input
            v-model="form.first_name"
            type="text"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
          <input
            v-model="form.last_name"
            type="text"
            required
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="8"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Повтор пароля</label>
          <input
            v-model="form.password_confirm"
            type="password"
            required
            minlength="8"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div v-if="isAdmin" class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Роль в системе</label>
          <select
            v-model="form.role"
            class="w-full md:max-w-xs rounded-lg border border-gray-300 px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="manager">Менеджер</option>
            <option value="client">Клиент</option>
          </select>
        </div>
        <div v-else class="md:col-span-2 text-sm text-gray-600">
          Роль нового пользователя: <span class="font-medium text-gray-900">Клиент</span>
        </div>
        <div class="md:col-span-2 flex items-center gap-3">
          <button
            type="submit"
            :disabled="creating"
            class="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {{ creating ? 'Создание…' : 'Создать пользователя' }}
          </button>
          <span v-if="createMessage" class="text-sm text-green-600">{{ createMessage }}</span>
          <span v-if="createError" class="text-sm text-red-600">{{ createError }}</span>
        </div>
      </form>
    </div>

    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-lg font-medium text-gray-900">Пользователи</h2>
        <button
          type="button"
          class="text-sm text-blue-600 hover:text-blue-800"
          :disabled="loading"
          @click="loadUsers"
        >
          Обновить
        </button>
      </div>
      <div v-if="actionError" class="px-6 py-3 bg-red-50 text-red-700 text-sm border-b border-red-100">{{ actionError }}</div>
      <div v-if="loading" class="p-8 text-center text-gray-500">Загрузка…</div>
      <div v-else-if="loadError" class="p-6 text-red-600 text-sm">{{ loadError }}</div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Имя</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Роль</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Регистрация</th>
              <th v-if="isAdmin" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Действия
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50">
              <td class="px-6 py-3 text-sm text-gray-900">{{ u.email }}</td>
              <td class="px-6 py-3 text-sm text-gray-700">
                {{ u.first_name }} {{ u.last_name }}
              </td>
              <td class="px-6 py-3 text-sm text-gray-700">{{ u.role_display || roleLabel(u.role) }}</td>
              <td class="px-6 py-3 text-sm">
                <span
                  class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="u.is_active ? 'bg-green-100 text-green-800' : 'bg-slate-300 text-slate-900'"
                >
                  {{ u.is_active ? 'Активен' : 'Неактивен' }}
                </span>
              </td>
              <td class="px-6 py-3 text-sm text-gray-500">{{ formatDate(u.date_joined) }}</td>
              <td v-if="isAdmin" class="px-6 py-3 text-sm">
                <button
                  v-if="currentUserId && u.id !== currentUserId"
                  type="button"
                  :disabled="togglingId === u.id"
                  class="text-sm font-medium"
                  :class="u.is_active ? 'text-amber-600 hover:text-amber-800' : 'text-green-600 hover:text-green-800'"
                  @click="toggleUserActive(u)"
                >
                  {{ togglingId === u.id ? '…' : u.is_active ? 'Отключить' : 'Включить' }}
                </button>
                <span v-else class="text-gray-400 text-xs">—</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="users.length === 0" class="p-8 text-center text-gray-500">Нет пользователей</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { fetchTeamUsers, createTeamUser, patchTeamUserActive } from '@/services/usersTeamService.js'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.user?.role === 'admin')
const currentUserId = computed(() => authStore.user?.id)

const users = ref([])
const loading = ref(true)
const loadError = ref('')
const creating = ref(false)
const createMessage = ref('')
const createError = ref('')
const togglingId = ref(null)
const actionError = ref('')

const form = ref({
  email: '',
  username: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  role: 'client'
})

function roleLabel(role) {
  if (role === 'admin') return 'Администратор'
  if (role === 'manager') return 'Менеджер'
  if (role === 'client') return 'Клиент'
  return role
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('ru-RU', {
      dateStyle: 'short',
      timeStyle: 'short'
    })
  } catch {
    return iso
  }
}

async function loadUsers() {
  loading.value = true
  loadError.value = ''
  actionError.value = ''
  try {
    const { data } = await fetchTeamUsers()
    users.value = Array.isArray(data) ? data : data?.results || []
  } catch (e) {
    loadError.value = e.response?.data?.detail || e.message || 'Не удалось загрузить список'
    users.value = []
  } finally {
    loading.value = false
  }
}

function flattenErrors(errPayload) {
  if (!errPayload || typeof errPayload !== 'object') return 'Ошибка сохранения'
  const parts = []
  for (const [k, v] of Object.entries(errPayload)) {
    if (Array.isArray(v)) parts.push(`${k}: ${v.join(', ')}`)
    else if (typeof v === 'object') parts.push(flattenErrors(v))
    else parts.push(`${k}: ${v}`)
  }
  return parts.join('; ') || 'Ошибка сохранения'
}

async function handleCreate() {
  createMessage.value = ''
  createError.value = ''
  if (form.value.password !== form.value.password_confirm) {
    createError.value = 'Пароли не совпадают'
    return
  }
  const payload = { ...form.value }
  if (!isAdmin.value) {
    payload.role = 'client'
  }
  creating.value = true
  try {
    await createTeamUser(payload)
    createMessage.value = 'Пользователь создан'
    form.value = {
      email: '',
      username: '',
      first_name: '',
      last_name: '',
      password: '',
      password_confirm: '',
      role: isAdmin.value ? 'client' : 'client'
    }
    await loadUsers()
  } catch (e) {
    const d = e.response?.data
    createError.value = typeof d === 'string' ? d : flattenErrors(d)
  } finally {
    creating.value = false
  }
}

async function toggleUserActive(u) {
  if (!isAdmin.value || u.id === currentUserId.value) return
  togglingId.value = u.id
  actionError.value = ''
  try {
    await patchTeamUserActive(u.id, !u.is_active)
    await loadUsers()
  } catch (e) {
    const d = e.response?.data
    actionError.value = typeof d === 'string' ? d : flattenErrors(d)
  } finally {
    togglingId.value = null
  }
}

onMounted(() => {
  loadUsers()
})
</script>
