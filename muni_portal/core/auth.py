from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token
from rest_registration.auth_token_managers import AbstractAuthTokenManager, AuthToken
from typing import Type, Sequence


class RestFrameworkAuthJWTTokenManager(AbstractAuthTokenManager):

    def get_authentication_class(self) -> Type[BaseAuthentication]:
        return JWTAuthentication

    def get_app_names(self) -> Sequence[str]:
        return [
            'rest_framework_simplejwt',
        ]

    def provide_token(self, user: settings.AUTH_USER_MODEL) -> AuthToken:
        return Token.for_user(user)
