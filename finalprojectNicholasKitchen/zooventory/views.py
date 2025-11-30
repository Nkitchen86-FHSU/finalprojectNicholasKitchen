import requests

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from django.conf import settings
from .models import MyAnimal, UniqueAnimal, Food, FeedingSchedule, Log
from zooventory.utils.conversions import *
from datetime import datetime, timedelta

# -----------------------------
# Fetch request for animal API
# -----------------------------

def fetch_uniqueanimal_data(name):
    # Prepare API url and headers for it
    api_url = f'https://api.api-ninjas.com/v1/animals?name={name}'
    headers = {"X-Api-Key": settings.API_NINJAS_KEY}

    # Try to fetch a request, return empty array if request cannot be completed
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return []

# -----------------------------
# Home / Dashboard Views
# -----------------------------

def index(request):
    """Public landing page."""
    return render(request, 'zooventory/index.html')

@login_required
def dashboard(request):
    """User dashboard."""
    return render(request, 'zooventory/dashboard/dashboard.html')

# -----------------------------
# Login / Registration Views
# -----------------------------

def custom_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        # Ensure form was filled in correctly, then create the user
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')

        # Return error message with extra tag to automatically bring up register modal
        else:
            messages.error(request, "Registration failed. Ensure inputs are correct. Note: Password must be 8 or more characters.", extra_tags='register-error')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to authenticate user with set username and password
        user = authenticate(request, username=username, password=password)

        # Login user if authentication worked
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')

        # Return error message with extra tag to automatically bring up login modal
        messages.error(request, "Incorrect username or password.", extra_tags='login-error')
        return redirect('index')

    return render(request, 'registration/login.html')

# -----------------------------
# MyAnimal CRUD
# -----------------------------

@login_required
def myanimal_index(request):
    myanimals = MyAnimal.objects.filter(owner=request.user)
    return render(request, 'zooventory/myanimal/index.html', {'myanimals': myanimals})

@login_required
def myanimal_create(request):
    uniqueanimals = UniqueAnimal.objects.all()
    default_species = uniqueanimals[0].name if uniqueanimals else ""

    if request.method == 'POST':
        name = request.POST.get('name')
        unique_animal = UniqueAnimal.objects.get(id=request.POST.get('unique_animal'))
        age = request.POST.get('age')
        weight_lb = request.POST.get('weight_lb')
        weight_oz = request.POST.get('weight_oz')

        # Ensure myanimal age and weight is an integer
        try:
            int(age)
            int(weight_lb)
            int(weight_oz)
        except ValueError:
            messages.error(request, "Age and weight must be an integer.")
            return render(request, 'zooventory/myanimal/create.html', {
                'uniqueanimals': UniqueAnimal.objects.all(),
                'current_species': default_species
            })

        # Ensure myanimal age is more than 0
        if int(age) <= 0 or int(weight_lb) < 0 or int(weight_oz) < 0:
            messages.error(request, "Age and weight must be over 0.")
            return render(request, 'zooventory/myanimal/create.html', {
                'uniqueanimals': UniqueAnimal.objects.all(),
                'current_species': default_species
            })

        # Create myanimal if all required field are filled
        if name and unique_animal and age and weight_lb and weight_oz:
            MyAnimal.objects.create(owner=request.user, unique_animal=unique_animal, name=name, species=unique_animal.name, age=age, weight_lb=weight_lb, weight_oz=weight_oz)
            messages.success(request, 'MyAnimal added successfully!')
            return redirect('myanimal_index')
        else:
            messages.error(request, 'Please fill out all required fields.')

    return render(request, 'zooventory/myanimal/create.html', {
        'uniqueanimals': UniqueAnimal.objects.all(),
        'current_species': default_species
    })

