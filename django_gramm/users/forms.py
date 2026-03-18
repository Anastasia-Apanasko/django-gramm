from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'loginUsername',
                'placeholder': 'Username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'loginPassword',
                'placeholder': 'Password'
            }
        )
    )


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.email:
            self.fields['email'].disabled = True

    def clean_email(self):
        if self.fields['email'].disabled:
            return self.instance.email

        data = self.cleaned_data['email']
        qs = User.objects.exclude(pk=self.instance.pk).filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.date_of_birth:
            self.fields['date_of_birth'].disabled = True


class SignupForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        help_text='',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'floatingUsername',
                'placeholder': 'Username'
            }
        )
    )
    email = forms.EmailField(
        max_length=200,
        help_text='',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'id': 'floatingInput',
                'placeholder': 'name@example.com'
            }
        )
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        help_text='',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'floatingPassword',
                'placeholder': 'Password'
            }
        )
    )
    password2 = forms.CharField(
        label='Confirm Password',
        strip=False,
        help_text='',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'floatingConfirmPassword',
                'placeholder': 'Confirm Password'
            }
        )
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
