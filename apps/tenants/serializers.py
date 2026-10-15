from rest_framework import serializers

from .models import ApiClient, Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApiClientSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = ApiClient
        fields = ['id', 'tenant', 'name', 'is_active', 'created_at', 'last_used_at', 'api_key']
        read_only_fields = ['id', 'created_at', 'last_used_at']

    def create(self, validated_data):
        tenant = validated_data.get('tenant')
        key = validated_data.pop('api_key', None)
        if key:
            key_hash = ApiClient.hash_key(key)
            validated_data['key_hash'] = key_hash
        else:
            raw_key, key_hash = ApiClient.generate_key(tenant.name)
            validated_data['key_hash'] = key_hash
            self._generated_key = raw_key
        return ApiClient.objects.create(**validated_data)
