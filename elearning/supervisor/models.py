from django.db import models
from django.contrib.auth.models import User  # Εισάγουμε το User model
from django.templatetags.static import static
import uuid


# Create your models here.
class Supervisor(models.Model):
    # Σύνδεση με User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')

    # Πρόσθετα πεδία για τον εποπτη
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    unique = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.name} ({self.department})"
    
class ContactMessage(models.Model):
    STATUS = (
        (0, 'Unread'),
        (1, 'Read'),
    )

    name = models.CharField(max_length=150, verbose_name="Ονοματεπώνυμο")
    email = models.EmailField(verbose_name="Email")
    subject = models.CharField(max_length=255, verbose_name="Θέμα")
    message = models.TextField(verbose_name="Μήνυμα")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ημ/νία")
    notification_admin = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS, default=0, verbose_name="Κατάσταση")
    unique = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

class SiteFront(models.Model):
    site_name = models.CharField(
        max_length=100,
        verbose_name="Όνομα Ιστοσελίδας",
        default="My Website"
    )

    site_name_sort = models.CharField(
        max_length=100,
        verbose_name="Όνομα Ιστοσελίδας Sort",
        default="My Website Sort Name"
    )

    description = models.TextField(
        verbose_name="Περιγραφή",
        blank=True,
        null=True,
        default="Καλώς ήρθατε στην ιστοσελίδα μας!"
    )
    main_image = models.ImageField(
        upload_to='sitefront/',
        blank=True,
        null=True,
        verbose_name="Κύρια Εικόνα",
        help_text="Εικόνα hero ή banner"
    )
    favicon = models.ImageField(
        upload_to='sitefront/favicon/',
        blank=True,
        null=True,
        verbose_name="Favicon"
    )
    facebook = models.URLField(blank=True, null=True, default="https://facebook.com")
    instagram = models.URLField(blank=True, null=True, default="https://instagram.com")
    twitter = models.URLField(blank=True, null=True, default="https://twitter.com")
    linkedin = models.URLField(blank=True, null=True, default="https://linkedin.com")
    email = models.EmailField(blank=True, null=True, default="info@example.com")
    phone = models.CharField(max_length=20, blank=True, null=True, default="+30 210 1234567")
    address = models.CharField(max_length=255, blank=True, null=True, default="Αθήνα, Ελλάδα")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ρύθμιση Ιστοσελίδας"
        verbose_name_plural = "Ρυθμίσεις Ιστοσελίδας"

    def __str__(self):
        return self.site_name or "Ρυθμίσεις Ιστοσελίδας"

    # ✅ Επιστρέφει default εικόνες αν λείπουν
    def get_main_image_url(self):
        if self.main_image and hasattr(self.main_image, 'url'):
            return self.main_image.url
        return static('AdminLte-3-2-0/dist/img/AdminLTELogo.png')  # βάλε default hero

    def get_favicon_url(self):
        if self.favicon and hasattr(self.favicon, 'url'):
            return self.favicon.url
        return static('AdminLte-3-2-0/dist/img/AdminLTELogo.png')  # βάλε default favicon
