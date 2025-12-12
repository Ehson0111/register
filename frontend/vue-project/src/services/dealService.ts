// frontend/src/services/dealService.ts
import api from './api'

export interface Deal {
  id: number
  title: string
  description: string
  contact: number
  contact_name: string
  service: number
  service_name: string
  amount: string
  probability: number
  status: string
  status_display: string
  status_color: string
  is_closed: boolean
  expected_close_date: string
  actual_close_date: string
  created_at: string
  updated_at: string
  days_open: number
}

export interface CreateDealData {
  title: string
  description: string
  contact: number
  service: number
  amount: number
  probability: number
  status: string
  expected_close_date: string
}

class DealService {
  async getDeals(params?: any): Promise<Deal[]> {
    const response = await api.get('/deals/', { params })
    return response.data
  }

  async getDeal(id: number): Promise<Deal> {
    const response = await api.get(`/deals/${id}/`)
    return response.data
  }

  async createDeal(data: CreateDealData): Promise<Deal> {
    const response = await api.post('/deals/add/', data)
    return response.data.deal
  }

  async updateDeal(id: number, data: Partial<Deal>): Promise<Deal> {
    const response = await api.put(`/deals/${id}/`, data)
    return response.data
  }

  async deleteDeal(id: number): Promise<void> {
    await api.delete(`/deals/remove/${id}/`)
  }

  async changeDealStatus(id: number, status: string): Promise<Deal> {
    const response = await api.post(`/deals/${id}/change-status/`, { status })
    return response.data.deal
  }

  async getContactDealsStats(contactId: number): Promise<any> {
    const response = await api.get(`/contacts/${contactId}/deals/stats/`)
    return response.data
  }
}

export default new DealService()