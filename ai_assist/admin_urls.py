from django.conf.urls import url
from .views import AIConfigAPIView

urlpatterns = [
    url(r"^ai_config/?$", AIConfigAPIView.as_view(), name="ai_config_admin"),
]