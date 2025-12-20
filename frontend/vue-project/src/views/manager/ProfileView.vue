<!-- frontend/src/views/manager/ProfileView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Мой профиль</h2>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
              <input 
                v-model="profile.phone"
                type="tel" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Должность</label>
              <input 
                v-model="profile.position"
                type="text" 
                class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
          </div>
          
          <div class="flex justify-end mt-6">
            <button 
              @click="updateProfile"
              class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Сохранить изменения
            </button>
          </div>
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
              class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Сменить пароль
            </button>
          </div>
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
          <h3 class="text-lg font-medium text-gray-900">{{ profile.first_name }} {{ profile.last_name }}</h3>
          <p class="text-gray-600">{{ profile.position }}</p>
          
          <button class="mt-4 text-blue-600 hover:text-blue-700 text-sm">
            Сменить фото
          </button>
        </div>

        <!-- Статистика -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Статистика</h3>
          
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-gray-600">Активные сделки</span>
              <span class="font-medium">{{ stats.activeDeals }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Контакты</span>
              <span class="font-medium">{{ stats.totalContacts }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Успешные сделки</span>
              <span class="font-medium text-green-600">{{ stats.successRate }}%</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">В системе</span>
              <span class="font-medium">{{ stats.daysInSystem }} дн.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../../store/auth'

const authStore = useAuthStore()

const profile = ref({
  first_name: 'Иван',
  last_name: 'Петров',
  email: 'ivan.petrov@company.com',
  phone: '+7 (999) 123-45-67',
  position: 'Менеджер по продажам'
})

const password = ref({
  current: '',
  new: '',
  confirm: ''
})

const stats = ref({
  activeDeals: 12,
  totalContacts: 45,
  successRate: 78,
  daysInSystem: 156
})

const userInitials = computed(() => {
  return `${profile.value.first_name.charAt(0)}${profile.value.last_name.charAt(0)}`.toUpperCase()
})

const updateProfile = async () => {
  // Здесь будет логика обновления профиля
  console.log('Updating profile:', profile.value)
  // await authStore.updateProfile(profile.value)
}

const changePassword = async () => {
  if (password.value.new !== password.value.confirm) {
    alert('Пароли не совпадают')
    return
  }
  
  // Здесь будет логика смены пароля
  console.log('Changing password')
  // await authStore.changePassword(password.value)
  
  // Сброс формы
  password.value = {
    current: '',
    new: '',
    confirm: ''
  }
}
</script>