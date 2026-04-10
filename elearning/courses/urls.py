from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/complete-theory/', views.complete_theory, name='complete_theory'),
    path('course/<slug:slug>/section/<int:section_id>/viewed/', views.mark_course_section_viewed, name='mark_course_section_viewed'),
    path('course/<slug:slug>/quiz/', views.quiz_view, name='quiz'),
    path('course/<slug:slug>/result/', views.quiz_result, name='quiz_result'),
]