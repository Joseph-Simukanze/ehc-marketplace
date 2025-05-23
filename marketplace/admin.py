from django.contrib import admin
from .models import Category, Product

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ['title', 'price', 'is_available']
    readonly_fields = ['seller', 'date_posted']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'product_count')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    ordering = ('name',)
    inlines = [ProductInline]

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products'

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'date_posted', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'description')
    ordering = ('date_posted',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)