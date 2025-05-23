# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django.utils.html import format_html
# from .models import User, Product, Subscription, Order, OrderItem, Payment, Category, Cart, CartItem
# from django.db.models import Sum, Count
# from django.urls import reverse
# from django.utils import timezone

# # Custom User Admin
# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'is_seller', 'phone_number', 'location', 'is_subscription_active', 'subscription_end')
#     list_filter = ('is_seller', 'is_active', 'is_staff')
#     search_fields = ('username', 'email', 'phone_number')
#     readonly_fields = ('date_joined', 'last_login')
#     fieldsets = (
#         (,None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'location')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_seller', 'groups', 'user_permissions')}),
#         ('Subscription', {'fields': ('subscription_end',)}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )

#     def is_subscription_active(self, obj):
#         status = obj.is_subscription_active()
#         color = 'green' if status else 'red'
#         return format_html('<span style="color: {}">{}</span>', color, status)
#     is_subscription_active.short_description = 'Subscription Active'
#     is_subscription_active.admin_order_field = 'subscription_end'

# # Subscription Admin
# @admin.register(Subscription)
# class SubscriptionAdmin(admin.ModelAdmin):
#     list_display = ('user', 'start_date', 'end_date', 'amount_paid', 'payment_id', 'is_active')
#     list_filter = ('start_date', 'end_date')
#     search_fields = ('user__username', 'payment_id')
#     date_hierarchy = 'start_date'

#     def is_active(self, obj):
#         return obj.end_date > timezone.now()
#     is_active.boolean = True
#     is_active.short_description = 'Active'

# # Category Admin
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description')
#     search_fields = ('name',)

# # Product Admin
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('title', 'seller', 'category', 'price', 'stock', 'is_low_stock', 'is_available', 'date_posted')
#     list_filter = ('category', 'is_available', 'date_posted')
#     search_fields = ('title', 'description', 'seller__username')
#     list_editable = ('price', 'stock', 'is_available')
#     date_hierarchy = 'date_posted'
#     actions = ['mark_as_available', 'mark_as_unavailable', 'restock_products']

#     def is_low_stock(self, obj):
#         status = obj.is_low_stock()
#         color = 'red' if status else 'green'
#         return format_html('<span style="color: {}">{}</span>', color, status)
#     is_low_stock.boolean = True
#     is_low_stock.short_description = 'Low Stock'

#     def mark_as_available(self, request, queryset):
#         queryset.update(is_available=True)
#         self.message_user(request, "Selected products marked as available.")
#     mark_as_available.short_description = "Mark selected products as available"

#     def mark_as_unavailable(self, request, queryset):
#         queryset.update(is_available=False)
#         self.message_user(request, "Selected products marked as unavailable.")
#     mark_as_unavailable.short_description = "Mark selected products as unavailable"

#     def restock_products(self, request, queryset):
#         for product in queryset:
#             product.restock(10)  # Default restock by 10 units
#         self.message_user(request, "Selected products restocked by 10 units.")
#     restock_products.short_description = "Restock selected products"

# # Order Admin
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'buyer', 'order_date', 'status', 'total_amount', 'delivery_fee', 'delivery_location')
#     list_filter = ('status', 'order_date')
#     search_fields = ('buyer__username', 'id')
#     list_editable = ('status',)
#     date_hierarchy = 'order_date'
#     actions = ['mark_as_delivered', 'mark_as_cancelled']

#     def mark_as_delivered(self, request, queryset):
#         queryset.update(status='delivered')
#         self.message_user(request, "Selected orders marked as delivered.")
#     mark_as_delivered.short_description = "Mark selected orders as delivered"

#     def mark_as_cancelled(self, request, queryset):
#         queryset.update(status='cancelled')
#         self.message_user(request, "Selected orders marked as cancelled.")
#     mark_as_cancelled.short_description = "Mark selected orders as cancelled"

# # OrderItem Admin
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ('order', 'product', 'quantity', 'price', 'total_price')
#     search_fields = ('product__title', 'order__id')
#     list_filter = ('order__status',)

# # Payment Admin
# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('transaction_id', 'order', 'payment_method', 'amount', 'payment_date', 'is_verified', 'status')
#     list_filter = ('payment_method', 'is_verified', 'payment_date')
#     search_fields = ('transaction_id', 'order__id')
#     list_editable = ('is_verified', 'status')
#     date_hierarchy = 'payment_date'
#     actions = ['verify_payments']

#     def verify_payments(self, request, queryset):
#         queryset.update(is_verified=True, status='successful')
#         self.message_user(request, "Selected payments verified and marked as successful.")
#     verify_payments.short_description = "Verify selected payments"

# # Cart Admin
# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('user', 'created_at', 'get_total_price')
#     search_fields = ('user__username',)

# # CartItem Admin
# @admin.register(CartItem)
# class CartItemAdmin(admin.ModelAdmin):
#     list_display = ('cart', 'product', 'quantity')
#     search_fields = ('product__title', 'cart__user__username')

