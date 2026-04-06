from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def author_profile_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'author_profile'):
            messages.error(request, 'Δεν έχετε δικαίωμα πρόσβασης σε αυτή την ενότητα.')
            return redirect('login')

        if not user.author_profile.is_active or not user.author_profile.can_take_lessons:
            messages.error(request, 'Ο λογαριασμός σας δεν έχει πρόσβαση σε θεωρία και τεστ.')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper