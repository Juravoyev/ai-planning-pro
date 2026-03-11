from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email manzilingiz'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Foydalanuvchi nomi'
        })
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ismingiz'
        })
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Familiyangiz'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Parol'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Parolni tasdiqlang'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email manzilingiz'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Parolingiz'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'bio', 'avatar', 'work_start_time', 'work_end_time', 'preferred_language')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'work_start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'work_end_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'preferred_language': forms.Select(attrs={'class': 'form-input'}),
        }
