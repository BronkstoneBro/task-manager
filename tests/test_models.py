from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import Task, TaskType, Team

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.task_type = TaskType.objects.create(name='Test Type')
        self.task = Task.objects.create(
            name='Test Task',
            description='Test Description',
            task_type=self.task_type,
            created_by=self.user
        )

    def test_task_creation(self):
        self.assertEqual(self.task.name, 'Test Task')
        self.assertEqual(self.task.description, 'Test Description')
        self.assertEqual(self.task.task_type, self.task_type)
        self.assertEqual(self.task.created_by, self.user)

    def test_task_str_representation(self):
        self.assertEqual(str(self.task), 'Test Task (Test Type)')

class TaskTypeModelTest(TestCase):
    def setUp(self):
        self.task_type = TaskType.objects.create(name='Test Type')

    def test_task_type_creation(self):
        self.assertEqual(self.task_type.name, 'Test Type')

    def test_task_type_str_representation(self):
        self.assertEqual(str(self.task_type), 'Test Type')

class TeamModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.team = Team.objects.create(
            name='Test Team',
            description='Test Description',
            created_by=self.user
        )
        self.team.members.add(self.user)

    def test_team_creation(self):
        self.assertEqual(self.team.name, 'Test Team')
        self.assertEqual(self.team.description, 'Test Description')
        self.assertEqual(self.team.created_by, self.user)
        self.assertIn(self.user, self.team.members.all())

    def test_team_str_representation(self):
        self.assertEqual(str(self.team), 'Test Team') 