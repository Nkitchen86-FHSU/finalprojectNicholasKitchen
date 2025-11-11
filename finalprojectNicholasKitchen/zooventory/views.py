from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MyAnimal, Food
from django.utils import timezone

# -----------------------------
# Home / Dashboard Views
# -----------------------------

def index(request):
    """Public landing page."""
    return render(request, 'zooventory/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please check your inputs.")
    else:
        form = UserCreationForm()
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

        if name and species and age:
            MyAnimal.objects.create(owner=request.user, name=name, species=species, age=age)
            messages.success(request, 'MyAnimal added successfully!')
            return redirect('myanimal_index')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'zooventory/myanimal/create.html')


@login_required
def myanimal_update(request, id):
    myanimal = get_object_or_404(MyAnimal, id=id, owner=request.user)

    if request.method == 'POST':
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

        if food.amount >= amount > 0:
            food.amount -= amount
            food.save()
            myanimal.last_fed = timezone.now()
            myanimal.save()
            messages.success(request, f'{myanimal.name} has been fed!')
        else:
            messages.error(request, 'Not enough food available.')

        return redirect('calculator')

    return render(request, 'zooventory/calculator/feed.html', {
        'myanimals': myanimals,
        'food': food_items,
    })
