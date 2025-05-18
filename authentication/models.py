from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('Le numéro de téléphone doit être défini'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None  # Supprime le champ username par défaut
    phone_number = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()  # Utilise le manager personnalisé

    def __str__(self):
        return self.phone_number