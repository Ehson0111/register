from django.urls import path

from .views import (
    WorkflowCatalogView,
    WorkflowEventIngestView,
    WorkflowExecutionListView,
    WorkflowRunView,
    WorkflowViewSet,
    health_check,
)


workflow_list = WorkflowViewSet.as_view({"get": "list", "post": "create"})
workflow_detail = WorkflowViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
)


urlpatterns = [
    path("health/", health_check, name="work-process-health"),
    path("catalog/", WorkflowCatalogView.as_view(), name="work-process-catalog"),
    path("events/", WorkflowEventIngestView.as_view(), name="work-process-events"),
    path("workflows/", workflow_list, name="work-process-workflow-list"),
    path("workflows/<int:pk>/", workflow_detail, name="work-process-workflow-detail"),
    path("workflows/<int:workflow_id>/run/", WorkflowRunView.as_view(), name="work-process-run"),
    path(
        "workflows/<int:workflow_id>/executions/",
        WorkflowExecutionListView.as_view(),
        name="work-process-executions",
    ),
]
