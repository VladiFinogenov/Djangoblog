from django.db import IntegrityError
from django.shortcuts import redirect
from social_django.middleware import SocialAuthExceptionMiddleware
from django.contrib import messages


class CustomSocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    """
    Middleware которое обрабатывает ошибку IntegrityError в нескольких вариантов:
        1. При регистрации пользователя через соцсеть, если email уже существует в базе.
        2. При всех остальных случаев.
    """

    def process_exception(self, request, exception):
        if isinstance(exception, IntegrityError):
            if request.path.find('github') != -1 or request.path.find('google') != -1:
                # Обработка ошибки IntegrityError при регистрации пользователя через социальную сеть
                messages.error(
                    request,
                    message='Пользователь с такими данными уже существует. '
                            'Пожалуйста, выберите другие данные для входа.'
                )
                return redirect('/')
            else:
                # Обработка других случаев IntegrityError
                messages.error(
                    request,
                    message='Произошла ошибка IntegrityError. '
                            'Пожалуйста, попробуйте еще раз или обратитесь к администратору.',
                )
                # Дополнительные действия при необходимости
                pass

        return super().process_exception(request, exception)
