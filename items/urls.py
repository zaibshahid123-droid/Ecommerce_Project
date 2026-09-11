from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
from .api_views import item_list_api, item_detail_api

urlpatterns = [
    # Static pages & App root
    path('', views.item_list, name='item_list'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # REST API Endpoints
    path('api/items/', item_list_api, name='api_item_list'),
    path('api/items/<str:pk>/', item_detail_api, name='api_item_detail'),
    path('api/protected/', views.protected_view, name='protected'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Items Management (Static paths MUST come before dynamic <str:pk>)
    path('create/', views.item_create, name='item_create'),
    path('<str:pk>/image/', views.item_image, name='item_image'),
    path('<str:pk>/update/', views.item_update, name='item_update'),
    path('<str:pk>/delete/', views.item_delete, name='item_delete'),

    # Dashboard & Employee Management
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    path('dashboard/employees/<int:profile_id>/approve/', views.approve_employee, name='approve_employee'),
    path('dashboard/employees/<int:profile_id>/disapprove/', views.disapprove_employee, name='disapprove_employee'),
    path('dashboard/employees/<int:profile_id>/activate/', views.activate_employee, name='activate_employee'),
    path('dashboard/employees/<int:profile_id>/deactivate/', views.deactivate_employee, name='deactivate_employee'),
    path('dashboard/employees/<int:profile_id>/delete/', views.delete_employee, name='delete_employee'),

    # Cart Operations
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<str:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:pk>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<str:pk>/', views.remove_from_cart, name='remove_from_cart'),

    # Orders & Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('manage/orders/', views.order_management, name='order_management'),

    # Table & Gazebo Reservations
    path('reserve/', views.reserve_table, name='reserve_table'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('manage/reservations/', views.manage_reservations, name='manage_reservations'),
    path('manage/reservations/<str:reservation_id>/status/', views.update_reservation_status, name='update_reservation_status'),
]