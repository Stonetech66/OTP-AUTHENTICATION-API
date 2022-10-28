from django.conf import settings
from django.utils import timezone
access_token_name=settings.ACCESS_TOKEN_NAME
refresh_token_name=settings.REFRESH_TOKEN_NAME
access_token_expiration=timezone.now()+settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
refresh_token_expiration=timezone.now()+settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
cookie_secure=settings.COOKIE_SECURE
def set_access_cookie(response, user):
    response.set_cookie(
        access_token_name,
        user.get_tokens()['access_token'],
        expires=access_token_expiration,
        secure=cookie_secure,
        httponly=True,

    )

def set_refresh_cookie(request, user):
        request.set_cookie(
        refresh_token_name,
        user.get_tokens()['refresh_token'],
        expires=refresh_token_expiration,
        secure=cookie_secure,
        httponly=True,

    )

def delete_cookies(response):
    response.delete_cookie(refresh_token_name)
    response.delete_cookie(access_token_name)