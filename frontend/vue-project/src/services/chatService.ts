import api from './api.js'

export interface ChatParticipant {
  id: number
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: 'manager' | 'admin' | 'telegram_client'
  full_name: string
  joined_at: string
}

export interface ChatMessage {
  id: number
  room: number
  sender_id: number
  sender_email: string
  sender_first_name: string
  sender_last_name: string
  sender_role: 'manager' | 'admin' | 'telegram_client'
  sender_name: string
  text: string
  created_at: string
}

export interface ChatRoom {
  id: number
  title: string
  created_by_id: number
  created_by_email: string
  created_by_name: string
  is_active: boolean
  created_at: string
  updated_at: string
  messages_count: number
  last_message: ChatMessage | null
  is_telegram: boolean
  telegram_chat_id: number | null
  participants: ChatParticipant[]
}

export interface TeamUser {
  id: number
  email: string
  first_name: string
  last_name: string
  role: 'admin' | 'manager' | 'client'
  role_display?: string
  is_active: boolean
}

interface CreateRoomParticipant {
  user_id: number
  role: 'manager' | 'admin'
  email?: string
  first_name?: string
  last_name?: string
}

class ChatService {
  async getRooms(): Promise<ChatRoom[]> {
    const response = await api.get('/chat/rooms/')
    return response.data
  }

  async getRoom(roomId: number): Promise<ChatRoom> {
    const response = await api.get(`/chat/rooms/${roomId}/`)
    return response.data
  }

  async deleteRoom(roomId: number): Promise<void> {
    await api.delete(`/chat/rooms/${roomId}/`)
  }

  async createRoom(title: string, participants: CreateRoomParticipant[]): Promise<ChatRoom> {
    const response = await api.post('/chat/rooms/', { title, participants })
    return response.data
  }

  async getMessages(roomId: number): Promise<ChatMessage[]> {
    const response = await api.get(`/chat/rooms/${roomId}/messages/`)
    return response.data
  }

  async sendMessage(roomId: number, text: string): Promise<ChatMessage> {
    const response = await api.post(`/chat/rooms/${roomId}/messages/`, { text })
    return response.data
  }

  async getStaffUsers(): Promise<TeamUser[]> {
    const response = await api.get('/users/team/')
    const users = Array.isArray(response.data) ? response.data : response.data?.results || []
    return users.filter((u: TeamUser) => u.is_active && (u.role === 'manager' || u.role === 'admin'))
  }
}

export default new ChatService()
