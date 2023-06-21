from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = 'Create and apply migrations'

    def handle(self, *args, **kwargs) -> None:
        management.call_command('makemigrations')
        management.call_command('migrate')
