import api from './api.js'

export interface ClientProfile {
  id: number
  first_name: string
  last_name: string
  full_name: string
  email: string
  phone: string
  status: string
  status_display: string
  company: string
  position: string
  address: string
  notes: string
  deals?: unknown[]
  created_at: string
}

export interface ClientDeal {
  id: number
  title: string
  description: string
  contact: number
  contact_name: string
  service: number
  service_name: string
  amount: number
  probability: number
  status: string
  status_display: string
  status_color: string
  is_closed: boolean
  expected_close_date: string | null
  actual_close_date: string | null
  created_at: string
}

export interface ClientDealsResponse {
  contact: { id: number; full_name: string; email: string }
  total_deals: number
  deals: ClientDeal[]
}

export interface ClientServiceOption {
  id: number
  name: string
  price: number
}

export interface CreateRequestPayload {
  service_id: number
  message?: string
  budget?: number
}

class ClientService {
  async getProfile(): Promise<ClientProfile> {
    const response = await api.get<ClientProfile>('/client/profile/')
    return response.data
  }

  async getDeals(status?: string): Promise<ClientDealsResponse> {
    const response = await api.get<ClientDealsResponse>('/client/deals/', {
      params: status ? { status } : undefined
    })
    return response.data
  }

  async getServices(): Promise<ClientServiceOption[]> {
    const response = await api.get<ClientServiceOption[]>('/client/services/')
    return response.data
  }

  async createRequest(payload: CreateRequestPayload): Promise<{ deal_id: number; message: string; deal: ClientDeal }> {
    const response = await api.post('/client/request/', payload)
    return response.data
  }
}

export default new ClientService()
