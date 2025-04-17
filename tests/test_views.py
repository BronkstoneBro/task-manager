from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import Task, TaskType, Team

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.team = Team.objects.create(
            name='Test Team',
            description='Test Description',
            created_by=self.user
        )
        self.team.members.add(self.user)

    def test_home_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

    def test_task_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:task-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_list.html')

    def test_task_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:task-detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_detail.html')

    def test_task_create_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:task-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_form.html')

    def test_task_type_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:task-type-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/task_type_list.html')

    def test_team_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:team-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/team_list.html')

    def test_team_detail_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:team-detail', args=[self.team.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/team_detail.html') 