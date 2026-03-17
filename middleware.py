from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils import translation
from django.utils.translation import get_language_from_request
from django.shortcuts import redirect


class LanguageMiddleware:
    """
    Middleware to handle language selection and URL-based language switching.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for language in session
        language = request.session.get('django_language')
        
        # Check for language in URL parameter
        if not language and 'lang' in request.GET:
            lang_code = request.GET.get('lang')
            if lang_code in [lang[0] for lang in settings.LANGUAGES]:
                language = lang_code
                request.session['django_language'] = language
        
        # Check for language in HTTP headers
        if not language:
            language = get_language_from_request(request)
        
        # Activate the language
        if language and language in [lang[0] for lang in settings.LANGUAGES]:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            # Fallback to default language
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        
        response = self.get_response(request)
        return response


def set_language(request):
    """
    View to handle language selection.
    """
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        
        if lang_code and lang_code in [lang[0] for lang in settings.LANGUAGES]:
            # Set language in session
            request.session['django_language'] = lang_code
            
            # Activate language for current request
            translation.activate(lang_code)
            
            # Set language cookie
            response = redirect(next_url)
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
            return response
    
    # Fallback to current page
    return redirect(request.META.get('HTTP_REFERER', '/'))
