import logging

from django.conf import settings
from django_q.tasks import async_task
from pywebpush import webpush, WebPushException

from muni_portal.core.models import WebPushNotification, WebPushSubscription, WebPushNotificationResult

logger = logging.getLogger(__name__)


def queue_send_webpush_notification(notification_id):
    notification = WebPushNotification.objects.get(id=notification_id)
    for subscription in WebPushSubscription.objects.all():
        result = WebPushNotificationResult(subscription=subscription, notification=notification)
        try:
            response = webpush(
                subscription.serialize(),
                {
                    "type": "notification",
                    "notification": notification.serialize(),
                },
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.DEFAULT_FROM_EMAIL}"}
            )
            result.status_code = response.status_code
        except WebPushException as e:
            logger.exception(f"Can't send web push notification to subscription #{subscription.id}, error {e.message}")
            result.message = e.message
            if e.response and e.response.json():
                result.status_code = e.response.status_code
                result.data = e.response.json()
        except Exception as e:
            logger.exception(f"Web push unhandled error for subscription #{subscription.id}, error {e}")
            result.message = e
        result.save()
    notification.status = notification.STATUS_COMPLETED
    notification.save()
    return True


def webpush_notification_result_hook(task):
    if not task.success:
        notification = WebPushNotification.objects.get(id=task.args[0])
        notification.status = notification.STATUS_FAILED_INCOMPLETE
        notification.data = {"result": task.result}
        notification.save()


def send_webpush_notification(notification):
    async_task(queue_send_webpush_notification, notification.id, hook=webpush_notification_result_hook)
