<!--
  [VIEW] DealsKanbanView — канбан-доска сделок по колонкам статусов
  Маршрут: /manager/deals-kanban | Альтернатива табличному DealsView
-->
<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Канбан сделок</h1>
        <p class="text-gray-600 mt-1">Сделки распределены по текущим статусам, можно перетаскивать между колонками</p>
      </div>
      <div class="flex items-center gap-2">
        <router-link
          to="/manager/deals"
          class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50"
        >
          Таблица сделок
        </router-link>
      </div>
    </div>

    <div class="bg-white rounded-lg border border-gray-200 p-4">
      <div class="flex flex-wrap items-center gap-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по названию, контакту, услуге..."
          class="flex-1 min-w-[240px] px-3 py-2 border border-gray-300 rounded-lg"
          @input="loadDeals"
        />
        <button
          @click="loadAll"
          :disabled="loading"
          class="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 disabled:opacity-60"
        >
          {{ loading ? "Обновляю..." : "Обновить" }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-10 text-gray-500">Загрузка канбана...</div>
    <div v-else class="overflow-x-auto pb-2">
      <div class="flex gap-4 min-w-max">
        <section
          v-for="column in statusColumns"
          :key="column.status"
          class="w-80 bg-gray-50 border border-gray-200 rounded-xl transition-colors"
          :class="{ 'ring-2 ring-blue-300 border-blue-300': dropTargetStatus === column.status }"
          @dragover.prevent="onColumnDragOver(column.status)"
          @dragenter.prevent="onColumnDragOver(column.status)"
          @dragleave="onColumnDragLeave(column.status)"
          @drop.prevent="onColumnDrop(column.status)"
        >
          <header class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full" :class="column.dotClass"></span>
              <h3 class="font-medium text-gray-900">{{ column.label }}</h3>
            </div>
            <span class="text-xs text-gray-500">{{ dealsByStatus(column.status).length }}</span>
          </header>

          <div class="p-3 space-y-3 min-h-[220px] max-h-[70vh] overflow-y-auto">
            <article
              v-for="deal in dealsByStatus(column.status)"
              :key="deal.id"
              draggable="true"
              class="bg-white border border-gray-200 rounded-lg p-3 space-y-2 cursor-grab active:cursor-grabbing"
              :class="{ 'opacity-60': draggedDealId === deal.id }"
              @dragstart="onDragStart(deal.id)"
              @dragend="onDragEnd"
            >
              <div class="flex justify-between items-start gap-2">
                <button
                  @click="$router.push(`/manager/deals/${deal.id}`)"
                  class="text-left font-medium text-gray-900 hover:text-blue-700"
                >
                  {{ deal.title }}
                </button>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="statusClass(deal.status)">
                  {{ dealStatusLabel(deal) }}
                </span>
              </div>
              <div class="text-sm text-gray-600">
                <div>{{ deal.contact_name || "-" }}</div>
                <div>{{ deal.service_name || "-" }}</div>
              </div>
              <div class="text-sm font-semibold text-gray-900">
                {{ formatCurrency(Number(deal.amount || 0)) }}
              </div>
              <div class="flex items-center justify-between text-xs text-gray-500">
                <span>Вероятность: {{ deal.probability }}%</span>
                <span>{{ deal.expected_close_date ? formatDate(deal.expected_close_date) : "Без даты" }}</span>
              </div>
            </article>

            <div
              v-if="dealsByStatus(column.status).length === 0"
              class="text-sm text-gray-400 text-center py-6 border border-dashed border-gray-300 rounded-lg"
            >
              Нет сделок
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue"
import { useToast } from "../../composables/useToast"
import dealService from "../../services/dealService"
import type { Deal } from "../../services/contactService"
import { getDealStatusLabel } from "../../constants/dealStatuses"

const { showSuccess, showError } = useToast()
const deals = ref<Deal[]>([])
const loading = ref(false)
const searchQuery = ref("")
const draggedDealId = ref<number | null>(null)
const dropTargetStatus = ref<string | null>(null)

const statusColumns = computed(() => [
  { status: "new", label: "Новые", dotClass: "bg-blue-500" },
  { status: "in_progress", label: "В работе", dotClass: "bg-orange-500" },
  { status: "on_hold", label: "На паузе", dotClass: "bg-slate-500" },
  { status: "won", label: "Выиграны", dotClass: "bg-green-500" },
  { status: "lost", label: "Проиграны", dotClass: "bg-red-500" },
])

const dealsByStatus = (status: string) => deals.value.filter((deal) => deal.status === status)

const dealStatusLabel = (deal: Deal) => deal.status_display || getDealStatusLabel(deal.status)

const loadDeals = async () => {
  const params: Record<string, string> = {}
  if (searchQuery.value.trim()) {
    params.search = searchQuery.value.trim()
  }
  deals.value = await dealService.getDeals(params)
}

const loadAll = async () => {
  try {
    loading.value = true
    await loadDeals()
  } catch (error) {
    console.error("Ошибка загрузки канбана", error)
    showError("Не удалось загрузить канбан")
  } finally {
    loading.value = false
  }
}

const onDragStart = (dealId: number) => {
  draggedDealId.value = dealId
}

const onDragEnd = () => {
  draggedDealId.value = null
  dropTargetStatus.value = null
}

const onColumnDragOver = (status: string) => {
  dropTargetStatus.value = status
}

const onColumnDragLeave = (status: string) => {
  if (dropTargetStatus.value === status) {
    dropTargetStatus.value = null
  }
}

const onColumnDrop = async (targetStatus: string) => {
  const dealId = draggedDealId.value
  if (!dealId) {
    dropTargetStatus.value = null
    return
  }

  const currentDeal = deals.value.find((deal) => deal.id === dealId)
  if (!currentDeal || currentDeal.status === targetStatus) {
    onDragEnd()
    return
  }

  try {
    await dealService.changeDealStatus(dealId, targetStatus)
    showSuccess("Сделка перемещена")
    await loadDeals()
  } catch (error) {
    console.error("Ошибка перемещения сделки", error)
    showError("Не удалось переместить сделку")
  } finally {
    onDragEnd()
  }
}

const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    new: "bg-blue-100 text-blue-800",
    in_progress: "bg-orange-100 text-orange-800",
    won: "bg-green-100 text-green-800",
    lost: "bg-red-100 text-red-800",
    on_hold: "bg-slate-300 text-slate-900",
  }
  return classes[status] || "bg-slate-300 text-slate-900"
}

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(amount)

const formatDate = (date: string) =>
  new Date(date).toLocaleDateString("ru-RU")

onMounted(() => {
  loadAll()
})
</script>
