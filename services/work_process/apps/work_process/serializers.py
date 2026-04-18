from rest_framework import serializers

from .models import Workflow, WorkflowExecution


def default_graph():
    return {
        "nodes": [
            {
                "id": "start-1",
                "type": "start",
                "label": "Старт",
                "position": {"x": 80, "y": 180},
                "config": {},
            },
            {
                "id": "action-1",
                "type": "action",
                "label": "Действие",
                "position": {"x": 340, "y": 180},
                "config": {
                    "action_type": "log_message",
                    "message": "Процесс {{ workflow.name }} выполнен",
                },
            },
        ],
        "edges": [
            {
                "id": "edge-start-1-action-1-default",
                "source": "start-1",
                "target": "action-1",
                "branch": "default",
            }
        ],
    }


class WorkflowSerializer(serializers.ModelSerializer):
    execution_count = serializers.IntegerField(read_only=True)
    last_execution_status = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "trigger_type",
            "graph",
            "created_by_id",
            "created_by_email",
            "created_by_name",
            "created_by_role",
            "updated_by_id",
            "updated_by_email",
            "updated_by_name",
            "updated_by_role",
            "created_at",
            "updated_at",
            "execution_count",
            "last_execution_status",
        ]
        read_only_fields = [
            "created_by_id",
            "created_by_email",
            "created_by_name",
            "created_by_role",
            "updated_by_id",
            "updated_by_email",
            "updated_by_name",
            "updated_by_role",
            "created_at",
            "updated_at",
            "execution_count",
            "last_execution_status",
        ]

    def get_last_execution_status(self, obj):
        latest = getattr(obj, "_latest_execution", None)
        if latest is not None:
            return latest.status
        last_execution = obj.executions.order_by("-started_at").first()
        return last_execution.status if last_execution else None

    def validate_graph(self, value):
        graph = value or {}
        nodes = graph.get("nodes") or []
        edges = graph.get("edges") or []

        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise serializers.ValidationError("Граф процесса должен содержать списки nodes и edges.")

        if not nodes:
            raise serializers.ValidationError("Добавьте хотя бы один блок.")

        node_ids = set()
        start_nodes = 0
        for node in nodes:
            if not isinstance(node, dict):
                raise serializers.ValidationError("Каждый блок должен быть объектом.")
            node_id = str(node.get("id") or "").strip()
            node_type = str(node.get("type") or "").strip()
            if not node_id:
                raise serializers.ValidationError("У каждого блока должен быть id.")
            if node_id in node_ids:
                raise serializers.ValidationError(f"Повторяющийся id блока: {node_id}.")
            node_ids.add(node_id)
            if node_type == "start":
                start_nodes += 1

        if start_nodes != 1:
            raise serializers.ValidationError("В процессе должен быть ровно один стартовый блок.")

        for edge in edges:
            if not isinstance(edge, dict):
                raise serializers.ValidationError("Каждая связь должна быть объектом.")
            source = str(edge.get("source") or "").strip()
            target = str(edge.get("target") or "").strip()
            if not source or not target:
                raise serializers.ValidationError("У каждой связи должны быть source и target.")
            if source not in node_ids or target not in node_ids:
                raise serializers.ValidationError("Связь указывает на несуществующий блок.")

        return graph

    def create(self, validated_data):
        validated_data["graph"] = validated_data.get("graph") or default_graph()
        user = self.context["request"].user
        validated_data["created_by_id"] = getattr(user, "id", None)
        validated_data["created_by_email"] = getattr(user, "email", "") or ""
        validated_data["created_by_name"] = (
            f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
            or getattr(user, "email", "")
            or "manager"
        )
        validated_data["created_by_role"] = getattr(user, "role", "") or ""
        validated_data["updated_by_id"] = validated_data["created_by_id"]
        validated_data["updated_by_email"] = validated_data["created_by_email"]
        validated_data["updated_by_name"] = validated_data["created_by_name"]
        validated_data["updated_by_role"] = validated_data["created_by_role"]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data["updated_by_id"] = getattr(user, "id", None)
        validated_data["updated_by_email"] = getattr(user, "email", "") or ""
        validated_data["updated_by_name"] = (
            f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
            or getattr(user, "email", "")
            or "manager"
        )
        validated_data["updated_by_role"] = getattr(user, "role", "") or ""
        return super().update(instance, validated_data)


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    workflow_name = serializers.CharField(source="workflow.name", read_only=True)

    class Meta:
        model = WorkflowExecution
        fields = [
            "id",
            "workflow",
            "workflow_name",
            "event_type",
            "source",
            "trigger_payload",
            "status",
            "logs",
            "error_text",
            "started_at",
            "finished_at",
        ]
        read_only_fields = fields
