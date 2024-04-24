import re
from PIL import Image
from mysite import settings
from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from taggit.models import Tag
from django.views.generic import View
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from urllib.parse import urlparse

from .forms import PostCreateForm, PostUpdateForm, CommentCreateForm, SearchForm
from .models import Comment, Rating, Post, Category
from ..services.mixins import AuthorRequiredMixin


def upload_image(request):
    if request.method == 'POST':
        # Получаем изображение и метаданные из запроса
        uploaded_image = request.FILES['upload']
        previous_url = request.META.get('HTTP_REFERER', None)

        match = re.search(r'/post/(.*?)/update/', previous_url)
        slug = None
        if match:
            slug = match.group(1)
            print(slug)

        file_path = f'/images/upload/{slug}'
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + file_path)
        filename = fs.save(uploaded_image.name, uploaded_image)
        image_url = fs.url(file_path + filename)

        # Возвращаем URL загруженного изображения
        return JsonResponse({'url': image_url})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)

        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.custom.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,
                  'blog/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})


class RatingCreateView(View):
    model = Rating

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('post_id')
        value = int(request.POST.get('value'))
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        ip_address = ip
        user = request.user if request.user.is_authenticated else None

        rating, created = self.model.objects.get_or_create(
            post_id=post_id,
            ip_address=ip_address,
            defaults={'value': value, 'user': user},
        )

        if not created:
            if rating.value == value:
                rating.delete()
                return JsonResponse({'status': 'deleted', 'rating_sum': rating.post.get_sum_rating()})
            else:
                rating.value = value
                rating.user = user
                rating.save()
                return JsonResponse({'status': 'updated', 'rating_sum': rating.post.get_sum_rating()})
        return JsonResponse({'status': 'created', 'rating_sum': rating.post.get_sum_rating()})


class PostByTagListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    tag = None

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['tag'])
        queryset = Post.objects.filter(tags__slug=self.tag.slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Статьи по тегу: {self.tag.name}'
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """
    Представление: для создания комментария к посту.
    """

    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post_id = self.kwargs.get('pk')
        comment.author = self.request.user
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'author': comment.author.username,
                'parent_id': comment.parent_id,
                'time_create': comment.time_create.strftime('%Y-%b-%d %H:%M:%S'),
                'avatar': comment.author.avatar.url,
                'content': comment.content,
                'get_absolute_url': comment.author.get_absolute_url()
            }, status=200)

        return redirect(comment.post.get_absolute_url())

    def handle_no_permission(self):
        return JsonResponse(
            data={'error': 'Необходимо авторизоваться для добавления комментариев'},
            status=400
        )


class CommentDeleteView(LoginRequiredMixin, View):
    """
    Представление: удаление комментария к посту.
    """

    def delete(self, request, pk):
        print('comment_id1', pk)
        comment = get_object_or_404(Comment, id=pk)
        if comment.author != self.request.user:
            messages.info(request, 'удаление комментария доступно только автору!')

        comment.delete()
        messages.info(request, 'Комментарий успешно удален!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('home')))
    #
    # def get_success_url(self):
    #     return reverse_lazy('comment_detail', kwargs={'pk': self.object.post.pk})


class PostUpdateView(AuthorRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Представление: обновления материала на сайте
    """
    model = Post
    template_name = 'blog/post_update.html'
    context_object_name = 'post'
    form_class = PostUpdateForm
    login_url = 'home'
    success_message = 'Запись была успешно обновлена!'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title}'
        return context

    def form_valid(self, form):
        # form.instance.updater = self.request.user
        form.save()
        return super().form_valid(form)


class PostCreateView(LoginRequiredMixin, CreateView):
    """
    Представление: создание материалов на сайте
    """
    model = Post
    template_name = 'blog/post_create.html'
    form_class = PostCreateForm
    login_url = 'home'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление статьи на сайт'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)


class PostFromCategory(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    category = None
    paginate_by = 5
    queryset = Post.custom.all()

    def get_queryset(self):
        self.category = Category.objects.get(slug=self.kwargs['slug'])
        queryset = Post.objects.filter(category__slug=self.category.slug)
        if not queryset:
            sub_cat = Category.objects.filter(parent=self.category)
            queryset = Post.objects.filter(category__in=sub_cat)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Записи из категории: {self.category.title}'
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 5
    queryset = Post.custom.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список постов'
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    queryset = Post.custom.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['form'] = CommentCreateForm

        return context
