from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_registration.auth_token_managers import AbstractAuthTokenManager, AuthToken
from typing import Type, Sequence, Dict


class RestFrameworkAuthJWTTokenManager(AbstractAuthTokenManager):

    def get_authentication_class(self) -> Type[BaseAuthentication]:
        return JWTAuthentication

    def get_app_names(self) -> Sequence[str]:
        return [
            "rest_framework_simplejwt",
        ]

    def provide_token(self, user: settings.AUTH_USER_MODEL) -> Dict[str, str]:
        refresh_token = RefreshToken.for_user(user)
        return {
            "access": str(refresh_token.access_token),
            "refresh": str(refresh_token)
        }

    def revoke_token(self, user: settings.AUTH_USER_MODEL, *args, **kwargs) -> None:
        for token in OutstandingToken.objects.filter(user=user):
            token = RefreshToken(token.token)
            token.blacklist()
