from accounts.models import Notification

def global_notifications(request):
    if request.user.is_authenticated:
        return {
            'unread_notifications': Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).order_by('-created_at')
        }
    return {}
