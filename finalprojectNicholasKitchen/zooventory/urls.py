from django.urls import path
from . import views

urlpatterns = [
    # Index and Dashboard URL
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Login / Register URLs
    path('register/', views.custom_register, name='register'),
    path('login/', views.custom_login, name='login'),

    # MyAnimal URLs
    path('myanimal/', views.myanimal_index, name='myanimal_index'),
    path('myanimal/create/', views.myanimal_create, name='myanimal_create'),
    path('myanimal/<int:id>/update/', views.myanimal_update, name='myanimal_update'),
    path('myanimal/<int:id>/delete/', views.myanimal_delete, name='myanimal_delete'),

    # UniqueAnimal URLs
    path('uniqueanimal/', views.uniqueanimal_index, name='uniqueanimal_index'),
    path('uniqueanimal/<int:id>/info/', views.uniqueanimal_info, name='uniqueanimal_info'),
    path('uniqueanimal/create/', views.uniqueanimal_create, name='uniqueanimal_create'),
    path('uniqueanimal/create/api', views.uniqueanimal_create_api, name='uniqueanimal_create_api'),
    path('uniqueanimal/<int:id>/update/', views.uniqueanimal_update, name='uniqueanimal_update'),
    path('uniqueanimal/search/', views.uniqueanimal_search, name='uniqueanimal_search'),

    # Food URLs
    path('food/', views.food_index, name='food_index'),
    path('food/create/', views.food_create, name='food_create'),
    path('food/<int:id>/update/', views.food_update, name='food_update'),
    path('food/<int:id>/delete/', views.food_delete, name='food_delete'),

    # Calculator URLs
    path('calculator/feed/', views.feed_myanimal, name='feed_myanimal'),
    path('calculator/weigh/', views.weigh_myanimal, name='weigh_myanimal'),

    # Chart URLs
    path('chart/food-usage', views.chart_food_usage, name='chart_food_usage'),
    path('chart/feeding-frequency', views.chart_feeding_frequency, name='chart_feeding_frequency'),
    path('chart/top-food', views.chart_top_food, name='chart_top_food'),
    path('chart/weight-trends', views.chart_weight_trends, name='chart_weight_trends'),
]
