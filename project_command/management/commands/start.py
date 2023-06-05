from sys import stdout
from django.utils.translation import gettext_lazy as _
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create and apply migrations'

    def handle(self, *args, **kwargs) -> None:
        management.call_command('migration')
        management.call_command('fixtures')
        management.call_command('compilemessages', '--locale=ru', '--locale=en')
        stdout.write(_('Getting the exchange rate...'))
        management.call_command('update_rates')
        management.call_command('createsuperuser')
