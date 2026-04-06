from django.contrib import admin
from .models import AuthorProfile

# Register your models here.
@admin.register(AuthorProfile)
class UserAuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('user','user__first_name','user__last_name','user__email','slug','phone','is_active')
