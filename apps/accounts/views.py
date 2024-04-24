from django.views.generic import DetailView, UpdateView
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import Http404
from django.utils import timezone
from datetime import timedelta
from apps.blog.models import Post

from .forms import UserUpdateForm
from .forms import UserRegisterForm, UserLoginForm
from .models import CustomUser
from .tasks import update_user_status


def verify(request, uuid):
    try:
        user = CustomUser.objects.get(verification_uuid=uuid, is_verified=False)
        if user.created < timezone.now() - timedelta(hours=24):
            user.delete()
            return render(request, 'accounts/error_activate.html')
    except CustomUser.DoesNotExist:
        raise Http404("User does not exist or is already verified")

    user.is_verified = True
    user.save()
    return render(request, 'accounts/activate.html')


class UserLogoutView(LogoutView):
    """
    Выход с сайта
    """
    next_page = 'home'

    def dispatch(self, request, *args, **kwargs):

        user_id = self.request.user.id
        # Помечаем пользователя как оффлайн перед выходом
        update_user_status.delay(user_id, False)

        return super().dispatch(request, *args, **kwargs)


class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    Представление регистрации на сайте с формой регистрации
    """
    form_class = UserRegisterForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/user_register.html'
    success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context


class UserLoginView(SuccessMessageMixin, LoginView):
    """
    Авторизация на сайте
    """
    form_class = UserLoginForm
    template_name = 'accounts/user_login.html'
    next_page = 'home'
    success_message = 'Добро пожаловать на сайт!'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context

    def form_valid(self, form):
        form_result = super().form_valid(form)
        user = form.get_user()
        # Вызов функции для обновления статуса пользователя
        user.is_online = True
        user.save()
        update_user_status.delay(user.pk, True)
        return form_result


class ProfileDetailView(DetailView):
    """
    Представление для просмотра профиля
    """
    model = CustomUser
    context_object_name = 'profile'
    template_name = 'accounts/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Профиль пользователя: {self.request.user.username}'
        author_posts = Post.custom.filter(author=self.object)

        context['author_posts'] = author_posts

        return context


class ProfileUpdateView(UpdateView):
    """
    Представление для редактирования профиля
    """
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'accounts/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.POST:
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context

    def form_valid(self, form):
        user_form = UserUpdateForm(self.request.POST, instance=self.request.user)
        if user_form.is_valid():
            user_form.save()
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('profile_detail', kwargs={'slug': self.request.user.slug})
