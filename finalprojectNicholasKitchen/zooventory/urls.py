from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.custom_register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('myanimal/', views.myanimal_index, name='myanimal_index'),
    path('myanimal/create/', views.myanimal_create, name='myanimal_create'),
    path('myanimal/<int:id>/update/', views.myanimal_update, name='myanimal_update'),
    path('myanimal/<int:id>/delete/', views.myanimal_delete, name='myanimal_delete'),
    path('uniqueanimal/', views.uniqueanimal_index, name='uniqueanimal_index'),
    path('uniqueanimal/<int:id>/info/', views.uniqueanimal_info, name='uniqueanimal_info'),
    path('uniqueanimal/create/', views.uniqueanimal_create, name='uniqueanimal_create'),
    path('uniqueanimal/<int:id>/update/', views.uniqueanimal_update, name='uniqueanimal_update'),
    path('uniqueanimal/search/', views.uniqueanimal_search, name='uniqueanimal_search'),
    path('food/', views.food_index, name='food_index'),
    path('food/create/', views.food_create, name='food_create'),
    path('food/<int:id>/update/', views.food_update, name='food_update'),
    path('food/<int:id>/delete/', views.food_delete, name='food_delete'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calculator/feed/', views.feed_myanimal, name='calculator'),
]
