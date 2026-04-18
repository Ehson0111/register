import api from "./api.js";

export type WorkflowTriggerType = "manual" | "user_created" | "deal_status_changed";
export type WorkflowNodeType = "start" | "condition" | "action";

export interface WorkflowNode {
  id: string;
  type: WorkflowNodeType;
  label: string;
  position: { x: number; y: number };
  config: Record<string, any>;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  branch?: "default" | "true" | "false";
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
}

export interface Workflow {
  id: number;
  name: string;
  description: string;
  is_active: boolean;
  trigger_type: WorkflowTriggerType;
  graph: WorkflowGraph;
  execution_count: number;
  last_execution_status: "success" | "failed" | "skipped" | null;
  created_at: string;
  updated_at: string;
}

export interface WorkflowExecution {
  id: number;
  workflow: number;
  workflow_name: string;
  event_type: string;
  source: string;
  trigger_payload: Record<string, any>;
  status: "success" | "failed" | "skipped";
  logs: Array<Record<string, any>>;
  error_text: string;
  started_at: string;
  finished_at: string | null;
}

class WorkProcessService {
  async getCatalog(): Promise<any> {
    const response = await api.get("/work-process/catalog/");
    return response.data;
  }

  async getWorkflows(): Promise<Workflow[]> {
    const response = await api.get("/work-process/workflows/");
    return response.data;
  }

  async createWorkflow(payload: Partial<Workflow>): Promise<Workflow> {
    const response = await api.post("/work-process/workflows/", payload);
    return response.data;
  }

  async updateWorkflow(id: number, payload: Partial<Workflow>): Promise<Workflow> {
    const response = await api.patch(`/work-process/workflows/${id}/`, payload);
    return response.data;
  }

  async deleteWorkflow(id: number): Promise<void> {
    await api.delete(`/work-process/workflows/${id}/`);
  }

  async runWorkflow(id: number, payload?: Record<string, any>): Promise<WorkflowExecution> {
    const response = await api.post(`/work-process/workflows/${id}/run/`, { payload: payload || {} });
    return response.data;
  }

  async getWorkflowExecutions(id: number): Promise<WorkflowExecution[]> {
    const response = await api.get(`/work-process/workflows/${id}/executions/`);
    return response.data;
  }
}

export default new WorkProcessService();
