from django.db import models
from accounts.models import User
from django.utils import timezone



# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


# Product model
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='products/')
    location = models.CharField(max_length=255)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)

    # New fields
    stock = models.PositiveIntegerField(default=1)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.title

    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    def reduce_stock(self, quantity=1):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def restock(self, quantity):
        self.stock += quantity
        self.save()

    def is_in_stock(self):
        return self.stock > 0

    def update_availability(self):
        self.is_available = self.stock > 0
        self.save()

   
    def average_rating(self):
        ratings = self.rating_set.all()
        if ratings.exists():
            return sum([r.score for r in ratings]) / ratings.count()
        return 0

    def get_rating_stars(self):
        return range(int(self.average_rating()))

    # def get_rating_stars(self):
    #     # Return a list of stars based on the average rating
    #     stars = [1 for _ in range(int(self.average_rating))]
#     #     return range(int(self.average_rating())
# ) 

    # def __str__(self):
    #     return self.title
   

# Order model
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_location = models.CharField(max_length=255)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer.username}"


# OrderItem model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.title} at ZMW {self.price:.2f} each"
    payment_method = models.CharField(
        max_length=30,
        choices=[
            ('cash', 'Cash'),
            ('payment_on_delivery', 'Payment on Delivery'),
            ('mtn_money', 'MTN Mobile Money'),
            ('airtel_money', 'Airtel Money'),
        ],
        default='cash'
    )

# Cart model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


# CartItem model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"


from django.db import models
from django.contrib.auth import get_user_model
from .models import Product

User = get_user_model()

class ProductRating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    review = models.TextField(null=True, blank=True)  # Optional review
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating for {self.product.title} by {self.user.username} - {self.rating} Stars"

    class Meta:
        unique_together = ('product', 'user')  # Prevent duplicate ratings by the same user
from django.conf import settings
from django.db import models

class Rating(models.Model):
    RATING_CHOICES = [(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Each user can rate a product only once
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.product.title} - {self.rating} Star{'s' if self.rating > 1 else ''}"


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()  # typically 1–5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.score} stars"