from django.conf.urls import url

from .views import SimditorImageUploadAPIView, SimditorFileUploadAPIView
from .i18n_views import set_language, get_languages

urlpatterns = [
    url(r"^upload_image/?$", SimditorImageUploadAPIView.as_view(), name="upload_image"),
    url(r"^upload_file/?$", SimditorFileUploadAPIView.as_view(), name="upload_file"),
    url(r"^set_language/?$", set_language, name="set_language"),
    url(r"^languages/?$", get_languages, name="get_languages"),
]
