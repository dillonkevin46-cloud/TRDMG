from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class PDFViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.management_user = User.objects.create_user(username='manager', role='Management', password='testpassword123')
        self.staff_user = User.objects.create_user(username='staff', role='Staff', password='testpassword123')

    def test_pdf_generation(self):
        self.client.login(username='manager', password='testpassword123')
        url = reverse('kpi:download_staff_report_pdf', args=[self.staff_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response['Content-Disposition'].startswith('attachment; filename='))
        self.assertIn('staff_Report.pdf', response['Content-Disposition'])
