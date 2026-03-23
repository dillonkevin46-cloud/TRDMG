from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SettingsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.management_user = User.objects.create_user(username='manager', role='Management', password='testpassword123')
        self.staff_user = User.objects.create_user(username='staff', role='Staff', password='testpassword123')
        self.viewer_user = User.objects.create_user(username='viewer', role='Viewer', password='testpassword123')

        self.settings_url = reverse('accounts:settings_dashboard')

    def test_management_access(self):
        self.client.login(username='manager', password='testpassword123')
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 200)

    def test_staff_access_forbidden(self):
        self.client.login(username='staff', password='testpassword123')
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 403)

    def test_viewer_access_forbidden(self):
        self.client.login(username='viewer', password='testpassword123')
        response = self.client.get(self.settings_url)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_redirect(self):
        response = self.client.get(self.settings_url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
