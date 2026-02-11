<!-- frontend/src/views/manager/ProfileView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Мой профиль</h2>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Информация профиля -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Основная информация</h3>
          
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                <input 
                  v-model="profile.first_name"
                  type="text" 
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                <input 
                  v-model="profile.last_name"
                  type="text" 
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input 
                v-model="profile.email"
                type="email" 
                disabled
                class="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50 text-gray-500"
              >
              <p class="text-xs text-gray-500 mt-1">Email нельзя изменить</p>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
              <input 
                v-model="profile.phone"
                type="tel" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+7 (999) 123-45-67"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Должность</label>
              <input 
                v-model="profile.position"
                type="text" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Менеджер по продажам"
              >
            </div>
          </div>
          
          <div class="flex justify-end mt-6">
            <button 
              @click="updateProfile"
              :disabled="updateLoading"
              class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {{ updateLoading ? 'Сохранение...' : 'Сохранить изменения' }}
            </button>
          </div>
          <p v-if="updateError" class="text-sm text-red-600 mt-2">{{ updateError }}</p>
          <p v-if="updateSuccess" class="text-sm text-green-600 mt-2">Профиль успешно обновлён</p>
        </div>

        <!-- Смена пароля -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Смена пароля</h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Текущий пароль</label>
              <input 
                v-model="password.current"
                type="password" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Новый пароль</label>
              <input 
                v-model="password.new"
                type="password" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Подтверждение пароля</label>
              <input 
                v-model="password.confirm"
                type="password" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
          </div>
          
          <div class="flex justify-end mt-6">
            <button 
              @click="changePassword"
              :disabled="passwordLoading"
              class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {{ passwordLoading ? 'Смена...' : 'Сменить пароль' }}
            </button>
          </div>
          <p v-if="passwordError" class="text-sm text-red-600 mt-2">{{ passwordError }}</p>
          <p v-if="passwordSuccess" class="text-sm text-green-600 mt-2">Пароль успешно изменён</p>
        </div>
      </div>

      <!-- Боковая панель -->
      <div class="space-y-6">
        <!-- Аватар -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
          <div class="w-32 h-32 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl font-bold text-blue-600">
              {{ userInitials }}
            </span>
          </div>
          <h3 class="text-lg font-medium text-gray-900">{{ profile.full_name || `${profile.first_name} ${profile.last_name}` }}</h3>
          <p class="text-gray-600">{{ profile.position || 'Менеджер' }}</p>
        </div>

        <!-- Статистика -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Статистика</h3>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Роль</span>
              <span class="font-medium">{{ profile.role || 'Менеджер' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Email</span>
              <span class="font-medium text-sm truncate ml-2">{{ profile.email }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../store/auth'
import authService from '../../services/auth.js'

const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const profile = ref({
  id: 0,
  first_name: '',
  last_name: '',
  full_name: '',
  email: '',
  phone: '',
  position: '',
  role: ''
})

const password = ref({
  current: '',
  new: '',
  confirm: ''
})

const updateLoading = ref(false)
const updateError = ref('')
const updateSuccess = ref(false)
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref(false)

const userInitials = computed(() => {
  const name = profile.value.full_name || `${profile.value.first_name} ${profile.value.last_name}`.trim()
  if (!name) return 'М'
  return name
    .split(' ')
    .map((part) => part.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const response = await authService.getProfile()
    if (response.data) {
      profile.value = {
        id: response.data.id || 0,
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        full_name: response.data.full_name || '',
        email: response.data.email || '',
        phone: response.data.profile?.phone || '',
        position: response.data.profile?.position || '',
        role: response.data.role || 'manager'
      }
    }
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || 'Не удалось загрузить профиль'
  } finally {
    loading.value = false
  }
}

async function updateProfile() {
  updateError.value = ''
  updateSuccess.value = false
  updateLoading.value = true
  try {
    await authService.updateProfile({
      phone: profile.value.phone,
      position: profile.value.position
    })
    updateSuccess.value = true
    setTimeout(() => { updateSuccess.value = false }, 3000)
  } catch (e: any) {
    updateError.value = e.response?.data?.error || e.message || 'Ошибка обновления профиля'
  } finally {
    updateLoading.value = false
  }
}

async function changePassword() {
  if (password.value.new !== password.value.confirm) {
    passwordError.value = 'Пароли не совпадают'
    return
  }
  if (!password.value.current || !password.value.new) {
    passwordError.value = 'Заполните все поля'
    return
  }
  
  passwordError.value = ''
  passwordSuccess.value = false
  passwordLoading.value = true
  
  try {
    // TODO: добавить API для смены пароля, если есть
    passwordError.value = 'Смена пароля пока не реализована на сервере'
  } catch (e: any) {
    passwordError.value = e.response?.data?.error || e.message || 'Ошибка смены пароля'
  } finally {
    passwordLoading.value = false
  }
}

onMounted(loadProfile)
</script>
