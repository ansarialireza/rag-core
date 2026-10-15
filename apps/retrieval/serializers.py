from rest_framework import serializers


class RetrievalRequestSerializer(serializers.Serializer):
    knowledge_base_id = serializers.IntegerField()
    query = serializers.CharField()
    top_k = serializers.IntegerField(min_value=1, max_value=20, required=False, default=5)
    similarity_threshold = serializers.FloatField(required=False, default=0.0)
