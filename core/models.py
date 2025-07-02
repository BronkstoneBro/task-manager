from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.conf import settings

Worker = get_user_model()


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"


class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="created_teams"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        Worker, through="TeamMember", related_name="teams"
    )

    def __str__(self):
        return self.name

    def is_creator(self, user):
        return self.created_by == user

    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()

    def can_manage_members(self, user):
        return self.is_creator(user)

    def can_manage_tasks(self, user):
        return self.is_member(user)


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    member = models.ForeignKey(Worker, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ("team", "member")

    def __str__(self):
        return f"{self.member} in {self.team}"


class Task(models.Model):
    class Priority(models.IntegerChoices):
        CRITICAL = 1, "Critical"
        IMPORTANT = 2, "Important"
        NORMAL = 3, "Normal"
        LOW = 4, "Low"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    priority = models.IntegerField(choices=Priority, default=Priority.LOW)
    task_type = models.ForeignKey(
        TaskType, on_delete=models.CASCADE, related_name="tasks"
    )
    created_by = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assigners = models.ManyToManyField(Worker, related_name="assigned_tasks")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
    )

    def can_edit(self, user):
        if self.team:
            return self.team.members.filter(pk=user.pk).exists()
        return self.created_by == user or user in self.assigners.all()

    def can_delete(self, user):
        if self.team:
            return self.team.members.filter(pk=user.pk).exists()
        return self.created_by == user

    def can_complete(self, user):
        if self.team:
            return self.team.members.filter(pk=user.pk).exists()
        return user in self.assigners.all()

    class Meta:
        default_related_name = "tasks"
        ordering = (
            "is_completed",
            F("deadline").asc(nulls_last=True),
            "priority",
        )

    def __str__(self):
        return f"{self.name} ({self.task_type})"


class TaskFile(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="files"
    )
    file = models.FileField(upload_to="task_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="task_files"
    )

    def __str__(self):
        return f"File for {self.task.name} uploaded by {self.uploaded_by.username}"

    class Meta:
        ordering = ["-uploaded_at"]


class Comment(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"


class TaskLog(models.Model):
    class ActionType(models.TextChoices):
        UPDATE = "update", "Update"
        COMMENT = "comment", "Comment"
        FILE = "file", "File"
        COMPLETE = "complete", "Complete"
        UNCOMPLETE = "uncomplete", "Uncomplete"

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=16, choices=ActionType.choices)
    field = models.CharField(max_length=64, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.message or f"{self.get_action_display()} {self.field} of task {self.task_id} by user {self.user_id} at {self.timestamp}"
