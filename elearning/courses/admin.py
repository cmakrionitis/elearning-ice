from django.contrib import admin
from .models import LessonModule, Lesson, TheorySection, Question, AnswerOption, UserLessonProgress, UserAnswer, BigBlueButtonMeeting

# Register your models here.
class TheorySectionInline(admin.TabularInline):
    model = TheorySection
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 2

@admin.register(LessonModule)
class LessonModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]    


@admin.register(Lesson)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [TheorySectionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'order', 'question_type')
    list_filter = ('lesson', 'question_type')
    inlines = [AnswerOptionInline]


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'theory_completed', 'quiz_completed', 'score', 'percentage')


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'question', 'is_correct', 'submitted_at')

@admin.register(BigBlueButtonMeeting)
class BigBlueButtonMeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'meeting_id', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'meeting_id', 'lesson__title')
    readonly_fields = ('created_at',)

    
