from celery import shared_task
from ..models import AuditLog
from apps.accounts.utils.email_utils import mask_email

@shared_task
def write_audit_log(event, email, ip_address=None, user_agent=None, metadata=None):
    """Write audit log entry asynchronously"""
    AuditLog.objects.create(
        event=event,
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {}
    )
    print(f"=== AUDIT LOG ===")
    print(f"Event: {event}")
    print(f"Email: {mask_email(email)}")
    print(f"IP: {ip_address}")
    print(f"User Agent: {user_agent}")
    print(f"Metadata: {metadata}")
    print(f"=================")
    return f"Audit log created: {event} for {email}"