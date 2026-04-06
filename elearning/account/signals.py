from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AuthorProfile


#@receiver(post_save, sender=User)
#def create_author_profile(sender, instance, created, **kwargs):
#    if created:
#        AuthorProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_author_profile(sender, instance, **kwargs):
    if hasattr(instance, 'author_profile'):
        instance.author_profile.save()