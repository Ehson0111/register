import json
from pathlib import Path
from uuid import uuid4
from urllib import request as urlrequest
from django.utils.deprecation import MiddlewareMixin


def _resolve_log_path() -> Path:
    cur = Path(__file__).resolve()
    for parent in cur.parents:
        if (parent / "manage.py").exists():
            return parent / "debug-ad25e9.log"
    return Path.cwd() / "debug-ad25e9.log"


LOG_PATH = _resolve_log_path()


def _dbg(hypothesis_id: str, location: str, message: str, data: dict):
    payload = {
        "sessionId": "ad25e9",
        "runId": "run1",
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": __import__("time").time_ns() // 1_000_000,
        "id": f"log_{uuid4().hex}",
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    try:
        # #region agent log
        req = urlrequest.Request(
            "http://host.docker.internal:7647/ingest/66103dc7-eaf0-4803-be05-aba9d5dec07c",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "X-Debug-Session-Id": "ad25e9",
            },
            method="POST",
        )
        urlrequest.urlopen(req, timeout=1).read()
        # #endregion
    except Exception:
        pass


class DebugApplicationsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith("/api/applications"):
            # #region agent log
            _dbg(
                "H1",
                "debug_middleware.py:process_request",
                "applications request received",
                {
                    "path": request.path,
                    "method": request.method,
                    "has_auth_header": bool(request.headers.get("Authorization")),
                    "auth_header_prefix": (request.headers.get("Authorization", "")[:12] or ""),
                },
            )
            # #endregion
        return None

    def process_response(self, request, response):
        if request.path.startswith("/api/applications"):
            # #region agent log
            _dbg(
                "H2",
                "debug_middleware.py:process_response",
                "applications response sent",
                {
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                },
            )
            # #endregion
        return response
