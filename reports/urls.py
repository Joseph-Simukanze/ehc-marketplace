from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('receipt/<int:order_id>/', views.generate_receipt, name='generate_receipt'),
    path('sales/', views.sales_report, name='sales_report'),
    # path('sales/export/', views.export_sales_report, name='export_sales_report'),
    path('admin/', views.admin_report, name='admin_report'),
    path('reports/export/pdf/', views.export_sales_report_pdf, name='export_sales_report_pdf '),
    path('export-sales-report-csv/', views.export_sales_report_csv, name='export_sales_report_csv '),
    path('export-products-sold-csv/', views.export_products_sold_csv, name='export_products_sold_csv'),
    path('export-users-csv/', views.export_users_csv, name='export_users_csv'),
    path('custom-sales/', views.custom_sales_report, name='custom_sales_report'),
    path('toggle-user/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('change-role/<int:user_id>/', views.change_user_role, name='change_user_role'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('change-list/', views.change_list_view, name='change_list'),
    path('export-sales-report-pdf/', views.export_sales_report_pdf, name='export_sales_report_pdf'),
    path('export-sales-report-csv/', views.export_sales_report_csv, name='export_sales_report_csv'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('receipt/<int:order_id>/', views.generate_receipt, name='generate_receipt'),
]