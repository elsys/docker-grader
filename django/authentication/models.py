from django.db import models

from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Email address is mandatory!')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        if not password:
            raise ValueError('Password is mandatory!')

        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_active = True

        user.save(using=self._db)
        return user

    def get_from_token(self, token):
        token = token.split('-', maxsplit=1)
        if len(token) != 2:
            return None

        uidb64 = token[0]
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = self.get(pk=uid)
        except (TypeError, ValueError, OverflowError, self.model.DoesNotExist):
            return None

        return user


class User(AbstractBaseUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    email = models.EmailField(unique=True, max_length=255)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_superuser

    def has_module_perms(self, module_name):
        return self.is_superuser

    def has_perm(self, perm):
        return self.is_superuser

    def get_token(self):
        token = default_token_generator.make_token(self)
        uid = urlsafe_base64_encode(force_bytes(self.pk)).decode('utf-8')
        return uid + '-' + token

    def check_token(self, token):
        token = token.split('-', maxsplit=1)
        if len(token) != 2:
            return False

        token = token[1]
        return default_token_generator.check_token(self, token)
