from django.db import transaction
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .models import ProjectRun
from .tasks import run_timepoint
from .utils import  handle_sequence, is_stuck, get_user_files,validate_timepoint_logic, get_user_file
# handle_timepoint,
@login_required
def create_project(request):
    user_files = get_user_files(request.user)

    if request.method == "POST":
        pipeline = request.POST.get("pipeline")

        if pipeline == "TIMEPOINT":
            # 1. Manually pull data from POST for the validator
            file_id = request.POST.get("timepoint_file")
            file_obj = get_user_file(request.user, file_id) 
            
            config_data = {
                "group_fields": [f.strip() for f in request.POST.get("group_fields", "").split(",")],
                "dose_field": request.POST.get("dose_field"),
                "od_field": request.POST.get("od_field"),
                "time_field": request.POST.get("time_field"),
            }

            # 2. Call the SHARED logic
            is_valid, error = validate_timepoint_logic(file_obj, config_data)
            
            if not is_valid:
                return render(request, "projects/project.html", {
                    "user_files": user_files, "error": error
                })

            # 3. Success -> Create the project
            project = ProjectRun.objects.create(
                user=request.user,
                pipeline="TIMEPOINT",
                config=config_data,
            )
            project.files.add(file_obj)
            run_timepoint.delay(project.id) # Trigger celery!
            return redirect("dashboard:dashboard")

        elif pipeline == "SEQUENCE":
            # Keeping your old sequence handler for now
            cleaned_data, error = handle_sequence(request) 
            if error:
                return render(request, "projects/project.html", {
                    "user_files": user_files, "error": error
                })

            project = ProjectRun.objects.create(user=request.user, pipeline="SEQUENCE")
            project.files.add(cleaned_data["ref_file"], *cleaned_data["read_files"])
            # run_sequence.delay(project.id)
            return redirect("dashboard:dashboard")

    # GET request → render empty form
    return render(request, "projects/project.html", {
        "user_files": user_files, "error": None
    })



@login_required
def project_detail(request, project_id):
    # FIXED: Changed id=project_id to project_id=project_id
    project = get_object_or_404(ProjectRun, project_id=project_id)

    result = None
    if project.pipeline == "TIMEPOINT":
        # Using hasattr is cleaner than a try/except block here
        if hasattr(project, 'timepoint_result'):
            result = project.timepoint_result

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
    # This one was already correct in your snippet!
    project = get_object_or_404(ProjectRun, project_id=project_id)

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
                # We use .id here because Celery prefers the integer PK for efficiency
                run_timepoint.delay(project.id)
            except Exception:
                project.status = "FAILED"
                project.error_message = "Could not connect to Redis. Task not queued."
                project.save()

        transaction.on_commit(queue_task)

    return redirect("dashboard:dashboard")
