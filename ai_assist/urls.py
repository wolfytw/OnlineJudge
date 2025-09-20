from django.conf.urls import url
from .views import (
    AIChatAPIView, AIConversationListAPIView, 
    AIConversationDetailAPIView, AIConfigAPIView, AIUsageStatsAPIView
)

urlpatterns = [
    url(r"^chat/?$", AIChatAPIView.as_view(), name="ai_chat"),
    url(r"^conversations/?$", AIConversationListAPIView.as_view(), name="ai_conversations"),
    url(r"^conversations/(?P<session_id>[^/]+)/?$", AIConversationDetailAPIView.as_view(), name="ai_conversation_detail"),
    url(r"^usage/?$", AIUsageStatsAPIView.as_view(), name="ai_usage_stats"),
]