from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem
from .forms import ProductForm, CheckoutForm
import googlemaps
from django.conf import settings
import uuid
from decimal import Decimal
from .models import Cart, Order, OrderItem
from .forms import CheckoutForm
from django.shortcuts import render, get_object_or_404
from .forms import ProductForm
from .models import Product, Category  # Import Product and Category models
from django import forms
from .models import Product, Category, Cart, CartItem, Order  # Remove OrderItem
 # Correct path if you placed it here



from django.utils import timezone
from django.db.models import Sum
from .models import Product, Category
from accounts.models import Subscription  # Adjust import if needed

def home(request):
    # Products and categories
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    # Subscription report calculations
    now = timezone.now()

    # Active subscriptions = subscriptions where end_date is in the future
    active_subscriptions = Subscription.objects.filter(end_date__gte=now).count()

    # Monthly revenue = sum of amount_paid for subscriptions started this month
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Subscription.objects.filter(start_date__gte=first_day_of_month).aggregate(
        total=Sum('amount_paid'))['total'] or 0

    # Total subscription revenue = sum of all amount_paid
    total_subscription_revenue = Subscription.objects.aggregate(
        total=Sum('amount_paid'))['total'] or 0

    context = {
        'products': products,
        'categories': categories,
        'active_subscriptions': active_subscriptions,
        'monthly_revenue': monthly_revenue,
        'total_subscription_revenue': total_subscription_revenue,
    }

    return render(request, 'marketplace/home.html', context)

def product_list(request):
    products = Product.objects.filter(is_available=True).order_by('-date_posted')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )
    
    categories = Category.objects.all()
    
    return render(request, 'marketplace/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'query': query
    })


from django.shortcuts import render, get_object_or_404
from .models import Product  # Ensure you import your Product model
from chat.models import ChatRoom  # Make sure to import the ChatRoom model
def product_detail(request, product_id):
    # Fetch the product
    product = get_object_or_404(Product, id=product_id, is_available=True)
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id)[:4]

    # Correct usage of average_rating method
    average_rating = product.average_rating() if callable(product.average_rating) else product.average_rating
    rating_percent = round((average_rating / 5) * 100, 2) if average_rating else 0

    # Handle chat room
    room = None
    if request.user.is_authenticated:
        room = ChatRoom.objects.filter(buyer=request.user, seller=product.seller).first()
        if not room:
            room = ChatRoom.objects.create(buyer=request.user, seller=product.seller, product=product)

    return render(request, 'marketplace/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'room': room,
        'rating_percent': rating_percent,
    })


@login_required
def add_product(request):
    # Check if the user has an active subscription before posting products
    if not request.user.is_subscription_active():
        messages.error(request, "You need an active subscription to post products.")
        return redirect('subscribe')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            # Save the form but don't commit yet to modify the seller
            product = form.save(commit=False)
            
            # Set the seller to the logged-in user for non-staff users
            if not request.user.is_staff:
                product.seller = request.user
            else:
                # Staff users can choose the seller (this will come from the form)
                product.seller = form.cleaned_data.get('seller', request.user)  # Default to current user if no seller is provided

            # Save the product to the database
            product.save()

            messages.success(request, "Product added successfully!")
            return redirect('marketplace:product_detail', product_id=product.id)
    else:
        form = ProductForm()

    # Hide the seller field for non-staff users
    if not request.user.is_staff and 'seller' in form.fields:
        form.fields['seller'].widget = forms.HiddenInput()

    return render(request, 'marketplace/add_product.html', {'form': form})



@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('marketplace:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'marketplace/edit_product.html', {'form': form, 'product': product})

from django.contrib import messages
from .models import Product

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)

    if request.method == 'POST':
        # Mark the product as unavailable (soft delete)
        product.is_available = False
        product.save()
        messages.success(request, "Product deleted successfully!")

        # Redirect to the 'my_products' page after deletion
        return redirect('marketplace:my_products')

    return render(request, 'marketplace/delete_product.html', {'product': product})

from django.shortcuts import render
from django.db.models import F
from .models import Product

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Product, Order

