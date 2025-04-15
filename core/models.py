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


class Task(models.Model):
    class Priority(models.IntegerChoices):
        CRITICAL = 1, "Critical"
        IMPORTANT = 2, "Important"
        NORMAL = 3, "Normal"
        LOW = 4, "Low"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True)
    is_completed = models.BooleanField(default=False)
    priority = models.SmallIntegerField(choices=Priority, default=Priority.LOW)
    task_type = models.ForeignKey(TaskType, on_delete=models.PROTECT)
    assigners = models.ManyToManyField(Worker)

    class Meta:
        default_related_name = "tasks"
        ordering = (
            "is_completed",
            F("deadline").asc(nulls_last=True),
            "priority",
        )

    def __str__(self):
        return f"{self.name} ({self.task_type})"
