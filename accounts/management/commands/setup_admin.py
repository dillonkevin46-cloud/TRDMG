from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates the default admin superuser'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'Admin'
        password = 'Tradecore@2468$'

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(
                username=username,
                password=password,
                role='Superuser'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