@login_required
def my_products(request):
    # Get base queryset
    products_list = Product.objects.filter(seller=request.user).order_by('-date_posted')
    
    # Apply filters if any
    status_filter = request.GET.get('status')
    if status_filter == 'available':
        products_list = products_list.filter(is_available=True)
    elif status_filter == 'out_of_stock':
        products_list = products_list.filter(is_available=False)
    
    # Pagination - 10 items per page
    paginator = Paginator(products_list, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    # Get low-stock products (stock <= 5)
    low_stock_threshold = 5
    low_stock_products = products_list.filter(stock__lte=low_stock_threshold)
    
    # Calculate dashboard statistics
    total_products = products_list.count()
    available_count = products_list.filter(is_available=True).count()
    
    # Get order statistics (assuming you have an Order model)
    order_count = Order.objects.filter(
        items__product__seller=request.user
    ).distinct().count()
    
    total_revenue = Order.objects.filter(
        items__product__seller=request.user
    ).aggregate(
        total=Sum('items__price')
    )['total'] or 0
    
    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'available_count': available_count,
        'order_count': order_count,
        'total_revenue': total_revenue,
        'status_filter': status_filter,
    }
    
    return render(request, 'marketplace/my_products.html', context)


@login_required
def add_to_cart(request, product_id):
    # Get the product or return a 404 if not available
    product = get_object_or_404(Product, id=product_id, is_available=True)

    # Check if the product is out of stock
    if product.stock <= 0:
        messages.error(request, f"{product.title} is currently out of stock.")
        return redirect('marketplace:product_detail', product_id=product.id)

    # Get or create the cart for the current user
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Get or create the CartItem
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If item already exists in cart, check stock before increasing
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Another {product.title} added to your cart!")
        else:
            messages.warning(request, f"You have reached the stock limit for {product.title}.")
    else:
        # First time adding this product to cart
        cart_item.quantity = 1
        cart_item.save()
        messages.success(request, f"{product.title} added to your cart!")

    return redirect('marketplace:cart')

@login_required
def cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []
    
    total = sum(item.product.price * item.quantity for item in cart_items)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'marketplace/cart.html', context)


from django.contrib import messages

@login_required
def update_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
        messages.error(request, "Cart item not found.")
        return redirect('marketplace:cart')

    action = request.POST.get('action')

    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, "Quantity increased.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, "Quantity decreased.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect('marketplace:cart')




@login_required(login_url='/accounts/login.html/')  # Redirect unauthenticated users to login
def checkout(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart_items = []
        cart = None

    subtotal = sum(Decimal(item.product.price) * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            delivery_option = form.cleaned_data['delivery_option']
            phone_number = form.cleaned_data['phone_number']
            location = form.cleaned_data.get('location', '')
            room_number = form.cleaned_data.get('room_number', '')
            payment_method = form.cleaned_data['payment_method']

            # Extra validation for phone_number and room_number depending on delivery_option
            if not phone_number:
                form.add_error('phone_number', 'Phone number is required.')

            if delivery_option == 'inside' and not room_number:
                form.add_error('room_number', 'Room number is required for inside campus delivery.')

            if form.errors:
                return render(request, 'marketplace/checkout.html', {
                    'form': form,
                    'cart_items': cart_items,
                    'subtotal': subtotal,
                })

            # Save checkout info in session for use in next steps
            request.session['checkout_data'] = {
                'delivery_option': delivery_option,
                'phone_number': phone_number,
                'location': location,
                'room_number': room_number,
                'payment_method': payment_method,
            }

            request.session['cart_id'] = cart.id if cart else None

            # Send OTP with Twilio Verify service
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verifications \
                .create(to=phone_number, channel='sms')

            request.session['phone_number'] = phone_number

            return redirect('verify_otp')

        # If form invalid
        return render(request, 'marketplace/checkout.html', {
            'form': form,
            'cart_items': cart_items,
            'subtotal': subtotal,
        })

    else:
        form = CheckoutForm()
    
    return render(request, 'marketplace/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
    })


def calculate_delivery_fee(origin, destination):
    """
    Calculate delivery fee based on distance
    Base fee: 10 ZMW
    Per km fee: 2 ZMW
    """
    base_fee = 10.0
    per_km_fee = 2.0
    
    # In a real implementation, we would use Google Maps API to calculate distance
    # For now, we'll return a fixed fee
    return base_fee
from django.shortcuts import render
from .models import Order  # Make sure Order model is imported

def marketplace_order_changelist(request):
    orders = Order.objects.all()
    return render(request, 'marketplace/marketplace_order_changelist.html', {'orders': orders})
# marketplace/views.py

from .models import Product, Category
from django.db.models import Q

def product_list(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category')
    query = request.GET.get('q', '')
    products = Product.objects.all()
    selected_category = None

    # Filter by category if provided
    if category_id and category_id.isdigit():
        selected_category = int(category_id)
        products = products.filter(category__id=selected_category)

    # Filter by search query if provided
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'marketplace/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
    })

