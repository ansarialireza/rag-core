from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ApiClient, Tenant
from .serializers import ApiClientSerializer, TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tenant.objects.filter(id=self.request.tenant.id)


class ApiClientViewSet(viewsets.ModelViewSet):
    serializer_class = ApiClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApiClient.objects.filter(tenant=self.request.tenant)

    @action(detail=False, methods=['post'])
    def create_with_key(self, request):
        serializer = self.get_serializer(data={**request.data, 'tenant': request.tenant.id})
        serializer.is_valid(raise_exception=True)
        api_client = serializer.save()
        response = ApiClientSerializer(api_client).data
        if hasattr(serializer, '_generated_key'):
            response['api_key'] = serializer._generated_key
        return Response(response)
