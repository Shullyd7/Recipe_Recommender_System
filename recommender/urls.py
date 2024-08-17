from django.urls import path
from .views import ClassificationView, RecipeRecommendationView, RateRecipeView

urlpatterns = [
    path('classify/', ClassificationView.as_view(), name='classification'),
    path('recommend/', RecipeRecommendationView.as_view(), name='recommendation'),
    path('rate/', RateRecipeView.as_view(), name='rate_recipe'),
]