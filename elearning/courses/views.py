from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Lesson, UserLessonProgress, Question, UserAnswer, UserLessonSectionProgress
from elearning.decorators import author_profile_required
from django.http import JsonResponse

# Create your views here.
def get_user_allowed_modules(user):
    author_profile = getattr(user, 'author_profile', None)
    if not author_profile:
        return None
    return author_profile.lesson_modules.all()


@login_required
@author_profile_required
def course_list(request):
    allowed_modules = get_user_allowed_modules(request.user)

    courses = Lesson.objects.filter(
        is_active=True,
        module__in=allowed_modules
    ).distinct()

    progress_map = {
        p.lesson_id: p
        for p in UserLessonProgress.objects.filter(user=request.user)
    }

    return render(request, 'courses/pages/course_list.html', {
        'courses': courses,
        'progress_map': progress_map
    })


@login_required
@author_profile_required
def course_detail(request, slug):
    allowed_modules = get_user_allowed_modules(request.user)

    course = get_object_or_404(
        Lesson.objects.prefetch_related('theory_sections', 'questions'),
        slug=slug,
        is_active=True,
        module__in=allowed_modules
    )

    progress, created = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=course
    )

    sections = list(course.theory_sections.all())
    total_sections = len(sections)

    viewed_section_ids = set(
        UserLessonSectionProgress.objects.filter(
            user=request.user,
            lesson=course,
            viewed=True
        ).values_list('section_id', flat=True)
    )

    viewed_count = len(viewed_section_ids)

    theory_progress_percent = 0
    if total_sections > 0:
        theory_progress_percent = round((viewed_count / total_sections) * 80)

    # Αν έχει δει όλες τις θεωρίες, θεωρείται ολοκληρωμένη η θεωρία
    if total_sections > 0 and viewed_count == total_sections:
        if not progress.theory_completed:
            progress.theory_completed = True
            progress.theory_completed_at = timezone.now()
            progress.save()
    else:
        if progress.theory_completed:
            progress.theory_completed = False
            progress.theory_completed_at = None
            progress.save()

    final_progress_percent = 100 if progress.quiz_completed else theory_progress_percent


    return render(request, 'courses/pages/course_detail.html', {
        'course': course,
        'sections': sections,
        'progress': progress,
        'total_sections': total_sections,
        'viewed_count': viewed_count,
        'viewed_section_ids': viewed_section_ids,
        'theory_progress_percent': theory_progress_percent,
        'final_progress_percent': final_progress_percent,
        'total_questions': course.questions.count(),
    })


@login_required
@author_profile_required
def complete_theory(request, slug):
    allowed_modules = get_user_allowed_modules(request.user)

    course = get_object_or_404(
        Lesson,
        slug=slug,
        is_active=True,
        module__in=allowed_modules
    )

    progress, created = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=course
    )

    progress.theory_completed = True
    progress.theory_completed_at = timezone.now()
    progress.save()

    messages.success(request, 'Ολοκληρώσατε τη θεωρία. Μπορείτε τώρα να ξεκινήσετε το τεστ.')
    return redirect('courses:quiz', slug=course.slug)


