import requests

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MyAnimal, UniqueAnimal, Food
from django.utils import timezone
from django.conf import settings

# -----------------------------
# Fetch request for animal API
# -----------------------------
def fetch_uniqueanimal_data(name):
    api_url = f'https://api.api-ninjas.com/v1/animals?name={name}'
    headers = {"X-Api-Key": settings.API_NINJAS_KEY}

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

def custom_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Ensure inputs are correct. Note: Password must be 8 or more characters.", extra_tags='register-error')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')

        messages.error(request, "Incorrect username or password.", extra_tags='login-error')
        return redirect('index')

    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """User dashboard."""
    return render(request, 'zooventory/dashboard/dashboard.html')


# -----------------------------
# MyAnimal CRUD
# -----------------------------

@login_required
def myanimal_index(request):
    myanimals = MyAnimal.objects.filter(owner=request.user)
    return render(request, 'zooventory/myanimal/index.html', {'myanimals': myanimals})


@login_required
def myanimal_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        species = request.POST.get('species')
        age = request.POST.get('age')

        try:
            int(age)
        except ValueError:
            messages.error(request, "Age must be an integer.")
            return render(request, 'zooventory/myanimal/create.html')

        if int(age) <= 0:
            messages.error(request, "Age must be over 0.")
            return render(request, 'zooventory/myanimal/create.html')

        if name and species and age:
            MyAnimal.objects.create(owner=request.user, name=name, species=species, age=age)
            messages.success(request, 'MyAnimal added successfully!')
            return redirect('myanimal_index')
        else:
            messages.error(request, 'Please fill out all required fields.')

    return render(request, 'zooventory/myanimal/create.html')


@login_required
def myanimal_update(request, id):
    myanimal = get_object_or_404(MyAnimal, id=id, owner=request.user)

    if request.method == 'POST':
        try:
            int(request.POST.get('age', myanimal.age))
        except ValueError:
            messages.error(request, "Age must be an integer.")
            return render(request, 'zooventory/myanimal/update.html', {'myanimal': myanimal})

        if int(request.POST.get('age', myanimal.age)) <= 0:
            messages.error(request, "Age must be over 0.")
            return render(request, 'zooventory/myanimal/update.html', {'myanimal': myanimal})

        myanimal.name = request.POST.get('name', myanimal.name)
        myanimal.species = request.POST.get('species', myanimal.species)
        myanimal.age = request.POST.get('age', myanimal.age)
        myanimal.save()
        messages.success(request, 'MyAnimal updated successfully!')
        return redirect('myanimal_index')

    return render(request, 'zooventory/myanimal/update.html', {'myanimal': myanimal})


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

def uniqueanimal_index(request):
    uniqueanimals = UniqueAnimal.objects.all()
    return render(request, 'zooventory/uniqueanimal/index.html', {'uniqueanimals': uniqueanimals})


def uniqueanimal_info(request, id):
    uniqueanimal = get_object_or_404(UniqueAnimal, id=id)
    return render(request, 'zooventory/uniqueanimal/index.html', {'uniqueanimal': uniqueanimal})

def uniqueanimal_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        if not name:
            messages.error(request, 'Name is required.')
            return redirect('uniqueanimal_create')

        if UniqueAnimal.objects.filter(name__iexact=name).exists():
            messages.error(request, f'{name} already exists in the database!')
            return redirect('uniqueanimal_index')

        api_results = fetch_uniqueanimal_data(name)

        if api_results:
            api_animal = api_results[0]

            taxonomy = api_animal.get('taxonomy', {})
            characteristics = api_animal.get('characteristics', {})

            UniqueAnimal.objects.create(
                name = api_animal.get('name', name),
                scientific_name = taxonomy.get('scientific_name'),
                kingdom = taxonomy.get('kingdom'),
                phylum = taxonomy.get('phylum'),
                animal_class = taxonomy.get('animal_class'),
                order = taxonomy.get('order'),
                family = taxonomy.get('family'),
                genus = taxonomy.get('genus'),
                characteristics = characteristics
            )

        UniqueAnimal.objects.create(
            owner=request.user,
            name=name,
            scientific_name=request.POST.get('scientific_name'),
            kingdom=request.POST.get('kingdom'),
            phylum=request.POST.get('phylum'),
            animal_class=request.POST.get('animal_class'),
            order=request.POST.get('order'),
            family=request.POST.get('family'),
            genus=request.POST.get('genus'),
            characteristics={
                'prey': request.POST.get('prey'),
                'name_of_young': request.POST.get('name_of_young'),
                'group_behavior': request.POST.get('group_behavior'),
                'estimated_population_size': request.POST.get('estimated_population_size'),
                'biggest_threat': request.POST.get('biggest_threat'),
                'most_distinctive_feature': request.POST.get('most_distinctive_feature'),
                'gestation_period': request.POST.get('gestation_period'),
                'habitat': request.POST.get('habitat'),
                'diet': request.POST.get('diet'),
                'average_litter_size': request.POST.get('average_litter_size'),
                'lifestyle': request.POST.get('lifestyle'),
                'common_name': request.POST.get('common_name'),
                'number_of_species': request.POST.get('number_of_species'),
                'location': request.POST.get('location'),
                'slogan': request.POST.get('slogan'),
                'group': request.POST.get('group'),
                'color': request.POST.get('color'),
                'skin_type': request.POST.get('skin_type'),
                'top_speed': request.POST.get('top_speed'),
                'lifespan': request.POST.get('lifespan'),
                'weight': request.POST.get('weight'),
                'height': request.POST.get('height'),
                'age_of_sexual_maturity': request.POST.get('age_of_sexual_maturity'),
                'age_of_weaning': request.POST.get('age_of_weaning')
            }
        )
        messages.success(request, 'UniqueAnimal added successfully!')
        return redirect('uniqueanimal_index')

    return render(request, 'zooventory/uniqueanimal/create')

