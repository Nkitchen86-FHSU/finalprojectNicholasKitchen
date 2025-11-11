from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('animal/', views.animal_index, name='animal_index'),
    path('animal/create/', views.animal_create, name='animal_create'),
    path('animal/<int:id>/update/', views.animal_update, name='animal_update'),
    path('animal/<int:id>/delete/', views.animal_delete, name='animal_delete'),
    path('food/', views.food_index, name='food_index'),
    path('food/create/', views.food_create, name='food_create'),
    path('food/<int:id>/update/', views.food_update, name='food_update'),
    path('food/<int:id>/delete/', views.food_delete, name='food_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calculator/feed/', views.feed_animal, name='calculator'),
]
