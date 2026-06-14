from core.models import Worker


def current_worker(request):
    if request.user.is_authenticated:
        worker = Worker.objects.filter(user=request.user).first()
        return {"current_worker": worker}
    return {}
