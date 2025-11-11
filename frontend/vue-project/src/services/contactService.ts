// frontend/src/services/contactService.ts
import api from './api'

export interface Contact {
  id: number
    first_name: string
    last_name: string
  email: string
  phone: string
  company: string
  status: string
  status_display: string
  position: string
  address: string
  notes: string
  created_at: string
  active_deals_count: number
}

export interface CreateContactData {
  first_name: string
  last_name: string
  email: string
  phone: string
  company: string
  status: string
  position: string
  address: string
  notes: string
}

class ContactService {
  async getContacts(params?: any): Promise<Contact[]> {
    const response = await api.get('/contacts/', { params })
    return response.data
  }

  async getContact(id: number): Promise<Contact> {
    const response = await api.get(`/contacts/${id}/`)
    return response.data
  }

  async createContact(data: CreateContactData): Promise<Contact> {
    const response = await api.post('/contacts/add/', data)
    return response.data.contact
  }

  async updateContact(id: number, data: Partial<Contact>): Promise<Contact> {
    const response = await api.put(`/contacts/${id}/`, data)
    return response.data
  }

  async deleteContact(id: number): Promise<void> {
    await api.delete(`/contacts/remove/${id}/`)
  }
}

export default new ContactService()