<!--
  [VIEW] ClientProfileView — просмотр профиля (только чтение)
  Маршрут: /client/profile | API: clientService.getProfile()
-->
<template>
  <div class="space-y-6">
    <div v-if="loading" class="text-center py-12 text-gray-500">Загрузка...</div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>
    <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 max-w-2xl">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Мои данные</h3>
      <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <dt class="text-sm text-gray-500">Имя</dt>
          <dd class="font-medium text-gray-900">{{ profile?.full_name || '—' }}</dd>
        </div>
        <div>
          <dt class="text-sm text-gray-500">Email</dt>
          <dd class="font-medium text-gray-900">{{ profile?.email || '—' }}</dd>
        </div>
        <div>
          <dt class="text-sm text-gray-500">Телефон</dt>
          <dd class="font-medium text-gray-900">{{ profile?.phone || '—' }}</dd>
        </div>
        <div>
          <dt class="text-sm text-gray-500">Компания</dt>
          <dd class="font-medium text-gray-900">{{ profile?.company || '—' }}</dd>
        </div>
        <div>
          <dt class="text-sm text-gray-500">Должность</dt>
          <dd class="font-medium text-gray-900">{{ profile?.position || '—' }}</dd>
        </div>
        <div>
          <dt class="text-sm text-gray-500">Адрес</dt>
          <dd class="font-medium text-gray-900">{{ profile?.address || '—' }}</dd>
        </div>
        <div class="sm:col-span-2">
          <dt class="text-sm text-gray-500">Заметки</dt>
          <dd class="font-medium text-gray-900">{{ profile?.notes || '—' }}</dd>
        </div>
      </dl>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import clientService, { type ClientProfile } from '../../services/clientService'

const loading = ref(true)
const error = ref('')
const profile = ref<ClientProfile | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    profile.value = await clientService.getProfile()
  } catch (e: any) {
    error.value = e.response?.data?.detail || e.message || 'Не удалось загрузить профиль'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
