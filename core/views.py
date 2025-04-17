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
    View,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.db.models import Q

from .models import Task, TaskType, Team, TeamMember

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context["can_edit"] = task.can_edit(self.request.user)
        context["can_delete"] = task.can_delete(self.request.user)
        context["can_complete"] = task.can_complete(self.request.user)
        return context


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
    template_name = "core/task_form.html"
    fields = ["name", "description", "deadline", "priority", "task_type", "assigners"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        task = self.get_object()
        if task.team:
            form.fields["assigners"].queryset = task.team.members.all()
        return form

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if not task.can_edit(request.user):
            messages.error(request, "You don't have permission to edit this task.")
            return redirect("core:task-detail", pk=task.pk)
        return super().dispatch(request, *args, **kwargs)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = "core/task_confirm_delete.html"
    success_url = reverse_lazy("core:task-list")

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if not task.can_delete(request.user):
            messages.error(request, "You don't have permission to delete this task.")
            return redirect("core:task-detail", pk=task.pk)
        return super().dispatch(request, *args, **kwargs)


class TaskCompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        if not task.can_complete(request.user):
            messages.error(request, "You don't have permission to complete this task.")
            return redirect("core:task-detail", pk=task.pk)
        task.is_completed = True
        task.save()
        messages.success(request, "Task marked as completed.")
        return redirect("core:task-detail", pk=task.pk)


class TaskUncompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs["pk"])
        if not task.can_complete(request.user):
            messages.error(request, "You don't have permission to uncomplete this task.")
            return redirect("core:task-detail", pk=task.pk)
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
            worker.active_tasks_count = worker.assigned_tasks.filter(
                is_completed=False
            ).count()
            worker.completed_tasks_count = worker.assigned_tasks.filter(
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
        context["assigned_tasks"] = worker.assigned_tasks.filter(is_completed=False)
        context["completed_tasks"] = worker.assigned_tasks.filter(is_completed=True)
        context["created_tasks"] = worker.created_tasks.all()
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


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "core/team_list.html"
    context_object_name = "teams"

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user)


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    template_name = "core/team_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("core:team-list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Add creator as team member
        TeamMember.objects.create(
            team=form.instance,
            member=self.request.user,
            is_admin=True
        )
        return response


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "core/team_detail.html"
    context_object_name = "team"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.get_object()
        context["members"] = team.members.all()
        context["tasks"] = team.tasks.all()
        # Add all users for the Add Member modal
        context["all_users"] = Worker.objects.exclude(pk__in=team.members.values_list('pk', flat=True))
        return context


class TeamAddMemberView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, pk=kwargs["pk"])
        if not team.can_manage_members(request.user):
            messages.error(request, "You don't have permission to add members to this team.")
            return redirect("core:team-detail", pk=team.pk)

        user_id = request.POST.get("user_id")
        if not user_id:
            messages.error(request, "No user selected.")
            return redirect("core:team-detail", pk=team.pk)

        user = get_object_or_404(Worker, pk=user_id)
        if team.members.filter(pk=user.pk).exists():
            messages.warning(request, "User is already a member of this team.")
            return redirect("core:team-detail", pk=team.pk)

        TeamMember.objects.create(team=team, member=user)
        messages.success(request, f"{user.username} has been added to the team.")
        return redirect("core:team-detail", pk=team.pk)


class TeamRemoveMemberView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        team = get_object_or_404(Team, pk=kwargs["pk"])
        if not team.can_manage_members(request.user):
            messages.error(request, "You don't have permission to remove members from this team.")
            return redirect("core:team-detail", pk=team.pk)

        user_id = request.POST.get("user_id")
        if not user_id:
            messages.error(request, "No user selected.")
            return redirect("core:team-detail", pk=team.pk)

        user = get_object_or_404(Worker, pk=user_id)
        if not team.members.filter(pk=user.pk).exists():
            messages.warning(request, "User is not a member of this team.")
            return redirect("core:team-detail", pk=team.pk)

        TeamMember.objects.filter(team=team, member=user).delete()
        messages.success(request, f"{user.username} has been removed from the team.")
        return redirect("core:team-detail", pk=team.pk)


class TeamTaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "core/task_form.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        team = get_object_or_404(Team, pk=self.kwargs["pk"])
        # Only show team members in the assigners field
        form.fields["assigners"].queryset = team.members.all()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Team Task'
        return context

    def form_valid(self, form):
        team = get_object_or_404(Team, pk=self.kwargs["pk"])
        if not team.can_manage_tasks(self.request.user):
            messages.error(self.request, "You don't have permission to create tasks in this team.")
            return redirect("core:team-detail", pk=team.pk)

        form.instance.created_by = self.request.user
        form.instance.team = team
        response = super().form_valid(form)
        messages.success(self.request, "Task created successfully.")
        return response

    def get_success_url(self):
        return reverse_lazy("core:team-detail", kwargs={"pk": self.kwargs["pk"]})
