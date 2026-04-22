import api from './api.js'

export interface DealInvoice {
  id: number
  deal_id: number
  deal_title: string
  contact_id: number | null
  contact_name: string
  contact_email: string
  contact_phone: string
  service_id: number | null
  service_name: string
  comment: string
  invoice_number: string
  onec_document_id: string
  onec_invoice_number: string
  onec_payment_document_id: string
  amount: number
  status: 'draft' | 'waiting' | 'paid' | 'cancelled'
  payment_id: string | null
  payment_url: string
  onec_sync_status: 'pending' | 'synced' | 'error'
  crm_sync_status: 'pending' | 'synced' | 'error'
  onec_retry_count: number
  crm_retry_count: number
  last_onec_error: string
  last_crm_error: string
  created_at: string
  paid_at: string | null
  sent_to_1c: boolean
  pay_link_sent_at: string | null
  next_retry_at: string | null
}

class PaymentService {
  async getDealInvoice(dealId: number): Promise<DealInvoice | null> {
    const response = await api.get(`/payment/deals/${dealId}/invoice/`, {
      validateStatus: (status) => (status >= 200 && status < 300) || status === 204,
    })
    if (response.status === 204) return null
    return response.data
  }

  async createInvoiceFromDeal(dealId: number): Promise<DealInvoice> {
    const response = await api.post(`/payment/deals/${dealId}/invoice/`)
    return response.data
  }

  async retryInvoiceSync(invoiceId: number): Promise<DealInvoice> {
    const response = await api.post(`/payment/invoices/${invoiceId}/retry-sync/`)
    return response.data
  }
}

export default new PaymentService()
