from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Supervisor

# Register your models here.
class SupervisorInline(admin.StackedInline):
    model = Supervisor
    can_delete = False
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [SupervisorInline]


@admin.register(Supervisor)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'department', 'phone', 'is_active')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)