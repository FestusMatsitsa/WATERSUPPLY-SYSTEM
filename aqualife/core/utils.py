from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from core.models import Worker


def get_worker_for_user(user):
    if not user or not user.is_authenticated:
        return None
    return Worker.objects.filter(user=user).first()


def require_worker_role(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            worker = get_worker_for_user(request.user)
            if not worker or worker.role not in allowed_roles:
                messages.error(request, "Your account does not have permission to access this page.")
                if worker and worker.role == "supervisor":
                    return redirect("supervisor_dashboard")
                if worker and worker.role in ("driver", "turnboy"):
                    return redirect("field_dashboard")
                return redirect("login")
            request.worker = worker
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
