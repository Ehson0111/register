import axios from "axios";

export interface ApplicationItem {
  id: number;
  subject: string;
  date: string;
  text: string;
  sender_email: string;
  is_processed: boolean;
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

const applicationsApi = axios.create({
  baseURL: import.meta.env.VITE_APPLICATIONS_API_URL || "http://127.0.0.1:8009/api/applications/",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

function debugLog(hypothesisId: string, location: string, message: string, data: Record<string, unknown>) {
  // #region agent log
  fetch("http://127.0.0.1:7647/ingest/66103dc7-eaf0-4803-be05-aba9d5dec07c", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Debug-Session-Id": "ad25e9" },
    body: JSON.stringify({
      sessionId: "ad25e9",
      runId: "run2",
      hypothesisId,
      location,
      message,
      data,
      timestamp: Date.now(),
    }),
  }).catch(() => {});
  // #endregion
}

class ApplicationService {
  async fetchFromMail(): Promise<{ total: number; new: number; duplicates: number }> {
    const response = await applicationsApi.post("fetch_from_mail/");
    return response.data;
  }

  async getApplications(params?: Record<string, any>): Promise<ApplicationItem[]> {
    debugLog("H5", "applications.ts:getApplications", "request start", {
      baseURL: applicationsApi.defaults.baseURL,
      hasSearch: Boolean(params?.search),
    });
    const response = await applicationsApi.get<PaginatedResponse<ApplicationItem>>("", { params });
    debugLog("H5", "applications.ts:getApplications", "request success", {
      status: response.status,
      count: response.data?.count ?? null,
      resultsLen: Array.isArray(response.data?.results) ? response.data.results.length : -1,
    });
    return Array.isArray(response.data?.results) ? response.data.results : [];
  }

  async getApplication(id: number): Promise<ApplicationItem> {
    const response = await applicationsApi.get<ApplicationItem>(`${id}/`);
    return response.data;
  }

  async markProcessed(id: number, isProcessed = true): Promise<ApplicationItem> {
    const response = await applicationsApi.patch<ApplicationItem>(`${id}/`, {
      is_processed: isProcessed,
    });
    return response.data;
  }
}

export default new ApplicationService();