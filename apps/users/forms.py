from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User
from .widgets import PhoneMaskInput


class UserAdminCreationForm(UserCreationForm):
    """
    Форма для создания пользователя в админке
    """
    phone = forms.CharField(
        required=False,
        widget=PhoneMaskInput(),
        label="Телефон"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'password1', 'password2')


class UserAdminChangeForm(UserChangeForm):
    """
    Форма для редактирования пользователя в админке
    """
    phone = forms.CharField(
        required=False,
        widget=PhoneMaskInput(),
        label="Телефон"
    )
    
    class Meta:
        model = User
        fields = '__all__'