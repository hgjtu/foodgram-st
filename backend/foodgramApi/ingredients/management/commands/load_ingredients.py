# yourapp/management/commands/load_ingredients.py
import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from JSON file"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to JSON file")

    def handle(self, *args, **options):
        file_path = options["json_file"]

        with open(file_path, "r", encoding="utf-8") as file:
            ingredients = json.load(file)

            created_count = 0
            for item in ingredients:
                _, created = Ingredient.objects.get_or_create(
                    name=item["name"],
                    measurement_unit=item["measurement_unit"]
                )
                if created:
                    created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully loaded {created_count} ingredients"
                )
            )
