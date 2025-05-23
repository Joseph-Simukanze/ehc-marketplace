from django.core.management.base import BaseCommand
from marketplace.models import Product
from django.core.mail import send_mail
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check for low stock products and notify admin'

    def handle(self, *args, **kwargs):
        low_stock_products = Product.objects.filter(stock__lte=5)

        if low_stock_products.exists():
            admin_emails = [user.email for user in User.objects.filter(is_superuser=True)]
            product_list = "\n".join([f"{product.title} - Stock: {product.stock}" for product in low_stock_products])

            send_mail(
                'Low Stock Alert',
                f'The following products are low in stock:\n\n{product_list}',
                'noreply@ehcmarketplace.com',
                admin_emails,
                fail_silently=False,
            )

            self.stdout.write(self.style.SUCCESS('Low stock notification sent.'))
        else:
            self.stdout.write('No low stock products found.')
