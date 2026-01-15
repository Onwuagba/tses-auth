from django.db import models

class AuditLog(models.Model):
    event = models.CharField(max_length=50)
    email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(null=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
