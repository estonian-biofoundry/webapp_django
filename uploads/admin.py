from .models import File
from django.contrib import admin


# To register the File model with the admin site and customize its display
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "upload_id",
        "user",
        "original_filename",
        "file_size",
        "status",
        "uploaded_at",
    )
    search_fields = ("upload_id", "original_filename", "user__username")
    list_filter = ("status", "uploaded_at")


admin.site.register(File, FileAdmin)
