from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect


def mock_login(request):
    """Mock login view for demo purposes"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check for demo credentials
        if username == 'demo' and password == 'demo123':
            # Create or get demo user
            user, created = User.objects.get_or_create(
                username='demo',
                defaults={
                    'email': 'demo@aibusinessvalidator.com',
                    'first_name': 'Demo',
                    'last_name': 'User',
                }
            )
            
            # Set password for demo user (only needed if user was just created)
            if created:
                user.set_password('demo123')
                user.save()
            
            # Log in the user
            login(request, user)
            
            # Add success message
            messages.success(request, 'Successfully logged in as demo user!')
            
            # Check for next parameter
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            # Default redirect to modern UI
            return redirect('analyzer:home')
        
        else:
            # Add error message
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('auth:login')
    
    return render(request, 'auth/login.html')


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('auth:mock_login')


def login_required_redirect(request):
    """Redirect to login if not authenticated"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to access this page.')
        return redirect('auth:mock_login')
    return None