@login_required
def myanimal_update(request, id):
    myanimal = get_object_or_404(MyAnimal, id=id, owner=request.user)

    if request.method == 'POST':
        # Ensure myanimal age is an integer
        try:
            int(request.POST.get('age', myanimal.age))
        except ValueError:
            messages.error(request, "Age must be an integer.")
            return render(request, 'zooventory/myanimal/update.html', {
                'myanimal': myanimal,
                'uniqueanimals': UniqueAnimal.objects.all(),
                'current_species': myanimal.species,
            })


        # Ensure myanimal age is more than 0
        if int(request.POST.get('age', myanimal.age)) <= 0:
            messages.error(request, "Age must be over 0.")
            return render(request, 'zooventory/myanimal/update.html', {
                'myanimal': myanimal,
                'uniqueanimals': UniqueAnimal.objects.all(),
                'current_species': myanimal.species,
            })

        # Update and save myanimal changes
        unique_animal = UniqueAnimal.objects.get(id=request.POST.get('unique_animal'))
        myanimal.unique_animal = unique_animal
        myanimal.name = request.POST.get('name', myanimal.name)
        myanimal.species = unique_animal.name
        myanimal.age = request.POST.get('age', myanimal.age)
        myanimal.save()
        messages.success(request, 'MyAnimal updated successfully!')
        return redirect('myanimal_index')

    return render(request, 'zooventory/myanimal/update.html', {
        'myanimal': myanimal,
        'uniqueanimals': UniqueAnimal.objects.all(),
        'current_species': myanimal.species,
    })

@login_required
def myanimal_delete(request, id):
    myanimal = get_object_or_404(MyAnimal, id=id, owner=request.user)

    if request.method == 'POST':
        myanimal.delete()
        messages.success(request, 'MyAnimal deleted.')
        return redirect('myanimal_index')

    return redirect('myanimal_index')

# -----------------------------
# UniqueAnimal CRUD
# -----------------------------

@login_required
def uniqueanimal_index(request):
    uniqueanimals = UniqueAnimal.objects.all()
    return render(request, 'zooventory/uniqueanimal/index.html', {'uniqueanimals': uniqueanimals})

@login_required
def uniqueanimal_info(request, id):
    uniqueanimal = get_object_or_404(UniqueAnimal, id=id)
    return render(request, 'zooventory/uniqueanimal/info.html', {'uniqueanimal': uniqueanimal})

@login_required
def uniqueanimal_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        # Ensure the user entered a name
        if not name:
            messages.error(request, 'Name is required.')
            return redirect('uniqueanimal_create')

        # Ensure the Unique Animal does not already exist in the database
        if UniqueAnimal.objects.filter(name__iexact=name).exists():
            messages.error(request, f'{name} already exists in the database!')
            return redirect('uniqueanimal_index')

        # Search Animals API for animal name
        api_results = fetch_uniqueanimal_data(name)

        # Create animal from Animals API if the first result matches the name
        if api_results and api_results[0].get('name', '').lower() == name.lower():
            api_animal = api_results[0]

            taxonomy = api_animal.get('taxonomy', {})
            characteristics = api_animal.get('characteristics', {})

            UniqueAnimal.objects.create(
                name = api_animal.get('name', name),
                scientific_name = taxonomy.get('scientific_name'),
                kingdom = taxonomy.get('kingdom'),
                phylum = taxonomy.get('phylum'),
                animal_class = taxonomy.get('class'),
                order = taxonomy.get('order'),
                family = taxonomy.get('family'),
                genus = taxonomy.get('genus'),
                prey=characteristics.get('prey'),
                name_of_young=characteristics.get('name_of_young'),
                group_behavior=characteristics.get('group_behavior'),
                estimated_population_size=characteristics.get('estimated_population_size'),
                biggest_threat=characteristics.get('biggest_threat'),
                most_distinctive_feature=characteristics.get('most_distinctive_feature'),
                gestation_period=characteristics.get('gestation_period'),
                habitat=characteristics.get('habitat'),
                diet=characteristics.get('diet'),
                average_litter_size=characteristics.get('average_litter_size'),
                lifestyle=characteristics.get('lifestyle'),
                common_name=characteristics.get('common_name'),
                number_of_species=characteristics.get('number_of_species'),
                slogan=characteristics.get('slogan'),
                color=characteristics.get('color'),
                skin_type=characteristics.get('skin_type'),
                top_speed=characteristics.get('top_speed'),
            )

            # Let user know the Unique Animal information has been pulled from the Animals API
            messages.success(request, f'Imported {name} from the API successfully!')
            return redirect('uniqueanimal_index')

        # Create the Unique Animal if the API did not have a match
        UniqueAnimal.objects.create(
            owner=request.user,
            name=name,
            scientific_name=request.POST.get('scientific_name'),
            kingdom=request.POST.get('kingdom'),
            phylum=request.POST.get('phylum'),
            animal_class=request.POST.get('class'),
            order=request.POST.get('order'),
            family=request.POST.get('family'),
            genus=request.POST.get('genus'),
            prey=request.POST.get('prey'),
            name_of_young=request.POST.get('name_of_young'),
            group_behavior=request.POST.get('group_behavior'),
            estimated_population_size=request.POST.get('estimated_population_size'),
            biggest_threat=request.POST.get('biggest_threat'),
            most_distinctive_feature=request.POST.get('most_distinctive_feature'),
            gestation_period=request.POST.get('gestation_period'),
            habitat=request.POST.get('habitat'),
            diet=request.POST.get('diet'),
            average_litter_size=request.POST.get('average_litter_size'),
            lifestyle=request.POST.get('lifestyle'),
            common_name=request.POST.get('common_name'),
            number_of_species=request.POST.get('number_of_species'),
            slogan=request.POST.get('slogan'),
            color=request.POST.get('color'),
            skin_type=request.POST.get('skin_type'),
            top_speed=request.POST.get('top_speed')
        )
        messages.success(request, 'UniqueAnimal added successfully! (No API match found)')
        return redirect('uniqueanimal_index')

    return render(request, 'zooventory/uniqueanimal/create.html')

