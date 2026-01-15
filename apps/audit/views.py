from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema
from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters.audit_filters import AuditLogFilter

class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = AuditLogFilter
    
    @extend_schema(
        summary="List audit logs",
        description="Get paginated list of audit logs with filtering support",
        parameters=[
            {'name': 'email', 'in': 'query', 'description': 'Filter by email'},
            {'name': 'event', 'in': 'query', 'description': 'Filter by event type'},
            {'name': 'from_date', 'in': 'query', 'description': 'Filter from date (ISO format)'},
            {'name': 'to_date', 'in': 'query', 'description': 'Filter to date (ISO format)'},
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
