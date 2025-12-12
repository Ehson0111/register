// frontend/src/services/serviceService.ts
import api from './api'

export interface Service {
  id: number
  name: string
  description: string
  price: string
  duration_days: number
  is_active: boolean
  created_at: string
  active_deals_count: number
}

export interface CreateServiceData {
  name: string
  description: string
  price: number
  duration_days: number
  is_active: boolean
}

class ServiceService {
  async getServices(): Promise<Service[]> {
    const response = await api.get('/services/')
    return response.data
  }

  async getService(id: number): Promise<Service> {
    const response = await api.get(`/services/${id}/`)
    return response.data
  }

  async createService(data: CreateServiceData): Promise<Service> {
    const response = await api.post('/services/add/', data)
    return response.data.service
  }

  async updateService(id: number, data: Partial<Service>): Promise<Service> {
    const response = await api.put(`/services/${id}/`, data)
    return response.data
  }

  async deleteService(id: number): Promise<void> {
    await api.delete(`/services/remove/${id}/`)
  }

  async getServicesForSelect(): Promise<any[]> {
    const response = await api.get('/services/select/')
    return response.data
  }
}

export default new ServiceService()