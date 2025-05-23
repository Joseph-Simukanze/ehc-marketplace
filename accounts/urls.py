from django.urls import path
from . import views  # Only import views once

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),  # Adjusted path for logout
    path('profile/', views.profile, name='profile'),
    path('subscription/', views.subscription_status, name='subscription_status'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('forgot-password/', views.forgot_password, name='forgetpassword'),
]
