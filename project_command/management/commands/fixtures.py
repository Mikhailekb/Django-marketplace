import os
from typing import List

from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    help = 'All fixtures apply'

    @staticmethod
    def get_fixtures() -> list[str]:
        fixtures_path = os.path.normpath(os.path.abspath('fixtures'))
        if os.path.exists(fixtures_path):
            shops_fixtures: List = os.listdir(fixtures_path)
            return shops_fixtures
        return []

    def handle(self, *args, **kwargs) -> None:
        fixtures_list = self.get_fixtures()
        management.call_command('loaddata', *fixtures_list)
