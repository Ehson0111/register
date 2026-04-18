from django.contrib import admin

from .models import Workflow, WorkflowExecution


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "trigger_type", "is_active", "updated_at")
    list_filter = ("trigger_type", "is_active")
    search_fields = ("name", "description")


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "workflow", "event_type", "status", "source", "started_at")
    list_filter = ("status", "event_type", "source")
    search_fields = ("workflow__name", "error_text")
