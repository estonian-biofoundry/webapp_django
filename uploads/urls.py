from django.urls import path
from .views import (
    upload_view,
    delete_file,
)

app_name = "uploads"

urlpatterns = [
    path("upload/", upload_view, name="upload"),  # new uploads page
    path("delete/<int:file_id>/", delete_file, name="delete_file"),
]
