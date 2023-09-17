import csv
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    """Класс для загрузки данных из CSV-файлов в модели Ingredient и Tag."""
    help = ' Загрузить данные в модель ингредиентов '

    def handle(self, *args, **options):
        with open(
            'data/ingredients.csv', encoding='utf-8'
        ) as data_file_ingredients:
            csv_reader_ingredients = csv.DictReader(
                data_file_ingredients, delimiter=','
            )
            line_count = 0
            for row in csv_reader_ingredients:
                name = row['name']
                unit = row['measurement_unit']
                ingredient = Ingredient(name=name, measurement_unit=unit)
                ingredient.save()
                line_count += 1
            print(f'Загружено {line_count} ингредиента(-ов)')

        with open(
            'data/tags.csv', encoding='utf-8',
        ) as data_file_tags:
            csv_reader_tags = csv.DictReader(
                data_file_tags, delimiter=','
            )
            line_count_tags = 0
            for row in csv_reader_tags:
                name = row['name_tag']
                slug = row['tag_slug']
                color = row['color']
                tags = Tag(
                    name=name,
                    color=color,
                    slug=slug
                )
                tags.save()
                line_count_tags += 1
            print(f'Загружено {line_count_tags} тэга(-ов)')
