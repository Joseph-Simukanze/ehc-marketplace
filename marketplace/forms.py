from django import forms
from .models import Product, Category, User, Order, Cart
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation

User = get_user_model()

class ProductForm(forms.ModelForm):
    seller = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        label="Seller (Admin Only)",
        empty_label="Select a seller"
    )

    class Meta:
        model = Product
        fields = [
            'title', 'description', 'price', 'category', 'image', 'location',
            'stock', 'low_stock_threshold', 'seller'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'min': '1'}),
            'low_stock_threshold': forms.NumberInput(attrs={'min': '1'}),
            'location': forms.TextInput(attrs={'placeholder': 'Enter product location'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if not user or not user.is_staff:
            self.fields.pop('seller', None)

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be a positive value.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock <= 0:
            raise forms.ValidationError("Stock must be greater than zero.")
        return stock

    def clean_low_stock_threshold(self):
        threshold = self.cleaned_data.get('low_stock_threshold')
        if threshold is not None and threshold < 0:
            raise forms.ValidationError("Low stock threshold cannot be negative.")
        return threshold

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            valid_image_formats = ['image/jpeg', 'image/png', 'image/gif']
            if image.content_type not in valid_image_formats:
                raise forms.ValidationError("Unsupported image format. Only JPG, PNG, or GIF are allowed.")
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image size must not exceed 5MB.")
        return image

class CheckoutForm(forms.ModelForm):
    DELIVERY_OPTION_CHOICES = [
        ('inside', 'Inside Campus'),
        ('outside', 'Outside Campus'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('payment_on_delivery', 'Payment on Delivery'),
        ('mtn_money', 'MTN Mobile Money'),
        ('airtel_money', 'Airtel Money'),
    ]
    
    DELIVERY_METHOD_CHOICES = [
        ('bicycle', 'Bicycle (ZMW 20.00)'),
        ('motorbike', 'Motorbike (ZMW 35.00)'),
        ('small_car', 'Small Car (ZMW 50.00)'),
    ]
    
    IS_STUDENT_CHOICES = [
        ('', 'Select an option...'),
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    phone_number_inside = forms.CharField(
        max_length=15,
        required=False,
        label="Phone Number (Inside Campus)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +260123456789 or 0971234567',
            'pattern': '\+?([0-9]{10,15})',
            'aria-describedby': 'phone-help-inside',
        }),
        error_messages={
            'invalid': 'Enter a valid phone number (10-15 digits, e.g., +260123456789 or 0971234567).'
        }
    )
    
    phone_number_outside = forms.CharField(
        max_length=15,
        required=False,
        label="Phone Number (Outside Campus)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +260123456789 or 0971234567',
            'pattern': '\+?([0-9]{10,15})',
            'aria-describedby': 'phone-help-outside',
        }),
        error_messages={
            'invalid': 'Enter a valid phone number (10-15 digits, e.g., +260123456789 or 0971234567).',
            'required': 'Phone number is required for outside-campus delivery.'
        }
    )

    delivery_location = forms.CharField(
        max_length=255,
        required=True,
        label="Delivery Location",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter specific delivery instructions (e.g., Library entrance)',
        }),
        error_messages={'required': 'Delivery location is required.'}
    )

    gps_location = forms.CharField(
        max_length=255,
        required=False,
        label="GPS Location",
        widget=forms.HiddenInput(attrs={'id': 'gps_location'})
    )

    delivery_option = forms.ChoiceField(
        choices=DELIVERY_OPTION_CHOICES,
        required=True,
        label="Delivery Option",
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Please select a delivery area.'}
    )

    hostel_name = forms.CharField(
        max_length=100,
        required=False,
        label="Hostel Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Main Hostel'
        })
    )

    room_number = forms.CharField(
        max_length=10,
        required=False,
        label="Room Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., A-12'
        })
    )

    is_student = forms.ChoiceField(
        choices=IS_STUDENT_CHOICES,
        required=False,
        label="Are you a student? (Inside Campus)",
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Please select if you are a student.'}
    )

    is_student_outside = forms.ChoiceField(
        choices=IS_STUDENT_CHOICES,
        required=False,
        label="Are you a student? (Outside Campus)",
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Please select if you are a student.'}
    )

    student_number = forms.CharField(
        max_length=50,
        required=False,
        label="Student Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., EH123456'
        })
    )

    program_of_study = forms.CharField(
        max_length=100,
        required=False,
        label="Program of Study",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Computer Science'
        })
    )

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        required=True,
        label="Payment Method",
        widget=forms.Select(attrs={'class': 'form-select'}),
        error_messages={'required': 'Please select a payment method.'}
    )

    delivery_method = forms.ChoiceField(
        choices=DELIVERY_METHOD_CHOICES,
        required=False,
        label="Delivery Method",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    airtel_number = forms.CharField(
        max_length=15,
        required=False,
        label="Airtel Money Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +260123456789 or 0971234567',
            'pattern': '\+?([0-9]{10,15})',
        }),
        error_messages={'required': 'Airtel Money number is required for Airtel payment.'}
    )

    mtn_number = forms.CharField(
        max_length=15,
        required=False,
        label="MTN Money Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +260123456789 or 0971234567',
            'pattern': '\+?([0-9]{10,15})',
        }),
        error_messages={'required': 'MTN Money number is required for MTN payment.'}
    )

    delivery_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0.00,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    total_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0.00,
        disabled=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = Order
        fields = [
            'delivery_location', 'gps_location', 'delivery_option', 'phone_number_inside',
            'phone_number_outside', 'hostel_name', 'room_number', 'is_student',
            'is_student_outside', 'student_number', 'program_of_study', 'payment_method',
            'delivery_method', 'airtel_number', 'mtn_number', 'delivery_fee', 'total_amount'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            try:
                cart = Cart.objects.get(user=user)
                total = sum(item.get_total_price() for item in cart.items.all())
                self.fields['total_amount'].initial = total
                self.fields['delivery_fee'].initial = 0.00
            except Cart.DoesNotExist:
                self.fields['total_amount'].initial = 0.00
                self.fields['delivery_fee'].initial = 0.00

    def clean_phone_number_inside(self):
        phone = self.cleaned_data.get('phone_number_inside')
        if phone:
            phone = phone.strip().replace(" ", "")
            if phone.startswith("+"):
                if not phone.startswith("+260") or not phone[4:].isdigit() or len(phone) != 13:
                    raise forms.ValidationError("Enter a valid Zambian phone number starting with +260 (13 digits).")
            elif phone.startswith("09"):
                if not phone.isdigit() or len(phone) != 10:
                    raise forms.ValidationError("Phone number must be 10 digits starting with 09.")
            else:
                raise forms.ValidationError("Phone number must start with +260 or 09.")
        return phone

    def clean_phone_number_outside(self):
        phone = self.cleaned_data.get('phone_number_outside')
        if phone:
            phone = phone.strip().replace(" ", "")
            if phone.startswith("+"):
                if not phone.startswith("+260") or not phone[4:].isdigit() or len(phone) != 13:
                    raise forms.ValidationError("Enter a valid Zambian phone number starting with +260 (13 digits).")
            elif phone.startswith("09"):
                if not phone.isdigit() or len(phone) != 10:
                    raise forms.ValidationError("Phone number must be 10 digits starting with 09.")
            else:
                raise forms.ValidationError("Phone number must start with +260 or 09.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        delivery_option = cleaned_data.get('delivery_option')
        room_number = cleaned_data.get('room_number')
        is_student = cleaned_data.get('is_student')
        is_student_outside = cleaned_data.get('is_student_outside')
        student_number = cleaned_data.get('student_number')
        program_of_study = cleaned_data.get('program_of_study')
        payment_method = cleaned_data.get('payment_method')
        delivery_method = cleaned_data.get('delivery_method')
        airtel_number = cleaned_data.get('airtel_number')
        mtn_number = cleaned_data.get('mtn_number')
        phone_number_inside = cleaned_data.get('phone_number_inside')
        phone_number_outside = cleaned_data.get('phone_number_outside')
        delivery_location = cleaned_data.get('delivery_location')

        # Validate delivery_location
        if not delivery_location:
            self.add_error('delivery_location', "Delivery location is required.")

        # Validate phone number based on delivery option
        if delivery_option == 'inside' and not phone_number_inside:
            self.add_error('phone_number_inside', "Phone number is required for inside-campus delivery.")
        elif delivery_option == 'outside' and not phone_number_outside:
            self.add_error('phone_number_outside', "Phone number is required for outside-campus delivery.")

        # Validate room_number for inside-campus delivery
        if delivery_option == 'inside' and not room_number:
            self.add_error('room_number', "Room number is required for inside-campus delivery.")

        # Validate is_student based on delivery option
        if delivery_option == 'inside':
            if not is_student:
                self.add_error('is_student', "Please select if you are a student.")
            elif is_student == 'no':
                self.add_error('is_student', "Sorry, only students are eligible to purchase this product.")
            elif is_student == 'yes':
                if not student_number:
                    self.add_error('student_number', "Student number is required for students.")
                if not program_of_study:
                    self.add_error('program_of_study', "Program of study is required for students.")
        elif delivery_option == 'outside':
            if not is_student_outside:
                self.add_error('is_student_outside', "Please select if you are a student.")
            elif is_student_outside == 'no':
                self.add_error('is_student_outside', "Sorry, only students are eligible to purchase this product.")
            elif is_student_outside == 'yes':
                if not student_number:
                    self.add_error('student_number', "Student number is required for students.")
                if not program_of_study:
                    self.add_error('program_of_study', "Program of study is required for students.")

        # Validate delivery_method for payment_on_delivery (outside campus)
        if payment_method == 'payment_on_delivery' and delivery_option == 'outside' and not delivery_method:
            self.add_error('delivery_method', "Delivery method is required for payment on delivery outside campus.")

        # Validate mobile money numbers
        if payment_method == 'airtel_money' and not airtel_number:
            self.add_error('airtel_number', "Airtel Money number is required for Airtel payment.")
        if payment_method == 'mtn_money' and not mtn_number:
            self.add_error('mtn_number', "MTN Money number is required for MTN payment.")

        # Calculate delivery fee using Decimal for precision
        delivery_fees = {
            'bicycle': Decimal('20.00'),
            'motorbike': Decimal('35.00'),
            'small_car': Decimal('50.00')
        }
        if payment_method == 'payment_on_delivery' and delivery_option == 'outside' and delivery_method:
            delivery_fee = delivery_fees.get(delivery_method, Decimal('0.00'))
        else:
            delivery_fee = Decimal('0.00')

        cleaned_data['delivery_fee'] = delivery_fee

        # Safely get total_amount as Decimal
        try:
            total_amount = Decimal(str(cleaned_data.get('total_amount', '0.00')))
        except (TypeError, InvalidOperation):
            total_amount = Decimal('0.00')

        # Add delivery fee to total amount
        cleaned_data['total_amount'] = total_amount + delivery_fee

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        delivery_option = self.cleaned_data.get('delivery_option')
        phone_number = self.cleaned_data.get('phone_number_inside') if delivery_option == 'inside' else self.cleaned_data.get('phone_number_outside')
        is_student = self.cleaned_data.get('is_student') if delivery_option == 'inside' else self.cleaned_data.get('is_student_outside')

        # Map form fields to model fields
        order.phone_number = phone_number  # Assuming Order model has a single phone_number field
        order.is_student = is_student == 'yes'
        order.student_number = self.cleaned_data.get('student_number')
        order.program_of_study = self.cleaned_data.get('program_of_study')
        order.delivery_fee = self.cleaned_data.get('delivery_fee')
        order.total_amount = self.cleaned_data.get('total_amount')

        if commit:
            order.save()
        return order