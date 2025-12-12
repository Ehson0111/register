<!-- frontend/src/views/manager/MarketingView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Маркетинг и рассылки</h2>
      <button 
        @click="showCreateCampaign = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
      >
        + Новая рассылка
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Статистика рассылок -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Общая статистика</h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Всего рассылок</span>
            <span class="font-semibold">{{ stats.totalCampaigns }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-600">Открываемость</span>
            <span class="font-semibold text-green-600">{{ stats.openRate }}%</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-gray-600">CTR</span>
            <span class="font-semibold text-blue-600">{{ stats.ctr }}%</span>
          </div>
        </div>
      </div>

      <!-- Активные рассылки -->
      <div class="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Активные рассылки</h3>
        <div class="space-y-4">
          <div 
            v-for="campaign in activeCampaigns"
            :key="campaign.id"
            class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex-1">
              <h4 class="font-medium text-gray-900">{{ campaign.name }}</h4>
              <p class="text-sm text-gray-600">{{ campaign.recipients }} получателей</p>
            </div>
            <div class="text-right">
              <div class="text-sm font-medium text-gray-900">{{ campaign.progress }}%</div>
              <div class="w-24 bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-blue-500 h-2 rounded-full"
                  :style="{ width: campaign.progress + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Шаблоны писем -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Шаблоны писем</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div 
          v-for="template in emailTemplates"
          :key="template.id"
          class="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors cursor-pointer"
        >
          <h4 class="font-medium text-gray-900 mb-2">{{ template.name }}</h4>
          <p class="text-sm text-gray-600 mb-3">{{ template.description }}</p>
          <div class="flex space-x-2">
            <button class="text-blue-600 hover:text-blue-700 text-sm">Использовать</button>
            <button class="text-gray-600 hover:text-gray-700 text-sm">Редактировать</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showCreateCampaign = ref(false)

const stats = ref({
  totalCampaigns: 12,
  openRate: 24.5,
  ctr: 3.2
})

const activeCampaigns = ref([
  {
    id: 1,
    name: 'Новогодняя акция',
    recipients: 1245,
    progress: 65
  },
  {
    id: 2,
    name: 'Обновление услуг',
    recipients: 876,
    progress: 32
  }
])

const emailTemplates = ref([
  {
    id: 1,
    name: 'Приветственное письмо',
    description: 'Для новых клиентов'
  },
  {
    id: 2,
    name: 'Спецпредложение',
    description: 'Акционные предложения'
  },
  {
    id: 3,
    name: 'Напоминание',
    description: 'О неоплаченных счетах'
  }
])
</script>