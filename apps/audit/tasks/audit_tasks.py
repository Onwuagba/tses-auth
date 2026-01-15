from celery import shared_task
from ..models import AuditLog

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
    return f"Audit log created: {event} for {email}"