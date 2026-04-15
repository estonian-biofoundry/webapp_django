import secrets
from django.db import models
from django.contrib.auth.models import User


# Generate unique project ID
def generate_project_id():
    return f"PRJ_{secrets.token_hex(3).upper()}"


# Main model to track project runs
class ProjectRun(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("QUEUED", "Queued"),
        ("RUNNING", "Running"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
    ]

    PIPELINE_CHOICES = [
        ("TIMEPOINT", "Timepoint Selection"),  # single file
        ("SEQUENCE", "Sequence Analysis"),  # multiple files
    ]

    id = models.BigAutoField(primary_key=True)
    project_id = models.CharField(
        max_length=20, unique=True, default=generate_project_id, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    files = models.ManyToManyField("uploads.File", related_name="projects")
    pipeline = models.CharField(max_length=20, choices=PIPELINE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)
    config = models.JSONField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)  # automatically calculated
    error_message = models.TextField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.project_id


# pipeline 1 - timepoint selection
class TimepointResult(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.OneToOneField(
        ProjectRun, on_delete=models.CASCADE, related_name="timepoint_result"
    )
    result_json = models.JSONField()

    def __str__(self):
        return f"Result for {self.project.project_id}"
