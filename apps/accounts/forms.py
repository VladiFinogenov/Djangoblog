from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django_recaptcha.fields import ReCaptchaField
from django.core.exceptions import ValidationError

from .models import CustomUser


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Enter Password Again', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')

    def clean_password2(self):
        # Убедимся, что две записи пароля совпадают

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Сохраним предоставленный пароль в хэшированном формате
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Форма обновления данных пользователя
    """

    username = forms.CharField(max_length=100)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    avatar = forms.ImageField()
    birth_date = forms.DateField(
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'class': 'form-control',
                'placeholder': ('Введите дату рождения'),
                'type': 'date'
            }),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ('avatar', 'username', 'first_name', 'last_name', 'birth_date', 'bio')


class UserRegisterForm(UserCreationForm):
    """
    Переопределенная форма регистрации пользователей
    """

    recaptcha = ReCaptchaField()

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')

    def clean_email(self):
        """
        Проверка email на уникальность
        """

        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and CustomUser.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Такой email уже используется в системе')
        return email

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы регистрации
        """

        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"placeholder": "Введите имя на сайте"})
        self.fields['email'].widget.attrs.update({"placeholder": "Введите логин: email"})
        self.fields['password1'].widget.attrs.update({"placeholder": "Придумайте свой пароль"})
        self.fields['password2'].widget.attrs.update({"placeholder": "Повторите пароль"})


class UserLoginForm(AuthenticationForm):
    """
    Форма авторизации на сайте
    """

    def confirm_login_allowed(self, user):
        if not user.is_verified:
            raise forms.ValidationError(
                'Email is not verified'
            )

    class Meta:
        model = CustomUser
        fields = ['password', 'recaptcha']

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы авторизации
        """

        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Логин пользователя'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль пользователя'
        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['username'].label = 'Log in'
        self.fields['username'].widget.attrs['autofocus'] = False
