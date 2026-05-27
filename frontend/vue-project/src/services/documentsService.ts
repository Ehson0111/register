import api from './api.js'

export interface ClientDocument {
  id: number
  client_id: number
  original_filename: string
  content_type: string
  file_size: number | null
  uploaded_by: number
  uploaded_at: string
  download_url: string
}

class DocumentsService {
  async getList(clientId: number): Promise<ClientDocument[]> {
    const response = await api.get<ClientDocument[]>(`/documents/${clientId}/list/`)
    return response.data
  }

  async upload(clientId: number, file: File): Promise<ClientDocument> {
    const formData = new FormData()
    formData.append('client_id', String(clientId))
    formData.append('file', file)
    const response = await api.post<ClientDocument>('/documents/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  async delete(documentId: number): Promise<void> {
    await api.delete(`/documents/delete/${documentId}/`)
  }

  async download(documentId: number, originalFilename: string): Promise<void> {
    const response = await api.get(`/documents/download/${documentId}/`, {
      responseType: 'blob'
    })
    const blob = response.data as Blob
    const disposition = response.headers['content-disposition']
    const filename = (disposition && /filename="?([^"]+)"?/.exec(disposition)?.[1]) || originalFilename
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }
}

export default new DocumentsService()