# Alternate create function so the Animals API doesn't get searched twice
@login_required
def uniqueanimal_create_api(request):
    name = request.POST.get('name')
    # Ensure the Unique Animal does not already exist in the database
    if UniqueAnimal.objects.filter(name__iexact=name).exists():
        messages.error(request, f'{name} already exists in the database!')
        return redirect('uniqueanimal_index')

    UniqueAnimal.objects.create(
        name=request.POST.get('name'),
        scientific_name=request.POST.get('scientific_name'),
        kingdom=request.POST.get('kingdom'),
        phylum=request.POST.get('phylum'),
        animal_class=request.POST.get('animal_class'),
        order=request.POST.get('order'),
        family=request.POST.get('family'),
        genus=request.POST.get('genus'),
        prey=request.POST.get('prey'),
        name_of_young=request.POST.get('name_of_young'),
        group_behavior=request.POST.get('group_behavior'),
        estimated_population_size=request.POST.get('estimated_population_size'),
        biggest_threat=request.POST.get('biggest_threat'),
        most_distinctive_feature=request.POST.get('most_distinctive_feature'),
        gestation_period=request.POST.get('gestation_period'),
        habitat=request.POST.get('habitat'),
        diet=request.POST.get('diet'),
        average_litter_size=request.POST.get('average_litter_size'),
        lifestyle=request.POST.get('lifestyle'),
        common_name=request.POST.get('common_name'),
        number_of_species=request.POST.get('number_of_species'),
        slogan=request.POST.get('slogan'),
        color=request.POST.get('color'),
        skin_type=request.POST.get('skin_type'),
        top_speed=request.POST.get('top_speed')
    )
    messages.success(request, 'UniqueAnimal added successfully!')
    return redirect('uniqueanimal_index')

