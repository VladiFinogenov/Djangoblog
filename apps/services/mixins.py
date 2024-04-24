from django.contrib.auth.mixins import AccessMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse


class AuthorRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_authenticated:
            if (request.user == self.get_object().author) or request.user.is_staff:
                return super().dispatch(request, *args, **kwargs)
            else:
                messages.info(request, 'Изменение статьи доступно только автору!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))
