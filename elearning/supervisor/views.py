import uuid
import mimetypes
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, JsonResponse
from .models import Supervisor, ContactMessage, SiteFront
from .forms import SupervisorCreateForm, SupervisorEditForm, SiteFrontForm, LessonModuleForm, LessonForm, TheorySectionForm,QuestionForm, AnswerOptionForm, BaseAnswerOptionInlineFormSet, AnswerOptionFormSet
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from account.forms import AuthorProfileSupervisorForm, AuthorPasswordChangeForm, QuickAuthorCreateForm
from account.models import AuthorProfile
from courses.models import (
    LessonModule, Lesson, TheorySection,
    Question, AnswerOption, UserLessonProgress, UserAnswer
)


# Create your views here.
def is_supervisor(user):
    return user.is_authenticated and user.is_staff

def login_view(request):
    if request.user.is_authenticated:
        # Αν είναι ήδη συνδεδεμένος και έχει δικαιώματα, πάει στο dashboard
        if request.user.is_superuser or hasattr(request.user, 'supervisor_profile'):
            return redirect('supervisor:supervisor_dashboard')
        else:
            return HttpResponseForbidden("Δεν έχετε πρόσβαση.")

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Έλεγχος αν είναι supervisor ή superuser
            if user.is_superuser or hasattr(user, 'supervisor_profile'):
                login(request, user)
                return redirect('supervisor:supervisor_dashboard')
            else:
                messages.error(request, "Δεν έχετε δικαίωμα πρόσβασης.")
        else:
            messages.error(request, "Λάθος όνομα χρήστη ή κωδικός.")

    return render(request, 'supervisor/login.html')

@login_required
@user_passes_test(is_supervisor)
def logout_view(request):
    logout(request)
    return redirect('supervisor:login')

@login_required
@user_passes_test(is_supervisor)
def dashboard(request):
    quick_author_form = QuickAuthorCreateForm()

    if request.method == 'POST' and request.POST.get('form_type') == 'quick_author_create':
        quick_author_form = QuickAuthorCreateForm(request.POST)

        if quick_author_form.is_valid():
            author = quick_author_form.save()

            messages.success(
                request,
                f'Ο author δημιουργήθηκε επιτυχώς. Username: {author.user.username} | Password: !#{author.user.email}-ice2000$!'
            )
            return redirect('supervisor:supervisor_dashboard')
        else:
            messages.error(request, 'Υπάρχουν σφάλματα στη φόρμα δημιουργίας author.')

    author_profiles = AuthorProfile.objects.select_related('user').prefetch_related('lesson_modules').order_by('-id')

    # Αν δεν είναι superuser ή supervisor -> απαγόρευση
    user = request.user
    if not (user.is_superuser or hasattr(user, 'supervisor_profile')):
        return HttpResponseForbidden("Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη σελίδα.")

    context = {
        # Basic counts
        'modules_count': LessonModule.objects.count(),
        'lessons_count': Lesson.objects.count(),
        'theory_count': TheorySection.objects.count(),
        'questions_count': Question.objects.count(),
        'answers_count': AnswerOption.objects.count(),

        # Users activity
        'progress_count': UserLessonProgress.objects.count(),
        'user_answers_count': UserAnswer.objects.count(),

        # extra stats
        'completed_lessons': UserLessonProgress.objects.filter(quiz_completed=True).count(),
        'theory_completed': UserLessonProgress.objects.filter(theory_completed=True).count(),

        'supervisors_count': Supervisor.objects.count(),
        'author_profiles_count': AuthorProfile.objects.count(),
        'author_profiles': author_profiles,
        'quick_author_form': quick_author_form,
    }
    return render(request, "supervisor/pages/dashboard.html", context)

