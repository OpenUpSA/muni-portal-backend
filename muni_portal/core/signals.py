import logging

from django.conf import settings
from django_q.tasks import async_task
from pywebpush import webpush, WebPushException
from rest_framework import status

from muni_portal.core.models import WebPushNotification, WebPushSubscription, WebPushNotificationResult

import json

logger = logging.getLogger(__name__)


def queue_send_webpush_notification(notification_id):
    notification = WebPushNotification.objects.get(id=notification_id)
    for subscription in WebPushSubscription.objects.filter(enabled=True):
        result = WebPushNotificationResult(subscription=subscription, notification=notification)
        try:
            response = webpush(
                subscription.subscription_object,
                json.dumps({
                    "type": "notification",
                    "notification": notification.serialize(),
                }),
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.DEFAULT_FROM_EMAIL}"}
            )
            result.status_code = response.status_code
            result.data = response.json() if response.json() else {}
            message = f"Push success: {response.reason}"
        except WebPushException as e:
            if e.response:
                result.status_code = e.response.status_code
                result.data = e.response.json()
                message = f"Push failed: {e.response.reason}\n"
                if e.response.status_code == status.HTTP_410_GONE:
                    message += f"Subscription #{subscription.id} has unsubscribed or expired"
                    subscription.enabled = False
                    subscription.save()
                else:
                    message += f"Response {e.response.text}"
            else:
                message = f"Can't send web push notification to subscription #{subscription.id}, error {e}"
            logger.exception(message)
        except Exception as e:
            message = f"Web push unhandled error for subscription #{subscription.id}, error {e}"
            logger.exception(message)
        result.message = message
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
