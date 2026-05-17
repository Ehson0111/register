import api from '../services/api.js'

// Интерфейсы
export interface Contact {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  inn?: string
  status: string
  status_display: string
  company: string
  position: string
  address: string
  notes: string
  full_name: string
  active_deals_count: number
  created_at: string
  company_details?: ContactCompanyDetails
}

export interface ContactCompanyDetails {
  company_name: string
  inn: string
  kpp: string
  ogrn: string
  status_text: string
  address: string
  okved: string
  director: string
  updated_at: string
}

export interface SimpleContact {
  id: number
  full_name: string
  company: string
}

export interface CreateContactData {
  first_name: string
  last_name: string
  email: string
  phone: string
  inn?: string
  company: string
  status: string
  position: string
  address: string
  notes: string
}

export interface Service {
  id: number
  name: string
  description: string
  price: number
  duration_days: number
  is_active: boolean
  active_deals_count: number
  created_at: string
}

export interface SimpleService {
  id: number
  name: string
  price: number
}

export interface Deal {
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
  stage?: number | null
  stage_name?: string
  stage_color?: string
  expected_close_date: string
  actual_close_date: string
  created_at: string
  days_open: number
}

export interface DealStage {
  id: number
  name: string
  order: number
  color: string
  is_default: boolean
}

export interface CreateDealData {
  title: string
  description: string
  contact: number
  service: number
  amount: number
  probability: number
  status: string
  stage?: number | null
  expected_close_date?: string
}

export interface CreateServiceData {
  name: string
  description: string
  price: number
  duration_days: number
  is_active?: boolean
}

// Analytics interfaces
export interface AnalyticsOverview {
  overview: {
    total_contacts: number
    total_deals: number
    total_services: number
    total_revenue: number
    avg_deal_amount: number
    conversion_rate: number
  }
  deals_by_status: Array<{
    status: string
    count: number
    total_amount: number
  }>
  contacts_by_status: Array<{
    status: string
    count: number
  }>
}

export interface TopContact {
  id: number
  full_name: string
  company: string
  deal_count: number
  total_deal_amount: number
  won_deals: number
  won_amount: number
  win_rate?: number
}

export interface TopService {
  id: number
  name: string
  description: string
  price: number
  deal_count: number
  total_amount: number
  won_deals: number
  won_amount: number
}

export interface DealPerformance {
  monthly_performance: Array<{
    month: number
    total_deals: number
    won_deals: number
    lost_deals: number
    total_amount: number
    conversion_rate: number
  }>
  probability_analysis: Array<{
    range: string
    total_deals: number
    won_deals: number
    conversion_rate: number
  }>
}

export interface ContactDealsStats {
  contact: string
  total_deals: number
  won_deals: number
  active_deals: number
  total_amount: number
  success_rate: number
}

export interface AuditTrailItem {
  id: number
  actor: string
  action: string
  entity_type: string
  entity_id: number | null
  metadata: Record<string, any>
  created_at: string
}

class ContactService {
  // ==================== CONTACTS ====================
  
  async getContacts(params?: any): Promise<Contact[]> {
    const response = await api.get('/contacts/', { params })
    return response.data
  }

  async getContact(id: number): Promise<Contact> {
    const response = await api.get(`/contacts/${id}/`)
    return response.data
  }

  async createContact(data: CreateContactData): Promise<any> {
    const response = await api.post('/contacts/add/', data)
    return response.data
  }

  async updateContact(id: number, data: Partial<Contact>): Promise<Contact> {
    const response = await api.put(`/contacts/${id}/`, data)
    return response.data
  }

  async deleteContact(id: number): Promise<void> {
    await api.delete(`/contacts/remove/${id}/`)
  }

  async getContactsForSelect(): Promise<SimpleContact[]> {
    const response = await api.get('/contacts/select/')
    return response.data
  }

  async loadCompanyDataByInn(contactId: number, inn?: string): Promise<{ message: string; company_details: ContactCompanyDetails }> {
    const response = await api.post(`/contacts/${contactId}/load-company-data/`, { inn })
    return response.data
  }

