from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", views.TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/complete/", views.mark_task_completed, name="task-complete"),
    path("workers/", views.WorkerListView.as_view(), name="worker-list"),
    path("workers/<int:pk>/", views.WorkerDetailView.as_view(), name="worker-detail"),
]
