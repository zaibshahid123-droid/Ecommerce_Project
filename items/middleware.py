from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import resolve, Resolver404


class PendingApprovalMiddleware:
    EXEMPT_URL_NAMES = {'pending_approval', 'logout', 'login', 'signup'}

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



