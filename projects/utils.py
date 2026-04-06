# utils.py
from uploads.models import File
from django.shortcuts import get_object_or_404


# returns a queryset (for listing dropdowns, templates)
def get_user_files(user):

    if user.is_superuser:
        return File.objects.filter(status="UPLOADED")
    return File.objects.filter(user=user, status="UPLOADED")


# returns a single object (for POST requests, permission checks)
def get_user_file(user, file_id):
    if user.is_superuser:
        return get_object_or_404(File, id=file_id, status="UPLOADED")
    return get_object_or_404(File, id=file_id, user=user, status="UPLOADED")
