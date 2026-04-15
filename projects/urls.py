from . import views
from django.urls import path

app_name = "projects"

urlpatterns = [
    path("create/", views.create_project, name="create"),
    path("run/<int:project_id>/", views.run_project_celery, name="run"),
    path("<int:project_id>/", views.project_detail, name="project_detail"),
]