from django.shortcuts import render

def cart_view(request):
    # your logic to display cart items
    return render(request, 'marketplace/cart.html', context)
from django.shortcuts import render

def about(request):
    return render(request, 'marketplace/about.html')
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f"New Contact Us Message from {name}"
        full_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        send_mail(
            subject,
            full_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],  # Admin email where you want to receive messages
            fail_silently=False,
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact')

    return render(request, 'marketplace/contact.html')
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CheckoutForm
from .models import Order, Cart, CartItem, OrderItem
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def process_checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)

                if not cart_items.exists():
                    messages.error(request, "Your cart is empty.")
                    return redirect('marketplace:checkout')

                # Calculate total
                total_amount = sum(item.product.price * item.quantity for item in cart_items)

                # Extract delivery info from the form
                delivery_location = form.cleaned_data.get('delivery_location')
                delivery_fee = form.cleaned_data.get('delivery_fee') or 0

                # Create the order
                order = Order.objects.create(
                    buyer=request.user,
                    delivery_location=delivery_location,
                    delivery_fee=delivery_fee,
                    total_amount=total_amount + delivery_fee,  # Include fee if applicable
                    status='pending'
                )

                # Save order items
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price,
                    )

                # Clear cart
                cart_items.delete()

                # Redirect to payment
                return redirect(reverse('payments:process_payment', args=[order.id]))

            except Cart.DoesNotExist:
                messages.error(request, "You do not have a cart.")
                return redirect('marketplace:checkout')
        else:
            messages.error(request, "Please correct the errors in the form.")
            return render(request, 'marketplace/checkout.html', {'form': form})
    else:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            subtotal = sum(item.product.price * item.quantity for item in cart_items)
        except Cart.DoesNotExist:
            cart_items = []
            subtotal = 0

        form = CheckoutForm()
        context = {
            'form': form,
            'cart_items': cart_items,
            'subtotal': subtotal,
        }
        return render(request, 'marketplace/checkout.html', context)


def gps(request):
    return render(request, 'marketplace/gps.html')

import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def get_openai_response(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "There was an error reaching the AI bot. Please try again later."


from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductRating
from django.contrib.auth.decorators import login_required

@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        review = request.POST.get('review')

        # Check if the user already rated this product
        if ProductRating.objects.filter(product=product, user=request.user).exists():
            return redirect('product_detail', product_id=product.id)

        ProductRating.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            review=review
        )
        return redirect('product_detail', product_id=product.id)

    return render(request, 'rate_product.html', {'product': product})
from .models import Product  # Make sure you import the correct models

def top_selling_products(request):
    # Assuming you have an OrderItem model that connects orders and products
    products = Product.objects.annotate(
        orders_count=Count('order_items')  # Count the number of order items associated with each product
    ).order_by('-orders_count')  # Sort by the most sold product
    
    return render(request, 'top_selling_products.html', {'products': products})



@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        stars = int(request.POST['stars'])
        review_text = request.POST['review_text']
        from .models import Product, Rating
        Rating.objects.create(
            product=product,
            stars=stars,
            review_text=review_text
        )
        return redirect('product_detail', product_id=product.id)
    
    return render(request, 'marketplace/product_detail.html', {'product': product})


from django.shortcuts import get_object_or_404, redirect
from marketplace.models import Product
from marketplace.models import Review
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        score = int(request.POST.get('score'))
        Review.objects.create(product=product, score=score)
    return redirect('marketplace:product_detail', product_id=product.id)


# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Product, Rating

@require_POST
@login_required
def rate_product(request):
    product_id = request.POST.get('product_id')
    value = int(request.POST.get('value'))

    product = Product.objects.get(id=product_id)

    # Create or update rating
    rating_obj, created = Rating.objects.get_or_create(user=request.user, product=product)
    rating_obj.value = value
    rating_obj.save()

    # Recalculate average
    all_ratings = Rating.objects.filter(product=product)
    avg = sum(r.value for r in all_ratings) / all_ratings.count()
    product.rating = avg
    product.num_ratings = all_ratings.count()
    product.save()

    return JsonResponse({'success': True, 'average': round(avg, 1)})


