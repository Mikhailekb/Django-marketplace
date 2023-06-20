from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'commands are executed: migrations, fixtures, compilemessages, update_rates, createsuperuser'

    def handle(self, *args, **kwargs) -> None:
        management.call_command('migration')
        management.call_command('fixtures')
        management.call_command(
            'compilemessages', '--locale=ru', '--locale=en')
        print('Getting the exchange rate...')
        management.call_command('update_rates')
        management.call_command('createsuperuser')
