from django.db import models

class AuditLog(models.Model):
    EVENT_CHOICES = [
        ('OTP_REQUESTED', 'OTP Requested'),
        ('OTP_VERIFIED', 'OTP Verified'),
        ('OTP_FAILED', 'OTP Failed'),
        ('OTP_LOCKED', 'OTP Locked'),
    ]
    
    event = models.CharField(max_length=20, choices=EVENT_CHOICES)
    email = models.EmailField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.event} - {self.email} - {self.created_at}"
