from django.contrib import admin
from .models import UniqueAnimal, MyAnimal, Food, FeedingSchedule, Log, Notification


@admin.register(UniqueAnimal)
class UniqueAnimalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'scientific_name', 'created_at', 'owner')
    list_filter = ('name',)
    search_fields = ('name', 'owner__username')
    ordering = ('name',)

@admin.register(MyAnimal)
class MyAnimalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'species', 'age', 'owner', 'last_fed')
    list_filter = ('species',)
    search_fields = ('name', 'species', 'owner__username')
    ordering = ('name',)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount', 'unit', 'owner')
    search_fields = ('name', 'owner__username')
    ordering = ('name',)

@admin.register(FeedingSchedule)
class FeedingScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'myanimal', 'next_run', 'time_of_day', 'frequency', 'hours_interval', 'day_of_week')
    search_fields = ('myanimal__name',)
    ordering = ('-next_run',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'log_type', 'created_at', 'owner', 'myanimal', 'food', 'description', 'amount_fed', 'unit', 'converted_amount_grams', 'converted_amount_ml', 'weight_lb', 'weight_oz')
    search_fields = ('log_type', 'owner__username', 'myanimal__name')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'owner', 'message', 'is_read')
    search_fields = ('owner__username',)
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False