@login_required
@user_passes_test(is_supervisor)
def create_supervisor(request):
    if not (request.user.is_superuser or hasattr(request.user, 'supervisor_profile')):
        return HttpResponseForbidden("Δεν έχετε δικαίωμα πρόσβασης.")

    if request.method == 'POST':
        form = SupervisorCreateForm(request.POST)
        if form.is_valid():
            supervisor = form.save()
            return JsonResponse({'success': True, 'message': f'Ο επόπτης {supervisor.name} δημιουργήθηκε επιτυχώς!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = SupervisorCreateForm()
    return render(request, 'supervisor/pages/supervisor_create.html', {'form': form})

@login_required
@user_passes_test(is_supervisor)
def supervisor_list(request):
    if not (request.user.is_superuser or hasattr(request.user, 'supervisor_profile')):
        return HttpResponseForbidden("Δεν έχετε δικαίωμα πρόσβασης.")
    
    supervisors = Supervisor.objects.select_related('user').all()
    return render(request, 'supervisor/pages/supervisor_list.html', {'supervisors': supervisors})

@login_required
@user_passes_test(is_supervisor)
def delete_supervisor(request, unique):
    if not (request.user.is_superuser or hasattr(request.user, 'supervisor_profile')):
        return HttpResponseForbidden("Δεν έχετε δικαίωμα πρόσβασης.")
    
    supervisor = get_object_or_404(Supervisor, unique=unique)
    supervisor.user.delete()  # διαγράφει και το σχετικό User
    return JsonResponse({'success': True, 'message': 'Ο επόπτης διαγράφηκε επιτυχώς!'})

@login_required
@user_passes_test(is_supervisor)
def edit_supervisor(request, unique):
    if not (request.user.is_superuser or hasattr(request.user, 'supervisor_profile')):
        return HttpResponseForbidden("Δεν έχετε δικαίωμα πρόσβασης.")

    supervisor = get_object_or_404(Supervisor, unique=unique)
    if request.method == 'POST':
        form = SupervisorEditForm(request.POST, instance=supervisor)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Ο επόπτης ενημερώθηκε επιτυχώς!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = SupervisorEditForm(instance=supervisor)
        data = {
            'username': supervisor.user.username,
            'name': supervisor.name,
            'email': supervisor.email,
            'department': supervisor.department,
            'phone': supervisor.phone,
            'is_active': supervisor.is_active,
        }
        return JsonResponse({'success': True, 'data': data})
    
@login_required
@user_passes_test(is_supervisor)
def change_password(request, unique):
    if not (request.user.is_superuser or hasattr(request.user, 'supervisor_profile')):
        return HttpResponseForbidden("Δεν έχετε δικαίωμα πρόσβασης.")

    supervisor = get_object_or_404(Supervisor, unique=unique)
    user = supervisor.user

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if not new_password or len(new_password) < 6:
            return JsonResponse({'success': False, 'error': 'Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες.'})
        user.set_password(new_password)
        user.save()
        return JsonResponse({'success': True, 'message': f'Ο κωδικός του {user.username} ενημερώθηκε επιτυχώς.'}) 

@login_required
@user_passes_test(is_supervisor)
def change_own_password(request):
    user = request.user
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if not new_password or len(new_password) < 6:
            return JsonResponse({'success': False, 'error': 'Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες.'})
        user.set_password(new_password)
        user.save()
        return JsonResponse({'success': True, 'message': 'Ο κωδικός ενημερώθηκε επιτυχώς.'})       

@login_required
@user_passes_test(is_supervisor)
def profile_view(request):
    # Παίρνει το συνδεδεμένο χρήστη
    user = request.user
    supervisor = getattr(user, 'supervisor_profile', None)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        department = request.POST.get('department')
        phone = request.POST.get('phone')

        user.email = email
        user.save()

        if supervisor:
            supervisor.name = name
            supervisor.email = email
            supervisor.department = department
            supervisor.phone = phone
            supervisor.save()

        return JsonResponse({'success': True, 'message': 'Το προφίλ ενημερώθηκε επιτυχώς.'})

    return render(request, 'supervisor/pages/profile.html', {'user': user, 'supervisor': supervisor})

@login_required
@user_passes_test(is_supervisor)
def author_list(request):
    authors = AuthorProfile.objects.select_related('user')
    return render(request, 'supervisor/pages/account_list.html', {'authors': authors})

@login_required
@user_passes_test(is_supervisor)
def author_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        form = AuthorProfileSupervisorForm(
            request.POST,
            request.FILES
        )

        errors = {}

        if not username:
            errors['username'] = ['Το username είναι υποχρεωτικό.']
        elif User.objects.filter(username=username).exists():
            errors['username'] = ['Υπάρχει ήδη χρήστης με αυτό το username.']

        if not password1:
            errors['password1'] = ['Το password είναι υποχρεωτικό.']

        if password1 != password2:
            errors['password1'] = ['Ο κωδικός και η επιβεβαίωση δεν ταιριάζουν.']
            errors['password2'] = ['Ο κωδικός και η επιβεβαίωση δεν ταιριάζουν.']

        if not email:
            errors['email'] = ['Το email είναι υποχρεωτικό.']
        elif User.objects.filter(email__iexact=email).exists():
            errors['email'] = ['Υπάρχει ήδη χρήστης με αυτό το email.']

        if not form.is_valid():
            for field, field_errors in form.errors.items():
                errors[field] = field_errors

        if errors:
            return JsonResponse({
                'success': False,
                'errors': errors
            }, status=400)

        # Δημιουργία user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=True
        )

        # Αν υπάρχει signal που φτιάχνει AuthorProfile, το πιάνουμε εδώ.
        author, created = AuthorProfile.objects.get_or_create(user=user)

        # Ξαναδένουμε το form πάνω στο υπάρχον author instance
        form = AuthorProfileSupervisorForm(
            request.POST,
            request.FILES,
            instance=author
        )

        if form.is_valid():
            author = form.save(user=user)

        return JsonResponse({
            'success': True,
            'message': 'Ο συγγραφέας δημιουργήθηκε επιτυχώς.',
            'author_id': author.id,
        })

    form = AuthorProfileSupervisorForm()

    return render(request, 'supervisor/pages/account_create.html', {
        'form': form,
    })

@login_required
@user_passes_test(is_supervisor)
def author_edit(request, pk):
    author = get_object_or_404(AuthorProfile, pk=pk)

    if request.method == 'POST':
        form = AuthorProfileSupervisorForm(
            request.POST,
            request.FILES,
            instance=author,
            user=author.user
        )

        if form.is_valid():
            author = form.save(user=author.user)
            author.save()

            return JsonResponse({
                'updated': True,
                'message': 'Το προφίλ ενημερώθηκε επιτυχώς.'
            })

        return JsonResponse({
            'updated': False,
            'errors': form.errors
        }, status=400)

    form = AuthorProfileSupervisorForm(
        instance=author,
        user=author.user
    )

    return render(request, 'supervisor/pages/account_edit.html', {
        'form': form,
        'author': author
    })

@login_required
@user_passes_test(is_supervisor)
def author_delete(request, pk):
    author = get_object_or_404(AuthorProfile, pk=pk)
    user = author.user
    author.delete()
    user.delete()
    messages.success(request, 'Ο συγγραφέας διαγράφηκε επιτυχώς.')
    return redirect('supervisor:author_list')

@login_required
@user_passes_test(is_supervisor)
def author_change_password(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)  # να μη γίνει logout
            return JsonResponse({'success': True})
        else:
            # επιστρέφει error messages στο Ajax
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = AuthorPasswordChangeForm(user)
    return render(request, 'supervisor/pages/account_change_password.html', {'form': form, 'user': user})    

@login_required
@user_passes_test(is_supervisor)
def contact_list(request):
    messages = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'supervisor/pages/contact_list.html', {'messages': messages})

