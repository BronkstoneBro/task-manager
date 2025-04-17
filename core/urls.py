from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "core"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("task/create/", views.TaskCreateView.as_view(), name="task-create"),
    path("task/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
    path(
        "task/<int:pk>/update/",
        views.TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "task/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="task-delete",
    ),
    path(
        "task/<int:pk>/complete/",
        views.TaskCompleteView.as_view(),
        name="task-complete",
    ),
    path(
        "task-types/", views.TaskTypeListView.as_view(), name="task-type-list"
    ),
    path(
        "task-types/create/",
        views.TaskTypeCreateView.as_view(),
        name="task-type-create",
    ),
    path(
        "task-types/<int:pk>/update/",
        views.TaskTypeUpdateView.as_view(),
        name="task-type-update",
    ),
    path(
        "task-types/<int:pk>/delete/",
        views.TaskTypeDeleteView.as_view(),
        name="task-type-delete",
    ),
    path("workers/", views.WorkerListView.as_view(), name="worker-list"),
    path(
        "worker/<int:pk>/",
        views.WorkerDetailView.as_view(),
        name="worker-detail",
    ),
    # Authentication
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
]
