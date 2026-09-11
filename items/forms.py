import uuid
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
<<<<<<< HEAD
from .models import Item, Reservation, Profile
=======
from .models import Item, Reservation ,Profile
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa


class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )

    class Meta:
        model = Profile
        fields = ['date_of_birth']


<<<<<<< HEAD
=======

>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
class ItemForm(forms.Form):
    CATEGORY_CHOICES = [(c, c) for c in Item.CATEGORY_CHOICES]

    name = forms.CharField(max_length=200, label='Dish Name')
<<<<<<< HEAD
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        initial=Item.CATEGORY_CHOICES[0][0] if isinstance(Item.CATEGORY_CHOICES[0], tuple) else Item.CATEGORY_CHOICES[0],
        label='Menu Category'
    )
    description = forms.CharField(
        max_length=2000,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Culinary Description'
    )
=======
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, initial=Item.CATEGORY_CHOICES[0], label='Menu Category')
    description = forms.CharField(max_length=2000, required=False, widget=forms.Textarea(attrs={'rows': 3}),
                                  label='Culinary Description')
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=10, label='Price ($)')
    quantity = forms.IntegerField(min_value=0, label='Portions in Stock')
    discount_percent = forms.DecimalField(
        min_value=0, max_value=90, decimal_places=2, max_digits=4, required=False,
        initial=0,
        label='Discount % (Special Deal)',
        help_text="Leave at 0 for standard pricing. e.g. 20 = 20% off.",
    )

    image = forms.ImageField(required=False, label='Dish Photography')

    def clean_discount_percent(self):
        return self.cleaned_data.get('discount_percent') or 0


class SignupForm(UserCreationForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Date of Birth"
    )
    email = forms.EmailField(required=True)
    account_type = forms.ChoiceField(
        choices=[('customer', "I'm here to shop"), ('employee', 'I work here (staff)')],
        widget=forms.RadioSelect,
        initial='customer',
        label='Account type',
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'date_of_birth', 'account_type']

<<<<<<< HEAD
    def clean_email(self):
        """Ensure email address is unique across PostgreSQL / Neon database."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
=======
    def clean_username(self):
        """Bypass Django's default uniqueness check on display names."""
        return self.cleaned_data.get('username')

    def clean_email(self):
        """Ensure email address is unique across the entire site."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
            raise ValidationError("An account with this email address already exists.")
        return email

    def save(self, commit=True):
<<<<<<< HEAD
        """Saves standard User instance directly to PostgreSQL / Neon."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
=======
        """Append a unique suffix to the internal username so SQLite allows duplicate display names."""
        user = super().save(commit=False)
        display_name = self.cleaned_data['username']
        user.username = f"{display_name}_{uuid.uuid4().hex[:8]}"
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa

        if commit:
            user.save()
        return user


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit / Debit Card'),
    ]
    shipping_name = forms.CharField(max_length=200, label='Full name')
<<<<<<< HEAD
    shipping_address = forms.CharField(
        max_length=500,
        label='Delivery address',
        widget=forms.Textarea(attrs={'rows': 2})
    )
=======
    shipping_address = forms.CharField(max_length=500, label='Delivery address',
                                       widget=forms.Textarea(attrs={'rows': 2}))
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    shipping_city = forms.CharField(max_length=200, label='City')
    shipping_phone = forms.CharField(max_length=50, label='Phone number')
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, initial='cod')


class OrderStatusForm(forms.Form):
    STATUS_CHOICES = [(s, s) for s in ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled')]
    status = forms.ChoiceField(choices=STATUS_CHOICES)


class ReservationForm(forms.Form):
    TABLE_TYPE_CHOICES = [(t, t) for t in Reservation.TABLE_TYPE_CHOICES]
    TIME_SLOT_CHOICES = [(ts, ts) for ts in Reservation.TIME_SLOT_CHOICES]

    guest_name = forms.CharField(max_length=200, label='Guest Name (or Party Host)')
    guest_email = forms.EmailField(label='Email Address')
    guest_phone = forms.CharField(max_length=50, label='Contact Phone')
    guest_count = forms.IntegerField(min_value=1, max_value=50, initial=2, label='Number of Guests')
    reservation_date = forms.CharField(
        max_length=50,
        label='Reservation Date',
        widget=forms.TextInput(attrs={'type': 'date'}),
        help_text='Select your desired dining date'
    )
    time_slot = forms.ChoiceField(choices=TIME_SLOT_CHOICES, label='Preferred Dining Time Slot')
<<<<<<< HEAD
    table_type = forms.ChoiceField(
        choices=TABLE_TYPE_CHOICES,
        initial=Reservation.TABLE_TYPE_CHOICES[0] if Reservation.TABLE_TYPE_CHOICES else '',
        label='Seating & Ambiance Preference'
    )
=======
    table_type = forms.ChoiceField(choices=TABLE_TYPE_CHOICES, initial='Poolside VIP Gazebo',
                                   label='Seating & Ambiance Preference')
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    special_requests = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(
<<<<<<< HEAD
            attrs={'rows': 3, 'placeholder': 'Anniversary, birthday, dietary requirements, high chair needs, etc.'}
        ),
=======
            attrs={'rows': 3, 'placeholder': 'Anniversary, birthday, dietary requirements, high chair needs, etc.'}),
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
        label='Special Requests / Celebrations'
    )


class ReservationStatusForm(forms.Form):
    STATUS_CHOICES = [(s, s) for s in Reservation.STATUS_CHOICES]
    status = forms.ChoiceField(choices=STATUS_CHOICES)