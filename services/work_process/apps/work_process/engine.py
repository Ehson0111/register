import json
from urllib import error as urlerror
from urllib import request as urlrequest

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import WorkflowExecution


MAX_STEPS = 100


def resolve_value(data, path, default=None):
    if not path:
        return default

    current = data
    for raw_part in str(path).split("."):
        part = raw_part.strip()
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part, default)
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            current = current[index] if 0 <= index < len(current) else default
        else:
            current = getattr(current, part, default)

        if current is default:
            break

    return current


def render_template(value, context):
    if isinstance(value, str):
        rendered = value
        for _ in range(20):
            start = rendered.find("{{")
            end = rendered.find("}}", start + 2)
            if start == -1 or end == -1:
                break
            key = rendered[start + 2 : end].strip()
            resolved = resolve_value(context, key, "")
            rendered = rendered[:start] + str(resolved) + rendered[end + 2 :]
        return rendered

    if isinstance(value, list):
        return [render_template(item, context) for item in value]

    if isinstance(value, dict):
        return {key: render_template(item, context) for key, item in value.items()}

    return value


def coerce_number(value):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def evaluate_condition(config, context):
    field = config.get("field") or ""
    operator = config.get("operator") or "eq"
    expected_raw = config.get("value")
    actual = resolve_value(context, field)
    expected = render_template(expected_raw, context)

    if operator == "truthy":
        return bool(actual), actual, expected
    if operator == "falsy":
        return not bool(actual), actual, expected

    actual_num = coerce_number(actual)
    expected_num = coerce_number(expected)

    if operator == "contains":
        if isinstance(actual, list):
            return expected in actual, actual, expected
        return str(expected).lower() in str(actual or "").lower(), actual, expected
    if operator == "not_contains":
        if isinstance(actual, list):
            return expected not in actual, actual, expected
        return str(expected).lower() not in str(actual or "").lower(), actual, expected
    if operator == "gt" and actual_num is not None and expected_num is not None:
        return actual_num > expected_num, actual, expected
    if operator == "gte" and actual_num is not None and expected_num is not None:
        return actual_num >= expected_num, actual, expected
    if operator == "lt" and actual_num is not None and expected_num is not None:
        return actual_num < expected_num, actual, expected
    if operator == "lte" and actual_num is not None and expected_num is not None:
        return actual_num <= expected_num, actual, expected
    if operator == "neq":
        return str(actual) != str(expected), actual, expected
    return str(actual) == str(expected), actual, expected


def outgoing_edges(graph, node_id):
    return [edge for edge in graph.get("edges", []) if str(edge.get("source")) == str(node_id)]


def next_node_id(graph, node_id, branch="default"):
    candidates = outgoing_edges(graph, node_id)
    for edge in candidates:
        if str(edge.get("branch") or "default") == branch:
            return edge.get("target")
    for edge in candidates:
        if str(edge.get("branch") or "default") == "default":
            return edge.get("target")
    return None


