from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.utils.text import slugify
from django.forms import BaseInlineFormSet
from .models import Supervisor, ContactMessage, SiteFront
from django_ckeditor_5.widgets import CKEditor5Widget
from courses.models import (
    LessonModule, Lesson, TheorySection,
    Question, AnswerOption
)
from account.models import AuthorProfile

class SupervisorCreateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        required=True,
        help_text="Εισάγετε κωδικό για τον νέο χρήστη."
    )

    class Meta:
        model = Supervisor
        fields = ['name', 'email', 'department', 'phone', 'is_active']

    def save(self, commit=True):
        supervisor = super().save(commit=False)
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']

        # Δημιουργία νέου χρήστη
        user = User.objects.create_user(
            username=username,
            password=password,
            email=self.cleaned_data['email']
        )
        supervisor.user = user

        if commit:
            supervisor.save()

        return supervisor
    
class SupervisorEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")

    class Meta:
        model = Supervisor
        fields = ['name', 'email', 'department', 'phone', 'is_active']

    def clean(self):
        cleaned_data = super().clean()
        supervisor = self.instance
        if not hasattr(supervisor, 'user') or supervisor.user is None:
            raise ValidationError("Ο επόπτης δεν έχει συνδεδεμένο User και δεν μπορεί να επεξεργαστεί.")
        return cleaned_data

    def save(self, commit=True):
        supervisor = super().save(commit=False)
        user = supervisor.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.save()

        if commit:
            supervisor.save()
        return supervisor
    
class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Το όνομά σας'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Το email σας'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Θέμα'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Το μήνυμά σας...'}),
        }

class SiteFrontForm(forms.ModelForm):
    class Meta:
        model = SiteFront
        fields = '__all__'
        widgets = {
            'site_name_sort': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'site_name': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LessonModuleForm(forms.ModelForm):
    class Meta:
        model = LessonModule
        fields = [
            'title', 'slug', 'short_description', 'description',
            'hero_image', 'is_active', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'hero_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        title = self.cleaned_data.get('title')
        slug = self.cleaned_data.get('slug')

        if not slug:
            base_slug = slugify(title, allow_unicode=True)
            slug = base_slug
            
        counter = 1

        while LessonModule.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1    

        instance.slug = slug

        if commit:
            instance.save()

        return instance

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'module', 'title', 'slug', 'short_description',
            'description', 'hero_image', 'is_active'
        ]
        widgets = {
            'module': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'hero_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)

        title = self.cleaned_data.get('title')
        slug = self.cleaned_data.get('slug')

        print(slug)

        if not slug:
            base_slug = slugify(title, allow_unicode=True)
            slug = base_slug
            
        counter = 1

        while Lesson.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1    

        instance.slug = slug

        if commit:
            instance.save()

        return instance    

class TheorySectionForm(forms.ModelForm):
    class Meta:
        model = TheorySection
        fields = ['lesson', 'title', 'content', 'image', 'order']

        widgets = {
            'lesson': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['lesson', 'text', 'question_type', 'order']
        widgets = {
            'lesson': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AnswerOptionForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['question','text', 'is_correct']
        widgets = {
            'question': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Κείμενο επιλογής'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AnswerOptionInlineForm(forms.ModelForm):
    class Meta:
        model = AnswerOption
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Κείμενο επιλογής'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }        

class BaseAnswerOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        question_type = self.instance.question_type if self.instance else None

        correct_count = 0
        total_valid_options = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue

            if form.cleaned_data.get('DELETE', False):
                continue

            text = form.cleaned_data.get('text')
            is_correct = form.cleaned_data.get('is_correct', False)

            if text:
                total_valid_options += 1

            if text and is_correct:
                correct_count += 1

        if total_valid_options < 2:
            raise ValidationError("Πρέπει να υπάρχουν τουλάχιστον 2 επιλογές απάντησης.")

        if question_type == 'true_false':
            if total_valid_options != 2:
                raise ValidationError("Η ερώτηση Σωστό / Λάθος πρέπει να έχει ακριβώς 2 επιλογές.")
            if correct_count != 1:
                raise ValidationError("Η ερώτηση Σωστό / Λάθος πρέπει να έχει ακριβώς 1 σωστή επιλογή.")
        elif question_type == 'single':
            if correct_count != 1:
                raise ValidationError("Η πολλαπλής επιλογής ερώτηση πρέπει να έχει ακριβώς 1 σωστή απάντηση.")
        elif question_type == 'multiple':
            if correct_count < 1:
                raise ValidationError("Η checkbox ερώτηση πρέπει να έχει τουλάχιστον 1 σωστή απάντηση.")


AnswerOptionFormSet = inlineformset_factory(
    Question,
    AnswerOption,
    form=AnswerOptionInlineForm,
    formset=BaseAnswerOptionInlineFormSet,
    extra=2,
    can_delete=True
)