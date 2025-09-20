from rest_framework import serializers
from .models import AIConversation, AIMessage

class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ['id', 'content', 'is_user', 'timestamp', 'message_type']

class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = AIConversation
        fields = ['id', 'session_id', 'created_at', 'updated_at', 'is_active', 'messages']

class AIChatSerializer(serializers.Serializer):
    problem_id = serializers.CharField(max_length=32)
    message = serializers.CharField()
    session_id = serializers.CharField(max_length=64, required=False)
    message_type = serializers.ChoiceField(choices=['chat', 'hint', 'solution'], default='chat')

class AIConfigSerializer(serializers.Serializer):
    ai_assist_enabled = serializers.BooleanField()
    openai_api_key = serializers.CharField(max_length=200, allow_blank=True)
    openai_model = serializers.CharField(max_length=50, allow_blank=True)
    openai_base_url = serializers.URLField(allow_blank=True)
    azure_openai_endpoint = serializers.URLField(allow_blank=True)
    azure_openai_key = serializers.CharField(max_length=200, allow_blank=True)
    azure_openai_deployment_name = serializers.CharField(max_length=100, allow_blank=True)