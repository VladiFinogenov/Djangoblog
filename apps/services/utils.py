import os
from uuid import uuid4
from mysite import settings
from pytils.translit import slugify
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from urllib.parse import urljoin


def unique_slugify(instance, slug):
    """
    Генератор уникальных SLUG для моделей, в случае существования такого SLUG.
    """
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid4().hex[:8]}'
    return unique_slug


def validate_file_size(file: InMemoryUploadedFile) -> None:
    """ Функция проверяет допустимый размер файлов """
    if file.size > 1048576:
        raise ValidationError('File size should be less than 1MB')


class CustomStorage(FileSystemStorage):
    """Custom storage for django_ckeditor_5 images."""

    location = os.path.join(settings.MEDIA_ROOT, "upload")
    base_url = urljoin(settings.MEDIA_URL, "upload/")


