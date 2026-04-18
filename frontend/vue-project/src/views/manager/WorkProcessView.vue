<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-3">
      <div>
        <h2 class="text-2xl font-bold text-gray-900">Автоматизация рабочих процессов</h2>
        <p class="text-gray-600 mt-1">
          Создавайте блок-схемы из условий и действий: при создании пользователя, отказе клиента и других событиях.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50"
          @click="createWorkflow"
        >
          + Новый процесс
        </button>
        <button
          class="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
          :disabled="!selectedWorkflow || saving"
          @click="saveWorkflow"
        >
          {{ saving ? "Сохранение..." : "Сохранить" }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-12 gap-4">
      <aside class="xl:col-span-3 bg-white border border-gray-200 rounded-lg p-3 space-y-2 max-h-[80vh] overflow-auto">
        <div
          v-for="item in workflows"
          :key="item.id"
          class="p-3 rounded-lg border cursor-pointer transition-colors"
          :class="selectedWorkflow?.id === item.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'"
          @click="selectWorkflow(item.id)"
        >
          <div class="flex justify-between items-start gap-2">
            <div>
              <p class="font-medium text-gray-900">{{ item.name }}</p>
              <p class="text-xs text-gray-500">{{ triggerLabel(item.trigger_type) }}</p>
            </div>
            <span
              class="inline-flex px-2 py-1 rounded-full text-xs"
              :class="item.is_active ? 'bg-green-100 text-green-700' : 'bg-slate-300 text-slate-900'"
            >
              {{ item.is_active ? "Активен" : "Пауза" }}
            </span>
          </div>
          <div class="mt-2 text-xs text-gray-500">
            Запусков: {{ item.execution_count || 0 }}
          </div>
        </div>
      </aside>

      <section class="xl:col-span-9 space-y-4">
        <div v-if="!selectedWorkflow" class="bg-white border border-gray-200 rounded-lg p-8 text-center text-gray-500">
          Выберите процесс слева или создайте новый.
        </div>

        <template v-else>
          <div class="bg-white border border-gray-200 rounded-lg p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
            <label class="space-y-1">
              <span class="text-sm text-gray-600">Название</span>
              <input v-model="selectedWorkflow.name" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </label>
            <label class="space-y-1">
              <span class="text-sm text-gray-600">Триггер</span>
              <select v-model="selectedWorkflow.trigger_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                <option v-for="tr in catalog.triggers" :key="tr.value" :value="tr.value">{{ tr.label }}</option>
              </select>
            </label>
            <label class="space-y-1 md:col-span-2">
              <span class="text-sm text-gray-600">Описание</span>
              <textarea
                v-model="selectedWorkflow.description"
                rows="2"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              />
            </label>
            <label class="inline-flex items-center gap-2">
              <input v-model="selectedWorkflow.is_active" type="checkbox" />
              <span class="text-sm text-gray-700">Процесс активен</span>
            </label>
            <div class="text-right">
              <button class="px-3 py-2 rounded-lg border border-red-300 text-red-700 hover:bg-red-50" @click="deleteCurrent">
                Удалить процесс
              </button>
            </div>
          </div>

          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
              <div class="font-medium text-gray-900">Конструктор блок-схемы</div>
              <div class="flex items-center gap-2 text-sm">
                <button class="px-3 py-1.5 rounded border border-gray-300 hover:bg-gray-50" @click="addNode('condition')">
                  + Условие
                </button>
                <button class="px-3 py-1.5 rounded border border-gray-300 hover:bg-gray-50" @click="addNode('action')">
                  + Действие
                </button>
                <button
                  v-if="connectState"
                  class="px-3 py-1.5 rounded border border-amber-300 text-amber-700 bg-amber-50"
                  @click="connectState = null"
                >
                  Отменить связь
                </button>
              </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
              <div class="lg:col-span-2">
                <div
                  ref="canvasRef"
                  class="relative h-[430px] rounded-lg border border-gray-200 bg-slate-50 overflow-hidden"
                  @mousemove="onCanvasMouseMove"
                  @mouseup="onCanvasMouseUp"
                  @mouseleave="onCanvasMouseUp"
                >
                  <svg class="absolute inset-0 w-full h-full pointer-events-none">
                    <line
                      v-for="edge in graphEdges"
                      :key="edge.id"
                      :x1="edge.x1"
                      :y1="edge.y1"
                      :x2="edge.x2"
                      :y2="edge.y2"
                      stroke="#94a3b8"
                      stroke-width="2"
                    />
                    <text
                      v-for="edge in graphEdges"
                      :key="`label-${edge.id}`"
                      :x="(edge.x1 + edge.x2) / 2"
                      :y="(edge.y1 + edge.y2) / 2 - 6"
                      fill="#475569"
                      font-size="11"
                      text-anchor="middle"
                    >
                      {{ edge.branch }}
                    </text>
                  </svg>

                  <div
                    v-for="node in selectedWorkflow.graph.nodes"
                    :key="node.id"
                    class="absolute w-52 rounded-lg border shadow-sm select-none"
                    :class="nodeClasses(node)"
                    :style="{ left: `${node.position.x}px`, top: `${node.position.y}px` }"
                    @mousedown.stop="startDrag(node, $event)"
                    @click.stop="onNodeClick(node)"
                  >
                    <div class="px-3 py-2 border-b border-gray-200 flex items-center justify-between">
                      <div class="font-medium text-sm truncate">{{ node.label || node.type }}</div>
                      <button
                        v-if="node.type !== 'start'"
                        class="text-xs text-red-600 hover:underline"
                        @click.stop="removeNode(node.id)"
                      >
                        удалить
                      </button>
                    </div>
                    <div class="px-3 py-2 text-xs text-gray-600">
                      {{ nodeTypeLabel(node.type) }}
                    </div>
                    <div class="px-3 pb-3 flex flex-wrap gap-1">
                      <button
                        class="px-2 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"
                        @click.stop="armConnect(node.id, 'default')"
                      >
                        Связь
                      </button>
                      <button
                        v-if="node.type === 'condition'"
                        class="px-2 py-1 text-xs rounded border border-green-300 text-green-700 hover:bg-green-50"
                        @click.stop="armConnect(node.id, 'true')"
                      >
                        Если ДА
                      </button>
                      <button
                        v-if="node.type === 'condition'"
                        class="px-2 py-1 text-xs rounded border border-red-300 text-red-700 hover:bg-red-50"
                        @click.stop="armConnect(node.id, 'false')"
                      >
                        Если НЕТ
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="border border-gray-200 rounded-lg p-3 bg-white space-y-3">
                <div class="font-medium text-gray-900">Свойства блока</div>
                <div v-if="!selectedNode" class="text-sm text-gray-500">Кликните на блок, чтобы редактировать параметры.</div>
                <template v-else>
                  <label class="space-y-1 block">
                    <span class="text-sm text-gray-600">Название</span>
                    <input v-model="selectedNode.label" type="text" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
                  </label>

                  <template v-if="selectedNode.type === 'condition'">
                    <label class="space-y-1 block">
                      <span class="text-sm text-gray-600">Поле (из события)</span>
                      <input
                        v-model="selectedNode.config.field"
                        type="text"
                        placeholder="event.new_status"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </label>
                    <label class="space-y-1 block">
                      <span class="text-sm text-gray-600">Оператор</span>
                      <select v-model="selectedNode.config.operator" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                        <option v-for="op in catalog.operators" :key="op.value" :value="op.value">{{ op.label }}</option>
                      </select>
                    </label>
                    <label class="space-y-1 block">
                      <span class="text-sm text-gray-600">Значение</span>
                      <input
                        v-model="selectedNode.config.value"
                        type="text"
                        placeholder="lost"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                      />
                    </label>
                  </template>

                  <template v-if="selectedNode.type === 'action'">
                    <label class="space-y-1 block">
                      <span class="text-sm text-gray-600">Тип действия</span>
                      <select v-model="selectedNode.config.action_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                        <option v-for="ac in catalog.actions" :key="ac.value" :value="ac.value">{{ ac.label }}</option>
                      </select>
                    </label>

                    <template v-if="selectedNode.config.action_type === 'send_email'">
                      <label class="space-y-1 block">
                        <span class="text-sm text-gray-600">Кому</span>
                        <input
                          v-model="selectedNode.config.to"
                          type="text"
                          placeholder="manager@crm.local"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </label>
                      <label class="space-y-1 block">
                        <span class="text-sm text-gray-600">Тема</span>
                        <input
                          v-model="selectedNode.config.subject"
                          type="text"
                          placeholder="Новый пользователь: {{ event.user.email }}"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </label>
                    </template>

                    <template v-if="selectedNode.config.action_type === 'webhook'">
                      <label class="space-y-1 block">
                        <span class="text-sm text-gray-600">Webhook URL</span>
                        <input
                          v-model="selectedNode.config.url"
                          type="text"
                          placeholder="http://localhost:8010/api/chat/telegram/inbound/"
                          class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      </label>
                    </template>

                    <label class="space-y-1 block">
                      <span class="text-sm text-gray-600">Сообщение / body</span>
                      <textarea
                        v-model="selectedNode.config.message"
                        rows="3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        placeholder="Клиент {{ event.user.email }} создан"
                      />
                    </label>
                  </template>
                </template>
              </div>
            </div>
          </div>

          <div class="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
            <div class="flex items-center justify-between gap-2">
              <div class="font-medium text-gray-900">Тестовый запуск</div>
              <button
                class="px-3 py-1.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60"
                :disabled="running || !selectedWorkflow"
                @click="runSelected"
              >
                {{ running ? "Запуск..." : "Запустить сейчас" }}
              </button>
            </div>
            <textarea
              v-model="testPayloadText"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
              rows="6"
              placeholder='{"new_status":"lost"}'
            />
            <div class="text-xs text-gray-500">
              Доступные плейсхолдеры: {{ (catalog.placeholders || []).join(", ") }}
            </div>
          </div>

          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <div class="font-medium text-gray-900 mb-3">История выполнений</div>
            <div v-if="executions.length === 0" class="text-sm text-gray-500">Пока запусков не было.</div>
            <div v-else class="space-y-2 max-h-64 overflow-auto">
              <div v-for="execution in executions" :key="execution.id" class="border border-gray-200 rounded-lg p-3">
                <div class="flex items-center justify-between gap-2">
                  <div class="text-sm font-medium text-gray-900">
                    {{ execution.workflow_name }} / {{ execution.event_type }}
                  </div>
                  <span
                    class="inline-flex px-2 py-1 rounded-full text-xs"
                    :class="statusClass(execution.status)"
                  >
                    {{ execution.status }}
                  </span>
                </div>
                <div class="text-xs text-gray-500 mt-1">{{ formatDate(execution.started_at) }}</div>
                <div class="text-xs text-gray-700 mt-1" v-if="execution.error_text">{{ execution.error_text }}</div>
                <ul class="mt-2 text-xs text-gray-600 list-disc pl-5">
                  <li v-for="(log, idx) in execution.logs" :key="idx">{{ log.message || JSON.stringify(log) }}</li>
                </ul>
              </div>
            </div>
          </div>
        </template>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import workProcessService, { type Workflow, type WorkflowExecution, type WorkflowNode } from "../../services/workProcessService";
import { useToast } from "../../composables/useToast";

const workflows = ref<Workflow[]>([]);
const selectedWorkflow = ref<Workflow | null>(null);
const selectedNodeId = ref<string | null>(null);
const executions = ref<WorkflowExecution[]>([]);
const catalog = ref<any>({ triggers: [], actions: [], operators: [], placeholders: [] });
const saving = ref(false);
const running = ref(false);
const testPayloadText = ref('{"comment":"manual test"}');
const canvasRef = ref<HTMLElement | null>(null);
const { showError, showSuccess } = useToast();

const dragState = ref<{
  nodeId: string;
  offsetX: number;
  offsetY: number;
} | null>(null);

const connectState = ref<{
  sourceId: string;
  branch: "default" | "true" | "false";
} | null>(null);

const selectedNode = computed<WorkflowNode | null>(() => {
  if (!selectedWorkflow.value || !selectedNodeId.value) return null;
  return selectedWorkflow.value.graph.nodes.find((node) => node.id === selectedNodeId.value) || null;
});

type RenderEdge = { id: string; branch: "default" | "true" | "false"; x1: number; y1: number; x2: number; y2: number };

const graphEdges = computed<RenderEdge[]>(() => {
  if (!selectedWorkflow.value) return [];
  const nodesMap = new Map<string, WorkflowNode>(selectedWorkflow.value.graph.nodes.map((n) => [n.id, n]));
  return selectedWorkflow.value.graph.edges
    .map((edge) => {
      const source = nodesMap.get(edge.source);
      const target = nodesMap.get(edge.target);
      if (!source || !target) return null;
      return {
        id: edge.id,
        branch: edge.branch || "default",
        x1: source.position.x + 208,
        y1: source.position.y + 52,
        x2: target.position.x,
        y2: target.position.y + 52,
      };
    })
    .filter((edge): edge is RenderEdge => Boolean(edge));
});

const uid = (prefix: string) => `${prefix}-${Math.random().toString(36).slice(2, 10)}`;

const clone = <T>(data: T): T => JSON.parse(JSON.stringify(data));

const nodeTypeLabel = (type: string) => {
  if (type === "start") return "Старт";
  if (type === "condition") return "Условие";
  return "Действие";
};

const nodeClasses = (node: WorkflowNode) => {
  const active = selectedNodeId.value === node.id;
  if (node.type === "start") return active ? "bg-indigo-50 border-indigo-500" : "bg-indigo-50 border-indigo-300";
  if (node.type === "condition") return active ? "bg-amber-50 border-amber-500" : "bg-amber-50 border-amber-300";
  return active ? "bg-emerald-50 border-emerald-500" : "bg-white border-gray-300";
};

const triggerLabel = (trigger: string) => {
  const found = (catalog.value.triggers || []).find((t: any) => t.value === trigger);
  return found?.label || trigger;
};

const statusClass = (status: string) => {
  if (status === "success") return "bg-green-100 text-green-700";
  if (status === "failed") return "bg-red-100 text-red-700";
  return "bg-slate-300 text-slate-900";
};

const formatDate = (value: string) => new Date(value).toLocaleString("ru-RU");

const loadAll = async () => {
  try {
    const [workflowList, catalogData] = await Promise.all([
      workProcessService.getWorkflows(),
      workProcessService.getCatalog(),
    ]);
    workflows.value = workflowList;
    catalog.value = catalogData;
    if (workflowList.length && !selectedWorkflow.value) {
      const firstWorkflow = workflowList[0];
      if (firstWorkflow) {
        await selectWorkflow(firstWorkflow.id);
      }
    }
  } catch (error) {
    console.error("Не удалось загрузить автоматизации", error);
    showError("Не удалось загрузить процессы. Проверь запуск work-process сервиса.");
  }
};

const selectWorkflow = async (id: number) => {
  const found = workflows.value.find((item) => item.id === id);
  if (!found) return;
  selectedWorkflow.value = clone(found);
  selectedNodeId.value = selectedWorkflow.value.graph.nodes[0]?.id || null;
  executions.value = await workProcessService.getWorkflowExecutions(id);
};

const createWorkflow = async () => {
  try {
    const created = await workProcessService.createWorkflow({
      name: "Новый процесс",
      description: "",
      is_active: true,
      trigger_type: "manual",
    });
    workflows.value = [created, ...workflows.value];
    await selectWorkflow(created.id);
    showSuccess("Новый процесс создан");
  } catch (error) {
    console.error("Не удалось создать процесс", error);
    showError("Не удалось создать процесс. Проверь доступность API /api/work-process/.");
  }
};

const saveWorkflow = async () => {
  if (!selectedWorkflow.value) return;
  saving.value = true;
  try {
    const updated = await workProcessService.updateWorkflow(selectedWorkflow.value.id, {
      name: selectedWorkflow.value.name,
      description: selectedWorkflow.value.description,
      trigger_type: selectedWorkflow.value.trigger_type,
      is_active: selectedWorkflow.value.is_active,
      graph: selectedWorkflow.value.graph,
    });
    const idx = workflows.value.findIndex((item) => item.id === updated.id);
    if (idx >= 0) workflows.value[idx] = updated;
    selectedWorkflow.value = clone(updated);
    showSuccess("Процесс сохранен");
  } catch (error) {
    console.error("Ошибка сохранения процесса", error);
    showError("Не удалось сохранить процесс");
  } finally {
    saving.value = false;
  }
};

const deleteCurrent = async () => {
  if (!selectedWorkflow.value) return;
  if (!confirm("Удалить процесс?")) return;
  try {
    await workProcessService.deleteWorkflow(selectedWorkflow.value.id);
    workflows.value = workflows.value.filter((item) => item.id !== selectedWorkflow.value?.id);
    selectedWorkflow.value = null;
    selectedNodeId.value = null;
    executions.value = [];
    showSuccess("Процесс удален");
  } catch (error) {
    console.error("Ошибка удаления процесса", error);
    showError("Не удалось удалить процесс");
  }
};

const addNode = (type: "condition" | "action") => {
  if (!selectedWorkflow.value) return;
  const id = uid(type);
  const node: WorkflowNode = {
    id,
    type,
    label: type === "condition" ? "Новое условие" : "Новое действие",
    position: { x: 120 + Math.floor(Math.random() * 220), y: 60 + Math.floor(Math.random() * 220) },
    config:
      type === "condition"
        ? { field: "event.new_status", operator: "eq", value: "lost" }
        : { action_type: "log_message", message: "Выполнено действие {{ workflow.name }}" },
  };
  selectedWorkflow.value.graph.nodes.push(node);
  selectedNodeId.value = node.id;
};

const removeNode = (nodeId: string) => {
  if (!selectedWorkflow.value) return;
  selectedWorkflow.value.graph.nodes = selectedWorkflow.value.graph.nodes.filter((node) => node.id !== nodeId);
  selectedWorkflow.value.graph.edges = selectedWorkflow.value.graph.edges.filter(
    (edge) => edge.source !== nodeId && edge.target !== nodeId
  );
  if (selectedNodeId.value === nodeId) selectedNodeId.value = null;
};

const armConnect = (sourceId: string, branch: "default" | "true" | "false") => {
  connectState.value = { sourceId, branch };
};

const onNodeClick = (node: WorkflowNode) => {
  if (!selectedWorkflow.value) return;
  if (connectState.value) {
    const { sourceId, branch } = connectState.value;
    if (sourceId !== node.id) {
      const edgeId = uid("edge");
      selectedWorkflow.value.graph.edges = selectedWorkflow.value.graph.edges.filter(
        (edge) => !(edge.source === sourceId && (edge.branch || "default") === branch)
      );
      selectedWorkflow.value.graph.edges.push({
        id: edgeId,
        source: sourceId,
        target: node.id,
        branch,
      });
    }
    connectState.value = null;
  }
  selectedNodeId.value = node.id;
};

const startDrag = (node: WorkflowNode, event: MouseEvent) => {
  const canvas = canvasRef.value;
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  dragState.value = {
    nodeId: node.id,
    offsetX: event.clientX - rect.left - node.position.x,
    offsetY: event.clientY - rect.top - node.position.y,
  };
};

const onCanvasMouseMove = (event: MouseEvent) => {
  if (!dragState.value || !selectedWorkflow.value || !canvasRef.value) return;
  const node = selectedWorkflow.value.graph.nodes.find((item) => item.id === dragState.value?.nodeId);
  if (!node) return;
  const rect = canvasRef.value.getBoundingClientRect();
  node.position.x = Math.max(0, Math.min(rect.width - 216, event.clientX - rect.left - dragState.value.offsetX));
  node.position.y = Math.max(0, Math.min(rect.height - 110, event.clientY - rect.top - dragState.value.offsetY));
};

const onCanvasMouseUp = () => {
  dragState.value = null;
};

const runSelected = async () => {
  if (!selectedWorkflow.value) return;
  running.value = true;
  try {
    let payload: Record<string, any> = {};
    if (testPayloadText.value.trim()) {
      payload = JSON.parse(testPayloadText.value);
    }
    const execution = await workProcessService.runWorkflow(selectedWorkflow.value.id, payload);
    executions.value = [execution, ...executions.value].slice(0, 30);
    showSuccess(`Запуск выполнен: ${execution.status}`);
  } catch (error) {
    console.error("Ошибка запуска процесса", error);
    showError("Не удалось выполнить запуск. Проверь JSON и состояние сервиса.");
  } finally {
    running.value = false;
  }
};

onMounted(async () => {
  await loadAll();
});
</script>
