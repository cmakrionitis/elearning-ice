from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
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
    
