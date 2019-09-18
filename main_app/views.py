from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .forms import SignUpForm
from .models import Beer, LikeBeerUser, Restaurant, LikeRestaurantUser

# Create your views here.
def landing(request):
    return render(request, 'landing.html')

def about(request):
    return render(request, 'about.html')

@login_required
def home(request):
    recent_beers_added = Beer.objects.all().order_by('-id')[0:5]
    restaurants = Restaurant.objects.all()
    beers = Beer.objects.all()
    return render(request, 'home.html', {'recent_beers': recent_beers_added, 'restaurants': restaurants, 'beers': beers})

@login_required
def cooler(request):
  my_beers = LikeBeerUser.objects.filter(user=request.user)
  return render(request, 'cooler.html', { 'my_beers': my_beers})

@login_required
def my_restaurants(request):
  my_rests = LikeRestaurantUser.objects.filter(user=request.user)
  return render(request, 'my_restaurants.html', { 'my_rests': my_rests })

@login_required
def cooler_add(request, beer_id, user_id):
  beer = Beer.objects.get(id=beer_id)
  user = User.objects.get(id=user_id)
  add = LikeBeerUser(beer=beer, user=user)
  add.save()
  messages.success(request, f'Successfully added {beer.name} to Cooler')
  return HttpResponse('<script>history.back();</script>')

@login_required
def cooler_remove(request, beer_id, user_id):
  beer = Beer.objects.get(id=beer_id)
  rm_beer = LikeBeerUser.objects.get(beer=beer_id, user=user_id)
  rm_beer.delete()
  messages.success(request, f'Successfully removed {beer.name} from Cooler')
  return HttpResponse('<script>history.back();</script>')


@login_required
def restaurant_add(request, restaurant_id, user_id):
  rest = Restaurant.objects.get(id=restaurant_id)
  user = User.objects.get(id=user_id)
  add = LikeRestaurantUser(rest=rest, user=user)
  add.save()
  messages.success(request, f'You are now tracking {rest.name} in {rest.location}')
  return HttpResponse('<script>history.back();</script>')

@login_required
def restaurant_remove(request, restaurant_id, user_id):
  rest = Restaurant.objects.get(id=restaurant_id)
  rm_rest = LikeRestaurantUser.objects.get(rest=restaurant_id, user=user_id)
  rm_rest.delete()
  messages.success(request, f'You are no longer tracking {rest.name} in {rest.location}')
  return HttpResponse('<script>history.back();</script>')


def discover(request):
    beers = Beer.objects.all()
    my_beers = LikeBeerUser.objects.filter(user=request.user)
    my_beers_list = []
    restaurants = Restaurant.objects.all()
    my_rests = LikeRestaurantUser.objects.filter(user=request.user)
    my_rests_list = []
    for b in my_beers:
      my_beers_list.append(b.beer.name)
    for r in my_rests:
      my_rests_list.append(r.rest.name)
    return render(request, 'discover.html', {
       'beers': beers,
       'my_beers': my_beers,
       'my_beers_list': my_beers_list,
       'restaurants': restaurants,
       'my_rests': my_rests,
       'my_rests_list': my_rests_list,
       })

def search(request):
  beers = Beer.objects.filter(Q(name__icontains=request.GET['search_query']) | Q(brewer__icontains=request.GET['search_query']))
  restaurants = Restaurant.objects.filter(name__icontains=request.GET['search_query'])
  my_beers = LikeBeerUser.objects.filter(user=request.user)
  print(request.GET['search_query'])
  return render(request, 'discover.html', {
       'beers': beers,
       'restaurants': restaurants,
       'my_beers': my_beers})

def beer_detail(request, beer_id):
    beer = Beer.objects.get(id=beer_id)
    my_beers = LikeBeerUser.objects.filter(user=request.user)
    my_beers_list = []
    for b in my_beers:
      my_beers_list.append(b.beer.name)
    rests = Restaurant.objects.filter(beers_on_tap=beer_id)
    untapped_rests = Restaurant.objects.exclude(beers_on_tap=beer_id)
    return render(request, 'beers/beer_detail.html',
    {
        'beer': beer,
        'rests': rests,
        'untapped_rests': untapped_rests,
        'my_beers_list': my_beers_list,
    })

def tap_to_rest(request, beer_id, restaurant_id):
  beer = Beer.objects.get(id=beer_id)
  my_beers = LikeBeerUser.objects.filter(user=request.user)
  rest = Restaurant.objects.get(id=restaurant_id)
  rest.beers_on_tap.add(beer)
  rests = Restaurant.objects.filter(beers_on_tap=beer_id)
  untapped_rests = Restaurant.objects.exclude(beers_on_tap=beer_id)
  my_beers_list = []
  for b in my_beers:
    my_beers_list.append(b.beer.name)
  return render(request, 'beers/beer_detail.html',
  {
        'beer': beer,
        'rests': rests,
        'untapped_rests': untapped_rests,
        'my_beers_list': my_beers_list,
  })

def restaurant_detail(request, restaurant_id):
  restaurant = Restaurant.objects.get(id=restaurant_id)
  my_rests = LikeRestaurantUser.objects.filter(user=request.user)
  my_rests_list = []
  for r in my_rests:
    my_rests_list.append(r.rest.name)
  return render(request, 'restaurants/restaurant_detail.html',
  {
      'restaurant': restaurant,
      'my_rests': my_rests,
      'my_rests_list': my_rests_list,
  })


def signup(request):
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      user = form.save()
      username = form.cleaned_data.get('username')
      messages.success(request, f'New Account Created: {username}')
      login(request, user)
      messages.info(request, f'You are now logged in as {username}')
      return redirect('home')
    else:
      for msg in form.error_messages:
        messages.error(request, f'{msg}: {form.error_messages[msg]}')
  
  form = SignUpForm()
  return render(request,'registration/signup.html', {'form':form})

def logout_request(request):
  logout(request)
  messages.info(request, 'Logged out successfuly!')
  return redirect('landing')

def login_request(request):
  if request.method == 'POST':
    form = AuthenticationForm(request, request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      user = authenticate(username=username, password=password)
      if user is not None:
        login(request, user)
        messages.info(request, f'Your are now logged in as {username}')
        return redirect('home')
      else:
        messages.error(request, 'Invalid username or password')
    else:
      messages.error(request, 'Invalid username or password')

  form = AuthenticationForm()
  return render(request, 'registration/login.html', {'form': form})
