import datetime
import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from mongoengine.errors import DoesNotExist, ValidationError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .decorators import role_required
from .forms import (
    AddToCartForm,
    CheckoutForm,
    ItemForm,
    OrderStatusForm,
    ProfileForm,
    ReservationForm,
    ReservationStatusForm,
    SignupForm,
)
from .models import Cart, CartItem, Item, Order, OrderItem, Profile, Reservation

LOW_STOCK_THRESHOLD = 5


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello {request.user.username}, you're authenticated!"})


def item_list(request):
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    deals_only = request.GET.get('deals') == '1'

    if query:
        items = Item.objects.filter(name__icontains=query)
    else:
        items = Item.objects.all()

    if category_filter and category_filter in Item.CATEGORY_CHOICES:
        items = [i for i in items if getattr(i, 'category', Item.CATEGORY_CHOICES[0]) == category_filter]

    if deals_only:
        items = [i for i in items if i.is_on_sale]

    deals_count = Item.objects.filter(discount_percent__gt=0).count()

    return render(request, 'items/item_list.html', {
        'items': items,
        'query': query,
        'deals_only': deals_only,
        'deals_count': deals_count,
        'categories': Item.CATEGORY_CHOICES,
        'active_category': category_filter,
    })


def item_image(request, pk):
    item = _get_item_or_404(pk)

    if not item.image:
        raise Http404('Image not found')

    try:
        image_data = item.image.read()
        return HttpResponse(image_data, content_type=item.image.content_type)
    except Exception:
        raise Http404('Image not found')


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated — date of birth saved.')
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'items/edit_profile.html', {'form': form})


@role_required('owner', 'employee')
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            Item(
                name=form.cleaned_data['name'],
                category=form.cleaned_data.get('category', Item.CATEGORY_CHOICES[0]),
                description=form.cleaned_data['description'],
                price=form.cleaned_data['price'],
                quantity=form.cleaned_data['quantity'],
                discount_percent=form.cleaned_data['discount_percent'],
                image=form.cleaned_data['image'],
            ).save()
            messages.success(request, 'Dish created successfully.')
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'items/item_form.html', {'form': form, 'title': 'Add New Dish'})


def _get_item_or_404(pk):
    try:
        return Item.objects.get(id=pk)
    except (DoesNotExist, ValidationError):
        raise Http404('Item not found')