@login_required
@user_passes_test(is_supervisor)
def contact_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.status = 1  # μαρκάρουμε ως διαβασμένο
    msg.save()
    return render(request, 'supervisor/pages/contact_detail.html', {'msg': msg})

@login_required
@user_passes_test(is_supervisor)
def delete_message(request, pk):
    try:
        msg = ContactMessage.objects.get(pk=pk)
        msg.delete()
        return JsonResponse({'success': True})
    except ContactMessage.DoesNotExist:
        return JsonResponse({'success': False})

@login_required
@user_passes_test(is_supervisor)
def sitefront_settings(request):
    sitefront, _ = SiteFront.objects.get_or_create(pk=1)
    form = SiteFrontForm(instance=sitefront)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = SiteFrontForm(request.POST, request.FILES, instance=sitefront)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': 'Οι ρυθμίσεις αποθηκεύτηκαν επιτυχώς!',
                'logo_url': sitefront.main_image.url if sitefront.main_image else '',
                'favicon_url': sitefront.favicon.url if sitefront.favicon else ''
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return render(request, 'supervisor/pages/settings.html', {
        'form': form,
        'sitefront': sitefront,
    })

# =========================
# MODULES
# =========================

@login_required
@user_passes_test(is_supervisor)
def module_list(request):
    modules = LessonModule.objects.all()
    return render(request, 'supervisor/pages/courses/module_list.html', {
        'modules': modules
    })

