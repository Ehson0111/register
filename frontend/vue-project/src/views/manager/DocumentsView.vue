<!-- frontend/src/views/manager/DocumentsView.vue -->
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900">Мои документы</h2>
      <button 
        @click="showUploadModal = true"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
      >
        <ArrowUpTrayIcon class="w-5 h-5" />
        <span>Загрузить документ</span>
      </button>
    </div>

    <!-- Фильтры -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div class="flex flex-wrap gap-4">
        <select 
          v-model="selectedCategory"
          class="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Все категории</option>
          <option value="contract">Договоры</option>
          <option value="invoice">Счета</option>
          <option value="report">Отчеты</option>
          <option value="other">Прочие</option>
        </select>
        
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Поиск документов..."
          class="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>
    </div>

    <!-- Список документов -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="p-6">
        <div v-if="documents.length === 0" class="text-center py-12">
          <DocumentIcon class="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p class="text-gray-500 text-lg mb-2">Документов пока нет</p>
          <p class="text-gray-400">Загрузите первый документ</p>
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
                <h4 class="font-medium text-gray-900">{{ doc.name }}</h4>
                <p class="text-sm text-gray-500">
                  {{ doc.category_display }} • {{ formatFileSize(doc.size) }} • {{ formatDate(doc.created_at) }}
                </p>
              </div>
            </div>
            
            <div class="flex items-center space-x-3">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="getCategoryColor(doc.category)">
                {{ doc.category_display }}
              </span>
              
              <button 
                @click="downloadDocument(doc)"
                class="text-blue-600 hover:text-blue-700 p-1"
                title="Скачать"
              >
                <ArrowDownTrayIcon class="w-5 h-5" />
              </button>
              
              <button 
                @click="deleteDocument(doc)"
                class="text-red-600 hover:text-red-700 p-1"
                title="Удалить"
              >
                <TrashIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно загрузки -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-medium mb-4">Загрузить документ</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Название документа</label>
            <input 
              v-model="newDocument.name"
              type="text" 
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Введите название"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Категория</label>
            <select 
              v-model="newDocument.category"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="contract">Договор</option>
              <option value="invoice">Счет</option>
              <option value="report">Отчет</option>
              <option value="other">Прочее</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Файл</label>
            <div class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
              <input 
                type="file"
                @change="handleFileSelect"
                class="hidden"
                ref="fileInput"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
              >
              <DocumentIcon class="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p class="text-sm text-gray-600 mb-2">Перетащите файл или нажмите для выбора</p>
              <button 
                @click="$refs.fileInput.click()"
                class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                Выбрать файл
              </button>
              <p v-if="newDocument.file" class="text-sm text-green-600 mt-2">
                Выбран: {{ newDocument.file.name }}
              </p>
            </div>
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button 
            @click="showUploadModal = false"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Отмена
          </button>
          <button 
            @click="uploadDocument"
            :disabled="!newDocument.name || !newDocument.file"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Загрузить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  DocumentIcon, 
  ArrowUpTrayIcon, 
  ArrowDownTrayIcon, 
  TrashIcon 
} from '@heroicons/vue/24/outline'

interface Document {
  id: number
  name: string
  category: string
  category_display: string
  size: number
  created_at: string
  file_url: string
}

const showUploadModal = ref(false)
const selectedCategory = ref('')
const searchQuery = ref('')

const newDocument = ref({
  name: '',
  category: 'contract',
  file: null as File | null
})

const documents = ref<Document[]>([
  {
    id: 1,
    name: 'Договор с ООО "Ромашка"',
    category: 'contract',
    category_display: 'Договор',
    size: 2457600,
    created_at: '2024-01-15',
    file_url: '#'
  },
  {
    id: 2,
    name: 'Счет №12345',
    category: 'invoice',
    category_display: 'Счет',
    size: 512000,
    created_at: '2024-01-16',
    file_url: '#'
  },
  {
    id: 3,
    name: 'Отчет за январь',
    category: 'report',
    category_display: 'Отчет',
    size: 1024000,
    created_at: '2024-01-20',
    file_url: '#'
  }
])

const filteredDocuments = computed(() => {
  return documents.value.filter(doc => {
    const matchesCategory = !selectedCategory.value || doc.category === selectedCategory.value
    const matchesSearch = !searchQuery.value || 
      doc.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCategory && matchesSearch
  })
})

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    contract: 'bg-blue-100 text-blue-800',
    invoice: 'bg-green-100 text-green-800',
    report: 'bg-purple-100 text-purple-800',
    other: 'bg-gray-100 text-gray-800'
  }
  return colors[category] || colors.other
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    newDocument.value.file = target.files[0]
  }
}

const uploadDocument = () => {
  if (!newDocument.value.name || !newDocument.value.file) return
  
  // Здесь будет логика загрузки на сервер
  const newDoc: Document = {
    id: Date.now(),
    name: newDocument.value.name,
    category: newDocument.value.category,
    category_display: getCategoryDisplay(newDocument.value.category),
    size: newDocument.value.file.size,
    created_at: new Date().toISOString().split('T')[0],
    file_url: '#'
  }
  
  documents.value.unshift(newDoc)
  showUploadModal.value = false
  
  // Сброс формы
  newDocument.value = {
    name: '',
    category: 'contract',
    file: null
  }
}

const getCategoryDisplay = (category: string) => {
  const displays: Record<string, string> = {
    contract: 'Договор',
    invoice: 'Счет',
    report: 'Отчет',
    other: 'Прочее'
  }
  return displays[category] || 'Прочее'
}

const downloadDocument = (doc: Document) => {
  // Здесь будет логика скачивания
  console.log('Downloading:', doc.name)
}

const deleteDocument = (doc: Document) => {
  if (confirm(`Удалить документ "${doc.name}"?`)) {
    documents.value = documents.value.filter(d => d.id !== doc.id)
  }
}
</script>