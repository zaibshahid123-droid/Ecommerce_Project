from functools import wraps
<<<<<<< HEAD
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    """
    Decorator enforcing role-based access control.
    Checks user's attached Profile for role permissions and approval status.
    """
=======
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
<<<<<<< HEAD

            # 1. Missing Profile
            if not profile:
                messages.error(request, "User profile not found.")
                return redirect('item_list')

            # 2. Unapproved Employee Protection
            if profile.role == 'employee' and not profile.is_approved:
                return redirect('pending_approval')

            # 3. Role Authorization Check
            if profile.role not in roles:
                messages.error(request, "You do not have permission to access this page.")
                return redirect('dashboard')

=======
            if not profile or profile.role not in roles:
                raise PermissionDenied
>>>>>>> 2feabb2fe60d8c581b15980d33e09e7979fca5aa
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator