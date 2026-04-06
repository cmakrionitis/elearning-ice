from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST,require_http_methods
from account.models import AuthorProfile

# Create your views here.\
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if AuthorProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('courses:course_list')
            else:
                messages.error(request, 'Δεν έχετε δικαίωμα πρόσβασης.')
        else:
            messages.error(request, 'Λάθος στοιχεία σύνδεσης.')

    return render(request, 'account/registration/login.html')


@login_required
@require_http_methods(["GET", "POST"])
def author_logout(request):
    logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')  # βάλε εδώ το url name του login σου
