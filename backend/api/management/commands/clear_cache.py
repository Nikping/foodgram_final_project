from django.core.management.base import BaseCommand
from django.core.cache import cache

'''Функция очищает кэш приложения и выводит информацию об успешной очистке.'''
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cleared cache\n')
