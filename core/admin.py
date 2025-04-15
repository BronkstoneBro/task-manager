from django.contrib import admin
from .models import Task, TaskType

@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'task_type', 'priority', 'deadline', 'is_completed')
    list_filter = ('task_type', 'priority', 'is_completed')
    search_fields = ('name', 'description')
    filter_horizontal = ('assigners',)
