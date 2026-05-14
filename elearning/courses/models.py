from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field

class LessonModule(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    hero_image = models.ImageField(upload_to='lesson_modules/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def lesson_count(self):
        return self.lessons.filter(is_active=True).count()

class Lesson(models.Model):
    module = models.ForeignKey(
        LessonModule,
        on_delete=models.CASCADE,
        related_name='lessons', null=True, blank=True
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    hero_image = models.ImageField(upload_to='lessons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    @property
    def question_count(self):
        return self.questions.count()
    
class TheorySection(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='theory_sections')
    title = models.CharField(max_length=255)
    content = CKEditor5Field(
        'Περιεχόμενο',
        config_name='extends',
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to='theory_sections/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"  

class Question(models.Model):
    QUESTION_TYPES = (
        ('true_false', 'Σωστό / Λάθος'),
        ('single', 'Checkbox'),
        ('multiple', 'Πολλαπλής επιλογής'),
    )

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.lesson.title} - Ερώτηση {self.order}"

    def clean(self):
        if not self.pk:
            return

        if self.question_type == 'true_false':
            options_count = self.options.count()
            if options_count > 2:
                raise ValidationError("Οι ερωτήσεις Σωστό / Λάθος πρέπει να έχουν μέχρι 2 επιλογές.")

    def correct_option_ids(self):
        return set(self.options.filter(is_correct=True).values_list('id', flat=True))
    
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.text
    
class UserLessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    theory_completed = models.BooleanField(default=False)
    theory_completed_at = models.DateTimeField(blank=True, null=True)
    quiz_completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    percentage = models.FloatField(default=0)
    last_attempt_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"   

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    selected_options = models.ManyToManyField(AnswerOption, blank=True)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson', 'question')

    def __str__(self):
        return f"{self.user.username} - {self.question.id}"    

class UserLessonSectionProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='section_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='section_progress')
    section = models.ForeignKey(TheorySection, on_delete=models.CASCADE, related_name='user_views')
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'lesson', 'section')

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {self.section.title}"     
    
  

