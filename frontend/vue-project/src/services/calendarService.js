import api from './api'

const calendarService = {
  // Получить все задачи (уже фильтруются по manager_id на сервере)
  async getTasks(params = {}) {
    console.log('Fetching tasks from API...')
    const response = await api.get('/tasks/', { params })
    console.log('Tasks received:', response.data)
    return response.data
  },

  // Задачи на сегодня
  async getTodayTasks() {
    const response = await api.get('/tasks/today/')
    return response.data
  },

  // Предстоящие задачи (7 дней)
  async getUpcomingTasks() {
    const response = await api.get('/tasks/upcoming/')
    return response.data
  },

  // Просроченные задачи
  async getOverdueTasks() {
    const response = await api.get('/tasks/overdue/')
    return response.data
  },

  // Создать новую задачу
  async createTask(taskData) {
    console.log('Creating task:', taskData)
    const response = await api.post('/tasks/', taskData)
    console.log('Task created:', response.data)
    return response.data
  },

  // Обновить задачу
  async updateTask(id, taskData) {
    const response = await api.put(`/tasks/${id}/`, taskData)
    return response.data
  },

  // Частично обновить (например, отметить выполненной)
  async patchTask(id, taskData) {
    const response = await api.patch(`/tasks/${id}/`, taskData)
    return response.data
  },

  // Удалить задачу
  async deleteTask(id) {
    const response = await api.delete(`/tasks/${id}/`)
    return response.data
  },

  // Переключить статус выполнения
  async toggleTaskComplete(id) {
    const response = await api.post(`/tasks/${id}/toggle_complete/`)
    return response.data
  },

  // Получить статистику
  async getStats() {
    const response = await api.get('/tasks/stats/')
    return response.data
  },

  // Задачи по диапазону дат
  async getTasksByDateRange(start, end) {
    const response = await api.get('/tasks/by_date_range/', {
      params: { start, end }
    })
    return response.data
  },

  // Задачи по месяцу
  async getTasksByMonth(year, month) {
    const response = await api.get('/tasks/by_month/', {
      params: { year, month }
    })
    return response.data
  }
}

export default calendarService