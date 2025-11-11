from django.contrib import admin
from .models import Animal, Food


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species', 'age', 'owner', 'last_fed')
    list_filter = ('species',)
    search_fields = ('name', 'species', 'owner__username')
    ordering = ('name',)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'measurement', 'owner')
    search_fields = ('name', 'owner__username')
    ordering = ('name',)
