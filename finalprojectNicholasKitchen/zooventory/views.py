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
    if request.method == 'POST':
        name = request.POST.get('name')
        species = request.POST.get('species')
        age = request.POST.get('age')

        # Ensure myanimal age is an integer
        try:
            int(age)
        except ValueError:
            messages.error(request, "Age must be an integer.")
            return render(request, 'zooventory/myanimal/create.html')

        # Ensure myanimal age is more than 0
        if int(age) <= 0:
            messages.error(request, "Age must be over 0.")
            return render(request, 'zooventory/myanimal/create.html')

        # Create myanimal if all required field are filled
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
        # Ensure myanimal age is an integer
        try:
            int(request.POST.get('age', myanimal.age))
        except ValueError:
            messages.error(request, "Age must be an integer.")
            return render(request, 'zooventory/myanimal/update.html', {'myanimal': myanimal})

        # Ensure myanimal age is more than 0
        if int(request.POST.get('age', myanimal.age)) <= 0:
            messages.error(request, "Age must be over 0.")
            return render(request, 'zooventory/myanimal/update.html', {'myanimal': myanimal})

        # Update and save myanimal changes
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
    return render(request, 'zooventory/uniqueanimal/info.html', {'uniqueanimal': uniqueanimal})

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
def uniqueanimal_create_api(request):
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
        measurement = request.POST.get('measurement')

        # Ensure amount is a number
        try:
            float(amount)
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/food/create.html')

        # Ensure amount is more than 0
        if float(amount) <= 0:
            messages.error(request, "Amount must be over 0.")
            return render(request, 'zooventory/food/create.html')

        # Create the food object if required fields are filled
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
        # Ensure amount is a float value
        try:
            float(request.POST.get('amount', food.amount))
        except ValueError:
            messages.error(request, 'Amount must be a number.')
            return render(request, 'zooventory/food/update.html', {'food': food})

        #Ensure amount is more than 0
        if float(request.POST.get('amount', food.amount)) <= 0:
            messages.error(request, "Amount must be over 0.")
            return render(request, 'zooventory/food/update.html', {'food': food})

        # Save the changes
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
    # Get all myanimals and food that the user owns
    myanimals = MyAnimal.objects.filter(owner=request.user)
    food_items = Food.objects.filter(owner=request.user)

    if request.method == 'POST':
        myanimal_id = request.POST.get('myanimal_id')
        food_id = request.POST.get('food_id')
        amount = float(request.POST.get('amount', 0))

        myanimal = get_object_or_404(MyAnimal, id=myanimal_id, owner=request.user)
        food = get_object_or_404(Food, id=food_id, owner=request.user)

        # Ensure food amount is more than 0
        if food.amount > 0:
            # Only subtract if there is enough food in inventory
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

    # Render the feed.html with the myanimals and food list for the user to choose from
    return render(request, 'zooventory/calculator/feed.html', {
        'myanimals': myanimals,
        'food': food_items,
    })
