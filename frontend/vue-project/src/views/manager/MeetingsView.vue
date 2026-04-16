<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Встречи</h1>
        <p class="text-gray-600 mt-1">Планирование встреч на базе календаря задач</p>
      </div>
      <button
        @click="showCreate = !showCreate"
        class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700"
      >
        {{ showCreate ? "Скрыть форму" : "+ Новая встреча" }}
      </button>
    </div>

    <section v-if="showCreate" class="bg-white border border-gray-200 rounded-xl p-5 space-y-3">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <input v-model="draft.title" type="text" placeholder="Название встречи" class="px-3 py-2 border border-gray-300 rounded-lg" />
        <input v-model="draft.date" type="date" class="px-3 py-2 border border-gray-300 rounded-lg" />
        <input v-model="draft.time" type="time" class="px-3 py-2 border border-gray-300 rounded-lg" />
        <input v-model="draft.location" type="text" placeholder="Место / ссылка" class="px-3 py-2 border border-gray-300 rounded-lg" />
      </div>
      <textarea
        v-model="draft.description"
        rows="3"
        placeholder="Описание"
        class="w-full px-3 py-2 border border-gray-300 rounded-lg"
      />
      <div class="flex justify-end">
        <button
          @click="createMeeting"
          :disabled="saving"
          class="px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-black disabled:opacity-60"
        >
          {{ saving ? "Создаю..." : "Создать встречу" }}
        </button>
      </div>
    </section>

    <section class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <header class="px-5 py-4 border-b border-gray-200 flex justify-between">
        <h2 class="font-semibold text-gray-900">Список встреч</h2>
        <button @click="loadMeetings" class="text-sm text-blue-700 hover:text-blue-900">Обновить</button>
      </header>
      <div class="divide-y divide-gray-100">
        <article v-for="meeting in meetings" :key="meeting.id" class="px-5 py-4 flex items-start justify-between gap-4">
          <div>
            <p class="font-medium text-gray-900">{{ meeting.title }}</p>
            <p class="text-sm text-gray-500">
              {{ formatDate(meeting.date) }} <span v-if="meeting.time">· {{ meeting.time.slice(0, 5) }}</span>
            </p>
            <p v-if="meeting.location" class="text-sm text-gray-700 mt-1">{{ meeting.location }}</p>
            <p v-if="meeting.description" class="text-sm text-gray-600 mt-1">{{ meeting.description }}</p>
          </div>
          <button
            @click="toggleComplete(meeting)"
            class="px-3 py-1.5 text-xs rounded-lg border"
            :class="meeting.completed ? 'border-green-300 text-green-700 bg-green-50' : 'border-gray-300 text-gray-700 hover:bg-gray-50'"
          >
            {{ meeting.completed ? "Выполнено" : "Отметить выполненной" }}
          </button>
        </article>
        <p v-if="!loading && meetings.length === 0" class="px-5 py-8 text-sm text-gray-400 text-center">
          Встречи не найдены
        </p>
        <p v-if="loading" class="px-5 py-8 text-sm text-gray-500 text-center">Загрузка...</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import calendarService from "../../services/calendarService"
import { useToast } from "../../composables/useToast"

const { showSuccess, showError } = useToast()
const meetings = ref([])
const loading = ref(false)
const saving = ref(false)
const showCreate = ref(false)

const draft = ref({
  title: "",
  description: "",
  date: "",
  time: "",
  location: "",
})

const loadMeetings = async () => {
  try {
    loading.value = true
    const all = await calendarService.getTasks()
    meetings.value = (Array.isArray(all) ? all : [])
      .filter((item) => item.task_type === "meeting")
      .sort((a, b) => new Date(`${a.date}T${a.time || "00:00"}`) - new Date(`${b.date}T${b.time || "00:00"}`))
  } catch (error) {
    console.error("Ошибка загрузки встреч", error)
    showError("Не удалось загрузить встречи")
  } finally {
    loading.value = false
  }
}

const createMeeting = async () => {
  if (!draft.value.title.trim() || !draft.value.date) {
    showError("Укажите название и дату встречи")
    return
  }

  try {
    saving.value = true
    await calendarService.createTask({
      title: draft.value.title.trim(),
      description: draft.value.description.trim(),
      date: draft.value.date,
      time: draft.value.time || null,
      location: draft.value.location.trim(),
      priority: "medium",
      task_type: "meeting",
      color: "#3b82f6",
      is_recurring: false,
      recurrence_rule: "",
    })
    draft.value = { title: "", description: "", date: "", time: "", location: "" }
    showCreate.value = false
    showSuccess("Встреча создана")
    await loadMeetings()
  } catch (error) {
    console.error("Ошибка создания встречи", error)
    showError("Не удалось создать встречу")
  } finally {
    saving.value = false
  }
}

const toggleComplete = async (meeting) => {
  try {
    await calendarService.toggleTaskComplete(meeting.id)
    await loadMeetings()
  } catch (error) {
    console.error("Ошибка обновления встречи", error)
    showError("Не удалось обновить встречу")
  }
}

const formatDate = (d) => new Date(d).toLocaleDateString("ru-RU")

onMounted(() => {
  loadMeetings()
})
</script>
