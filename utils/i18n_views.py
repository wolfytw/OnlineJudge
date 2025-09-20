from django.http import JsonResponse
from django.utils import translation
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

@csrf_exempt
@require_http_methods(["POST", "GET"])
def set_language(request):
    """
    Set user's preferred language
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            language = data.get('language', 'en')
        except (json.JSONDecodeError, KeyError):
            language = request.POST.get('language', 'en')
    else:
        language = request.GET.get('language', 'en')
    
    # Validate language
    available_languages = [lang[0] for lang in settings.LANGUAGES]
    if language not in available_languages:
        return JsonResponse({
            'error': 'Invalid language code',
            'available_languages': available_languages
        }, status=400)
    
    # Activate the language
    translation.activate(language)
    
    # Set language in session
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    
    return JsonResponse({
        'message': _('Language changed successfully'),
        'language': language,
        'available_languages': dict(settings.LANGUAGES)
    })

@require_http_methods(["GET"])
def get_languages(request):
    """
    Get available languages
    """
    current_language = translation.get_language()
    
    return JsonResponse({
        'current_language': current_language,
        'available_languages': dict(settings.LANGUAGES),
        'languages': [
            {
                'code': lang[0],
                'name': lang[1],
                'is_current': lang[0] == current_language
            } for lang in settings.LANGUAGES
        ]
    })