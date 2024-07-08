from django.db import models


class Recipe(models.Model):
    local_name = models.CharField(max_length=255)
    english_name = models.CharField(max_length=255)
    search_name = models.TextField()
    total_carbohydrates = models.FloatField()  # Total carbohydrates
    fiber = models.FloatField()                # Fiber content
    nutritional_details = models.JSONField()  # Storing other nutritional details as a JSON object
    image_url = models.URLField(blank=True)  # Storing image URL
    rating = models.FloatField(default=0.0)  # Average rating
    rating_count = models.IntegerField(default=0)  # Number of ratings


    def __str__(self):
        return self.local_name

