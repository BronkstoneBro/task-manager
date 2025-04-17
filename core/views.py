from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.db.models import Q

from .models import Task, TaskType

Worker = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "core/home.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        return Task.objects.filter(assigners=self.request.user).order_by(
            "is_completed", "deadline", "priority"
        )


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "core/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        queryset = Task.objects.all()
        search_query = self.request.GET.get('search', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(task_type__name__icontains=search_query)
            )
        
        return queryset.order_by("is_completed", "deadline", "priority")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "core/task_detail.html"
    context_object_name = "task"


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "name",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assigners",
        ]
        widgets = {
            "deadline": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "assigners": forms.SelectMultiple(
                attrs={
                    "class": "form-select",
                    "data-placeholder": "Select assignees...",
                    "multiple": "multiple"
                }
            )
        }


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "core/task_form.html"
    success_url = reverse_lazy("core:task-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "core/task_form.html"
    success_url = reverse_lazy("core:task-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "core/task_confirm_delete.html"
    success_url = reverse_lazy("core:task-list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Task deleted successfully.")
        return super().delete(request, *args, **kwargs)


class TaskCompleteView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        task.is_completed = True
        task.save()
        messages.success(request, "Task marked as completed.")
        return redirect("core:task-detail", pk=task.pk)


class TaskUncompleteView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        task.is_completed = False
        task.save()
        messages.success(request, "Task marked as in progress.")
        return redirect("core:task-detail", pk=task.pk)


def mark_task_completed(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = True
    task.save()
    return redirect("core:task-detail", pk=pk)


class WorkerListView(LoginRequiredMixin, ListView):
    model = Worker
    template_name = "core/worker_list.html"
    context_object_name = "workers"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workers = context["workers"]
        for worker in workers:
            worker.active_tasks_count = worker.tasks.filter(
                is_completed=False
            ).count()
            worker.completed_tasks_count = worker.tasks.filter(
                is_completed=True
            ).count()
        return context


class WorkerDetailView(LoginRequiredMixin, DetailView):
    model = Worker
    template_name = "core/worker_detail.html"
    context_object_name = "worker"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worker = self.get_object()
        context["assigned_tasks"] = worker.tasks.filter(is_completed=False)
        context["completed_tasks"] = worker.tasks.filter(is_completed=True)
        return context


class TaskTypeListView(LoginRequiredMixin, ListView):
    model = TaskType
    template_name = "core/task_type_list.html"
    context_object_name = "task_types"


class TaskTypeCreateView(LoginRequiredMixin, CreateView):
    model = TaskType
    template_name = "core/task_type_form.html"
    fields = ["name"]
    success_url = reverse_lazy("core:task-type-list")

    def form_valid(self, form):
        messages.success(self.request, "Task type created successfully.")
        return super().form_valid(form)


class TaskTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = TaskType
    template_name = "core/task_type_form.html"
    fields = ["name"]
    success_url = reverse_lazy("core:task-type-list")

    def form_valid(self, form):
        messages.success(self.request, "Task type updated successfully.")
        return super().form_valid(form)


class TaskTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = TaskType
    template_name = "core/task_type_confirm_delete.html"
    success_url = reverse_lazy("core:task-type-list")

    def delete(self, request, *args, **kwargs):
        task_type = self.get_object()
        if task_type.tasks.exists():
            messages.error(
                request,
                f"Cannot delete '{task_type.name}' because it is being used by {task_type.tasks.count()} task(s). "
                "Please reassign or delete those tasks first.",
            )
            return redirect("core:task-type-list")

        messages.success(request, "Task type deleted successfully.")
        return super().delete(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        messages.success(self.request, "You have been logged in successfully.")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = "core:login"

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(
            self.request, "Account created successfully. Please log in."
        )
        return super().form_valid(form)


class LandingPageView(TemplateView):
    template_name = "core/landing_page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["features"] = [
            {
                "title": "Task Management",
                "description": "Efficiently create, track, and manage your tasks with our intuitive interface.",
                "icon": "fas fa-tasks"
            },
            {
                "title": "Priority System",
                "description": "Organize tasks by priority levels (Critical, Important, Normal, Low) for better workflow management.",
                "icon": "fas fa-flag"
            },
            {
                "title": "Task Types",
                "description": "Categorize tasks into different types like Bug Fix, Feature Development, Code Review, and more.",
                "icon": "fas fa-tags"
            },
            {
                "title": "Deadline Tracking",
                "description": "Set and track deadlines for all your tasks to ensure timely completion.",
                "icon": "fas fa-calendar-alt"
            },
            {
                "title": "Team Collaboration",
                "description": "Assign tasks to team members and track their progress in real-time.",
                "icon": "fas fa-users"
            },
            {
                "title": "User Profiles",
                "description": "Manage your profile and view your assigned tasks in one place.",
                "icon": "fas fa-user"
            }
        ]
        return context
