from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F

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
        Worker,
        on_delete=models.CASCADE,
        related_name='created_teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        Worker,
        through='TeamMember',
        related_name='teams'
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
        unique_together = ('team', 'member')

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
    priority = models.IntegerField(
        choices=Priority,
        default=Priority.LOW
    )
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    created_by = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name="created_tasks"
    )
    assigners = models.ManyToManyField(
        Worker,
        related_name="assigned_tasks"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks"
    )

    def can_complete(self, user):
        if not self.team:
            return True
        return self.team.is_member(user)

    def can_edit(self, user):
        if not self.team:
            return True
        return self.team.is_member(user)

    def can_delete(self, user):
        if not self.team:
            return True
        return self.team.is_member(user)

    class Meta:
        default_related_name = "tasks"
        ordering = (
            "is_completed",
            F("deadline").asc(nulls_last=True),
            "priority",
        )

    def __str__(self):
        return f"{self.name} ({self.task_type})"