from django.conf import settings
from django.shortcuts import render, redirect
from twilio.rest import Client
from django.contrib import messages

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_verification(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
            .verifications \
            .create(to=phone_number, channel='sms')
        request.session['phone_number'] = phone_number
        return redirect('verify_otp')
    return render(request, 'home/send_verification.html')


# def verify_otp(request):
#     if request.method == 'POST':
#         otp = request.POST.get('otp')
#         phone_number = request.session.get('phone_number')
#         verification_check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
#             .verification_checks \
#             .create(to=phone_number, code=otp)
#         if verification_check.status == 'approved':
#             messages.success(request, 'Phone number verified successfully!')
#             return redirect('home')  # or wherever
#         else:
#             messages.error(request, 'Invalid OTP. Try again.')
#     return render(request, 'home/verify_otp.html')

# from django.conf import settings
# from django.http import JsonResponse
# from twilio.rest import Client

# def send_sms_verification(request):
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

#     verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
#         .verifications \
#         .create(to='+260777672440', channel='sms')

#     return JsonResponse({'sid': verification.sid, 'status': verification.status})
# def send_sms_verification(request):
#     account_sid = settings.TWILIO_ACCOUNT_SID
#     auth_token = settings.TWILIO_AUTH_TOKEN
#     verify_sid = settings.TWILIO_VERIFY_SERVICE_SID

#     client = Client(account_sid, auth_token)

#     verification = client.verify.services(verify_sid).verifications.create(
#         to='+260777672440',  # ideally, get this dynamically from request/user
#         channel='sms'
#     )

#     # For debugging or API response, you can return JSON:
#     return JsonResponse({
#         'status': verification.status,
#         'sid': verification.sid,
#     })

# from django.http import JsonResponse
# from django.conf import settings
# from twilio.rest import Client
# import json
# import logging

# logger = logging.getLogger(__name__)

# def send_sms_verification(request):
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

#     try:
#         data = json.loads(request.body)
#         phone_number = data.get('phone_number')
#         if not phone_number:
#             return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)

#         # Optional: Normalize phone number to E.164 format (e.g., +260123456789)
#         if not phone_number.startswith('+'):
#             phone_number = '+260' + phone_number.lstrip('0')  # Adjust country code as needed

#         account_sid = settings.TWILIO_ACCOUNT_SID
#         auth_token = settings.TWILIO_AUTH_TOKEN
#         verify_sid = settings.TWILIO_VERIFY_SERVICE_SID

#         client = Client(account_sid, auth_token)

#         verification = client.verify.v2.services(verify_sid).verifications.create(
#             to=phone_number,
#             channel='sms'
#         )

#         # Store phone number in session for verification
#         request.session['phone_number'] = phone_number
#         logger.debug(f"OTP sent to {phone_number}, SID: {verification.sid}")

#         return JsonResponse({
#             'status': 'success',
#             'message': 'OTP sent successfully',
#             'sid': verification.sid,
#         })

#     except json.JSONDecodeError:
#         logger.error("Invalid JSON in request body")
#         return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
#     except Exception as e:
#         logger.error(f"Error sending OTP: {str(e)}")
#         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from twilio.rest import Client
from django.conf import settings

@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phone_number')
            otp_code = data.get('otp_code')

            if not phone_number or not otp_code:
                return JsonResponse({'status': 'error', 'message': 'Missing phone number or OTP'}, status=400)

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            verification_check = client.verify \
                .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verification_checks \
                .create(to=phone_number, code=otp_code)

            if verification_check.status == 'approved':
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid OTP. Please try again.'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error verifying OTP: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from django.conf import settings

@csrf_exempt
def send_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            verification = client.verify \
                .services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verifications \
                .create(to=phone_number, channel='sms')
            return JsonResponse({
                'status': 'success',
                'message': 'OTP sent successfully.',
                'sid': verification.sid
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })


@csrf_exempt
def check_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        code = data.get('code')
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            verification_check = client.verify.services(settings.TWILIO_VERIFY_SERVICE_SID) \
                .verification_checks \
                .create(to=phone_number, code=code)

            return JsonResponse({'status': verification_check.status})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
