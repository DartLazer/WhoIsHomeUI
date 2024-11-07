from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from whoishome.forms import EnterPasswordForm
from whoishome.scanner_functions import logger

def log_in(request):
    if request.POST:
        password_form = EnterPasswordForm(request.POST)
        if password_form.is_valid():
            password = password_form.cleaned_data['password']
            user = authenticate(username='login_user', password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.add_message(request, messages.INFO,
                                     'Invalid password!',
                                     extra_tags='Saved!')
                logger.warning('Invalid password entered!')
                return redirect(log_in)

    password_form = EnterPasswordForm()
    return render(request, 'pages/settings/enter_password.html', {'login_form': password_form})
