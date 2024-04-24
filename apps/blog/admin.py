from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from .models import Category, Post
from .models import Comment, Rating


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """
    Админ-панель модели рейтинга
    """
    pass


@admin.register(Comment)
class CommentAdminPage(DjangoMpttAdmin):
    """
    Админ-панель модели комментариев
    """
    pass


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    """
    Админ-панель модели категорий
    """
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Админ-панель модели записей
    """

    # Предзаполняем поле slug данными вводимыми из title
    prepopulated_fields = {'slug': ('title',)}
