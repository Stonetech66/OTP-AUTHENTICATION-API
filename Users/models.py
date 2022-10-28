from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission
import uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import auth
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import PermissionDenied

class UserManager(BaseUserManager):

    def create_user(self, password, fullname, phonenumber):
        if not fullname:
            raise TypeError('You must include your Fullname')
        if not phonenumber:
            raise TypeError('You must include your phonenumber')
        if not password:
            raise TypeError('You must include a password')

        
        user=self.model(fullname=fullname, phonenumber=phonenumber)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, phonenumber, fullname, password):
        if not fullname:
            raise TypeError('You must include your Fullname')
        if not phonenumber:
            raise TypeError('You must include your phonenumber')
        if not password:
            raise TypeError('You must include a password')

        user=self.model(fullname=fullname, phonenumber=phonenumber)
        user.set_password(password)
        user.is_superuser=True
        user.is_staff=True
        user.save(using=self.db)
        return user



def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False









class User(AbstractBaseUser, PermissionsMixin):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    fullname=models.CharField(max_length=200)
    phonenumber=PhoneNumberField(unique=True)
    phonenumber_verified=models.BooleanField(default=False)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    date_joined=models.DateTimeField(auto_now_add=True)

    objects=UserManager()

    USERNAME_FIELD= "phonenumber"
    REQUIRED_FIELDS=["fullname"]

    def __str__(self):
        return self.fullname

    def get_tokens(self):
        refresh=RefreshToken.for_user(self)
        return {'access_token':str(refresh.access_token), 'refresh_token':str(refresh)}



    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_module_perms(self, app_label)


class VerificationCode(models.Model):
    code=models.CharField(max_length=6)
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_code")
    date=models.DateTimeField(auto_now_add=True)
    active=models.BooleanField(default=True)