@login_required
def uniqueanimal_update(request, id):
    uniqueanimal = get_object_or_404(UniqueAnimal, id=id)

    # Deny the update if the current user did not create the Unique Animal
    if uniqueanimal.owner != request.user:
        messages.error(request, 'You do not have permission to update this Unique Animal.')
        return redirect('uniqueanimal_index')

    if request.method == 'POST':
        # Scientific Name. Base name cannot be modified since it is the unique identifier
        uniqueanimal.scientific_name = request.POST.get('scientific_name')

        # Taxonomy
        uniqueanimal.kingdom = request.POST.get('kingdom')
        uniqueanimal.phylum = request.POST.get('phylum')
        uniqueanimal.animal_class = request.POST.get('animal_class')
        uniqueanimal.order = request.POST.get('order')
        uniqueanimal.family = request.POST.get('family')
        uniqueanimal.genus = request.POST.get('genus')

        # Characteristics
        uniqueanimal.prey = request.POST.get('prey')
        uniqueanimal.name_of_young = request.POST.get('name_of_young')
        uniqueanimal.group_behavior = request.POST.get('group_behavior')
        uniqueanimal.estimated_population_size = request.POST.get('estimated_population_size')
        uniqueanimal.biggest_threat = request.POST.get('biggest_threat')
        uniqueanimal.most_distinctive_feature = request.POST.get('most_distinctive_feature')
        uniqueanimal.gestation_period = request.POST.get('gestation_period')
        uniqueanimal.habitat = request.POST.get('habitat')
        uniqueanimal.diet = request.POST.get('diet')
        uniqueanimal.average_litter_size = request.POST.get('average_litter_size')
        uniqueanimal.lifestyle = request.POST.get('lifestyle')
        uniqueanimal.common_name = request.POST.get('common_name')
        uniqueanimal.number_of_species = request.POST.get('number_of_species')
        uniqueanimal.slogan = request.POST.get('slogan')
        uniqueanimal.color = request.POST.get('color')
        uniqueanimal.skin_type = request.POST.get('skin_type')
        uniqueanimal.top_speed = request.POST.get('top_speed')

        # Save the Unique Animal
        uniqueanimal.save()
        messages.success(request, 'UniqueAnimal updated successfully!')
        return redirect('uniqueanimal_index')

    return render(request, 'zooventory/uniqueanimal/update.html', {'uniqueanimal': uniqueanimal})

@login_required
def uniqueanimal_search(request):
    results = None
    query = ''

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

        # If there is a query, send it to the Animals API and return results to te user
        if query:
            results = fetch_uniqueanimal_data(query)

            # Handle API errors gracefully
            if isinstance(results, str):
                messages.error(request, 'Error contacting animal API. Please try again later.')
                results = None

    return render(request, 'zooventory/uniqueanimal/search.html', {'query': query, 'results': results})

# -----------------------------
# Food CRUD
# -----------------------------

@login_required
def food_index(request):
    food_list = Food.objects.filter(owner=request.user)
    return render(request, 'zooventory/food/index.html', {'food_list': food_list})

@login_required
def food_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        unit = request.POST.get('unit')

        # Ensure amount is a number
        try:
            float(amount)
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/food/create.html', { 'unit_choices': Food.UNIT_CHOICES })

        # Ensure amount is more than 0
        if float(amount) <= 0:
            messages.error(request, "Amount must be over 0.")
            return render(request, 'zooventory/food/create.html', { 'unit_choices': Food.UNIT_CHOICES })

        # Create the food object if required fields are filled
        if name and amount and unit:
            Food.objects.create(owner=request.user, name=name, amount=amount, unit=unit)
            messages.success(request, 'Food added successfully!')
            return redirect('food_index')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'zooventory/food/create.html', { 'unit_choices': Food.UNIT_CHOICES })

@login_required
def food_update(request, id):
    food = get_object_or_404(Food, id=id, owner=request.user)

    if request.method == 'POST':
        # Ensure amount is a float value
        try:
            float(request.POST.get('amount', food.amount))
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/food/update.html', {'food': food, 'unit_choices': Food.UNIT_CHOICES})

        #Ensure amount is more than 0
        if float(request.POST.get('amount', food.amount)) <= 0:
            messages.error(request, "Amount must be over 0.")
            return render(request, 'zooventory/food/update.html', {'food': food, 'unit_choices': Food.UNIT_CHOICES})

        # Save the changes
        food.name = request.POST.get('name', food.name)
        food.amount = request.POST.get('amount', food.amount)
        food.unit = request.POST.get('unit', food.unit)
        food.save()
        messages.success(request, 'Food updated successfully!')
        return redirect('food_index')

    return render(request, 'zooventory/food/update.html', {'food': food, 'unit_choices': Food.UNIT_CHOICES})

@login_required
def food_delete(request, id):
    food = get_object_or_404(Food, id=id, owner=request.user)

    if request.method == 'POST':
        food.delete()
        messages.success(request, 'Food deleted.')
        return redirect('food_index')

    return redirect('food_index')

