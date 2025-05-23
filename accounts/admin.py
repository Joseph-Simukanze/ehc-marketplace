from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Subscription

# Custom UserAdmin
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'is_seller',
        'phone_number', 'location', 'subscription_active', 'subscription_end'
    ]
    list_filter = ['is_seller', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['username']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'location')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Subscription info', {'fields': ('subscription_end',)}),
        ('Seller Info', {'fields': ('is_seller',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'email',
                'first_name', 'last_name', 'phone_number', 'location', 'is_seller'
            ),
        }),
    )

    @admin.display(boolean=True, description='Active Subscription')
    def subscription_active(self, obj):
        return obj.is_subscription_active()

# Subscription Admin
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'start_date', 'end_date', 'amount_paid', 'payment_id']
    list_filter = ['start_date', 'end_date']
    search_fields = ['user__username', 'payment_id']
    ordering = ['-start_date']

# Register the models
admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
