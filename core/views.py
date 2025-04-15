from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth import get_user_model

from .models import Task, TaskType

Worker = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "core/home.html"
    context_object_name = "tasks"

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
        return Task.objects.all().order_by(
            "is_completed", "deadline", "priority"
        )


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "core/task_detail.html"
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = "core/task_form.html"
    fields = [
        "name",
        "description",
        "deadline",
        "priority",
        "task_type",
        "assigners",
    ]
    success_url = reverse_lazy("core:task-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = "core/task_form.html"
    fields = [
        "name",
        "description",
        "deadline",
        "priority",
        "task_type",
        "assigners",
    ]
    success_url = reverse_lazy("core:task-list")


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
