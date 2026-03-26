import { Applications } from './applications';
import api from '../services/api.js'
import type { ModelRef } from 'vue';

export interface Applications  {
    id:number
    subject:string
    date: number    
    text: string 
    sender_email:string
    message_id:number 
    is_processed:string
    created_at: string
    update_at: string

}

class ApplicationService {

    async getApplications(params?: any): Promise<Applications[]>{
        const response =await api.get('/applications/')
        return response.data
    }
}

export default new ApplicationService()