@login_required
@user_passes_test(is_supervisor)
def module_create(request):
    if request.method == 'POST':
        form = LessonModuleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Το module δημιουργήθηκε επιτυχώς.')
            return redirect('supervisor:module_list')
    else:
        form = LessonModuleForm()

    return render(request, 'supervisor/pages/courses/module_form.html', {
        'form': form,
        'page_title': 'Δημιουργία Module'
    })

@login_required
@user_passes_test(is_supervisor)
def module_update(request, pk):
    module = get_object_or_404(LessonModule, pk=pk)

    if request.method == 'POST':
        form = LessonModuleForm(request.POST, request.FILES, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Το module ενημερώθηκε επιτυχώς.')
            return redirect('supervisor:module_list')
    else:
        form = LessonModuleForm(instance=module)

    return render(request, 'supervisor/pages/courses/module_form.html', {
        'form': form,
        'page_title': 'Επεξεργασία Module',
        'object': module
    })

@login_required
@user_passes_test(is_supervisor)
def module_delete(request, pk):
    module = get_object_or_404(LessonModule, pk=pk)

    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Το module διαγράφηκε επιτυχώς.')
        return redirect('supervisor:module_list')

    return render(request, 'supervisor/pages/courses/module_delete.html', {
        'object': module
    })


# =========================
# LESSONS
# =========================

@login_required
@user_passes_test(is_supervisor)
def lesson_list(request):
    lessons = Lesson.objects.select_related('module').all()
    return render(request, 'supervisor/pages/courses/lesson_list.html', {
        'lessons': lessons
    })

@login_required
@user_passes_test(is_supervisor)
def lesson_create(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Το lesson δημιουργήθηκε επιτυχώς.')
            return redirect('supervisor:lesson_list')
    else:
        form = LessonForm()

    return render(request, 'supervisor/pages/courses/lesson_form.html', {
        'form': form,
        'page_title': 'Δημιουργία Lesson'
    })

@login_required
@user_passes_test(is_supervisor)
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Το lesson ενημερώθηκε επιτυχώς.')
            return redirect('supervisor:lesson_list')
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'supervisor/pages/courses/lesson_form.html', {
        'form': form,
        'page_title': 'Επεξεργασία Lesson',
        'object': lesson
    })

@login_required
@user_passes_test(is_supervisor)
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Το lesson διαγράφηκε επιτυχώς.')
        return redirect('supervisor:lesson_list')

    return render(request, 'supervisor/pages/courses/lesson_delete.html', {
        'object': lesson
    })


# =========================
# THEORY SECTIONS
# =========================

@login_required
@user_passes_test(is_supervisor)
def theory_section_list(request):
    sections = TheorySection.objects.select_related('lesson').all()
    return render(request, 'supervisor/pages/courses/theory_section_list.html', {
        'sections': sections
    })

@login_required
@user_passes_test(is_supervisor)
def theory_section_create(request):
    if request.method == 'POST':
        form = TheorySectionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Η theory section δημιουργήθηκε επιτυχώς.')
            return redirect('supervisor:theory_section_list')
    else:
        form = TheorySectionForm()

    return render(request, 'supervisor/pages/courses/theory_section_form.html', {
        'form': form,
        'page_title': 'Δημιουργία Theory Section'
    })

@login_required
@user_passes_test(is_supervisor)
def theory_section_update(request, pk):
    section = get_object_or_404(TheorySection, pk=pk)

    if request.method == 'POST':
        form = TheorySectionForm(request.POST, request.FILES, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Η theory section ενημερώθηκε επιτυχώς.')
            return redirect('supervisor:theory_section_list')
    else:
        form = TheorySectionForm(instance=section)

    return render(request, 'supervisor/pages/courses/theory_section_form.html', {
        'form': form,
        'page_title': 'Επεξεργασία Theory Section',
        'object': section
    })

@login_required
@user_passes_test(is_supervisor)
def theory_section_delete(request, pk):
    section = get_object_or_404(TheorySection, pk=pk)

    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Η theory section διαγράφηκε επιτυχώς.')
        return redirect('supervisor:theory_section_list')

    return render(request, 'supervisor/pages/courses/theory_section_delete.html', {
        'object': section
    })


# =========================
# QUESTIONS
# =========================

@login_required
@user_passes_test(is_supervisor)
def question_list(request):
    questions = Question.objects.select_related('lesson').all()
    return render(request, 'supervisor/pages/courses/question_list.html', {
        'questions': questions
    })

@login_required
@user_passes_test(is_supervisor)
@require_http_methods(["GET", "POST"])
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        question = Question()
        formset = AnswerOptionFormSet(request.POST,instance=question, prefix='options')

        if form.is_valid():
            # αποθηκεύουμε προσωρινά το question για να ξέρει το formset το question_type
            question = form.save(commit=False)
            formset = AnswerOptionFormSet(request.POST,instance=question, prefix='options')

            if formset.is_valid():
                question.save()
                formset.instance = question
                formset.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Η ερώτηση δημιουργήθηκε επιτυχώς.',
                })

        html = render_to_string(
            'supervisor/pages/courses/partials/question_form_inner.html',
            {
                'form': form,
                'formset': formset,
            },
            request=request
        )

        return JsonResponse({
            'success': False,
            'html': html
        }, status=400)

    else:
        form = QuestionForm()
        formset = AnswerOptionFormSet(instance=Question(), prefix='options')

    return render(request, 'supervisor/pages/courses/question_form.html', {
        'form': form,
        'formset': formset,
        'page_title': 'Δημιουργία Ερώτησης',
        'submit_url': request.path,
        'is_update': False,
    })

