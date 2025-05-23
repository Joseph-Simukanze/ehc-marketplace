from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from marketplace.models import Order, OrderItem, Product
from accounts.models import User
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db.models import Sum, Count
import csv
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
import datetime
from collections import defaultdict
from django.template.loader import render_to_string
import subprocess
import os
import tempfile
import json
from django.contrib.auth import get_user_model
from accounts.models import Subscription
Subscription.objects.all()
from datetime import datetime, timedelta


User = get_user_model()
@login_required
def generate_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Check if user is authorized to view this receipt
    if request.user != order.buyer and request.user != order.items.first().product.seller:
        return HttpResponse("Unauthorized", status=403)
    
    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up receipt header
    p.setFont("Helvetica-Bold", 18)
    p.drawString(1 * inch, 10 * inch, "EHC Marketplace - Receipt")
    
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 9.5 * inch, f"Order #: {order.id}")
    p.drawString(1 * inch, 9.3 * inch, f"Date: {order.order_date.strftime('%d %b %Y, %H:%M')}")
    p.drawString(1 * inch, 9.1 * inch, f"Buyer: {order.buyer.get_full_name() or order.buyer.username}")
    p.drawString(1 * inch, 8.9 * inch, f"Status: {order.status.capitalize()}")
    
    # Set up order details
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, 8.5 * inch, "Order Details")
    
    # Create table for order items
    data = [["Item", "Quantity", "Price", "Total"]]
    
    for item in order.items.all():
        data.append([
            item.product.title,
            str(item.quantity),
            f"ZMW {item.price}",
            f"ZMW {item.quantity * item.price}"
        ])
    
    # Add summary
    data.append(["", "", "Delivery Fee:", f"ZMW {order.delivery_fee}"])
    data.append(["", "", "Total Amount:", f"ZMW {order.total_amount}"])
    
    # Create table
    table = Table(data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), (0.8, 0.8, 0.8)),
        ('TEXTCOLOR', (0, 0), (3, 0), (0, 0, 0)),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (3, 0), 12),
        ('BACKGROUND', (0, 1), (3, -1), (0.95, 0.95, 0.95)),
        ('GRID', (0, 0), (-1, -3), 1, (0, 0, 0)),
    ]))
    
    # Draw table on the PDF
    table.wrapOn(p, 6.5*inch, 9*inch)
    table.drawOn(p, 1*inch, 7*inch)
    
    # Add footer
    p.setFont("Helvetica", 10)
    p.drawString(1 * inch, 1 * inch, "Thank you for shopping with EHC Marketplace!")
    p.drawString(1 * inch, 0.8 * inch, "For any inquiries, please contact support@ehc-marketplace.com")
    
    # Close the PDF object cleanly, and we're done
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and write it to the response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_order_{order.id}.pdf"'
    return response

from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from marketplace.models import Product, OrderItem
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
from marketplace.models import OrderItem

