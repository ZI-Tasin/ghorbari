from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from verify_email.email_handler import ActivationMailManager


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                inactive_user = ActivationMailManager.send_verification_link(request=request, form=form)

                messages.success(request, f"Registration successful, {inactive_user.username}! \
                                 A verification email has been sent to {inactive_user.email}. \
                                 Please check your inbox (and spam folder) to activate your account before logging in.")
                return redirect('users:login')

            except Exception as e:
                messages.error(request, f"Could not send verification email. Please contact support. Error: {e}")
                return render(request, 'users/register.html', {'form': form})

        else:
            messages.error(request, "Please correct the errors below.")
            return render(request, 'users/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def user_profile(request):
    return render(request, 'users/user_profile.html')