@login_required
@user_passes_test(is_supervisor)
@require_http_methods(["GET", "POST"])
def question_update(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerOptionFormSet(request.POST,instance=question, prefix='options')

        if form.is_valid():
            question = form.save(commit=False)
            formset = AnswerOptionFormSet(request.POST,instance=question, prefix='options')

            if formset.is_valid():
                question.save()
                formset.instance = question
                formset.save()

                return JsonResponse({
                    'success': True,
                    'message': 'Η ερώτηση ενημερώθηκε επιτυχώς.',
                })

        print("FORM ERRORS:", form.errors)
        print("FORM NON FIELD ERRORS:", form.non_field_errors())
        print("FORMSET ERRORS:", formset.errors)
        print("FORMSET NON FORM ERRORS:", formset.non_form_errors())
        print("POST DATA:", request.POST)

        html = render_to_string(
            'supervisor/pages/courses/partials/question_form_inner.html',
            {
                'form': form,
                'formset': formset,
            },
            request=request
        )

        

        return JsonResponse({
            'success': False,
            'message': form.errors,
            'html': html
        }, status=400)

    else:
        form = QuestionForm(instance=question)
        formset = AnswerOptionFormSet(instance=question, prefix='options')

    return render(request, 'supervisor/pages/courses/question_form.html', {
        'form': form,
        'formset': formset,
        'page_title': 'Επεξεργασία Ερώτησης',
        'submit_url': request.path,
        'is_update': True,
        'object': question,
    })

@login_required
@user_passes_test(is_supervisor)
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)

    if request.method == 'POST':
        question.delete()
        return JsonResponse({
            'success': True,
            'message': 'Η ερώτηση διαγράφηκε επιτυχώς.'
        })

    return JsonResponse({
        'success': False,
        'message': 'Μη έγκυρο αίτημα.'
    }, status=400)


