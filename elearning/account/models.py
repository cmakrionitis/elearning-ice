from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from courses.models import LessonModule


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    slug = models.SlugField(unique=True, blank=True, null=True)

    phone = models.CharField(max_length=30, blank=True, null=True)
    date_birth = models.DateField(blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    can_take_lessons = models.BooleanField(default=True)

    lesson_modules = models.ManyToManyField(
        LessonModule,
        blank=True,
        related_name='author_profiles',
        verbose_name='Ενότητες μαθημάτων'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name', 'user__username']

    def __str__(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        return full_name or self.user.username

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(
                f"{self.user.first_name}-{self.user.last_name}"
            ) or slugify(self.user.username)

            slug = base
            counter = 1
            while AuthorProfile.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)