from django.db import models
from django.conf import settings

# --- UniqueAnimal model ---
class UniqueAnimal(models.Model):
    # Owner if user created
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Basic and Scientific Name
    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=150, blank=True, null=True)

    # Taxonomy
    kingdom = models.CharField(max_length=100, blank=True, null=True)
    phylum = models.CharField(max_length=100, blank=True, null=True)
    animal_class = models.CharField(max_length=100, blank=True, null=True)
    order = models.CharField(max_length=100, blank=True, null=True)
    family = models.CharField(max_length=100, blank=True, null=True)
    genus = models.CharField(max_length=100, blank=True, null=True)

    # Characteristics
    prey = models.CharField(max_length=255, blank=True, null=True)
    name_of_young = models.CharField(max_length=255, blank=True, null=True)
    group_behavior = models.CharField(max_length=255, blank=True, null=True)
    estimated_population_size = models.CharField(max_length=255, blank=True, null=True)
    biggest_threat = models.CharField(max_length=255, blank=True, null=True)
    most_distinctive_feature = models.CharField(max_length=255, blank=True, null=True)
    gestation_period = models.CharField(max_length=255, blank=True, null=True)
    habitat = models.CharField(max_length=255, blank=True, null=True)
    diet = models.CharField(max_length=255, blank=True, null=True)
    average_litter_size = models.CharField(max_length=255, blank=True, null=True)
    lifestyle = models.CharField(max_length=255, blank=True, null=True)
    common_name = models.CharField(max_length=255, blank=True, null=True)
    number_of_species = models.CharField(max_length=255, blank=True, null=True)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    skin_type = models.CharField(max_length=255, blank=True, null=True)
    top_speed = models.CharField(max_length=255, blank=True, null=True)

    #Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Unique Animal'
        verbose_name_plural = 'Unique Animals'
        ordering = ['name']

# --- MyAnimal model ---
class MyAnimal(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='animals')
    unique_animal = models.ForeignKey(UniqueAnimal, on_delete=models.SET_NULL, null=True, blank=True, related_name='instances')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=1)  # CHECK (age >= 0)
    weight_lb = models.PositiveIntegerField(default=0) # CHECK (weight >= 0)
    weight_oz = models.PositiveIntegerField(default=0) # CHECK (weight >= 0)
    last_fed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.species})"


# --- Food model ---
class Food(models.Model):
    # Weight Units
    GRAM = 'g'
    OUNCE = 'oz'
    POUND = 'lb'

    # Volume Units
    FLUID_OUNCE = 'fl oz'
    GALLON = 'gal'
    LITER = 'l'

    UNIT_CHOICES = (
        (GRAM, 'g'),
        (OUNCE, 'oz'),
        (POUND, 'lb'),
        (FLUID_OUNCE, 'fl oz'),
        (GALLON, 'gal'),
        (LITER, 'L'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=100)
    amount = models.FloatField(null=True, blank=True)  # CHECK (amount >= 0)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=POUND)

    def __str__(self):
        return f"{self.name} - {self.amount} {self.unit}"

# --- Feeding Schedule model ---
class FeedingSchedule(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    EVERY_X_HOURS = 'every_x_hours'

    FREQUENCY_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (EVERY_X_HOURS, 'Every X Hours'),
    )

    myanimal = models.ForeignKey(MyAnimal, on_delete=models.CASCADE, related_name='feeding_schedules')
    time_of_day = models.TimeField(null=True, blank=True)
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES, default=DAILY)
    hours_interval = models.IntegerField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.myanimal.name}'s next feeding is at {self.next_run}"

# --- Log model ---
class Log(models.Model):
    FEEDING = 'feeding'
    WEIGHT_UPDATE = 'weight_update'
    NOTE = 'note'
    OTHER = 'other'

    LOG_TYPE_CHOICES = [
        (FEEDING, 'Feeding'),
        (WEIGHT_UPDATE, 'Weight Update'),
        (NOTE, 'Note'),
        (OTHER, 'Other'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='logs')
    myanimal = models.ForeignKey(MyAnimal, on_delete=models.CASCADE, related_name='logs')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    log_type = models.CharField(max_length=50, choices=LOG_TYPE_CHOICES, default=FEEDING)
    description = models.TextField(null=True, blank=True)

    # Track original inputs for reports
    amount_fed = models.FloatField(null=True, blank=True)
    unit = models.TextField(null=True, blank=True)

    # Convert inputs to make chart comparisons easier
    converted_amount_grams = models.FloatField(null=True, blank=True)
    converted_amount_ml = models.FloatField(null=True, blank=True)

    weight_lb = models.PositiveIntegerField(null=True, blank=True)
    weight_oz = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.myanimal.name} - {self.log_type} ({self.created_at:%m-%d-%Y %H:%M})"