def sales_report(request):
    report_type = request.GET.get('type', 'daily')  # daily, monthly, customer
    report_data = []
    total_quantity = 0
    total_revenue = 0
    total_orders = 0

    products = OrderItem.objects.values_list('product', flat=True).distinct()

    def process_sales(order_items, date_key, sales_data, report_type=None):
        nonlocal total_quantity, total_revenue, total_orders
        for item in order_items:
            if date_key == 'date':
                date = item.order.order_date.date()
            elif date_key == 'strftime' and report_type == 'monthly':
                date = item.order.order_date.strftime('%Y-%m')
            else:
                date = item.order.order_date.strftime('%Y-%m-%d')

            revenue = item.quantity * item.price

            if date not in sales_data:
                sales_data[date] = {'quantity': 0, 'revenue': 0}

            sales_data[date]['quantity'] += item.quantity
            sales_data[date]['revenue'] += revenue
            total_quantity += item.quantity
            total_revenue += revenue
            total_orders += 1

    if report_type == 'daily':
        start_date = timezone.now() - timedelta(days=30)
        for product_id in products:
            order_items = OrderItem.objects.filter(
                product__id=product_id,
                order__order_date__gte=start_date
            )
            if not order_items.exists():
                continue

            product = order_items.first().product
            daily_sales = {}
            process_sales(order_items, 'date', daily_sales, report_type='daily')

            report_data.append({
                'product': product,
                'sales': daily_sales,
                'total_quantity': sum(s['quantity'] for s in daily_sales.values()),
                'total_revenue': sum(s['revenue'] for s in daily_sales.values()),
            })

    elif report_type == 'monthly':
        start_date = timezone.now() - timedelta(days=365)
        for product_id in products:
            order_items = OrderItem.objects.filter(
                product__id=product_id,
                order__order_date__gte=start_date
            )
            if not order_items.exists():
                continue

            product = order_items.first().product
            monthly_sales = {}
            process_sales(order_items, 'strftime', monthly_sales, report_type='monthly')

            report_data.append({
                'product': product,
                'sales': monthly_sales,
                'total_quantity': sum(s['quantity'] for s in monthly_sales.values()),
                'total_revenue': sum(s['revenue'] for s in monthly_sales.values()),
            })

    elif report_type == 'customer':
        order_items = OrderItem.objects.filter(product__in=products)
        customer_sales = {}

        for item in order_items:
            customer = item.order.buyer
            revenue = item.quantity * item.price
            if customer.id not in customer_sales:
                customer_sales[customer.id] = {
                    'customer': customer,
                    'orders': 0,
                    'quantity': 0,
                    'revenue': 0
                }

            customer_sales[customer.id]['orders'] += 1
            customer_sales[customer.id]['quantity'] += item.quantity
            customer_sales[customer.id]['revenue'] += revenue
            total_orders += 1
            total_quantity += item.quantity
            total_revenue += revenue

        report_data = list(customer_sales.values())

    else:
        return HttpResponse("Invalid report type", status=400)

    return render(request, f'reports/{report_type}_report.html', {
        'report_type': report_type,
        'report_data': report_data,
        'total_revenue': total_revenue,
        'total_quantity': total_quantity,
        'total_orders': total_orders
    })

   
# @login_required
# def export_sales_report(request):
#     """Export sales report as CSV with detailed summary"""
#     if not request.user.is_seller:
#         return HttpResponse("Only sellers can access sales reports", status=403)
    
#     # Determine the report type and date range
#     report_type = request.GET.get('type', 'daily')  # Default to daily report
    
#     if report_type == 'daily':
#         start_date = timezone.now() - datetime.timedelta(days=30)  # Last 30 days
#     elif report_type == 'monthly':
#         start_date = timezone.now() - datetime.timedelta(days=365)  # Last 12 months
#     else:
#         return HttpResponse("Invalid report type", status=400)

#     # Create CSV file
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    
#     writer = csv.writer(response)
#     writer.writerow(['Product', 'Date', 'Quantity Sold', 'Revenue'])

#     # Initialize total variables
#     total_revenue = 0
#     total_quantity = 0
#     total_orders = 0

#     # Fetch products sold by the logged-in seller
#     products = Product.objects.filter(seller=request.user)
    
#     for product in products:
#         # Fetch the order items related to the current product within the specified date range
#         order_items = OrderItem.objects.filter(
#             product=product,
#             order__order_date__gte=start_date
#         )
        
#         for item in order_items:
#             date = item.order.order_date.strftime('%Y-%m-%d')
#             revenue = item.quantity * item.price
#             writer.writerow([
#                 product.title,
#                 date,
#                 item.quantity,
#                 revenue
#             ])
#             # Update total metrics
#             total_quantity += item.quantity
#             total_revenue += revenue
#             total_orders += 1

#     # Write summary totals at the end of the CSV
#     writer.writerow([])
#     writer.writerow(['Total Orders', total_orders])
#     writer.writerow(['Total Quantity', total_quantity])
#     writer.writerow(['Total Revenue (ZMW)', total_revenue])

#     return response

from django.db.models import Count, Sum
from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from marketplace.models import Order, OrderItem, Product
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from accounts.models import Subscription
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from accounts.models import Subscription
from django.contrib.auth import get_user_model
from datetime import datetime
datetime.now()
import datetime

