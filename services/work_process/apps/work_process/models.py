from django.db import models


class Workflow(models.Model):
    TRIGGER_MANUAL = "manual"
    TRIGGER_USER_CREATED = "user_created"
    TRIGGER_DEAL_STATUS_CHANGED = "deal_status_changed"

    TRIGGER_CHOICES = [
        (TRIGGER_MANUAL, "Manual launch"),
        (TRIGGER_USER_CREATED, "User created"),
        (TRIGGER_DEAL_STATUS_CHANGED, "Deal status changed"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    trigger_type = models.CharField(max_length=64, choices=TRIGGER_CHOICES, default=TRIGGER_MANUAL)
    graph = models.JSONField(default=dict, blank=True)
    created_by_id = models.IntegerField(null=True, blank=True)
    created_by_email = models.CharField(max_length=255, blank=True, default="")
    created_by_name = models.CharField(max_length=255, blank=True, default="")
    created_by_role = models.CharField(max_length=64, blank=True, default="")
    updated_by_id = models.IntegerField(null=True, blank=True)
    updated_by_email = models.CharField(max_length=255, blank=True, default="")
    updated_by_name = models.CharField(max_length=255, blank=True, default="")
    updated_by_role = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-id"]

    def __str__(self):
        return self.name


class WorkflowExecution(models.Model):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_SKIPPED = "skipped"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name="executions",
    )
    event_type = models.CharField(max_length=64)
    source = models.CharField(max_length=128, blank=True, default="")
    trigger_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_SUCCESS)
    logs = models.JSONField(default=list, blank=True)
    error_text = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at", "-id"]

    def __str__(self):
        return f"{self.workflow.name} [{self.status}]"
