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

export interface ApplicationAuditItem {
  id: number;
  application: number | null;
  actor: string;
  action: "approved" | "rejected" | "processed";
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface MailFolderCounts {
  all: number;
  inbox: number;
  sent: number;
  important: number;
  trash: number;
}

export interface MailItem {
  id: number;
  external_id: string;
  message_id: string;
  subject: string;
  sender_name: string;
  sender_email: string;
  recipients: string;
  date: string;
  preview: string;
  is_read: boolean;
  is_important: boolean;
  in_inbox: boolean;
  in_sent: boolean;
  in_trash: boolean;
  primary_folder: string;
}

export interface MailDetail extends MailItem {
  cc: string;
  body_text: string;
  body_html: string;
  raw_flags: string[];
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

const mailApi = axios.create({
  baseURL: (import.meta.env.VITE_APPLICATIONS_API_URL || "http://127.0.0.1:8009/api/applications/").replace(/applications\/?$/, ""),
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

function attachAuth(instance: ReturnType<typeof axios.create>) {
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers = config.headers || {};
      (config.headers as any).Authorization = `Bearer ${token}`;
    }
    return config;
  });
}

attachAuth(applicationsApi);
attachAuth(mailApi);

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

  async markProcessed(
    id: number,
    isProcessed = true,
    options?: { actor?: string; action?: "approved" | "rejected" | "processed" }
  ): Promise<ApplicationItem> {
    // Важно: не кладём actor в HTTP headers — кириллица ломает setRequestHeader в браузере.
    // Передаём audit_* в body, а бэкенд подхватывает их оттуда.
    const response = await applicationsApi.patch<ApplicationItem>(
      `${id}/`,
      {
        is_processed: isProcessed,
        ...(options?.actor ? { audit_actor: options.actor } : {}),
        ...(options?.action ? { audit_action: options.action } : {}),
      },
      {
        headers: {
          // action безопасно оставлять в headers (ASCII), но пусть будет только в body для единообразия
        },
      }
    );
    return response.data;
  }

  async getApplicationAuditTrail(): Promise<ApplicationAuditItem[]> {
    const response = await applicationsApi.get<ApplicationAuditItem[]>("audit_trail/");
    return Array.isArray(response.data) ? response.data : [];
  }

  async syncMailbox(): Promise<{ synced: number; created: number; updated: number }> {
    const response = await mailApi.post("mail/sync/");
    return response.data;
  }

  async getMailFolders(): Promise<MailFolderCounts> {
    const response = await mailApi.get("mail/folders/");
    return response.data;
  }

  async getMailMessages(params?: { folder?: string; search?: string }): Promise<MailItem[]> {
    const response = await mailApi.get<MailItem[]>("mail/", { params });
    return Array.isArray(response.data) ? response.data : [];
  }

  async getMailMessage(id: number): Promise<MailDetail> {
    const response = await mailApi.get<MailDetail>(`mail/${id}/`);
    return response.data;
  }

  async sendMail(data: { to: string; subject: string; body: string; cc?: string }): Promise<MailDetail> {
    const response = await mailApi.post<MailDetail>("mail/send/", data);
    return response.data;
  }
}

export default new ApplicationService();