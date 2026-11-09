"""Authentication backend allowing login with either username or email."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from .throttle import is_locked, register_failure, reset_failures


class EmailOrUsernameBackend(ModelBackend):
    """Authenticate against the username first, then the (unique) email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        ip = request.META.get("REMOTE_ADDR", "") if request is not None else ""
        if is_locked(username, ip):
            return None

        user = UserModel.objects.filter(username__iexact=username).first()
        if user is None:
            user = UserModel.objects.filter(Q(email__iexact=username)).first()

        if user is None:
            UserModel().set_password(password)
            register_failure(username, ip)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            reset_failures(username, ip)
            return user

        register_failure(username, ip)
        return None
