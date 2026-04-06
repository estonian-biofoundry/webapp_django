import secrets
from django.db import models
from django.contrib.auth.models import User


# Generate unique project ID
def generate_project_id():
    return f"PRJ_{secrets.token_hex(3).upper()}"


class ProjectRun(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("RUNNING", "Running"),
        ("FAILED", "Failed"),
        ("SUCCESS", "Success"),
    ]

    # Hardcoded pipeline types for now
    PIPELINE_CHOICES = [
        ("TIMEPOINT", "Timepoint Selection"),  # single file
        ("SEQUENCE", "Sequence Analysis"),  # multiple files
    ]

    id = models.BigAutoField(primary_key=True)
    project_id = models.CharField(
        max_length=20, unique=True, default=generate_project_id, editable=False
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # For now we allow multiple files to cover both single and multi-file pipelines, also use string reference to avoid circular import
    files = models.ManyToManyField("uploads.File", related_name="projects")

    pipeline = models.CharField(max_length=20, choices=PIPELINE_CHOICES)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="CREATED")

    created_at = models.DateTimeField(auto_now_add=True)

    # create a JSON field to store pipeline-specific config (like selected columns for timepoint)
    config = models.JSONField(null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)

    completed_at = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.project_id


# pipeline 1 - timepoint selection
class TimepointResult(models.Model):
    project = models.OneToOneField(
        ProjectRun, on_delete=models.CASCADE, related_name="timepoint_result"
    )

    result_json = models.JSONField()

    last_run_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=10, choices=ProjectRun.STATUS_CHOICES, default="SUCCESS"
    )

    def __str__(self):
        return f"Result for {self.project.project_id}"