# # Custom Admin Site for Reports
# class MarketplaceAdminSite(admin.AdminSite):
#     site_header = "Marketplace Administration"
#     site_title = "Marketplace Admin"
#     index_title = "Marketplace Dashboard"

#     def get_app_list(self, request):
#         app_list = super().get_app_list(request)
#         # Add custom reports section
#         app_list.append({
#             'name': 'Reports',
#             'app_label': 'reports',
#             'models': [
#                 {
#                     'name': 'Sales Report',
#                     'admin_url': reverse('admin:sales_report'),
#                     'perms': {'view': True},
#                 },
#                 {
#                     'name': 'User Subscription Report',
#                     'admin_url': reverse('admin:subscription_report'),
#                     'perms': {'view': True},
#                 },
#             ],
#         })
#         return app_list

# # Instantiate custom admin site
# marketplace_admin_site = MarketplaceAdminSite(name='marketplace_admin')

# # Register models with custom admin site
# marketplace_admin_site.register(User, CustomUserAdmin)
# marketplace_admin_site.register(Subscription, SubscriptionAdmin)
# marketplace_admin_site.register(Product, ProductAdmin)
# marketplace_admin_site.register(Order, OrderAdmin)
# marketplace_admin_site.register(OrderItem, OrderItemAdmin)
# marketplace_admin_site.register(Payment, PaymentAdmin)
# marketplace_admin_site.register(Category, CategoryAdmin)
# marketplace_admin_site.register(Cart, CartAdmin)
# marketplace_admin_site.register(CartItem, CartItemAdmin)

# # Custom admin views for reports
# from django.http import HttpResponse
# from django.template.response import TemplateResponse
# from django.urls import path
# from django.contrib.admin import ModelAdmin

# class ReportAdmin(ModelAdmin):
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('sales_report/', self.admin_site.admin_view(self.sales_report_view), name='sales_report'),
#             path('subscription_report/', self.admin_site.admin_view(self.subscription_report_view), name='subscription_report'),
#         ]
#         return custom_urls + urls

#     def sales_report_view(self, request):
#         # Aggregate sales data
#         sales_data = Order.objects.values('status').annotate(
#             total_sales=Sum('total_amount'),
#             order_count=Count('id')
#         )
#         product_sales = OrderItem.objects.values('product__title').annotate(
#             total_quantity=Sum('quantity'),
#             total_revenue=Sum('total_price')
#         )
#         context = {
#             'sales_data': sales_data,
#             'product_sales': product_sales,
#             'title': 'Sales Report',
#         }
#         return TemplateResponse(request, 'admin/sales_report.html', context)

#     def subscription_report_view(self, request):
#         # Aggregate subscription data
#         active_subscriptions = Subscription.objects.filter(end_date__gt=timezone.now()).count()
#         total_subscribers = User.objects.filter(subscription_end__gt=timezone.now()).count()
#         subscription_revenue = Subscription.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
#         context = {
#             'active_subscriptions': active_subscriptions,
#             'total_subscribers': total_subscribers,
#             'subscription_revenue': subscription_revenue,
#             'title': 'Subscription Report',
#         }
#         return TemplateResponse(request, 'admin/subscription_report.html', context)

# # Register ReportAdmin with the custom admin site
# marketplace_admin_site.register(None.__class__, ReportAdmin)

# # Custom templates for reports
# # Create these files in templates/admin/
# <xaiArtifact artifact_id="24ec660a-facc-478f-987e-19385f2748ee" artifact_version_id="5a165dbc-c728-400d-b36e-98b922911311" title="sales_report.html" contentType="text/html">
# {% extends "admin/base_site.html" %}
# {% block content %}
#     <h1>Sales Report</h1>
#     <h2>Order Status Summary</h2>
#     <table class="table">
#         <thead>
#             <tr>
#                 <th>Status</th>
#                 <th>Total Sales</th>
#                 <th>Order Count</th>
#             </tr>
#         </thead>
#         <tbody>
#             {% for data in sales_data %}
#                 <tr>
#                     <td>{{ data.status }}</td>
#                     <td>{{ data.total_sales|floatformat:2 }}</td>
#                     <td>{{ data.order_count }}</td>
#                 </tr>
#             {% endfor %}
#         </tbody>
#     </table>
#     <h2>Product Sales</h2>
#     <table class="table">
#         <thead>
#             <tr>
#                 <th>Product</th>
#                 <th>Total Quantity</th>
#                 <th>Total Revenue</th>
#             </tr>
#         </thead>
#         <tbody>
#             {% for sale in product_sales %}
#                 <tr>
#                     <td>{{ sale.product__title }}</td>
#                     <td>{{ sale.total_quantity }}</td>
#                     <td>{{ sale.total_revenue|floatformat:2 }}</td>
#                 </tr>
#             {% endfor %}
#         </tbody>
#     </table>
# {% endblock %}