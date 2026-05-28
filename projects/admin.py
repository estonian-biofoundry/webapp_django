from django.contrib import admin
from .models import ProjectRun


# To register the model with the admin site and customize its display
class ProjectRunAdmin(admin.ModelAdmin):
    list_display = (
        "project_id",
        "pipeline",
        "status",
        "user",
        "created_at",
        "started_at",
        "completed_at",
        "error_message",
    )
    search_fields = ("project_id", "status", "user__username")
    list_filter = ("status", "created_at")


admin.site.register(ProjectRun, ProjectRunAdmin)
