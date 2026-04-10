from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db import transaction
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import FileExtensionValidator
from .models import AuthorProfile
from unidecode import unidecode
from courses.models import LessonModule

class AuthorPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Παλαιός Κωδικός'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Νέος Κωδικός'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Επιβεβαίωση Νέου Κωδικού'}))

class AuthorProfileSupervisorForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Όνομα'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Επώνυμο'
        })
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Όνομα χρήστη'
        })
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )

    lesson_modules = forms.ModelMultipleChoiceField(
        queryset=LessonModule.objects.filter(is_active=True).order_by('order', 'title'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Ενότητες μαθημάτων'
    )

    class Meta:
        model = AuthorProfile
        fields = [
            'phone',
            'date_birth',
            'address',
            'city',
            'country',
            'zip_code',
            'is_active',
            'can_take_lessons',
            'lesson_modules',
        ]
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Τηλέφωνο'
            }),
            'date_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Διεύθυνση'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Πόλη'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Χώρα'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Τ.Κ.'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'can_take_lessons': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

        if self.instance and self.instance.pk:
            self.fields['lesson_modules'].initial = self.instance.lesson_modules.all()

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        if user:
            user.username = self.cleaned_data.get('username')
            user.email = self.cleaned_data.get('email')
            user.first_name = self.cleaned_data.get('first_name')
            user.last_name = self.cleaned_data.get('last_name')
            user.save()

            base_slug = slugify(
                f"elearning-ice-{unidecode(user.first_name)}-{unidecode(user.last_name)}",
                allow_unicode=False
            )
            if not base_slug:
                base_slug = slugify(unidecode(user.username), allow_unicode=False)
        else:
            base_slug = slugify("elearning-ice-author", allow_unicode=False)

        slug = base_slug
        counter = 1

        while AuthorProfile.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        instance.slug = slug

        if commit:
            instance.save()
            instance.lesson_modules.set(self.cleaned_data.get('lesson_modules'))
            self.save_m2m()

        return instance
    
class QuickAuthorCreateForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Όνομα'
        })
    )


    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Όνομα',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Όνομα'
        })
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Επώνυμο',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Επώνυμο'
        })
    )

    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )

    lesson_modules = forms.ModelMultipleChoiceField(
        queryset=LessonModule.objects.filter(is_active=True).order_by('order', 'title'),
        required=False,
        label='Ενότητες μαθημάτων',
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = AuthorProfile
        fields = ['lesson_modules']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Υπάρχει ήδη χρήστης με αυτό το email.')

        return email

    def _generate_unique_username(self, email, first_name='', last_name=''):
        base = email

        if not base:
            base = slugify(
                unidecode(f"{first_name}-{last_name}"),
                allow_unicode=False
            ).replace('-', '')

        if not base:
            base = slugify(unidecode(email.split('@')[0]), allow_unicode=False)

        if not base:
            base = "author"

        username = base
        counter = 1

        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1

        return username

    def _generate_unique_slug(self, instance, first_name='', last_name='', email=''):
        base_slug = slugify(
            f"elearning-ice-{unidecode(first_name)}-{unidecode(last_name)}",
            allow_unicode=False
        )

        if not base_slug:
            base_slug = slugify(unidecode(email.split('@')[0]), allow_unicode=False)

        if not base_slug:
            base_slug = "elearning-ice-author"

        slug = base_slug
        counter = 1

        while AuthorProfile.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    @transaction.atomic
    def save(self, commit=True):
        first_name = self.cleaned_data['first_name'].strip()
        last_name = self.cleaned_data['last_name'].strip()
        email = self.cleaned_data['email'].strip().lower()
        lesson_modules = self.cleaned_data.get('lesson_modules')

        default_password = f"!#{email}-ice2000$!"
        username = self._generate_unique_username(email, first_name, last_name)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=default_password,
            first_name=first_name,
            last_name=last_name
        )

        instance = super().save(commit=False)
        instance.user = user
        instance.slug = self._generate_unique_slug(
            instance=instance,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        if commit:
            instance.save()
            instance.lesson_modules.set(lesson_modules)
            self.save_m2m()

        return instance