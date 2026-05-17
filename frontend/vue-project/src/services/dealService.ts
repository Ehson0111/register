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

  async getDealsByContact(contactId: number) {
    return this.getDeals({ contact_id: contactId })
  }
}

export default new DealService()
