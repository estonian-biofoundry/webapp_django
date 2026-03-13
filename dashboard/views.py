# dashboard/views.py
from uploads.models import File
from django.shortcuts import render
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    user_files = File.objects.filter(user=request.user).order_by("-uploaded_at")
    paginator = Paginator(user_files, 5)  # 5 files per page

    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)  # Page object

    return render(
        request,
        "dashboard/dashboard.html",
        {"user": request.user, "files": page_obj},  # pass Page object
    )
