from rest_framework import serializers
from .models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['local_name', 'english_name']


class RecipeRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'rating']
