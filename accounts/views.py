from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, UserProfileForm
from .models import Subscription
from django.utils import timezone
from datetime import timedelta
import uuid
from django.conf import settings

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('marketplace:home')  # Redirect to home after login
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             next_url = request.GET.get('next', 'marketplace:home')  # Fallback to 'home' if no 'next' parameter
#             return redirect(next_url)
#         else:
#             # Handle invalid login
#             return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
#     return render(request, 'accounts/login.html')
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # Logs the user out
    return redirect('marketplace:home')  # Redirect to the homepage or any other URL you want

# Profile view
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')  # Redirect to profile page
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

# Subscription status view
@login_required
def subscription_status(request):
    is_active = request.user.is_subscription_active()
    subscription_end = request.user.subscription_end
    subscription_history = Subscription.objects.filter(user=request.user).order_by('-end_date')
    
    return render(request, 'accounts/subscription_status.html', {
        'is_active': is_active,
        'subscription_end': subscription_end,
        'subscription_history': subscription_history
    })

# Subscribe view (handle subscription)
@login_required
def subscribe(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        phone_number = request.POST.get('phone_number')

        amount = settings.MONTHLY_SUBSCRIPTION_AMOUNT  # Subscription amount from settings
        reference = str(uuid.uuid4())  # Unique transaction reference

        now = timezone.now()
        end_date = now + timedelta(days=30)
        
        if request.user.is_subscription_active():
            end_date = request.user.subscription_end + timedelta(days=30)
        
        request.user.subscription_end = end_date
        request.user.save()

        Subscription.objects.create(
            user=request.user,
            end_date=end_date,
            amount_paid=amount,
            payment_id=reference
        )
        
        return redirect('accounts:subscription_status')

    return render(request, 'accounts/subscribe.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import LoginForm  # assuming you have a form for login

# Login View
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in.")
                return redirect('marketplace:home')  # Redirect to the home page after login
            else:
                messages.error(request, "Invalid login credentials.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})  # Make sure you have the corresponding HTML file

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileForm

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

from django.contrib.auth import get_user_model, logout
User = get_user_model()

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  # Log the user out
        user.delete()    # Delete the user
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('marketplace:home')  # Redirect to homepage or login
    return render(request, 'accounts/delete_account_confirm.html')

from django.shortcuts import render
from django.db.models import Sum
from accounts.models import Subscription  # get the subscription model

def subscription_report(request):
    total_subscription_revenue = Subscription.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_subscribers = Subscription.objects.values('user').distinct().count()

    return render(request, 'reports/subscription_report.html', {
        'total_subscription_revenue': total_subscription_revenue,
        'total_subscribers': total_subscribers,
    })

from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client

def send_sms_verification(request):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verifications \
        .create(to='+260777672440', channel='sms')

    return JsonResponse({'sid': verification.sid, 'status': verification.status})


from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages

def forgot_password(request):
    message = None
    if request.method == "POST":
        email = request.POST.get("email")
        # Simulate sending a reset link (you can implement a real system later)
        message = f"A password reset link has been sent to {email} (simulation)."
        # Optionally: implement email sending via send_mail or Django's password reset

    return render(request, "accounts/forgetpassword.html", {"message": message})
