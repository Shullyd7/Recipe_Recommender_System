from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe
from .serializers import RecipeSerializer
from icrawler.builtin import BingImageCrawler
from threading import Thread
import os
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from bs4 import BeautifulSoup
import requests
from .serializers import RecipeRatingSerializer
from django.views.generic.base import View





class RecipeRecommendationView(View):
    def fetch_image_url(self, keyword):
        print(f"Search query: {keyword}")  # Print the search query
        url = f"https://www.bing.com/images/search?q={keyword}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_tags = soup.find_all('img', {'class': 'mimg'})

        if image_tags:
            return image_tags[0]['src']

        return None

    def get(self, request):
        return render(request, 'recommendation.html')  # Render the recommendation form initially

    def post(self, request):
        diabetes_type = request.POST.get('diabetes_type', '')
        if diabetes_type not in ['Type A', 'Type B', 'Type C']:
            return JsonResponse({"error": "Invalid diabetes type"}, status=400)

        # Define criteria based on diabetes type
        criteria = {
            'Type A': {'max_carbs': 50, 'min_fiber': 3},
            'Type B': {'max_carbs': 60, 'min_fiber': 4},
            'Type C': {'max_carbs': 70, 'min_fiber': 5}
        }

        max_carbs = criteria[diabetes_type]['max_carbs']
        min_fiber = criteria[diabetes_type]['min_fiber']

        unique_recipes = set()
        suitable_recipes = []

        # Fetch recipes from the database
        recipes = Recipe.objects.exclude(local_name__isnull=True).filter(
            total_carbohydrates__lt=max_carbs,
            fiber__gte=min_fiber
        ).exclude(local_name='nan')

        # Process each recipe
        for recipe in recipes:
            if recipe.local_name not in unique_recipes:
                unique_recipes.add(recipe.local_name)
                search_name_for_search = recipe.search_name.replace(',', '+')
                image_url = self.fetch_image_url(search_name_for_search)
                suitable_recipes.append({
                    "recipe_name": recipe.local_name,
                    "image_url": image_url,
                    "rating": recipe.rating
                })

        if not suitable_recipes:
            return render(request, 'no_recipes.html')  # Render a template for no recipes found

        return render(request, 'recipe_results.html', {"recipes": suitable_recipes})  # Render the results template with recipes


class RateRecipeView(APIView):
    def post(self, request):
        local_name = request.data.get('local_name')
        rating = request.data.get('rating')

        if not local_name:
            return Response({"error": "Local name is required"}, status=status.HTTP_400_BAD_REQUEST)

        if rating is None or not (1 <= rating <= 5):
            return Response({"error": "Rating must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the recipe by local_name
        recipe = get_object_or_404(Recipe, local_name=local_name)

        # Update the rating
        total_rating = recipe.rating * recipe.rating_count
        recipe.rating_count += 1
        recipe.rating = (total_rating + rating) / recipe.rating_count
        recipe.save()

        # Serialize the updated recipe for response
        serializer = RecipeRatingSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
