import contactService from './contactService'
import type { Deal, CreateDealData, DealStage } from './contactService'

export type { Deal, CreateDealData, DealStage } from './contactService'

class DealService {
  async getDeals(params?: any) {
    return contactService.getDeals(params)
  }

  async getDeal(id: number) {
    return contactService.getDeal(id)
  }

  async createDeal(data: CreateDealData) {
    return contactService.createDeal(data)
  }

  async updateDeal(id: number, data: Partial<Deal>) {
    return contactService.updateDeal(id, data)
  }

  async deleteDeal(id: number) {
    return contactService.deleteDeal(id)
  }

  async changeDealStatus(dealId: number, status: string) {
    return contactService.changeDealStatus(dealId, status)
  }

  async getDealStages() {
    return contactService.getDealStages()
  }

  async createDealStage(data: Pick<DealStage, 'name' | 'order' | 'color'> & { is_default?: boolean }) {
    return contactService.createDealStage(data)
  }

  async changeDealStage(dealId: number, stageId: number) {
    return contactService.changeDealStage(dealId, stageId)
  }

  // Дополнительные методы специфичные для сделок
  async getDealsByContact(contactId: number) {
    return this.getDeals({ contact_id: contactId })
  }

  async getActiveDeals() {
    return this.getDeals({ status: ['new', 'in_progress', 'on_hold'] })
  }

  async getWonDeals() {
    return this.getDeals({ status: 'won' })
  }

  async getLostDeals() {
    return this.getDeals({ status: 'lost' })
  }

  // Аналитика сделок
  async getDealsByStatus() {
    const deals = await this.getDeals()
    const statusCounts: Record<string, number> = {}
    const statusAmounts: Record<string, number> = {}
    
    deals?.forEach(deal => {
      if (!statusCounts[deal.status]) {
        statusCounts[deal.status] = 0
        statusAmounts[deal.status] = 0
      }
      statusCounts[deal.status]++
      statusAmounts[deal.status] = (statusAmounts[deal.status] || 0) + Number(deal.amount || 0)
    })
    
    return {
      counts: statusCounts,
      amounts: statusAmounts
    }
  }

  async getDealConversionRate() {
    const deals = await this.getDeals()
    const total = deals?.length || 0
    const won = deals?.filter(d => d.status === 'won').length || 0
    
    return total > 0 ? (won / total) * 100 : 0
  }

  async getRevenueByMonth(year: number) {
    const deals = await this.getDeals()
    const monthlyRevenue: Record<number, number> = {}
    
    deals
      ?.filter(deal => deal.status === 'won')
      .forEach(deal => {
        const date = new Date(deal.created_at)
        if (date.getFullYear() === year) {
          const month = date.getMonth() + 1
          if (!monthlyRevenue[month]) {
            monthlyRevenue[month] = 0
          }
          monthlyRevenue[month] += Number(deal.amount || 0)
        }
      })
    
    return monthlyRevenue
  }
}

export default new DealService()