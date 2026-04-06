# dashboard/views.py
from urllib import request

from uploads.models import File
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from uploads.models import File
from projects.models import ProjectRun


@login_required
def dashboard_view(request):

    # admin can see all files, regular users only their own
    if request.user.is_superuser:
        files = File.objects.all()
        projects = ProjectRun.objects.all().prefetch_related("files")
    else:
        files = File.objects.filter(user=request.user)
        projects = ProjectRun.objects.filter(user=request.user).prefetch_related(
            "files"
        )

    # get the file names to show in html
    for project in projects:
        project.file_names = ", ".join(f.original_filename for f in project.files.all())

    ## PROJECTS
    # --- PAGINATION ---
    # projects_paginator = Paginator(projects, 5)
    # projects_page_number = request.GET.get("page", 1)
    # projects_obj = projects_paginator.get_page(projects_page_number)

    ## UPLOADS
    # --- SEARCH ---
    search_query = request.GET.get("search")
    if search_query:
        files = files.filter(original_filename__icontains=search_query)

    # --- SORTING ---
    allowed_sorts = [
        "upload_id",
        "-upload_id",
        "uploaded_at",
        "-uploaded_at",
        "file_size",
        "-file_size",
        "original_filename",
        "-original_filename",
    ]

    sort = request.GET.get("sort", "-uploaded_at")

    if sort not in allowed_sorts:
        sort = "-uploaded_at"

    files = files.order_by(sort)

    # --- STATS ---
    stats = files.aggregate(total_files=Count("id"), total_size=Sum("file_size"))

    # --- PAGINATION ---
    file_paginator = Paginator(files, 5)
    file_page_number = request.GET.get("page", 1)
    files_obj = file_paginator.get_page(file_page_number)

    return render(
        request,
        "dashboard/dashboard.html",
        {
            "projects": projects,
            "files": files_obj,
            "total_files": stats["total_files"],
            "total_size": stats["total_size"] or 0,
            "search_query": search_query,
            "sort": sort,
        },
    )


@require_POST
@login_required
def delete_file_view(request, file_id):
    # Step 1: fetch the file object
    file_obj = get_object_or_404(File, id=file_id)
    # Step 2: check permissions
    if file_obj.user != request.user and not request.user.is_superuser:
        # the user is neither the owner nor admin → deny
        raise Http404("You do not have permission to delete this file.")
    # Step 3: delete the file (this triggers post_delete signal)
    file_obj.delete()
    # Step 4: redirect to dashboard with a success message
    return redirect("dashboard:dashboard")


@login_required
def download_file_view(request, file_id):
    # Step 1: fetch file object
    file_obj = get_object_or_404(File, id=file_id)

    # Step 2: permission check
    if file_obj.user != request.user and not request.user.is_superuser:
        raise Http404("You do not have permission to download this file.")

    # Step 3: send file as a response
    if not file_obj.file:
        raise Http404("File not found on the server.")

    response = FileResponse(file_obj.file.open("rb"), as_attachment=True)
    response["Content-Disposition"] = (
        f'attachment; filename="{file_obj.original_filename}"'
    )
    return response
