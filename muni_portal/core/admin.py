from django.contrib import admin
from muni_portal.core.models import Webhook, ServiceRequest, ServiceRequestAttachment


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("id", "data", "created_at")
    list_filter = ("created_at",)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "collaborator_object_id",
        "user_name",
        "user_surname",
        "user_email_address",
        "description",
        "request_date",
        "status",
        "collaborator_status",
    )
    list_filter = ("request_date", "type", "status")


@admin.register(ServiceRequestAttachment)
class ServiceRequestAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service_request",
        "file",
        "content_type",
        "date_created",
        "exists_on_collaborator",
    )
    list_filter = ("exists_on_collaborator", "date_created")