def uniqueanimal_update(request, id):
    uniqueanimal = get_object_or_404(UniqueAnimal, id=id)

    if request.method == 'POST':
        # Basic and Scientific Name
        uniqueanimal.name = request.POST.get('name')
        uniqueanimal.scientific_name = request.POST.get('scientific_name')

        # Taxonomy
        uniqueanimal.kingdom = request.POST.get('kingdom')
        uniqueanimal.phylum = request.POST.get('phylum')
        uniqueanimal.animal_class = request.POST.get('animal_class')
        uniqueanimal.order = request.POST.get('order')
        uniqueanimal.family = request.POST.get('family')
        uniqueanimal.genus = request.POST.get('genus')

        # Characteristics
        characteristics = uniqueanimal.characteristics or {}
        for field in [
            'prey', 'name_of_young', 'group_behavior', 'estimated_population_size',
            'biggest_threat', 'most_distinctive_feature', 'gestation_period',
            'habitat', 'diet', 'average_litter_size', 'lifestyle', 'common_name',
            'number_of_species', 'location', 'slogan', 'group', 'color',
            'skin_type', 'top_speed', 'lifespan', 'weight', 'height',
            'age_of_sexual_maturity', 'age_of_weaning'
        ]:
            characteristics[field] = request.POST.get(field)

        uniqueanimal.characteristics = characteristics

        uniqueanimal.save()
        messages.success(request, 'UniqueAnimal updated successfully!')
        return redirect('uniqueanimal_index')

    return render(request, 'zooventory/uniqueanimal/update')

def uniqueanimal_search(request):
    results = None
    query = ''

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()

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
        measurement = request.POST.get('measurement')
        try:
            float(amount)
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/food/create.html')

        if float(amount) <= 0:
            messages.error(request, "Amount must be over 0.")
            return render(request, 'zooventory/food/create.html')

        if name and amount and measurement:
            Food.objects.create(owner=request.user, name=name, amount=amount, measurement=measurement)
            messages.success(request, 'Food added successfully!')
            return redirect('food_index')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'zooventory/food/create.html')


@login_required
def food_update(request, id):
    food = get_object_or_404(Food, id=id, owner=request.user)

    if request.method == 'POST':
        try:
            float(request.POST.get('amount', food.amount))
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/food/update.html', {'food': food})

        if float(request.POST.get('amount', food.amount)) <= 0:
            messages.error(request, "Amount must be over 0.")
            return render(request, 'zooventory/food/update.html', {'food': food})
        food.name = request.POST.get('name', food.name)
        food.amount = request.POST.get('amount', food.amount)
        food.measurement = request.POST.get('measurement', food.measurement)
        food.save()
        messages.success(request, 'Food updated successfully!')
        return redirect('food_index')

    return render(request, 'zooventory/food/update.html', {'food': food})


@login_required
def food_delete(request, id):
    food = get_object_or_404(Food, id=id, owner=request.user)

    if request.method == 'POST':
        food.delete()
        messages.success(request, 'Food deleted.')
        return redirect('food_index')

    return redirect('food_index')


# -----------------------------
# Calculator: Feed a MyAnimal
# -----------------------------

@login_required
def feed_myanimal(request):
    myanimals = MyAnimal.objects.filter(owner=request.user)
    food_items = Food.objects.filter(owner=request.user)

    if request.method == 'POST':
        myanimal_id = request.POST.get('myanimal_id')
        food_id = request.POST.get('food_id')
        amount = float(request.POST.get('amount', 0))

        myanimal = get_object_or_404(MyAnimal, id=myanimal_id, owner=request.user)
        food = get_object_or_404(Food, id=food_id, owner=request.user)

        if food.amount > 0:
            if food.amount >= amount:
                food.amount -= amount
                food.save()
                myanimal.last_fed = timezone.now()
                myanimal.save()
                messages.success(request, f'{myanimal.name} has been fed!')
            else:
                messages.error(request, 'Not enough food to feed animal!')
        else:
            messages.error(request, 'Food amount cannot be negative!')

        return redirect('calculator')

    return render(request, 'zooventory/calculator/feed.html', {
        'myanimals': myanimals,
        'food': food_items,
    })
