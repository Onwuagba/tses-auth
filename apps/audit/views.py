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
    http_method_names = ['get']
    
    @extend_schema(
        summary="List audit logs",
        description="Get paginated list of audit logs with filtering support"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
