from django.db import transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import ProjectRun
from .tasks import run_timepoint
from .utils import handle_timepoint, handle_sequence, is_stuck, get_user_files


@login_required
def create_project(request):
    user_files = get_user_files(request.user)

    if request.method == "POST":
        pipeline = request.POST.get("pipeline")

        if pipeline == "TIMEPOINT":
            cleaned_data, error = handle_timepoint(request)
            if error:
                return render(
                    request,
                    "projects/project.html",
                    {"user_files": user_files, "error": error},
                )

            project = ProjectRun.objects.create(
                user=request.user,
                pipeline="TIMEPOINT",
                config={
                    "group_fields": cleaned_data["group_fields"],
                    "dose_field": cleaned_data["dose_field"],
                    "od_field": cleaned_data["od_field"],
                    "time_field": cleaned_data["time_field"],
                },
            )
            project.files.add(cleaned_data["file"])
            return redirect("dashboard:dashboard")

        elif pipeline == "SEQUENCE":
            cleaned_data, error = handle_sequence(request)
            if error:
                return render(
                    request,
                    "projects/project.html",
                    {"user_files": user_files, "error": error},
                )

            project = ProjectRun.objects.create(user=request.user, pipeline="SEQUENCE")
            project.files.add(cleaned_data["ref_file"], *cleaned_data["read_files"])
            return redirect("dashboard:dashboard")

    # GET request → render empty form
    return render(
        request, "projects/project.html", {"user_files": user_files, "error": None}
    )


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(ProjectRun, id=project_id)

    result = None
    if project.pipeline == "TIMEPOINT":
        try:
            result = project.timepoint_result
        except Exception:
            result = None

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "result": result,
        },
    )


@login_required
def run_project_celery(request, project_id):
    project = get_object_or_404(ProjectRun, id=project_id)

    if project.status in ["QUEUED", "RUNNING"] and not is_stuck(project):
        return redirect("dashboard:dashboard")

    with transaction.atomic():
        # Clear old results on rerun
        if hasattr(project, "timepoint_result"):
            project.timepoint_result.delete()

        # Reset project state
        project.status = "QUEUED"
        project.error_message = None
        project.started_at = None
        project.completed_at = None
        project.save()

        def queue_task():
            try:
                run_timepoint.delay(project.id)
            except Exception:
                project.status = "FAILED"
                project.error_message = "Could not connect to Redis. Task not queued."
                project.save()

        transaction.on_commit(queue_task)

    return redirect("dashboard:dashboard")