now = datetime.datetime.now()


User = get_user_model()
@login_required
def admin_report(request):
    """Generate comprehensive report for admin"""
    if not request.user.is_staff:
        return HttpResponse("Only administrators can access this report", status=403)

    # Date range filtering with safe defaults
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    try:
        now = timezone.now()
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d') if start_date else datetime.datetime(now.year, 1, 1)
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.datetime(now.year, 12, 31)

        if start > end:
            raise ValueError("Start date cannot be after end date.")
    except (ValueError, OverflowError):
        now = timezone.now()
        start = datetime.datetime(now.year, 1, 1)
        end = datetime.datetime(now.year, 12, 31)

    # Make aware if using timezone-aware datetimes
    if timezone.is_naive(start):
        start = timezone.make_aware(start)
    if timezone.is_naive(end):
        end = timezone.make_aware(end)

    # Filtered query range
    date_filter = {'order_date__range': (start, end)}

    # Total users and sellers
    total_users = User.objects.count()
    total_sellers = User.objects.filter(is_seller=True).count()

    # Total products
    total_products = Product.objects.count()

    # Orders and revenue
    total_orders = Order.objects.filter(**date_filter).count()
    total_revenue = Order.objects.filter(**date_filter).aggregate(total=Sum('total_amount'))['total'] or 0

    # Products sold data
    products_sold_data = OrderItem.objects.filter(order__order_date__range=(start, end)).values(
        'product__seller__username',
        'product__title',
        'product__category__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum('product__price')  # Consider quantity * price if needed
    ).order_by('product__seller__username')

    # Registered users (all)
    registered_users = User.objects.all()

    # Recent registered users (last 10)
    recent_registered_users = User.objects.order_by('-date_joined')[:10]

    # Revenue data for chart
    revenue_data = Order.objects.filter(**date_filter).values('order_date__date').annotate(
        revenue=Sum('total_amount'),
        orders=Count('id')
    ).order_by('order_date__date')

    # Registration data for chart
    registration_data = User.objects.values('date_joined__date').annotate(
        count=Count('id')
    ).order_by('date_joined__date')

    # Category data for chart
    category_data = Product.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('category__name')

    # Subscription data calculations
    now = timezone.now()
    active_subscriptions = Subscription.objects.filter(end_date__gte=now).count()

    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_subscription_revenue = Subscription.objects.filter(start_date__gte=first_day_of_month).aggregate(
        total=Sum('amount_paid'))['total'] or 0

    total_subscription_revenue = Subscription.objects.aggregate(
        total=Sum('amount_paid'))['total'] or 0

    # Fetch subscriptions in the filtered date range (or all)
    subscription_data = Subscription.objects.filter(
        start_date__range=(start, end)
    ).select_related('user').order_by('-start_date')

    # Recent orders
    recent_orders = Order.objects.filter(**date_filter).order_by('-order_date')[:10]

    context = {
        'products_sold_data': products_sold_data,
        'registered_users': registered_users,
        'recent_registered_users': recent_registered_users,  # Added here
        'total_users': total_users,
        'total_sellers': total_sellers,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'revenue_data': revenue_data,
        'registration_data': registration_data,
        'category_data': category_data,

        # Subscription data
        'active_subscriptions': active_subscriptions,
        'monthly_subscription_revenue': monthly_subscription_revenue,
        'total_subscription_revenue': total_subscription_revenue,
        'subscription_data': subscription_data,

        'recent_orders': recent_orders,
    }

    return render(request, 'reports/admin_report.html', context)

