from django.shortcuts import redirect
from django.urls import reverse
from core.utils import get_worker_for_user


class LoginRequiredMiddleware:
    """Require users to login, then allow authenticated access to the app."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        # Always allow login, logout, and static assets.
        if path.startswith("/login/") or path.startswith("/logout/") or path.startswith("/static/"):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        if request.user.is_superuser:
            return self.get_response(request)

        worker = get_worker_for_user(request.user)
        if not worker:
            return redirect(reverse('login'))

        if path.startswith("/admin/"):
            return redirect('supervisor_dashboard' if worker.is_supervisor() else 'field_dashboard')

        if worker.is_supervisor():
            if path.startswith("/field/"):
                return redirect('supervisor_dashboard')
            if path.startswith("/orders/") or path.startswith("/customers/") or path.startswith("/inventory/") or path.startswith("/deliveries/") or path.startswith("/payroll/") or path.startswith("/finance/") or path.startswith("/analytics/"):
                return redirect('supervisor_dashboard')
            return self.get_response(request)

        if worker.is_field_staff():
            if path.startswith("/supervisor/") or path.startswith("/orders/") or path.startswith("/customers/") or path.startswith("/inventory/") or path.startswith("/deliveries/") or path.startswith("/payroll/") or path.startswith("/finance/") or path.startswith("/analytics/"):
                return redirect('field_dashboard')
            return self.get_response(request)

        return self.get_response(request)


