# Task Manager 📋

https://task-manager-71xh.onrender.com/

A comprehensive task management system built with Django that allows users to create, manage, and track tasks both individually and within teams.

## Features

### Task Management
- Create, update, and delete tasks
- Set task priorities (Critical, Important, Normal, Low)
- Add deadlines and track completion status
- Assign tasks to team members
- Categorize tasks by type
- Search and filter tasks

### Team Collaboration
- Create and manage teams
- Add/remove team members
- Create team-specific tasks
- Manage team permissions
- Track team progress

### User Features
- User registration and authentication
- Personal task dashboard
- Task completion tracking
- Profile management
- Team membership management

## Tech Stack

- **Backend**: Django 5.2
- **Frontend**: 
  - Bootstrap 4
  - Django Crispy Forms
  - Font Awesome icons
- **Database**: SQLite (development)   🛠️ Postgres (production) soon

## Installation 📦

1. Clone the repository:
```bash
git clone https://github.com/BronkstoneBro/task-manager
cd task_manager
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```
⚠️ Note: Tasks reference users with IDs 1 and 2 (CREATE 2 USERS IN ADMIN PANEL!) ❗❗❗

6. Load fixtures:
```bash
python manage.py loaddata task_types tasks
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure  📂

```
task_manager/
├── core/                 # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── urls.py          # URL routing
│   └── admin.py         # Admin interface
├── templates/           # HTML templates
│   └── core/           # Application templates
├── tests/              # Test files
└── task_manager/       # Project configuration
```

## Testing 🧪

Run the test suite:
```bash
python manage.py test tests
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Fixtures

Pre-configured sample data is available in `core/fixtures/`:

1. `task_types.json` - Common task types
2. `tasks.json` - Sample tasks with different priorities
