from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Recipe
from .serializers import RecipeSerializer
from icrawler.builtin import BingImageCrawler
from threading import Thread
import os
from bs4 import BeautifulSoup
import requests
from .serializers import RecipeRatingSerializer
from django.views.generic.base import View
from django.http import JsonResponse
import requests






class ClassificationView(View):
    def get(self, request):
        # For GET request, render the classification form
        return render(request, 'classification.html')

    def post(self, request):
        # Extract answers
        autoimmune_disease = request.POST.get('autoimmune_disease')  # Type 1
        age_of_onset = request.POST.get('age_of_onset')  # Type 1 & 2
        insulin_dependence = request.POST.get('insulin_dependence')  # Type 1
        family_history = request.POST.get('family_history')  # Type 2
        symptoms = request.POST.get('symptoms')  # Type 2
        risk_factors = request.POST.get('risk_factors')  # Pre-diabetic
        fasting_glucose = float(request.POST.get('fasting_glucose', 0))  # Pre-diabetic
        normal_glucose_levels = request.POST.get('normal_glucose_levels')  # Healthy

        # Classification Logic with N/A handling
        if (autoimmune_disease == 'yes' and insulin_dependence == 'yes' and
            (age_of_onset == 'yes' or age_of_onset == 'na')):
            classification = 'Type 1 Diabetes'
        elif (age_of_onset == 'no' or age_of_onset == 'na') and (family_history == 'yes' or symptoms == 'yes'):
            classification = 'Type 2 Diabetes'
        elif risk_factors == 'yes' and 100 <= fasting_glucose <= 125:
            classification = 'Pre-Diabetic'
        elif normal_glucose_levels == 'yes' and not any([autoimmune_disease, insulin_dependence, symptoms, risk_factors]):
            classification = 'Healthy'
        else:
            classification = 'Healthy'

        # Render the appropriate template with the classification result
        return render(request, 'classification_result.html', {
            'classification': classification,
        })


class RecipeRecommendationView(View):
    def fetch_image_url(self, keyword):
        print(f"Search query: {keyword}")  # Print the search query
        url = f"https://www.bing.com/images/search?q={keyword}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            soup = BeautifulSoup(response.text, 'html.parser')
            image_tags = soup.find_all('img', {'class': 'mimg'})

            if image_tags:
                return image_tags[0]['src']
        except (RequestException, SSLError) as e:
            print(f"Error fetching image URL: {e}")  # Log the error
        return None

    def get(self, request):
        return render(request, 'recommendation.html')

    def post(self, request):
        diabetes_type = request.POST.get('diabetes_type', '')

        # Define criteria based on diabetes type
        criteria = {
            'Type 1 Diabetes': {'max_carbs': 50, 'min_fiber': 3},
            'Type 2 Diabetes': {'max_carbs': 60, 'min_fiber': 4},
        }

        # Determine classification message and criteria
        if diabetes_type in criteria:
            max_carbs = criteria[diabetes_type]['max_carbs']
            min_fiber = criteria[diabetes_type]['min_fiber']

            recipes = Recipe.objects.exclude(local_name__isnull=True).filter(
                total_carbohydrates__lt=max_carbs,
                fiber__gte=min_fiber
            ).exclude(local_name='nan').order_by('-rating')
        elif diabetes_type == 'Pre-Diabetic':
            recipes = Recipe.objects.exclude(local_name__isnull=True).exclude(local_name='nan').order_by('-rating')
        elif diabetes_type == 'Healthy':
            recipes = Recipe.objects.exclude(local_name__isnull=True).exclude(local_name='nan').order_by('-rating')
        else:
            return JsonResponse({"error": "Invalid diabetes type"}, status=400)

        unique_recipes = set()
        suitable_recipes = []

        # Process each recipe
        for recipe in recipes:
            if recipe.local_name not in unique_recipes:
                unique_recipes.add(recipe.local_name)

                # Check if the image URL already exists in the database
                if not recipe.image_url:
                    # If no image URL is present, fetch a new image URL
                    search_name_for_search = recipe.search_name.replace(',', '+')
                    try:
                        image_url = self.fetch_image_url(search_name_for_search)
                        if image_url:
                            # Save the image URL to the database
                            recipe.image_url = image_url
                            recipe.save()
                    except Exception as e:
                        print(f"Error processing recipe {recipe.local_name}: {e}")  # Log any errors
                        continue  # Skip this recipe

                suitable_recipes.append({
                    "recipe_name": recipe.local_name,
                    "image_url": recipe.image_url,
                    "rating": recipe.rating
                })

        if not suitable_recipes:
            return render(request, 'no_recipes.html')

        return render(request, 'recipe_results.html',
                      {"recipes": suitable_recipes})


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