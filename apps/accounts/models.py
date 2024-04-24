from PIL import Image
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.services.utils import unique_slugify
from django.contrib.auth.models import AbstractBaseUser
from django.core.validators import RegexValidator
from django.utils import timezone
from django.urls import reverse

from .manager import MyUserManager


def profile_images_directory_path(instance: 'CustomUser', filename: str) -> str:

    return 'images/avatars/{user_name}/{filename}'.format(
        user_name=instance.username,
        filename=filename,
    )


class CustomUser(AbstractBaseUser):
    """Модель пользователя"""

    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(
        verbose_name='first name',
        max_length=30,
        null=True,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=30,
        null=True,
        blank=True
    )
    is_online = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_verified = models.BooleanField(
        verbose_name='verified',
        default=False
    )
    verification_uuid = models.UUIDField(
        verbose_name='Unique Verification UUID',
        default=uuid.uuid4
    )
    created = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(
        verbose_name='URL',
        max_length=255,
        blank=True,
        unique=True
    )
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to=profile_images_directory_path,
        default='default-avatar.png',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg'))])
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Информация о себе'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    phone_regex = RegexValidator(
        regex=r'^((\+7)|8)\d{10}$',
        message="Phone number must be entered in the format: '+79999999999' or '89999999999'."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=12,
        null=True,
        blank=True
    )

    objects = MyUserManager()

    # уникальный идентификатор
    USERNAME_FIELD = 'email'
    # список обязательных полей
    REQUIRED_FIELDS = ['username']

    class Meta:
        """
        Сортировка, название таблицы в базе данных
        """
        ordering = ('username',)
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.username)
        super().save(*args, **kwargs)

        # Сохранение аватарки с разрешением 276 x 276
        if self.avatar and (self.avatar.width > 276 or self.avatar.height > 276):
            img = Image.open(self.avatar.path)
            new_img = (276, 276)
            img.thumbnail(new_img)
            img.save(self.avatar.path)

    def get_absolute_url(self):
        """
        Ссылка на профиль
        """
        return reverse('profile_detail', kwargs={'slug': self.slug})

    def get_full_name(self):
        if self.last_name:
            return f"{self.last_name} {self.first_name if self.first_name else self.username}"
        else:
            return self.first_name if self.first_name else self.username

    def __str__(self):
        """
        Возвращение строки
        """
        return self.username

    def has_perm(self, perm, obj=None):
        """
        Метод проверяет у пользователей конкретное разрешение
        """
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        """
        Метод проверяет, является ли пользователь сотрудником
        """
        return self.is_admin