@login_required
@author_profile_required
def quiz_view(request, slug):
    allowed_modules = get_user_allowed_modules(request.user)

    course = get_object_or_404(
        Lesson.objects.prefetch_related('questions__options'),
        slug=slug,
        is_active=True,
        module__in=allowed_modules
    )

    progress, created = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=course
    )

    total_sections = course.theory_sections.count()

    viewed_count = UserLessonSectionProgress.objects.filter(
        user=request.user,
        lesson=course,
        viewed=True
    ).count()

    # Τελικός έλεγχος: πρέπει να έχει δει όλες τις θεωρίες
    if total_sections == 0 or viewed_count < total_sections:
        messages.warning(
            request,
            'Πρέπει πρώτα να δείτε όλες τις ενότητες θεωρίας για να ξεκλειδώσει το τεστ.'
        )
        return redirect('elearning:lesson_detail', slug=lesson.slug)

    if not progress.theory_completed:
        progress.theory_completed = True
        progress.theory_completed_at = timezone.now()
        progress.save()

    questions = list(course.questions.all())

    if len(questions) < 3:
        print(len(questions))
        messages.error(request, 'Το τεστ πρέπει να έχει περισσότερες απο 3 ερωτήσεις.')
        return redirect('courses:course_detail', slug=course.slug)

    if request.method == 'POST':
        score = 0

        UserAnswer.objects.filter(user=request.user, lesson=course).delete()

        for question in questions:
            field_name = f"question_{question.id}"

            if question.question_type in ['single', 'true_false']:
                selected = request.POST.get(field_name)
                selected_ids = set()
                if selected:
                    selected_ids.add(int(selected))
            else:
                selected = request.POST.getlist(field_name)
                selected_ids = set(map(int, selected)) if selected else set()

            correct_ids = question.correct_option_ids()
            is_correct = selected_ids == correct_ids

            if is_correct:
                score += 1

            user_answer = UserAnswer.objects.create(
                user=request.user,
                lesson=course,
                question=question,
                is_correct=is_correct
            )

            if selected_ids:
                selected_options = question.options.filter(id__in=selected_ids)
                user_answer.selected_options.set(selected_options)

        total_questions = len(questions)
        percentage = round((score / total_questions) * 100, 2) if total_questions else 0

        progress.quiz_completed = True
        progress.score = score
        progress.total_questions = total_questions
        progress.percentage = percentage
        progress.last_attempt_at = timezone.now()
        progress.save()

        return redirect('courses:quiz_result', slug=course.slug)

    return render(request, 'courses/pages/quiz.html', {
        'course': course,
        'questions': questions,
        'progress': progress,
    })


@login_required
@author_profile_required
def quiz_result(request, slug):
    allowed_modules = get_user_allowed_modules(request.user)

    course = get_object_or_404(
        Lesson,
        slug=slug,
        is_active=True,
        module__in=allowed_modules
    )

    progress = get_object_or_404(
        UserLessonProgress,
        user=request.user,
        lesson=course
    )

    answers = UserAnswer.objects.filter(
        user=request.user,
        lesson=course
    ).select_related('question').prefetch_related('selected_options', 'question__options')

    return render(request, 'courses/pages/quiz_result.html', {
        'course': course,
        'progress': progress,
        'answers': answers,
    })


@login_required
@author_profile_required
@require_POST
def mark_course_section_viewed(request, slug, section_id):
    lesson = get_object_or_404(Lesson, slug=slug, is_active=True)
    section = get_object_or_404(lesson.theory_sections, id=section_id)

    progress, _ = UserLessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson
    )

    section_progress, _ = UserLessonSectionProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        section=section
    )

    if not section_progress.viewed:
        section_progress.viewed = True
        section_progress.viewed_at = timezone.now()
        section_progress.save()

    total_sections = lesson.theory_sections.count()

    viewed_count = UserLessonSectionProgress.objects.filter(
        user=request.user,
        lesson=lesson,
        viewed=True
    ).count()

    theory_progress_percent = 0
    if total_sections > 0:
        theory_progress_percent = round((viewed_count / total_sections) * 80)

    theory_completed = total_sections > 0 and viewed_count == total_sections

    if theory_completed and not progress.theory_completed:
        progress.theory_completed = True
        progress.theory_completed_at = timezone.now()
        progress.save()

    if not theory_completed and progress.theory_completed:
        progress.theory_completed = False
        progress.theory_completed_at = None
        progress.save()

    final_progress_percent = 100 if progress.quiz_completed else theory_progress_percent

    return JsonResponse({
        'success': True,
        'viewed_count': viewed_count,
        'total_sections': total_sections,
        'theory_progress_percent': theory_progress_percent,
        'theory_completed': theory_completed,
        'final_progress_percent': final_progress_percent,
    })
