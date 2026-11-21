from django.shortcuts import render

def login_view(request):
    return render(request, 'core/login.html')

def signup(request):
    return render(request, 'core/signup.html')

def profile(request):
    return render(request, 'core/profile.html')

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .forms import LoginForm, SignUpForm, ProfileForm
from .models import Profile


def get_safe_next_url(request, default='index'):
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return default


def login_view(request):
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(get_safe_next_url(request))
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form, 'next': next_url})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    # Возвращаем на текущую страницу (передается в скрытом поле next или из Referer)
    referer = request.META.get('HTTP_REFERER')
    next_url = request.POST.get('next') or referer
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('index')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'core/profile.html', {'form': form})