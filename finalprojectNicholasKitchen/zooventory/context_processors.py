from .models import Notification

def unread_notifcations(request):
    if request.user.is_authenticated:
        # Find all unread messages and store the most recent 5
        unread = Notification.objects.filter(owner=request.user, is_read=False)
        recent = unread.order_by('-created_at')[:5]
        return {
            'unread_notifications': unread,
            'recent_notifications': recent,
        }
    return {}