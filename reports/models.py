from django.db import models
from django.conf import settings  # <-- Use settings instead of importing User directly

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # <-- Use settings.AUTH_USER_MODEL
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('completed', 'Completed'),
            ('processing', 'Processing'),
            ('pending', 'Pending')
        ]
    )
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id}'
from django.db import models
from marketplace.models import Product
  # Adjust if different

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} - {self.quantity} sold"
