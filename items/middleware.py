from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from datetime import date
from django.shortcuts import redirect
from django.contrib import messages

class PendingApprovalMiddleware:
    EXEMPT_URL_NAMES = \
        {
         'pending_approval',
         'logout',
         'login',
         'signup'
         }
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.path.startswith('/admin/')
            or request.path.startswith(settings.MEDIA_URL)
            or request.path.startswith(settings.STATIC_URL)
        ):
            return self.get_response(request)

        user = request.user
        if user.is_authenticated:
            if not user.is_active:
                logout(request)
                messages.error(request, 'Your account has been deactivated. Contact the owner.')
                return redirect('login')

            profile = getattr(user, 'profile', None)
            if profile and profile.role == 'employee' and not profile.is_approved:
                try:
                    url_name = resolve(request.path_info).url_name
                except Resolver404:
                    url_name = None
                if url_name not in self.EXEMPT_URL_NAMES:
                    return redirect('pending_approval')

        return self.get_response(request)





from datetime import date
from django.shortcuts import redirect
from django.contrib import messages

class AgeRestrictionMiddleware:
    RESTRICTED_PREFIXES = (
        '/checkout/',
        '/reserve/',
        '/reservations/',
        '/orders/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(self.RESTRICTED_PREFIXES):

            # 1. Redirect unauthenticated users to login
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this page.")
                return redirect(f"/login/?next={request.path}")

            # 2. Safely retrieve Profile and date_of_birth
            profile = getattr(request.user, 'profile', None)
            dob = getattr(profile, 'date_of_birth', None) if profile else None

            # 3. Handle missing Date of Birth gracefully
            if not dob:
                messages.error(request, "Please update your profile with your date of birth to proceed.")
                return redirect('item_list')  # Redirects to home/item_list instead of unmapped '/profile/'

            # 4. Calculate exact age
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            # 5. Block access if under 18
            if age < 18:
                messages.error(request, "You must be 18 or older to complete bookings or orders.")
                return redirect('item_list')

        return self.get_response(request)