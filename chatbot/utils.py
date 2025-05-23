from marketplace.models import Product

def search_products_by_query(query):
    query = query.lower()
    matches = Product.objects.filter(
        name__icontains=query,
        is_available=True
    )
    return matches
# chatbot/utils.py
from marketplace.models import Product  # Or wherever your Product model is

def search_products_by_query(query):
    if not query:
        # Return empty queryset, never None
        return Product.objects.none()

    # Adjust 'title' field instead of 'name' based on your model
    products = Product.objects.filter(title__icontains=query)

    return products
