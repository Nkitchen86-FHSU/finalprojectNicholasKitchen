from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('myanimal/', views.myanimal_index, name='animal_index'),
    path('myanimal/create/', views.myanimal_create, name='myanimal_create'),
    path('myanimal/<int:id>/update/', views.myanimal_update, name='myanimal_update'),
    path('myanimal/<int:id>/delete/', views.myanimal_delete, name='myanimal_delete'),
    path('food/', views.food_index, name='food_index'),
    path('food/create/', views.food_create, name='food_create'),
    path('food/<int:id>/update/', views.food_update, name='food_update'),
    path('food/<int:id>/delete/', views.food_delete, name='food_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calculator/feed/', views.feed_myanimal, name='calculator'),
]
