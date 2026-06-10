
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('admin', 'Admin'),
    ]
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # New profile fields
    profile_picture = models.ImageField(
        upload_to='profiles/', null=True, blank=True
    )
    bio = models.TextField(max_length=300, blank=True)
    address = models.CharField(max_length=300, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    facebook_url = models.URLField(blank=True)
    is_phone_verified = models.BooleanField(default=False)

    def get_profile_picture(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None  # will use default avatar in template
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

import random
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=5)

    @classmethod
    def generate(cls, user):
        cls.objects.filter(user=user).delete()  # remove old OTPs
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, code=code)