# -----------------------------
# Feeding Schedule CRUD
# -----------------------------

@login_required
def feeding_schedule_index(request, id):
    myanimal = get_object_or_404(MyAnimal, id=id, owner=request.user)
    schedules = myanimal.feeding_schedules.all()
    return render(request, 'zooventory/feeding_schedule/index.html', {
        'myanimal': myanimal,
        'schedules': schedules,
    })

@login_required
def feeding_schedule_create(request, id):
    myanimal = get_object_or_404(MyAnimal, id=id, owner=request.user)

    if request.method == 'POST':
        frequency = request.POST.get('frequency')
        time_of_day = request.POST.get('time_of_day')
        hours_interval = request.POST.get('hours_interval')
        day_of_week = request.POST.get('day_of_week')

        # Convert time_of_day to a Time object
        parsed_time = None
        if time_of_day:
            parsed_time = datetime.strptime(time_of_day, '%H:%M').time()

        next_run = timezone.now()

        # Compute the next_run
        if frequency == FeedingSchedule.DAILY and parsed_time:
            today = timezone.now().date()
            next_run = timezone.make_aware(datetime.combine(today, parsed_time))
            if next_run < timezone.now():
                next_run += timedelta(days=1)

        elif frequency == FeedingSchedule.WEEKLY and parsed_time and day_of_week:
            today = timezone.now().date()
            today_weekday = today.weekday()
            target = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(day_of_week)

            days_ahead = (target - today_weekday) % 7
            # Schedule for next week if already passed this week
            if days_ahead < 0:
                temp = timezone.make_aware(datetime.combine(today, parsed_time))
                if temp < timezone.now():
                    days_ahead = 7

            run_date = today + timedelta(days=days_ahead)
            next_run = timezone.make_aware(datetime.combine(run_date, parsed_time))

        elif frequency == FeedingSchedule.EVERY_X_HOURS:
            next_run = timezone.now() + timedelta(hours=int(hours_interval))

        # Create the feeding schedule
        FeedingSchedule.objects.create(
            myanimal=myanimal,
            frequency=frequency,
            time_of_day=time_of_day,
            hours_interval=hours_interval,
            day_of_week=day_of_week,
            next_run=next_run,
        )

        messages.success(request, 'Feeding schedule created successfully!')
        return redirect('feeding_schedule_index', id=id)

    return render(request, 'zooventory/feeding_schedule/create.html', {
        'myanimal': myanimal,
        'frequency_choices': FeedingSchedule.FREQUENCY_CHOICES,
        'day_choices': FeedingSchedule.DAY_CHOICES,
    })

@login_required
def feeding_schedule_update(request, id):
    schedule = get_object_or_404(FeedingSchedule, id=id)
    myanimal = schedule.myanimal

    if schedule.myanimal.owner != request.user:
        messages.error(request, 'You are not the owner of this feeding schedule!')
        return redirect('feeding_schedule_index', id=id)

    if request.method == 'POST':
        frequency = request.POST.get('frequency')
        time_of_day = request.POST.get('time_of_day')
        hours_interval = request.POST.get('hours_interval')
        day_of_week = request.POST.get('day_of_week')

        parsed_time = datetime.strptime(time_of_day, '%H:%M').time() if time_of_day else None
        schedule.frequency = frequency
        schedule.time_of_day = parsed_time
        schedule.hours_interval = hours_interval
        schedule.day_of_week = request.POST.get('day_of_week')

        next_run = schedule.next_run

        # Recalculate next_run
        if frequency == FeedingSchedule.DAILY and parsed_time:
            today = timezone.now().date()
            next_run = timezone.make_aware(datetime.combine(today, parsed_time))
            if next_run < timezone.now():
                next_run += timedelta(days=1)


        elif frequency == FeedingSchedule.WEEKLY and parsed_time and day_of_week:
            today = timezone.now().date()
            today_weekday = today.weekday()
            target = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(day_of_week)

            days_ahead = (target - today_weekday) % 7
            # Schedule for next week if already passed this week
            if days_ahead < 0:
                temp = timezone.make_aware(datetime.combine(today, parsed_time))
                if temp < timezone.now():
                    days_ahead = 7

            run_date = today + timedelta(days=days_ahead)
            next_run = timezone.make_aware(datetime.combine(run_date, parsed_time))

        elif frequency == FeedingSchedule.EVERY_X_HOURS:
            next_run = timezone.now() + timedelta(hours=int(hours_interval))

        schedule.next_run = next_run
        schedule.save()

        messages.success(request, 'Feeding schedule updated successfully!')
        return redirect('feeding_schedule_index', id=id)

    return render(request, 'zooventory/feeding_schedule/update.html', {
        'myanimal': myanimal,
        'schedule': schedule,
        'frequency_choices': FeedingSchedule.FREQUENCY_CHOICES,
        'day_choices': FeedingSchedule.DAY_CHOICES,
    })