@role_required('owner', 'employee')
def item_update(request, pk):
    item = _get_item_or_404(pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item.name = form.cleaned_data['name']
            item.category = form.cleaned_data.get('category', Item.CATEGORY_CHOICES[0])
            item.description = form.cleaned_data['description']
            item.price = form.cleaned_data['price']
            item.quantity = form.cleaned_data['quantity']
            item.discount_percent = form.cleaned_data['discount_percent']
            item.updated_at = timezone.now()
            if form.cleaned_data.get('image'):
                item.image = form.cleaned_data['image']
            item.save()
            messages.success(request, 'Dish details updated.')
            return redirect('item_list')
    else:
        form = ItemForm(initial={
            'name': item.name,
            'category': getattr(item, 'category', Item.CATEGORY_CHOICES[0]),
            'description': item.description,
            'price': item.price,
            'quantity': item.quantity,
            'discount_percent': item.discount_percent,
        })
    return render(request, 'items/item_form.html', {'form': form, 'title': 'Edit Dish', 'item': item})


@role_required('owner')
def item_delete(request, pk):
    item = _get_item_or_404(pk)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Dish removed.')
        return redirect('item_list')
    return render(request, 'items/item_confirm_delete.html', {'item': item})


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            account_type = form.cleaned_data['account_type']
            dob = form.cleaned_data.get('date_of_birth')

            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = account_type
            profile.is_approved = (account_type == 'customer')
            profile.date_of_birth = dob
            profile.save()

            login(request, user, backend='items.backends.EmailBackend')
            if account_type == 'customer':
                messages.success(request, 'Welcome! Your account is ready — start shopping.')
                return redirect('item_list')
            messages.success(request, 'Account created — waiting on the owner to approve you.')
            return redirect('dashboard')
    else:
        form = SignupForm()
    return render(request, 'items/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=identifier, password=password)
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or 'dashboard')
        messages.error(request, 'Invalid username/email or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'items/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@role_required('owner', 'employee')
def pending_approval(request):
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'employee' or profile.is_approved:
        return redirect('dashboard')
    return render(request, 'items/pending_approval.html')


@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'owner':
        return _owner_dashboard(request)
    if profile.role == 'employee':
        return _employee_dashboard(request)
    return redirect('order_history')


def _owner_dashboard(request):
    total_items = Item.objects.count()
    low_stock_items = Item.objects.filter(quantity__lt=LOW_STOCK_THRESHOLD)
    employees = Profile.objects.filter(role='employee').select_related('user').order_by('-id')

    all_orders = list(Order.objects.all().order_by('-created_at'))
    gross_revenue = sum((o.total for o in all_orders if o.status != 'Cancelled'), Decimal('0.00'))
    delivered_revenue = sum((o.total for o in all_orders if o.status == 'Delivered'), Decimal('0.00'))

    today = timezone.now().date()
    days = [today - timezone.timedelta(days=i) for i in range(6, -1, -1)]
    revenue_chart_labels = [d.strftime('%a, %b %d') for d in days]
    revenue_chart_data = []
    for d in days:
        day_sum = sum(
            (o.total for o in all_orders if o.created_at and o.created_at.date() == d and o.status != 'Cancelled'),
            Decimal('0.00'))
        revenue_chart_data.append(float(day_sum))

    dish_sales = {}
    for o in all_orders:
        if o.status != 'Cancelled':
            for line in o.items:
                dish_sales[line.name] = dish_sales.get(line.name, 0) + line.quantity

    sorted_dishes = sorted(dish_sales.items(), key=lambda x: x[1], reverse=True)[:5]
    top_dish_labels = [d[0] for d in sorted_dishes]
    top_dish_data = [d[1] for d in sorted_dishes]

    status_counts = {s: 0 for s in Order.STATUS_CHOICES}
    for o in all_orders:
        if o.status in status_counts:
            status_counts[o.status] += 1

    status_chart_labels = list(status_counts.keys())
    status_chart_data = list(status_counts.values())

    cod_count = sum(1 for o in all_orders if getattr(o, 'payment_method', 'cod') == 'cod')
    card_count = sum(1 for o in all_orders if getattr(o, 'payment_method', 'cod') == 'card')
    payment_chart_labels = ['Cash on Delivery', 'Credit/Debit Card']
    payment_chart_data = [cod_count, card_count]

    all_reservations = list(Reservation.objects.all().order_by('-created_at'))
    total_reservations = len(all_reservations)
    pending_reservations = sum(1 for r in all_reservations if r.status == 'Pending')
    confirmed_reservations = sum(1 for r in all_reservations if r.status == 'Confirmed')
    recent_reservations = all_reservations[:5]

    context = {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'low_stock_count': low_stock_items.count(),
        'employees': employees,
        'pending_count': employees.filter(is_approved=False).count(),
        'order_count': len(all_orders),
        'pending_order_count': status_counts.get('Pending', 0),
        'gross_revenue': gross_revenue,
        'delivered_revenue': delivered_revenue,
        'revenue_chart_labels_json': json.dumps(revenue_chart_labels),
        'revenue_chart_data_json': json.dumps(revenue_chart_data),
        'top_dish_labels_json': json.dumps(top_dish_labels),
        'top_dish_data_json': json.dumps(top_dish_data),
        'status_chart_labels_json': json.dumps(status_chart_labels),
        'status_chart_data_json': json.dumps(status_chart_data),
        'payment_chart_labels_json': json.dumps(payment_chart_labels),
        'payment_chart_data_json': json.dumps(payment_chart_data),
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'recent_reservations': recent_reservations,
    }
    return render(request, 'items/owner_dashboard.html', context)


def _employee_dashboard(request):
    total_items = Item.objects.count()
    low_stock_count = Item.objects.filter(quantity__lt=LOW_STOCK_THRESHOLD).count()
    pending_reservations = Reservation.objects.filter(status='Pending').count()
    return render(request, 'items/employee_dashboard.html', {
        'total_items': total_items,
        'low_stock_count': low_stock_count,
        'order_count': Order.objects.count(),
        'pending_order_count': Order.objects.filter(status='Pending').count(),
        'pending_reservations': pending_reservations,
    })


@role_required('owner')
def approve_employee(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='employee')
    if request.method == 'POST':
        profile.is_approved = True
        profile.save()
        messages.success(request, f'{profile.user.username} approved.')
    return redirect('dashboard')


@role_required('owner')
def disapprove_employee(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='employee')
    if request.method == 'POST':
        profile.is_approved = False
        profile.save()
        messages.success(request, f'{profile.user.username} access paused.')
    return redirect('dashboard')


@role_required('owner')
def activate_employee(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='employee')
    if request.method == 'POST':
        profile.user.is_active = True
        profile.user.save()
        messages.success(request, f'{profile.user.username} reactivated.')
    return redirect('dashboard')


@role_required('owner')
def deactivate_employee(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='employee')
    if request.method == 'POST':
        profile.user.is_active = False
        profile.user.save()
        messages.success(request, f'{profile.user.username} deactivated.')
    return redirect('dashboard')


@role_required('owner')
def delete_employee(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, role='employee')
    if request.method == 'POST':
        username = profile.user.username
        profile.user.delete()
        messages.success(request, f'{username} removed permanently.')
    return redirect('dashboard')


def _get_or_create_cart(user):
    cart = Cart.objects(user_id=user.id).first()
    if cart is None:
        cart = Cart(user_id=user.id)
        cart.save()
    return cart


def _cart_line_items(cart):
    """Resolve a Cart's embedded CartItems into (item, quantity, line_total) tuples,
    silently dropping any lines whose Item no longer exists."""
    lines = []
    stale = False
    for ci in list(cart.items):
        try:
            item = Item.objects.get(id=ci.item_id)
        except (DoesNotExist, ValidationError):
            cart.items.remove(ci)
            stale = True
            continue
        qty = min(ci.quantity, item.quantity) if item.quantity >= 0 else ci.quantity
        if qty <= 0:
            cart.items.remove(ci)
            stale = True
            continue
        if qty != ci.quantity:
            ci.quantity = qty
            stale = True
        unit_price = item.discounted_price
        lines.append({
            'item': item,
            'quantity': ci.quantity,
            'unit_price': unit_price,
            'line_total': (unit_price * ci.quantity).quantize(Decimal('0.01')),
            'regular_line_total': (item.price * ci.quantity).quantize(Decimal('0.01')),
        })
    if stale:
        cart.updated_at = timezone.now()
        cart.save()
    return lines


def cart_item_count(request):
    """Small helper used by the nav badge; safe to call for anonymous users."""
    if not request.user.is_authenticated:
        return 0
    cart = Cart.objects(user_id=request.user.id).first()
    return cart.total_quantity() if cart else 0


@login_required
def cart_view(request):
    cart = _get_or_create_cart(request.user)
    lines = _cart_line_items(cart)
    subtotal = sum((l['regular_line_total'] for l in lines), Decimal('0.00'))
    total = sum((l['line_total'] for l in lines), Decimal('0.00'))
    savings = (subtotal - total).quantize(Decimal('0.01'))
    return render(request, 'items/cart.html', {
        'lines': lines,
        'subtotal': subtotal,
        'savings': savings,
        'total': total,
    })


@login_required
def add_to_cart(request, pk):
    item = _get_item_or_404(pk)
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            if item.quantity <= 0:
                messages.error(request, f'{item.name} is out of stock.')
                return redirect('item_list')

            cart = _get_or_create_cart(request.user)
            existing = next((ci for ci in cart.items if ci.item_id == str(item.id)), None)
            new_qty = qty + (existing.quantity if existing else 0)
            if new_qty > item.quantity:
                new_qty = item.quantity
                messages.warning(request, f'Only {item.quantity} of {item.name} available — added the max.')

            if existing:
                existing.quantity = new_qty
            else:
                cart.items.append(CartItem(item_id=str(item.id), quantity=new_qty))
            cart.updated_at = timezone.now()
            cart.save()
            messages.success(request, f'Added {item.name} to your cart.')
        else:
            messages.error(request, 'Please choose a valid quantity.')
    next_url = request.POST.get('next') or 'item_list'
    return redirect(next_url)


@login_required
def update_cart_item(request, pk):
    if request.method == 'POST':
        item = _get_item_or_404(pk)
        try:
            qty = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            qty = 1

        cart = _get_or_create_cart(request.user)
        existing = next((ci for ci in cart.items if ci.item_id == str(item.id)), None)
        if existing:
            if qty <= 0:
                cart.items.remove(existing)
                messages.success(request, f'Removed {item.name} from your cart.')
            else:
                qty = min(qty, item.quantity) if item.quantity > 0 else qty
                existing.quantity = qty
            cart.updated_at = timezone.now()
            cart.save()
    return redirect('cart_view')


@login_required
def remove_from_cart(request, pk):
    if request.method == 'POST':
        item = _get_item_or_404(pk)
        cart = _get_or_create_cart(request.user)
        existing = next((ci for ci in cart.items if ci.item_id == str(item.id)), None)
        if existing:
            cart.items.remove(existing)
            cart.updated_at = timezone.now()
            cart.save()
            messages.success(request, f'Removed {item.name} from your cart.')
    return redirect('cart_view')


@login_required
def checkout_view(request):
    cart = _get_or_create_cart(request.user)
    lines = _cart_line_items(cart)

    if not lines:
        messages.info(request, 'Your cart is empty.')
        return redirect('item_list')

    subtotal = sum((l['regular_line_total'] for l in lines), Decimal('0.00'))
    total = sum((l['line_total'] for l in lines), Decimal('0.00'))
    savings = (subtotal - total).quantize(Decimal('0.01'))

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            for line in lines:
                fresh_item = _get_item_or_404(str(line['item'].id))
                if fresh_item.quantity < line['quantity']:
                    messages.error(
                        request,
                        f"Sorry, only {fresh_item.quantity} of {fresh_item.name} left — please update your cart."
                    )
                    return redirect('cart_view')

            order_items = [
                OrderItem(
                    item_id=str(line['item'].id),
                    name=line['item'].name,
                    unit_price=line['unit_price'],
                    quantity=line['quantity'],
                )
                for line in lines
            ]
            order = Order(
                user_id=request.user.id,
                username=request.user.username,
                items=order_items,
                subtotal=subtotal,
                discount_total=savings,
                total=total,
                shipping_name=form.cleaned_data['shipping_name'],
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_phone=form.cleaned_data['shipping_phone'],
                payment_method=form.cleaned_data['payment_method'],
            )
            order.save()

            for line in lines:
                fresh_item = _get_item_or_404(str(line['item'].id))
                fresh_item.quantity = max(0, fresh_item.quantity - line['quantity'])
                fresh_item.save()

            cart.items = []
            cart.updated_at = timezone.now()
            cart.save()

            messages.success(request, 'Order placed! Thank you.')
            return redirect('order_detail', order_id=str(order.id))
    else:
        initial = {}
        full_name = request.user.get_full_name()
        if full_name:
            initial['shipping_name'] = full_name
        form = CheckoutForm(initial=initial)

    return render(request, 'items/checkout.html', {
        'form': form,
        'lines': lines,
        'subtotal': subtotal,
        'savings': savings,
        'total': total,
    })


def _get_order_or_404(order_id):
    try:
        return Order.objects.get(id=order_id)
    except (DoesNotExist, ValidationError):
        raise Http404('Order not found')


@login_required
def order_history(request):
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role in ('owner', 'employee'):
        return redirect('order_management')
    orders = Order.objects.filter(user_id=request.user.id).order_by('-created_at')
    return render(request, 'items/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = _get_order_or_404(order_id)
    profile = getattr(request.user, 'profile', None)
    is_staff = profile and profile.role in ('owner', 'employee')
    if not is_staff and order.user_id != request.user.id:
        raise Http404('Order not found')
    return render(request, 'items/order_detail.html', {
        'order': order,
        'is_staff': is_staff,
        'statuses': Order.STATUS_CHOICES,
    })


@role_required('owner', 'employee')
def order_management(request):
    status_filter = request.GET.get('status', '').strip()
    orders = Order.objects.all().order_by('-created_at')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'items/order_management.html', {
        'orders': orders,
        'status_filter': status_filter,
        'statuses': Order.STATUS_CHOICES,
    })


@role_required('owner', 'employee')
def update_order_status(request, order_id):
    order = _get_order_or_404(order_id)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST)
        if form.is_valid():
            order.status = form.cleaned_data['status']
            order.updated_at = timezone.now()
            order.save()
            messages.success(request, f'Order marked as {order.status}.')
    return redirect('order_detail', order_id=str(order.id))


def _get_reservation_or_404(reservation_id):
    try:
        return Reservation.objects.get(id=reservation_id)
    except (DoesNotExist, ValidationError):
        raise Http404('Reservation not found')


@login_required
def reserve_table(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = Reservation(
                user_id=request.user.id,
                username=request.user.username,
                guest_name=form.cleaned_data['guest_name'],
                guest_email=form.cleaned_data['guest_email'],
                guest_phone=form.cleaned_data['guest_phone'],
                guest_count=form.cleaned_data['guest_count'],
                reservation_date=form.cleaned_data['reservation_date'],
                time_slot=form.cleaned_data['time_slot'],
                table_type=form.cleaned_data['table_type'],
                special_requests=form.cleaned_data['special_requests'],
            )
            reservation.save()
            messages.success(
                request,
                f"Table reservation requested for {reservation.guest_name}! Our concierge will confirm shortly."
            )
            return redirect('my_reservations')
    else:
        form = ReservationForm(initial={
            'guest_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'guest_email': request.user.email,
            'guest_count': 2,
            'reservation_date': (timezone.now() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
        })

    return render(request, 'items/reservation_form.html', {
        'form': form,
        'table_types': Reservation.TABLE_TYPE_CHOICES,
        'time_slots': Reservation.TIME_SLOT_CHOICES,
    })


@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user_id=request.user.id).order_by('-created_at')
    return render(request, 'items/my_reservations.html', {
        'reservations': reservations,
    })


@role_required('owner', 'employee')
def manage_reservations(request):
    status_filter = request.GET.get('status', '').strip()
    reservations = Reservation.objects.all().order_by('-created_at')
    if status_filter:
        reservations = reservations.filter(status=status_filter)

    return render(request, 'items/manage_reservations.html', {
        'reservations': reservations,
        'status_filter': status_filter,
        'statuses': Reservation.STATUS_CHOICES,
    })


@role_required('owner', 'employee')
def update_reservation_status(request, reservation_id):
    reservation = _get_reservation_or_404(reservation_id)
    if request.method == 'POST':
        form = ReservationStatusForm(request.POST)
        if form.is_valid():
            reservation.status = form.cleaned_data['status']
            reservation.updated_at = timezone.now()
            reservation.save()
            messages.success(request, f"Reservation #{reservation.id} status updated to {reservation.status}.")
    return redirect('manage_reservations')