from .models import Notification


def notifications_context(request):
    """Notificaciones del usuario autenticado para el popup y el badge de todas las pantallas."""
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return {'unread_notifications_count': 0, 'recent_notifications': []}
    return {
        'unread_notifications_count': Notification.objects.filter(user=user, leida=False).count(),
        'recent_notifications': list(
            Notification.objects.filter(user=user)
            .select_related('from_user')
            .order_by('-created_at')[:5]
        ),
    }