@login_required
def feeding_schedule_delete(request, id):
    schedule = get_object_or_404(FeedingSchedule, id=id, owner=request.user)

    if schedule.myanimal.owner != request.user:
        messages.error(request, 'You are not the owner of this feeding schedule!')
        return redirect('myanimal_index')

    myanimal_id = schedule.myanimal.id
    schedule.delete()

    messages.success(request, 'Feeding schedule deleted successfully!')
    return redirect('feeding_schedule_index', id=myanimal_id)


# -----------------------------
# Calculator:
# - Feed a MyAnimal
# - Weigh a MyAnimal
# -----------------------------

@login_required
def feed_myanimal(request):
    # Get all myanimals and food that the user owns
    myanimals = MyAnimal.objects.filter(owner=request.user)
    food_items = Food.objects.filter(owner=request.user)

    if request.method == 'POST':
        myanimal_id = request.POST.get('myanimal_id')
        food_id = request.POST.get('food_id')
        amount = request.POST.get('amount', 0)
        notes = request.POST.get('notes')

        myanimal = get_object_or_404(MyAnimal, id=myanimal_id, owner=request.user)
        food = get_object_or_404(Food, id=food_id, owner=request.user)
        food_unit = food.unit

        # Verify amount is a float
        try:
            float(amount)
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/calculator/feed.html', {
                'myanimals': myanimals,
                'food': food_items,
            })

        if float(amount) <= 0:
            messages.error(request, 'Amount must be over 0.')
            return render(request, 'zooventory/calculator/feed.html', {
                'myanimals': myanimals,
                'food': food_items,
            })

        amount = float(amount)

        # Ensure food amount is more than 0
        if food.amount > 0:
            # Only subtract if there is enough food in inventory
            if food.amount >= amount:
                food.amount -= amount
                food.save()

                converted_grams = convert_to_grams(amount, food_unit)
                converted_ml = convert_to_ml(amount, food_unit)

                myanimal.last_fed = timezone.now()
                myanimal.save()

                Log.objects.create(
                    owner=request.user,
                    myanimal=myanimal,
                    food=food,
                    amount_fed=amount,
                    unit=food_unit,
                    converted_amount_grams=converted_grams,
                    converted_amount_ml=converted_ml,
                    log_type=Log.FEEDING,
                    description=notes
                )
                messages.success(request, f'{myanimal.name} has been fed!')
            else:
                messages.error(request, 'Not enough food to feed animal!')
        else:
            messages.error(request, 'Food amount cannot be negative!')

        return redirect('feed_myanimal')

    # Render the feed.html with the myanimals and food list for the user to choose from
    return render(request, 'zooventory/calculator/feed.html', {
        'myanimals': myanimals,
        'food': food_items,
    })

@login_required
def weigh_myanimal(request):
    myanimals = MyAnimal.objects.filter(owner=request.user)

    if request.method == 'POST':
        myanimal_id = request.POST.get('myanimal_id')
        weight_lb = request.POST.get('weight_lb')
        weight_oz = request.POST.get('weight_oz')
        notes = request.POST.get('notes')

        myanimal = get_object_or_404(MyAnimal, id=myanimal_id, owner=request.user)

        try:
            int(weight_lb)
            int(weight_oz)
        except ValueError:
            messages.error(request, 'Weight inputs must be an integer.')
            return render(request, 'zooventory/calculator/weigh.html', {'myanimals': myanimals})

        if int(weight_lb) < 0 or int(weight_oz) < 0:
            messages.error(request, 'Weight inputs cannot be negative.')
            return render(request, 'zooventory/calculator/weigh.html', {'myanimals': myanimals})

        myanimal.weight_lb = weight_lb
        myanimal.weight_oz = weight_oz
        myanimal.save()
        Log.objects.create(owner=request.user, myanimal=myanimal, log_type=Log.WEIGHT_UPDATE, description=notes, weight_lb=weight_lb, weight_oz=weight_oz)
        messages.success(request, 'Weight updated successfully!')
        return redirect('weigh_myanimal')

    return render(request, 'zooventory/calculator/weigh.html', {'myanimals': myanimals})

