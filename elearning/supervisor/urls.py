from django.urls import path
from . import views

app_name = 'supervisor'

urlpatterns = [
    path('', views.dashboard, name='supervisor_dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='supervisor_dashboard'),
    path('create/', views.create_supervisor, name='create_supervisor'),
    path('list/', views.supervisor_list, name='supervisor_list'),
    path('delete/<slug:unique>/', views.delete_supervisor, name='delete_supervisor'),
    path('edit/<slug:unique>/', views.edit_supervisor, name='edit_supervisor'),
    path('change-password/<slug:unique>/', views.change_password, name='change_password'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/change-password/', views.change_own_password, name='change_own_password'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/create/', views.author_create, name='author_create'),
    path('authors/<int:pk>/edit/', views.author_edit, name='author_edit'),
    path('authors/<int:pk>/delete/', views.author_delete, name='author_delete'),
    path('authors/<int:user_id>/change-password/', views.author_change_password, name='author_change_password'),
    path('contact/', views.contact_list, name='contact_list'),
    path('contact/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('delete-message/<int:pk>/', views.delete_message, name='delete_message'),
    path('sitefront/settings/', views.sitefront_settings, name='supervisor_sitefront_settings'),
    # Modules
    path('courses/modules/', views.module_list, name='module_list'),
    path('courses/modules/create/', views.module_create, name='module_create'),
    path('courses/modules/<int:pk>/edit/', views.module_update, name='module_update'),
    path('courses/modules/<int:pk>/delete/', views.module_delete, name='module_delete'),

    # Lessons
    path('courses/lessons/', views.lesson_list, name='lesson_list'),
    path('courses/lessons/create/', views.lesson_create, name='lesson_create'),
    path('courses/lessons/<int:pk>/edit/', views.lesson_update, name='lesson_update'),
    path('courses/lessons/<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),

    # Theory Sections
    path('courses/theory-sections/', views.theory_section_list, name='theory_section_list'),
    path('courses/theory-sections/create/', views.theory_section_create, name='theory_section_create'),
    path('courses/theory-sections/<int:pk>/edit/', views.theory_section_update, name='theory_section_update'),
    path('courses/theory-sections/<int:pk>/delete/', views.theory_section_delete, name='theory_section_delete'),

    # Questions
    path('courses/questions/', views.question_list, name='question_list'),
    path('courses/questions/create/', views.question_create, name='question_create'),
    path('courses/questions/<int:pk>/edit/', views.question_update, name='question_update'),
    path('courses/questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Answer Options
    path('courses/answer-options/', views.answer_option_list, name='answer_option_list'),
    path('courses/answer-options/create/', views.answer_option_create, name='answer_option_create'),
    path('courses/answer-options/<int:pk>/edit/', views.answer_option_update, name='answer_option_update'),
    path('courses/answer-options/<int:pk>/delete/', views.answer_option_delete, name='answer_option_delete'),

    # Progress / Answers
    path('courses/user-progress/', views.user_progress_list, name='user_progress_list'),
    path('courses/user-answers/', views.user_answer_list, name='user_answer_list'),

    # BBB
    path(
        'lesson/<slug:lesson_slug>/bbb/create_new/',
        views.create_bbb_meeting,
        name='create_bbb_meeting'
    ),
    path(
        'bbb/<str:meeting_id>/join/',
        views.join_bbb_meeting,
        name='join_bbb_meeting'
    ),
    path(
        "courses/<slug:lesson_slug>/bbb/create/",
        views.supervisor_create_lesson_meeting,
        name="create_lesson_meeting"
    ),

    path(
        "courses/<slug:lesson_slug>/bbb/links/",
        views.supervisor_lesson_meeting_links,
        name="lesson_meeting_links"
    ),
    path("courses/<slug:lesson_slug>/presentation/",
        views.supervisor_lesson_presentation,
        name="supervisor_lesson_presentation"
    ),
    path(
        "user-progress/<int:progress_id>/answers/",
        views.user_progress_answers,
        name="user_progress_answers"
    ),
]