  // ==================== SERVICES ====================
  
  async getServices(params?: any): Promise<Service[]> {
    const response = await api.get('/services/', { params })
    return response.data
  }

  async getService(id: number): Promise<Service> {
    const response = await api.get(`/services/${id}/`)
    return response.data
  }

  async createService(data: CreateServiceData): Promise<any> {
    const response = await api.post('/services/add/', data)
    return response.data
  }

  async updateService(id: number, data: Partial<Service>): Promise<Service> {
    const response = await api.put(`/services/${id}/`, data)
    return response.data
  }

  async deleteService(id: number): Promise<void> {
    await api.delete(`/services/remove/${id}/`)
  }

  async getServicesForSelect(): Promise<SimpleService[]> {
    const response = await api.get('/services/select/')
    return response.data
  }

  // ==================== DEALS ====================
  
  async getDeals(params?: any): Promise<Deal[]> {
    const response = await api.get('/deals/', { params })
    return response.data
  }

  async getDeal(id: number): Promise<Deal> {
    const response = await api.get(`/deals/${id}/`)
    return response.data
  }

  async createDeal(data: CreateDealData): Promise<any> {
    const response = await api.post('/deals/add/', data)
    return response.data
  }

  async updateDeal(id: number, data: Partial<Deal>): Promise<Deal> {
    const response = await api.put(`/deals/${id}/`, data)
    return response.data
  }

  async deleteDeal(id: number): Promise<void> {
    await api.delete(`/deals/remove/${id}/`)
  }

  async changeDealStatus(dealId: number, status: string): Promise<any> {
    const response = await api.post(`/deals/${dealId}/change-status/`, { status })
    return response.data
  }

  async getDealStages(): Promise<DealStage[]> {
    const response = await api.get('/deal-stages/')
    return response.data
  }

  async createDealStage(data: Pick<DealStage, 'name' | 'order' | 'color'> & { is_default?: boolean }): Promise<DealStage> {
    const response = await api.post('/deal-stages/', data)
    return response.data
  }

  async changeDealStage(dealId: number, stageId: number): Promise<any> {
    const response = await api.post(`/deals/${dealId}/change-stage/`, { stage_id: stageId })
    return response.data
  }

  // ==================== ANALYTICS ====================
  
  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    const response = await api.get('/contacts/analytics/overview/')
    return response.data
  }

  async getTopContacts(): Promise<{ by_deal_count: TopContact[], by_deal_amount: TopContact[] }> {
    const response = await api.get('/contacts/analytics/top-contacts/')
    return response.data
  }

  async getTopServices(): Promise<{ by_popularity: TopService[], by_revenue: TopService[] }> {
    const response = await api.get('/contacts/analytics/top-services/')
    return response.data
  }

  async getDealPerformance(): Promise<DealPerformance> {
    const response = await api.get('/contacts/analytics/deal-performance/')
    return response.data
  }

  async getContactDealsStats(contactId: number): Promise<ContactDealsStats> {
    const response = await api.get(`/contacts/${contactId}/deals/stats/`)
    return response.data
  }

  async getAuditTrail(params?: { entity_type?: string; entity_id?: number; action?: string }): Promise<AuditTrailItem[]> {
    const response = await api.get('/audit-trail/', { params })
    return response.data
  }

  // ==================== UTILITIES ====================
  
  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount)
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      'new': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'won': 'bg-green-100 text-green-800',
      'lost': 'bg-red-100 text-red-800',
      'on_hold': 'bg-gray-100 text-gray-800',
      'lead': 'bg-purple-100 text-purple-800',
      'client': 'bg-green-100 text-green-800',
      'partner': 'bg-orange-100 text-orange-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  getStatusText(status: string): string {
    const texts: Record<string, string> = {
      new: 'Новая',
      in_progress: 'В работе',
      won: 'Выиграна',
      lost: 'Проиграна',
      on_hold: 'На паузе',
      lead: 'Лид',
      client: 'Клиент',
      partner: 'Партнёр',
    }
    return texts[status] || status
  }
}

export default new ContactService()