def perform_action(node, context, execution_logs):
    config = node.get("config") or {}
    action_type = config.get("action_type") or "log_message"

    if action_type == "log_message":
        message = render_template(config.get("message") or "Выполнено действие", context)
        execution_logs.append(
            {
                "type": "action",
                "node_id": node.get("id"),
                "action": action_type,
                "message": message,
            }
        )
        return

    if action_type == "send_email":
        recipients = render_template(config.get("to") or "", context)
        if isinstance(recipients, str):
            recipient_list = [item.strip() for item in recipients.split(",") if item.strip()]
        else:
            recipient_list = [str(item).strip() for item in recipients if str(item).strip()]
        if not recipient_list:
            raise ValueError("Для email-действия не указаны получатели.")

        subject = render_template(config.get("subject") or "CRM workflow notification", context)
        body = render_template(config.get("message") or "", context)
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=recipient_list,
            fail_silently=False,
        )
        execution_logs.append(
            {
                "type": "action",
                "node_id": node.get("id"),
                "action": action_type,
                "message": f"Отправлено письмо: {', '.join(recipient_list)}",
            }
        )
        return

    if action_type == "webhook":
        url = render_template(config.get("url") or "", context)
        if not url:
            raise ValueError("Для webhook-действия нужен URL.")
        method = str(config.get("method") or "POST").upper()
        headers = render_template(config.get("headers") or {}, context)
        body = render_template(config.get("body") or {}, context)

        payload = body
        if isinstance(body, (dict, list)):
            payload = json.dumps(body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        elif isinstance(body, str):
            payload = body.encode("utf-8")
        else:
            payload = json.dumps(body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

        request = urlrequest.Request(url, data=payload, headers=headers, method=method)
        with urlrequest.urlopen(request, timeout=10) as response:
            response.read()
            status_code = getattr(response, "status", 200)

        execution_logs.append(
            {
                "type": "action",
                "node_id": node.get("id"),
                "action": action_type,
                "message": f"Webhook {method} {url} -> {status_code}",
            }
        )
        return

    raise ValueError(f"Неизвестный тип действия: {action_type}")


def execute_graph(workflow, payload, source):
    graph = workflow.graph or {}
    nodes = graph.get("nodes") or []
    nodes_by_id = {str(node.get("id")): node for node in nodes}
    start_node = next((node for node in nodes if node.get("type") == "start"), None)
    if start_node is None:
        raise ValueError("В графе нет стартового блока.")

    logs = []
    context = {
        "event": payload or {},
        "workflow": {
            "id": workflow.id,
            "name": workflow.name,
            "trigger_type": workflow.trigger_type,
            "source": source,
        },
        "now": timezone.now().isoformat(),
    }

    current = start_node
    visited = 0

    while current and visited < MAX_STEPS:
        visited += 1
        node_type = current.get("type")
        node_id = current.get("id")

        if node_type == "start":
            logs.append(
                {
                    "type": "start",
                    "node_id": node_id,
                    "message": current.get("label") or "Старт процесса",
                }
            )
            current = nodes_by_id.get(str(next_node_id(graph, node_id)))
            continue

        if node_type == "condition":
            matched, actual, expected = evaluate_condition(current.get("config") or {}, context)
            branch = "true" if matched else "false"
            logs.append(
                {
                    "type": "condition",
                    "node_id": node_id,
                    "message": current.get("label") or "Проверка условия",
                    "result": matched,
                    "actual": actual,
                    "expected": expected,
                }
            )
            current = nodes_by_id.get(str(next_node_id(graph, node_id, branch)))
            continue

        if node_type == "action":
            perform_action(current, context, logs)
            current = nodes_by_id.get(str(next_node_id(graph, node_id)))
            continue

        raise ValueError(f"Неподдерживаемый тип блока: {node_type}")

    if visited >= MAX_STEPS:
        raise ValueError("Превышен лимит шагов. Проверьте, нет ли циклов в схеме.")

    if len(logs) == 1 and logs[0]["type"] == "start":
        return WorkflowExecution.STATUS_SKIPPED, logs, ""

    return WorkflowExecution.STATUS_SUCCESS, logs, ""


def run_workflow(workflow, event_type, payload=None, source="manual"):
    execution = WorkflowExecution.objects.create(
        workflow=workflow,
        event_type=event_type,
        source=source,
        trigger_payload=payload or {},
        status=WorkflowExecution.STATUS_SUCCESS,
        logs=[],
        finished_at=None,
    )

    try:
        status, logs, error_text = execute_graph(workflow, payload or {}, source)
        execution.status = status
        execution.logs = logs
        execution.error_text = error_text
    except (ValueError, urlerror.URLError) as exc:
        execution.status = WorkflowExecution.STATUS_FAILED
        execution.logs = [
            {
                "type": "error",
                "message": str(exc),
            }
        ]
        execution.error_text = str(exc)
    except Exception as exc:  # pragma: no cover
        execution.status = WorkflowExecution.STATUS_FAILED
        execution.logs = [
            {
                "type": "error",
                "message": str(exc),
            }
        ]
        execution.error_text = str(exc)
    finally:
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "logs", "error_text", "finished_at"])

    return execution
