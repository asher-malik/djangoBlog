from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password, username):
        if not email:
            raise ValueError(("The Email must be set"))
        
        if not username:
            raise ValueError('User must have an username')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, username):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.is_verified = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=75, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True, null=True, default='profile_pictures/Default-profile.png', max_length=555)

    date_joined = models.DateTimeField(auto_now_add=True, null=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email