@login_required
def export_sales_report_csv(request):
    """Export sales report as CSV for admin"""
    if not request.user.is_staff:
        return HttpResponse("Only administrators can access this report", status=403)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    filters = {}
    if start_date:
        try:
            filters['order_date__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return render(request, 'reports/admin_report.html', {'error': 'Invalid start date format'})
    if end_date:
        try:
            filters['order_date__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return render(request, 'reports/admin_report.html', {'error': 'Invalid end date format'})

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Items', 'Total', 'Status', 'Date'])
    orders = Order.objects.filter(**filters)
    for order in orders:
        writer.writerow([
            order.id,
            order.buyer.get_full_name() or order.buyer.username,
            order.items.count(),
            f'ZMW {order.total_amount:.2f}',
            order.status.title(),
            order.order_date.strftime('%b %d, %Y')
        ])
    return response

import datetime
from collections import defaultdict
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from marketplace.models import Product, OrderItem

from collections import defaultdict
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from collections import defaultdict
import datetime
from django.utils import timezone


@login_required
def custom_sales_report(request):
    """Generate custom sales report based on a date range"""
    if not request.user.is_seller:
        return HttpResponse("Only sellers can access sales reports", status=403)

    # Get the start and end dates from the request (defaults to last 30 days)
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')

    # Try to parse the dates, default to last 30 days if not provided or in an invalid format
    try:
        if start_date_str and end_date_str:
            # Parse the dates
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Ensure end_date is after start_date
            if end_date < start_date:
                return HttpResponse("End date cannot be before start date.", status=400)
        else:
            # Default to the last 30 days
            end_date = timezone.now().date()
            start_date = end_date - datetime.timedelta(days=30)
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    # Filter products by seller
    products = Product.objects.filter(seller=request.user)

    # Initialize customer sales aggregation
    customer_data = defaultdict(lambda: {'orders': 0, 'quantity': 0, 'revenue': 0})

    # Totals
    total_orders = 0
    total_quantity = 0
    total_revenue = 0

    # Loop through each product and fetch the relevant order items
    for product in products:
        order_items = OrderItem.objects.filter(
            product=product,
            order__order_date__range=(start_date, end_date + datetime.timedelta(days=1))
        ).select_related('order', 'order__buyer')

        # Loop through the order items to aggregate data per customer
        for item in order_items:
            customer = item.order.buyer
            customer_data[customer]['orders'] += 1
            customer_data[customer]['quantity'] += item.quantity
            revenue = item.quantity * item.price
            customer_data[customer]['revenue'] += revenue

            # Update totals
            total_orders += 1
            total_quantity += item.quantity
            total_revenue += revenue

    # Convert customer_data dictionary into a list of customer sales
    customer_sales = [
        {
            'customer': customer,
            'orders': data['orders'],
            'quantity': data['quantity'],
            'revenue': data['revenue'],
        }
        for customer, data in customer_data.items()
    ]

    # Render the report in the template
    return render(request, 'reports/custom_sales_report.html', {
        'customer_sales': customer_sales,
        'total_orders': total_orders,
        'total_quantity': total_quantity,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
def export_products_sold_csv(request):
    """Export products sold as CSV for admin"""
    if not request.user.is_staff:
        return HttpResponse("Only administrators can access this report", status=403)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Date range filtering
    filters = {}
    if start_date:
        try:
            filters['order__order_date__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return render(request, 'reports/export_products_sold_csv.html', {'error': 'Invalid start date format'})
    if end_date:
        try:
            filters['order__order_date__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return render(request, 'reports/export_products_sold_csv.html', {'error': 'Invalid end date format'})

    # Query products sold
    products_sold = OrderItem.objects.filter(**filters).values(
        'product__seller__username',
        'product__title',
        'product__category__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum('product__price')
    ).order_by('product__seller__username')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_sold.csv"'

    writer = csv.writer(response)
    writer.writerow(['Seller', 'Product', 'Category', 'Quantity Sold', 'Revenue (ZMW)'])

    for sale in products_sold:
        writer.writerow([
            sale['product__seller__username'],
            sale['product__title'],
            sale['product__category__name'] or 'N/A',
            sale['quantity_sold'],
            f"{sale['revenue']:.2f}" if sale['revenue'] else '0.00'
        ])

    return response

@login_required
def export_users_csv(request):
    """Export registered users as CSV for admin"""
    if not request.user.is_staff:
        return HttpResponse("Only administrators can access this report", status=403)

    # Query all users
    users = User.objects.all()

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registered_users.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Date Joined', 'Status', 'Role'])

    for user in users:
        role = 'Buyer'  # Default role
        if user.is_seller:
            role = 'Seller'
        elif user.is_staff:
            role = 'Admin'
        writer.writerow([
            user.username,
            user.email or 'N/A',
            user.date_joined.strftime('%Y-%m-%d'),
            'Active' if user.is_active else 'Inactive',
            role
        ])

    return response

@login_required
@csrf_exempt
def toggle_user_active(request, user_id):
    """Toggle user active status"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Only administrators can perform this action'}, status=403)

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user.is_active = data.get('active', not user.is_active)
            user.save()
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request data'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def change_user_role(request, user_id):
    """Change user role"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Only administrators can perform this action'}, status=403)

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            role = data.get('role')
            if role not in ['buyer', 'seller', 'admin']:
                return JsonResponse({'success': False, 'error': 'Invalid role'})
            if role == 'seller':
                user.is_seller = True
                user.is_staff = False
            elif role == 'admin':
                user.is_seller = False
                user.is_staff = True
            else:  # buyer
                user.is_seller = False
                user.is_staff = False
            user.save()
            return JsonResponse({'success': True})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request data'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def delete_user(request, user_id):
    """Delete a user"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Only administrators can perform this action'}, status=403)

    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        try:
            user.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def export_sales_report_pdf(request):
    """Export sales report as PDF for admin using LaTeX"""
    if not request.user.is_staff:
        return HttpResponse("Only administrators can access this report", status=403)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Date range filtering
    filters = {}
    if start_date:
        try:
            filters['order_date__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return render(request, 'reports/admin_report.html', {'error': 'Invalid start date format'})
    if end_date:
        try:
            filters['order_date__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return render(request, 'reports/admin_report.html', {'error': 'Invalid end date format'})

    # Query recent orders
    recent_orders = Order.objects.filter(**filters).order_by('-order_date')[:10]

    # Render LaTeX template
    context = {
        'recent_orders': recent_orders,
        'start_date': start_date,
        'end_date': end_date,
    }
    latex_content = render_to_string('reports:export_sales_report_pdf.html', context)

    # Create temporary directory for LaTeX compilation
    with tempfile.TemporaryDirectory() as tmpdirname:
        tex_file_path = os.path.join(tmpdirname, 'sales_report.tex')
        pdf_file_path = os.path.join(tmpdirname, 'sales_report.pdf')

        # Write LaTeX content to file
        with open(tex_file_path, 'w', encoding='utf-8') as tex_file:
            tex_file.write(latex_content)

        # Compile LaTeX to PDF using latexmk
        try:
            subprocess.run(
                ['latexmk', '-pdf', '-interaction=nonstopmode', tex_file_path],
                cwd=tmpdirname,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return HttpResponse(f"LaTeX compilation failed: {e.stderr}", status=500)

        # Read the generated PDF
        try:
            with open(pdf_file_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
        except FileNotFoundError:
            return HttpResponse("PDF file was not generated.", status=500)

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
        response.write(pdf_data)

        return response


# at the top of reports/views.py
from .models import Sale

def change_list_view(request):
    data = Sale.objects.all()
    context = {
        'data': data,
    }
    return render(request, 'reports/change_list.html', context)


from reports.models import Sale
def get_sales_report_data():
    return Sale.objects.select_related('product__seller', 'product__category') \
        .values('product__seller__username', 'product__title', 'product__category__name') \
        .annotate(quantity_sold=Sum('quantity'), revenue=Sum('total_price'))

def export_sales_report_pdf(request):
    sales_data = get_sales_report_data()
    template_path = 'reports/export_sales_report_pdf.html'
    context = {
        'sales_data': sales_data,
        'date': datetime.now(),
    }
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
from django.template.loader import get_template
from xhtml2pdf import pisa


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

# reports/views.py
from django.http import HttpResponse
import csv

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product', 'Quantity', 'Price'])

    # Example dummy data
    writer.writerow(['Item 1', 5, 100])
    writer.writerow(['Item 2', 2, 50])

    return response
def generate_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/generate_receipt.html', {'order': order})