import os
from typing import List

from django.core.management.base import BaseCommand
from django.core import management

class Command(BaseCommand):
    help = 'All fixtures apply'
    @staticmethod
    def get_fixtures() -> list[str]:
        shops_fixtures_path = os.path.normpath(os.path.abspath('app_shops/fixtures'))
        # users_fixtures_path = os.path.normpath(os.path.abspath('app_users/fixtures'))
        if os.path.exists(shops_fixtures_path):
            shops_fixtures: List = os.listdir(shops_fixtures_path)
            # if os.path.exists(users_fixtures_path):
            #     users_fixtures: List = os.listdir(users_fixtures_path)
            #     shops_fixtures.extend(users_fixtures)
            return shops_fixtures
        return []

    def handle(self, *args, **kwargs) -> None:
        fixtures_list = self.get_fixtures()
        management.call_command('loaddata', *fixtures_list)

