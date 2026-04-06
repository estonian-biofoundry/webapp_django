from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from uploads.models import File
from .models import ProjectRun
from .utils import get_user_files, get_user_file


# pipeline1 - timepoint
def handle_timepoint(request):
    """
    Validates Timepoint pipeline POST data.
    Returns (cleaned_data, error)
    """
    error = None

    file_id = request.POST.get("timepoint_file")
    group_fields = request.POST.get("group_fields")
    dose_field = request.POST.get("dose_field")
    od_field = request.POST.get("od_field")
    time_field = request.POST.get("time_field")

    # Validate file exists and belongs to user
    try:
        file = get_user_file(request.user, file_id)
    except:
        return None, "Selected file is invalid or inaccessible."

    # Validate CSV extension
    if not file.original_filename.lower().endswith(".csv"):
        return None, "Only CSV files are allowed for the Timepoint pipeline."

    # Validate all required fields are filled
    if not all([group_fields, dose_field, od_field, time_field]):
        return None, "Please fill in all required fields."

    # If everything is valid, return cleaned data
    cleaned_data = {
        "file": file,
        "group_fields": [f.strip() for f in group_fields.split(",")],
        "dose_field": dose_field,
        "od_field": od_field,
        "time_field": time_field,
    }

    return cleaned_data, None


# pipeline2 - sequence
def handle_sequence(request):
    """
    Validates Sequence pipeline POST data.
    Returns (cleaned_data, error)
    """
    ref_file_id = request.POST.get("ref_file")
    read_file_ids = request.POST.getlist("read_files")

    # Ensure at least 1 reference and 1 read file
    if not ref_file_id or not read_file_ids:
        return None, "Please select a reference file and at least one read file."

    # Validate reference file
    try:
        ref_file = get_user_file(request.user, ref_file_id)
    except:
        return None, "Selected reference file is invalid or inaccessible."

    # Validate read files
    read_files = []
    for fid in read_file_ids:
        try:
            read_files.append(get_user_file(request.user, fid))
        except:
            return None, f"One of the read files (ID {fid}) is invalid or inaccessible."

    # Optional: enforce maximum 2 read files
    if len(read_files) > 2:
        return None, "You can select at most 2 read files."

    # Optional: validate file extensions if needed
    # e.g., ref_file.original_filename.lower().endswith(".fasta")
    #       read_file.original_filename.lower().endswith(".fastq")

    # Return cleaned data for project creation
    cleaned_data = {"ref_file": ref_file, "read_files": read_files}

    return cleaned_data, None


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

            # create Timepoint project
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

            # create Sequence project
            project = ProjectRun.objects.create(user=request.user, pipeline="SEQUENCE")
            project.files.add(cleaned_data["ref_file"], *cleaned_data["read_files"])
            return redirect("dashboard:dashboard")

    # GET request → just render form
    return render(
        request, "projects/project.html", {"user_files": user_files, "error": None}
    )


import threading
import time
from django.utils import timezone


@login_required
def run_project(request, project_id):
    try:
        project = ProjectRun.objects.get(id=project_id)

        project.started_at = timezone.now()

        project.status = "RUNNING"
        project.save()

        # just to mimic that its a long running pipeline
        time.sleep(15)
        if project.pipeline == "TIMEPOINT":
            from drc_timepoint import run_analysis_from_config
            from projects.models import TimepointResult

            # get the file path from the project's related file
            file_obj = project.files.first()
            file_path = file_obj.file.path

            # build config dict for the runner function using project.config and the file path
            config = {
                "file_path": file_path,
                "group_fields": project.config["group_fields"],
                "dose_field": project.config["dose_field"],
                "od_field": project.config["od_field"],
                "time_field": project.config["time_field"],
            }

            result_df = run_analysis_from_config(config)

            # save result back to project config or export to CSV
            TimepointResult.objects.update_or_create(
                project=project,
                defaults={"result_json": result_df.to_dict(orient="records")},
            )

        project.status = "SUCCESS"
        project.error_message = None

    except Exception as e:
        project.status = "FAILED"
        project.error_message = str(e)
    finally:
        project.completed_at = timezone.now()
        project.save()

    return redirect("dashboard:dashboard")


def project_detail(request, project_id):
    project = get_object_or_404(ProjectRun, id=project_id)

    result = None
    if project.pipeline == "TIMEPOINT":
        try:
            result = project.timepoint_result
        except:
            result = None

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "result": result,
        },
    )


# @login_required
# def run_thread_project(request, project_id):
#     project = get_object_or_404(ProjectRun, id=project_id)

#     if project.user != request.user and not request.user.is_superuser:
#         raise Http404("You do not have permission to run this project.")

#     project.status = "RUNNING"
#     project.completed_at = None
#     project.save()

#     thread = threading.Thread(target=run_project, args=(project.id,))
#     thread.start()
#     # thread.join()  # Wait for the thread to finish before redirecting

#     return redirect("dashboard:dashboard")
