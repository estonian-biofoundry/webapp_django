from uploads.models import File
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .utils import calculate_md5, validate_file
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


@login_required
def upload_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES["file"]  # browser ensures file is selected
        # Validate file
        is_valid, error_msg = validate_file(uploaded_file)
        if not is_valid:
            # If invalid, re-render template with error message
            return render(request, "uploads/upload.html", {"error": error_msg})

        # Calculate MD5
        file_md5 = calculate_md5(uploaded_file)

        # Save in database
        File.objects.create(
            user=request.user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            status="UPLOADED",
            md5=file_md5,
        )

        return redirect("dashboard:dashboard")

    # GET request → show template
    return render(request, "uploads/upload.html")


@login_required
@require_POST
def delete_file(request, file_id):

    file = get_object_or_404(File, id=file_id, user=request.user)

    file.delete()

    return redirect("accounts:dashboard")
