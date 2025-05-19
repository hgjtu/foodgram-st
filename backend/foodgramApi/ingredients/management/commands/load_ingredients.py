import json
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from JSON file"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str, help="Path to JSON file")

    def handle(self, *args, **options):
        file_path = options["json_file"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                ingredients_to_create = [
                    Ingredient(**item)
                    for item in json.load(file)
                    if not Ingredient.objects.filter(
                        name=item["name"],
                        measurement_unit=item["measurement_unit"]
                    ).exists()
                ]
                
                created_count = len(Ingredient.objects.bulk_create(ingredients_to_create))
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully loaded {created_count} ingredients"
                    )
                )
        except Exception:
            self.stdout.write(
                self.style.ERROR("Error loading ingredients")
            )
