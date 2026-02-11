<!-- frontend/src/views/manager/DocumentsView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center flex-wrap gap-4">
      <h2 class="text-2xl font-bold text-gray-900">Документы клиентов</h2>
      <button
        @click="openUploadModal()"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
      >
        <ArrowUpTrayIcon class="w-5 h-5" />
        <span>Загрузить документ</span>
      </button>
    </div>

    <!-- Выбор клиента -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">Клиент</label>
      <select
        v-model="selectedClientId"
        @change="loadDocuments()"
        class="w-full max-w-md border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option :value="null">Выберите клиента</option>
        <option v-for="c in contacts" :key="c.id" :value="c.id">
          {{ c.full_name || (c.first_name + ' ' + c.last_name) }} — {{ c.email }}
        </option>
      </select>
      <p v-if="contacts.length === 0 && !loadingContacts" class="text-sm text-gray-500 mt-2">Нет контактов.</p>
    </div>

    <!-- Поиск -->
    <div v-if="selectedClientId" class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Поиск по имени файла..."
        class="w-full max-w-md border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
    </div>

    <!-- Загрузка / Ошибка -->
    <div v-if="loading && selectedClientId" class="text-center py-8 text-gray-500">Загрузка документов...</div>
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
      {{ error }}
    </div>

    <!-- Список документов -->
    <div v-else-if="selectedClientId" class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="p-6">
        <div v-if="filteredDocuments.length === 0" class="text-center py-12">
          <DocumentIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500 text-lg mb-2">Документов пока нет</p>
          <p class="text-gray-400 mb-4">Загрузите первый документ для этого клиента</p>
          <button
            @click="openUploadModal()"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Загрузить документ
          </button>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="doc in filteredDocuments"
            :key="doc.id"
            class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <DocumentIcon class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h4 class="font-medium text-gray-900">{{ doc.original_filename }}</h4>
                <p class="text-sm text-gray-500">
                  {{ formatFileSize(doc.file_size) }} · {{ formatDate(doc.uploaded_at) }}
                </p>
              </div>
            </div>

            <div class="flex items-center space-x-3">
              <button
                @click="downloadDocument(doc)"
                :disabled="downloadId === doc.id"
                class="text-blue-600 hover:text-blue-700 p-1 disabled:opacity-50"
                title="Скачать"
              >
                <ArrowDownTrayIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
      <DocumentIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
      <p class="text-gray-500">Выберите клиента, чтобы просмотреть или загрузить документы.</p>
    </div>

    <!-- Модальное окно загрузки -->
    <Teleport to="body">
      <div
        v-if="showUploadModal"
        class="fixed inset-0 z-50 overflow-y-auto"
        aria-labelledby="upload-modal-title"
        role="dialog"
        aria-modal="true"
      >
        <div class="flex min-h-screen items-center justify-center p-4">
          <div class="fixed inset-0 bg-black/30" aria-hidden="true" @click="showUploadModal = false"></div>
          <div class="relative bg-white rounded-xl shadow-lg max-w-md w-full p-6">
            <h3 id="upload-modal-title" class="text-lg font-medium text-gray-900 mb-4">Загрузить документ</h3>

            <form @submit.prevent="uploadDocument" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Клиент *</label>
                <select
                  v-model="uploadForm.client_id"
                  required
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Выберите клиента</option>
                  <option v-for="c in contacts" :key="c.id" :value="c.id">
                    {{ c.full_name || (c.first_name + ' ' + c.last_name) }} — {{ c.email }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Файл *</label>
                <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                  <input
                    type="file"
                    @change="handleFileSelect"
                    class="hidden"
                    ref="fileInputRef"
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,image/*"
                  >
                  <DocumentIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p class="text-sm text-gray-600 mb-2">Нажмите для выбора файла</p>
                  <button
                    type="button"
                    @click="fileInputRef?.click()"
                    class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Выбрать файл
                  </button>
                  <p v-if="uploadForm.file" class="text-sm text-green-600 mt-2">
                    Выбран: {{ uploadForm.file.name }}
                  </p>
                </div>
              </div>

              <p v-if="uploadError" class="text-sm text-red-600">{{ uploadError }}</p>

              <div class="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  @click="showUploadModal = false"
                  class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  :disabled="!uploadForm.client_id || !uploadForm.file || uploadLoading"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {{ uploadLoading ? 'Загрузка...' : 'Загрузить' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  DocumentIcon,
  ArrowUpTrayIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'
import documentsService, { type ClientDocument } from '../../services/documentsService'
import contactService, { type Contact } from '../../services/contactService'

const selectedClientId = ref<number | null>(null)
const searchQuery = ref('')
const contacts = ref<Contact[]>([])
const documents = ref<ClientDocument[]>([])
const loading = ref(false)
const loadingContacts = ref(false)
const error = ref('')
const showUploadModal = ref(false)
const uploadForm = ref({
  client_id: '' as number | '',
  file: null as File | null
})
const uploadLoading = ref(false)
const uploadError = ref('')
const downloadId = ref<number | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const filteredDocuments = computed(() => {
  const list = documents.value
  if (!searchQuery.value.trim()) return list
  const q = searchQuery.value.toLowerCase()
  return list.filter(d => d.original_filename.toLowerCase().includes(q))
})

function formatFileSize(bytes: number | null): string {
  if (bytes == null || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

async function loadContacts() {
  loadingContacts.value = true
  try {
    contacts.value = await contactService.getContacts()
  } catch {
    contacts.value = []
  } finally {
    loadingContacts.value = false
  }
}

async function loadDocuments() {
  if (!selectedClientId.value) {
    documents.value = []
    return
  }
  loading.value = true
  error.value = ''
  try {
    documents.value = await documentsService.getList(selectedClientId.value)
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || 'Не удалось загрузить документы'
    documents.value = []
  } finally {
    loading.value = false
  }
}

function openUploadModal() {
  uploadForm.value = { client_id: selectedClientId.value ?? '', file: null }
  uploadError.value = ''
  showUploadModal.value = true
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    uploadForm.value.file = target.files[0]
  }
}

async function uploadDocument() {
  const clientId = uploadForm.value.client_id
  const file = uploadForm.value.file
  if (!clientId || !file) return
  uploadError.value = ''
  uploadLoading.value = true
  try {
    await documentsService.upload(Number(clientId), file)
    showUploadModal.value = false
    uploadForm.value = { client_id: '', file: null }
    if (selectedClientId.value === Number(clientId)) {
      await loadDocuments()
    }
  } catch (e: any) {
    uploadError.value = e.response?.data?.error || e.message || 'Ошибка загрузки'
  } finally {
    uploadLoading.value = false
  }
}

async function downloadDocument(doc: ClientDocument) {
  downloadId.value = doc.id
  try {
    await documentsService.download(doc.id, doc.original_filename)
  } catch (e: any) {
    error.value = e.response?.data?.error || e.message || 'Ошибка скачивания'
  } finally {
    downloadId.value = null
  }
}

onMounted(loadContacts)
</script>
