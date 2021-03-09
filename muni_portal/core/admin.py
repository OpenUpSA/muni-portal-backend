from django.contrib import admin
from muni_portal.core.models import Webhook, ServiceRequest


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "created_at")
    list_filter = ("created_at",)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "collaborator_object_id", "user_name", "user_surname", "user_email_address", "description", "request_date", "status")
    list_filter = ("request_date", "type", "status")