# -----------------------------
# Charts:
# - Food Usage
# - Feeding Frequency
# - Top Food
# - Weight Trends
# -----------------------------

@login_required
def chart_food_usage(request):
    # Variables to display food usage over last 30 days
    today = timezone.now().date()
    start_date = today - timedelta(days=29)
    date_list = [start_date + timedelta(days=i) for i in range(30)]

    # Get all FEEDING logs
    logs = (
        Log.objects.filter(owner=request.user, log_type=Log.FEEDING, created_at__gte=start_date)
        .values('created_at__date')
        .annotate(
            total_grams=Sum('converted_amount_grams'),
            total_ml=Sum('converted_amount_ml')
        )
        .order_by('created_at__date')
    )

    labels = []
    data_grams = []
    data_ml = []

    log_map = {entry['created_at__date']: entry for entry in logs}

    for date in date_list:
        labels.append(date.strftime('%Y-%m-%d'))

        entry = log_map.get(date, None)
        data_grams.append(entry['total_grams'] if entry else 0)
        data_ml.append(entry['total_ml'] if entry else 0)

    return JsonResponse({'labels': labels, 'data_grams': data_grams, 'data_ml': data_ml})

@login_required
def chart_feeding_frequency(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=29)

    logs = (
        Log.objects.filter(owner=request.user, log_type=Log.FEEDING, created_at__gte=start_date)
        .values('myanimal__name')
        .annotate(count=Sum(1))
        .order_by('myanimal__name')
    )

    labels = [entry['myanimal__name'] for entry in logs]
    data = [entry['count'] for entry in logs]

    return JsonResponse({'labels': labels, 'data': data})

@login_required
def chart_top_food(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=29)

    logs = (
        Log.objects.filter(owner=request.user, log_type=Log.FEEDING, created_at__gte=start_date)
        .values('food__name')
        .annotate(
            grams=Sum('converted_amount_grams'),
            ml=Sum('converted_amount_ml')
        )
    )

    food_list = []
    for entry in logs:
        amount = entry['grams'] if entry['grams'] is not None else entry['ml']
        food_list.append({
            'name': entry['food__name'],
            'amount': amount or 0,
        })

    top_foods = sorted(food_list, key=lambda food: food['amount'], reverse=True)[:5]

    labels = [entry['name'] for entry in food_list]
    data = [entry['amount'] for entry in food_list]

    return JsonResponse({'labels': labels, 'data': data})

@login_required
def chart_weight_trends(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=29)
    date_list = [start_date + timedelta(days=i) for i in range(30)]
    labels = [d.strftime('%Y-%m-%d') for d in date_list]

    logs = (
        Log.objects.filter(owner=request.user, log_type=Log.WEIGHT_UPDATE, created_at__date__gte=start_date)
        .values('myanimal__name', 'created_at__date', 'weight_lb', 'weight_oz')
        .order_by('myanimal__name', 'created_at__date')
    )

    data = {}

    for entry in logs:
        name = entry['myanimal__name']

        lb = entry['weight_lb'] or 0
        oz = entry['weight_oz'] or 0
        weight = lb + (oz/16)

        if name not in data:
            data[name] = [None] * 30

        date_obj = entry['created_at__date']
        index = (date_obj - start_date).days

        if 0 <= index < 30:
            data[name][index] = weight

    for name, values in data.items():
        last_value = None
        for i in range(30):
            if values[i] is None:
                values[i] = last_value
            else:
                last_value = values[i]

    return JsonResponse({'labels': labels, 'data': data})