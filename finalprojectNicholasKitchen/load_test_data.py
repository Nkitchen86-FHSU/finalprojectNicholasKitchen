import os
import django
import random
from datetime import datetime, timedelta, time

# -----------------------------
# Django Setup
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth.models import User
from zooventory.models import UniqueAnimal, MyAnimal, Food, FeedingSchedule, Log

# -----------------------------
# Helper Functions
# -----------------------------
def random_weight():
    lb = random.randint(1, 20)
    oz = random.randint(0, 15)
    return lb, oz

def convert_to_grams(amount, unit):
    MULTIPLIERS = {
        "g": 1,
        "oz": 28.3495,
        "lb": 453.592,
    }
    return amount * MULTIPLIERS.get(unit, 0)

def convert_to_ml(amount, unit):
    MULTIPLIERS = {
        "fl oz": 29.5735,
        "gal": 3785.41,
        "l": 1000,
    }
    return amount * MULTIPLIERS.get(unit, 0)

# -----------------------------
# Create a test user
# -----------------------------
from django.contrib.auth import get_user_model
User = get_user_model()

# Create or get the test user
user, created = User.objects.get_or_create(username="1234test")
if created:
    user.set_password("1234test")
    user.email = "test@example.com"
    user.is_active = True
    user.save()
else:
    # Optionally reset password every time you run the script
    user.set_password("1234test")
    user.save()

user_id = user.id

# -----------------------------
# Create Unique Animals
# -----------------------------
unique_animals_data = [
    ("Red Fox", "Vulpes vulpes"),
    ("Bald Eagle", "Haliaeetus leucocephalus"),
    ("Green Iguana", "Iguana iguana"),
]

unique_animals = []
for name, sci in unique_animals_data:
    ua, _ = UniqueAnimal.objects.get_or_create(
        name=name,
        defaults={"owner": user, "scientific_name": sci, "diet": "varied", "habitat": "forest"}
    )
    unique_animals.append(ua)

print(f"Created {len(unique_animals)} unique animals.")

# -----------------------------
# Create MyAnimals
# -----------------------------
my_animals = []
for ua in unique_animals:
    animal, _ = MyAnimal.objects.get_or_create(
        owner=user,
        unique_animal=ua,
        name=f"{ua.name.split()[0]}y",
        species=ua.name,
        age=random.randint(1, 8),
        weight_lb=random.randint(5, 20),
        weight_oz=random.randint(0, 15),
    )
    my_animals.append(animal)

print(f"Created {len(my_animals)} MyAnimals.")

# -----------------------------
# Create Food Items
# -----------------------------
foods_data = [
    ("Chicken", 10, "lb"),
    ("Fish", 5, "lb"),
    ("Vegetables", 500, "g"),
    ("Water", 1, "gal"),
]

foods = []
for name, amount, unit in foods_data:
    f, _ = Food.objects.get_or_create(
        owner=user,
        name=name,
        defaults={"amount": amount, "unit": unit},
    )
    foods.append(f)

print(f"Created {len(foods)} foods.")

# -----------------------------
# Create Feeding Schedules
# -----------------------------
for animal in my_animals:
    FeedingSchedule.objects.get_or_create(
        myanimal=animal,
        frequency="daily",
        time_of_day=time(hour=9, minute=0),
        next_run=datetime.now(),
    )

print(f"Created feeding schedules for {len(my_animals)} animals.")

# -----------------------------
# Create 60 Days of Logs
# -----------------------------

days_back = 60
now = datetime.now()

for day in range(days_back):
    day_timestamp = now - timedelta(days=day)

    for animal in my_animals:

        # ---------------------
        # Feeding Log
        # ---------------------
        food = random.choice(foods)
        amount = random.uniform(0.2, 1.0)

        grams = convert_to_grams(amount, food.unit)
        ml = convert_to_ml(amount, food.unit)

        log = Log.objects.create(
            owner=user,
            myanimal=animal,
            food=food,
            log_type=Log.FEEDING,
            description=f"Fed {amount:.2f} {food.unit} of {food.name}.",
            amount_fed=amount,
            unit=food.unit,
            converted_amount_grams=grams if grams > 0 else None,
            converted_amount_ml=ml if ml > 0 else None,
        )

        # Force timestamp
        Log.objects.filter(id=log.id).update(created_at=day_timestamp.replace(hour=8))

        # ---------------------
        # Random Weight Update Log
        # ---------------------
        if random.random() < 0.3:  # ~30% chance
            lb, oz = random_weight()

            log = Log.objects.create(
                owner=user,
                myanimal=animal,
                log_type=Log.WEIGHT_UPDATE,
                description="Routine weight check",
                weight_lb=lb,
                weight_oz=oz,
            )

            # Force timestamp
            Log.objects.filter(id=log.id).update(created_at=day_timestamp.replace(hour=12))

print("Done! Seed data for 60 days has been added.")
