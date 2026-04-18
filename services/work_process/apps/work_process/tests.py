from django.test import TestCase

from .engine import run_workflow
from .models import Workflow, WorkflowExecution


class WorkflowEngineTests(TestCase):
    def test_condition_branch_executes_action(self):
        workflow = Workflow.objects.create(
            name="Lost deal notification",
            trigger_type=Workflow.TRIGGER_DEAL_STATUS_CHANGED,
            graph={
                "nodes": [
                    {"id": "start", "type": "start", "label": "Старт", "position": {"x": 0, "y": 0}, "config": {}},
                    {
                        "id": "check-status",
                        "type": "condition",
                        "label": "Проверить статус",
                        "position": {"x": 200, "y": 0},
                        "config": {"field": "event.new_status", "operator": "eq", "value": "lost"},
                    },
                    {
                        "id": "notify",
                        "type": "action",
                        "label": "Заметка",
                        "position": {"x": 400, "y": 0},
                        "config": {"action_type": "log_message", "message": "Клиент отказался"},
                    },
                ],
                "edges": [
                    {"id": "e1", "source": "start", "target": "check-status", "branch": "default"},
                    {"id": "e2", "source": "check-status", "target": "notify", "branch": "true"},
                ],
            },
        )

        execution = run_workflow(
            workflow=workflow,
            event_type=Workflow.TRIGGER_DEAL_STATUS_CHANGED,
            payload={"new_status": "lost"},
            source="test",
        )

        self.assertEqual(execution.status, WorkflowExecution.STATUS_SUCCESS)
        self.assertTrue(any(log.get("message") == "Клиент отказался" for log in execution.logs))

    def test_empty_graph_after_start_is_skipped(self):
        workflow = Workflow.objects.create(
            name="Manual noop",
            trigger_type=Workflow.TRIGGER_MANUAL,
            graph={
                "nodes": [
                    {"id": "start", "type": "start", "label": "Старт", "position": {"x": 0, "y": 0}, "config": {}},
                ],
                "edges": [],
            },
        )

        execution = run_workflow(
            workflow=workflow,
            event_type=Workflow.TRIGGER_MANUAL,
            payload={"comment": "noop"},
            source="test",
        )

        self.assertEqual(execution.status, WorkflowExecution.STATUS_SKIPPED)
