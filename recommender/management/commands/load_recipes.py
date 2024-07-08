import pandas as pd
from django.core.management.base import BaseCommand
from recommender.models import Recipe


class Command(BaseCommand):
    help = 'Load recipes from an Excel file'

    def handle(self, *args, **kwargs):
        file_path = './recipes.xlsx'  # Update with actual path
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            nutritional_details = row.drop(['LocalName', 'SearchName']).to_dict()

            # Ensure all values in nutritional_details are JSON-serializable
            for key, value in nutritional_details.items():
                if pd.isna(value):
                    nutritional_details[key] = None  # Replace NaNs with None
                elif isinstance(value, (int, float)):
                    nutritional_details[key] = float(value)  # Ensure numeric values are floats
                else:
                    nutritional_details[key] = str(value)  # Convert other types to string

            Recipe.objects.create(
                local_name=row['LocalName'],
                english_name=row['EnglishName'],
                search_name=row['SearchName'].lower(),  # Ensure search name is lowercase
                total_carbohydrates=row['CHOCDF_g'] if pd.notna(row['CHOCDF_g']) else 0,
                fiber=row['FIB_g'] if pd.notna(row['FIB_g']) else 0,
                nutritional_details=nutritional_details
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded recipes'))
