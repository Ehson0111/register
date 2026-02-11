import api from './api.js'

export interface MarketingTemplate {
  id: number
  name: string
  template_type: string
  template_type_display: string
  subject: string
  content: string
  sms_content?: string
  variables: string[]
  description: string
  manager_id: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CampaignRecipientDetail {
  id: number
  recipient_id: number
  recipient_email: string
  recipient_phone: string
  status: string
  status_display: string
  sent_at: string | null
  delivered_at: string | null
  opened_at: string | null
  error_message: string
  created_at: string
}

export interface Campaign {
  id: number
  name: string
  campaign_type: string
  campaign_type_display: string
  status: string
  status_display: string
  template: number
  template_name: string
  subject: string
  content: string
  recipients: number[]
  recipient_count: number
  success_count: number
  failed_count: number
  sent_at: string | null
  delivery_rate: number
  recipients_detail?: CampaignRecipientDetail[]
  manager_id: number
  created_at: string
  updated_at: string
}

export interface CampaignStats {
  total_campaigns: number
  total_recipients: number
  total_sent: number
  recent_campaigns: number
  recent_recipients: number
  recent_sent: number
  by_type: { individual: number; bulk: number }
  by_status: { draft: number; sent: number; sending: number; failed: number }
}

export interface SendCampaignPayload {
  template_id: number
  subject?: string
  content?: string
  variables?: Record<string, string>
  recipient_ids: number[]
  campaign_name?: string
}

export interface SendIndividualPayload {
  template_id: number
  recipient_id: number
  variables?: Record<string, string>
}

export interface SendQuickMessagePayload {
  message: string
  subject?: string
  recipient_ids: number[]
  campaign_name?: string
}

class MarketingService {
  async getTemplates(): Promise<MarketingTemplate[]> {
    const response = await api.get<MarketingTemplate[]>('/marketing/templates/')
    return response.data
  }

  async getCampaigns(): Promise<Campaign[]> {
    const response = await api.get<Campaign[]>('/marketing/campaigns/')
    return response.data
  }

  async getCampaignStats(): Promise<CampaignStats> {
    const response = await api.get<CampaignStats>('/marketing/campaigns/stats/')
    return response.data
  }

  async sendCampaign(payload: SendCampaignPayload): Promise<{ success: boolean; message: string; campaign_id?: number; status?: string }> {
    const response = await api.post('/marketing/send-campaign/', payload)
    return response.data
  }

  async sendIndividual(payload: SendIndividualPayload): Promise<{ success: boolean; message?: string; error?: string; campaign_id?: number }> {
    const response = await api.post('/marketing/send-individual/', payload)
    return response.data
  }

  async sendQuickMessage(payload: SendQuickMessagePayload): Promise<{ success: boolean; message: string; campaign_id?: number; status?: string }> {
    const response = await api.post('/marketing/send-quick-message/', payload)
    return response.data
  }
}

export default new MarketingService()
