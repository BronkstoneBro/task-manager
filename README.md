# Task Manager

Django task management system.

## Fixtures

Pre-configured sample data is available in `core/fixtures/`:

1. `task_types.json` - Common task types
2. `tasks.json` - Sample tasks with different priorities

### Quick Start

1. Create superuser:

```bash
python manage.py createsuperuser
```

Note: Tasks reference users with IDs 1 and 2 (CREATE 2 USERS!)

2. Load fixtures:

```bash
python manage.py loaddata task_types tasks
```