# =========================
# ANSWER OPTIONS
# =========================

@login_required
@user_passes_test(is_supervisor)
def answer_option_list(request):
    options = AnswerOption.objects.select_related('question', 'question__lesson').all()
    return render(request, 'supervisor/pages/courses/answer_option_list.html', {
        'options': options
    })

@login_required
@user_passes_test(is_supervisor)
def answer_option_create(request):
    if request.method == 'POST':
        form = AnswerOptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Η επιλογή απάντησης δημιουργήθηκε επιτυχώς.')
            return redirect('supervisor:answer_option_list')
    else:
        form = AnswerOptionForm()

    return render(request, 'supervisor/pages/courses/answer_option_form.html', {
        'form': form,
        'page_title': 'Δημιουργία Answer Option'
    })

@login_required
@user_passes_test(is_supervisor)
def answer_option_update(request, pk):
    option = get_object_or_404(AnswerOption, pk=pk)

    if request.method == 'POST':
        form = AnswerOptionForm(request.POST, instance=option)
        if form.is_valid():
            form.save()
            messages.success(request, 'Η επιλογή ενημερώθηκε επιτυχώς.')
            return redirect('supervisor:answer_option_list')
    else:
        form = AnswerOptionForm(instance=option)

    return render(request, 'supervisor/pages/courses/answer_option_form.html', {
        'form': form,
        'page_title': 'Επεξεργασία Answer Option',
        'object': option
    })

@login_required
@user_passes_test(is_supervisor)
def answer_option_delete(request, pk):
    option = get_object_or_404(AnswerOption, pk=pk)

    if request.method == 'POST':
        option.delete()
        messages.success(request, 'Η επιλογή διαγράφηκε επιτυχώς.')
        return redirect('supervisor:answer_option_list')

    return render(request, 'supervisor/pages/courses/answer_option_delete.html', {
        'object': option
    })


# =========================
# USER PROGRESS / ANSWERS
# =========================

@login_required
@user_passes_test(is_supervisor)
def user_progress_list(request):
    progress_list = UserLessonProgress.objects.select_related('user', 'lesson').all()
    return render(request, 'supervisor/pages/courses/user_progress_list.html', {
        'progress_list': progress_list
    })

@login_required
@user_passes_test(is_supervisor)
def user_answer_list(request):
    answers = UserAnswer.objects.select_related('user', 'lesson', 'question').prefetch_related('selected_options').all()
    return render(request, 'supervisor/pages/courses/user_answer_list.html', {
        'answers': answers
    })

@login_required
@user_passes_test(is_supervisor)
def navbar_contact_messages(request):
    # Φέρνουμε τα 5 πιο πρόσφατα μηνύματα
    messages = (
        ContactMessage.objects
        .order_by('-created_at')[:5]
    )

    # Υπολογίζουμε πόσα είναι μη αναγνωσμένα
    badge_count = ContactMessage.objects.filter(status=0).count()

    return render(request, 'supervisor/core/nav_bar_notification.html', {
        'messages_contact': messages,
        'badge_count': badge_count,
    })