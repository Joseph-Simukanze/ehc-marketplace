ehc_marketplace/
├── manage.py
├── requirements.txt
├── ehc_marketplace/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   │   └── accounts/
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── profile.html
│   │       ├── subscription_status.html
│   │       └── subscribe.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── marketplace/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   │   └── marketplace/
│   │       ├── home.html
│   │       ├── product_list.html
│   │       ├── product_detail.html
│   │       ├── cart.html
│   │       └── checkout.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── payments/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   │   └── payments/
│   │       ├── process_payment.html
│   │       └── payment_success.html
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── messaging/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── migrations/
│   ├── models.py
│   ├── routing.py
│   ├── templates/
│   │   └── messaging/
│   │       ├── conversation_list.html
│   │       └── conversation_detail.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── reports/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── templates/
│   │   └── reports/
│   │       ├── sales_report.html
│   │       ├── customer_report.html
│   │       └── admin_report.html
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── static/
│   ├── css/
│   │   ├── main.css
│   │   └── bootstrap.min.css
│   ├── js/
│   │   ├── main.js
│   │   ├── bootstrap.min.js
│   │   └── chat.js
│   └── images/
│       └── logo.png
└── templates/
    ├── base.html
    └── includes/
        ├── navbar.html
        └── footer.html