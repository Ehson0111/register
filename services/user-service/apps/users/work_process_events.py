import json
import logging
from urllib import error as urlerror
from urllib import request as urlrequest

from django.conf import settings


logger = logging.getLogger(__name__)


def emit_workflow_event(event_type, payload, source="user-service"):
    url = f"{settings.WORK_PROCESS_SERVICE_URL.rstrip('/')}/api/work-process/events/"
    body = json.dumps(
        {
            "event_type": event_type,
            "payload": payload,
            "source": source,
        }
    ).encode("utf-8")
    request = urlrequest.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-Workflow-Secret": settings.WORK_PROCESS_EVENT_SECRET,
        },
        method="POST",
    )

    try:
        with urlrequest.urlopen(request, timeout=3) as response:
            response.read()
    except urlerror.URLError as exc:
        logger.warning("Failed to emit workflow event %s: %s", event_type, exc)
