from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class AdminTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="adminpass123",
            email="admin@example.com",
        )
        self.client = Client()
        self.client.login(username="admin", password="adminpass123")

    def test_task_admin_list(self):
        url = reverse("admin:core_task_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_type_admin_list(self):
        url = reverse("admin:core_tasktype_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_team_admin_list(self):
        url = reverse("admin:core_team_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_admin_add(self):
        url = reverse("admin:core_task_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_task_type_admin_add(self):
        url = reverse("admin:core_tasktype_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_team_admin_add(self):
        url = reverse("admin:core_team_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
