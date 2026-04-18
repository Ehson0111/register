from django.conf import settings
from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .engine import run_workflow
from .models import Workflow, WorkflowExecution
from .permissions import IsManager
from .serializers import WorkflowExecutionSerializer, WorkflowSerializer


TRIGGER_OPTIONS = [
    {
        "value": Workflow.TRIGGER_MANUAL,
        "label": "Ручной запуск",
        "description": "Менеджер запускает процесс вручную из интерфейса.",
        "sample_payload": {"comment": "manual run"},
    },
    {
        "value": Workflow.TRIGGER_USER_CREATED,
        "label": "Создан новый пользователь",
        "description": "Срабатывает после создания пользователя в user-service.",
        "sample_payload": {
            "user": {
                "id": 14,
                "email": "new-user@example.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "role": "client",
            }
        },
    },
    {
        "value": Workflow.TRIGGER_DEAL_STATUS_CHANGED,
        "label": "Изменился статус сделки",
        "description": "Подходит для сценариев вроде 'клиент отказался'.",
        "sample_payload": {
            "deal": {"id": 8, "title": "Сделка #8"},
            "old_status": "in_progress",
            "new_status": "lost",
        },
    },
]

ACTION_OPTIONS = [
    {
        "value": "log_message",
        "label": "Внутренняя заметка",
        "description": "Сохраняет текст в истории выполнения процесса.",
    },
    {
        "value": "send_email",
        "label": "Отправить email",
        "description": "Отправляет письмо по SMTP-настройкам сервиса.",
    },
    {
        "value": "webhook",
        "label": "Вызвать webhook",
        "description": "Отправляет HTTP-запрос во внешний или внутренний сервис.",
    },
]

CONDITION_OPERATORS = [
    {"value": "eq", "label": "Равно"},
    {"value": "neq", "label": "Не равно"},
    {"value": "contains", "label": "Содержит"},
    {"value": "not_contains", "label": "Не содержит"},
    {"value": "gt", "label": "Больше"},
    {"value": "gte", "label": "Больше или равно"},
    {"value": "lt", "label": "Меньше"},
    {"value": "lte", "label": "Меньше или равно"},
    {"value": "truthy", "label": "Есть значение"},
    {"value": "falsy", "label": "Нет значения"},
]


class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    permission_classes = [IsManager]

    def get_queryset(self):
        queryset = (
            Workflow.objects.annotate(execution_count=Count("executions"))
            .prefetch_related(
                Prefetch(
                    "executions",
                    queryset=WorkflowExecution.objects.order_by("-started_at"),
                    to_attr="_prefetched_executions",
                )
            )
            .order_by("-updated_at", "-id")
        )
        trigger_type = self.request.query_params.get("trigger_type")
        if trigger_type:
            queryset = queryset.filter(trigger_type=trigger_type)

        for workflow in queryset:
            prefetched = getattr(workflow, "_prefetched_executions", [])
            workflow._latest_execution = prefetched[0] if prefetched else None
        return queryset


class WorkflowExecutionListView(APIView):
    permission_classes = [IsManager]

    def get(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, pk=workflow_id)
        executions = workflow.executions.order_by("-started_at")[:30]
        serializer = WorkflowExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class WorkflowRunView(APIView):
    permission_classes = [IsManager]

    def post(self, request, workflow_id):
        workflow = get_object_or_404(Workflow, pk=workflow_id)
        payload = request.data.get("payload") or {}
        execution = run_workflow(
            workflow=workflow,
            event_type=workflow.trigger_type or Workflow.TRIGGER_MANUAL,
            payload=payload,
            source="manager_ui",
        )
        serializer = WorkflowExecutionSerializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkflowCatalogView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        return Response(
            {
                "triggers": TRIGGER_OPTIONS,
                "actions": ACTION_OPTIONS,
                "operators": CONDITION_OPERATORS,
                "placeholders": [
                    "{{ event.user.email }}",
                    "{{ event.new_status }}",
                    "{{ workflow.name }}",
                ],
            }
        )


class WorkflowEventIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if request.headers.get("X-Workflow-Secret") != settings.WORK_PROCESS_EVENT_SECRET:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        event_type = request.data.get("event_type")
        payload = request.data.get("payload") or {}
        source = request.data.get("source") or "internal"
        if not event_type:
            return Response({"error": "event_type is required"}, status=status.HTTP_400_BAD_REQUEST)

        workflows = Workflow.objects.filter(is_active=True, trigger_type=event_type).order_by("-updated_at")
        executions = []
        for workflow in workflows:
            execution = run_workflow(
                workflow=workflow,
                event_type=event_type,
                payload=payload,
                source=source,
            )
            executions.append(execution)

        serializer = WorkflowExecutionSerializer(executions, many=True)
        return Response(
            {
                "matched_workflows": workflows.count(),
                "executions": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


def health_check(request):
    return JsonResponse({"status": "healthy", "service": "work-process"})
