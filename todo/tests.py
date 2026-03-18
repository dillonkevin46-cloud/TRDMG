from django.test import TestCase
from django.contrib.auth import get_user_model
from todo.models import Task, Comment
from todo.forms import TaskStatusUpdateForm

User = get_user_model()

class TaskModelTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username='staff', role='Staff')
        self.mgmt_user = User.objects.create_user(username='mgmt', role='Management')

    def test_status_change_auto_populates_time(self):
        task = Task.objects.create(title="Test Task", assigned_to=self.staff_user, created_by=self.mgmt_user)
        self.assertIsNone(task.started_at)
        self.assertIsNone(task.completed_at)

        task.status = 'Started'
        task.save()
        self.assertIsNotNone(task.started_at)
        self.assertIsNone(task.completed_at)

        task.status = 'Completed'
        task.save()
        self.assertIsNotNone(task.completed_at)

class TaskFormTest(TestCase):
    def test_comment_required_when_stuck(self):
        form_data = {'status': 'Stuck', 'comment_text': ''}
        form = TaskStatusUpdateForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment_text', form.errors)

        form_data = {'status': 'Stuck', 'comment_text': 'I am blocked!'}
        form = TaskStatusUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
