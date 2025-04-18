from django.contrib import admin
from core.models import Task, TaskType, Team, TeamMember


@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "task_type",
        "priority",
        "deadline",
        "is_completed",
    )
    list_filter = ("task_type", "priority", "is_completed")
    search_fields = ("name", "description")
    filter_horizontal = ("assigners",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("team", "member", "joined_at", "is_admin")
    list_filter = ("is_admin", "joined_at")
    search_fields = ("team__name", "member__username")
