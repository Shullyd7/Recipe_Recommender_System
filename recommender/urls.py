from django.urls import path
from .views import RecipeRecommendationView, RateRecipeView

urlpatterns = [
    path('recommend/', RecipeRecommendationView.as_view(), name='recipe-recommendation'),
    path('rate/', RateRecipeView.as_view(), name='rate_recipe'),
]