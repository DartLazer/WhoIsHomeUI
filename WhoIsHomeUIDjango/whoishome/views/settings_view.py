import requests
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from whoishome.forms import ScannerSettingsForm, EmailSettingsForm, DiscordNotificationsForm, LockAppForm, \
    AutoDeleteAfterXDaysForm, TelegramNotificationsConfigForm, CurfewTimesForm
from whoishome.models import EmailConfig, DiscordNotificationsConfig, TelegramNotificationsConfig, ScannerConfig, \
    AppSettings
from whoishome.notification_functions import discord_test_message
from whoishome.authentication_utils import user_logged_in_if_locked
from whoishome.update_checker import logger, update_check, get_github_version


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def settings(request):
    email_settings, created_bool = EmailConfig.objects.get_or_create(pk=1)

    discord_config = DiscordNotificationsConfig.objects.get(pk=1)
    telegram_config = TelegramNotificationsConfig.objects.get(pk=1)
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
    app_settings, created_bool = AppSettings.objects.get_or_create(pk=1)

    scanner_running = True if scanner_config.scanner_enabled else False

    if 'update_scanner_settings' in request.POST:
        scanner_settings_form = ScannerSettingsForm(request.POST, request=request)
        if scanner_settings_form.is_valid():
            if scanner_settings_form.has_changed():

                if 'email' in scanner_settings_form.changed_data:
                    user = request.user
                    setattr(user, 'email', scanner_settings_form.cleaned_data['email'])
                    user.save()
                    scanner_settings_form.changed_data.remove('email')
                for changed_data in scanner_settings_form.changed_data:
                    setattr(scanner_config, changed_data, scanner_settings_form.cleaned_data[changed_data])

                    messages.add_message(request, messages.INFO,
                                         'Scanner settings saved!',
                                         extra_tags='Saved!')

                scanner_config.save()
            logger.warning('Scanner settings updated.')
            return redirect('settings')

    elif 'update_email_settings' in request.POST:
        email_settings_form = EmailSettingsForm(request.POST, request=request)
        if email_settings_form.is_valid():
            if email_settings_form.has_changed():
                email_config = EmailConfig.objects.get(pk=1)
                if 'email' in email_settings_form.changed_data:
                    user = request.user
                    setattr(user, 'email', email_settings_form.cleaned_data['email'])
                    user.save()
                    email_settings_form.changed_data.remove('email')
                for changed_data in email_settings_form.changed_data:
                    setattr(email_config, changed_data, email_settings_form.cleaned_data[changed_data])

                    messages.add_message(request, messages.INFO,
                                         'Email settings saved!',
                                         extra_tags='Saved!')

                email_config.save()
            logger.warning('Email settings updated.')
            return redirect('settings')


    elif 'update_discord_settings' in request.POST:
        discord_form = DiscordNotificationsForm(request.POST, request=request)
        if discord_form.is_valid():
            if discord_form.has_changed():
                for changed_data in discord_form.changed_data:
                    setattr(discord_config, changed_data, discord_form.cleaned_data[changed_data])
                discord_config.save()
            if discord_config.webhook_url:
                discord_test_message(discord_config)

                messages.add_message(request, messages.INFO,
                                     'Discord settings saved & test message sent!',
                                     extra_tags='Saved!')
            logger.warning('Discord settings updated.')
        return redirect('settings')

    elif 'lock_app_form' in request.POST:
        lock_app_form = LockAppForm(request.POST, request=request)
        if lock_app_form.is_valid():
            if lock_app_form.has_changed():
                app_settings.login_required = lock_app_form.cleaned_data['login_required']
                app_settings.save()
            if User.objects.filter(username='login_user').exists():
                user = User.objects.get(username='login_user')
                user.set_password(lock_app_form.cleaned_data['password'])
                user.save()
            else:
                User.objects.create_user(username='login_user', password=lock_app_form.cleaned_data['password'])
            logger.warning('Password updated')
            messages.add_message(request, messages.INFO,
                                 'Password settings changed',
                                 extra_tags='Saved!')

    elif 'auto_delete_after_x_days_form' in request.POST:
        form = AutoDeleteAfterXDaysForm(request.POST, instance=app_settings)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO,
                                 'Auto delete setting saved!',
                                 extra_tags='Saved!')
            logger.warning('Auto delete setting updated.')

    elif 'update_telegram_config' in request.POST:
        form = TelegramNotificationsConfigForm(request.POST, instance=telegram_config)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO,
                                 'Auto delete setting saved!',
                                 extra_tags='Saved!')
            logger.warning('Auto delete setting updated.')


    elif 'curfew_form' in request.POST:
        curfew_form = CurfewTimesForm(request.POST, request=request)
        if curfew_form.is_valid():
            if curfew_form.has_changed():
                for changed_data in curfew_form.changed_data:
                    setattr(app_settings, changed_data, curfew_form.cleaned_data[changed_data])
                app_settings.save()
                messages.add_message(request, messages.INFO,
                                     'Curfew settings saved!',
                                     extra_tags='Saved!')
                logger.warning('Curfew settings updated.')

    with open('logfile.log') as file:
        logfile = file.readlines()
        if len(logfile) > 30:
            logfile = logfile[-30:]

    scanner_settings_form = ScannerSettingsForm(request=request)
    email_settings_form = EmailSettingsForm(request=request)
    discord_form = DiscordNotificationsForm(request=request)
    lock_app_form = LockAppForm(request=request)
    curfew_form = CurfewTimesForm(request=request)
    telegram_config_form = TelegramNotificationsConfigForm(instance=telegram_config)
    auto_delete_form = AutoDeleteAfterXDaysForm(instance=app_settings)
    print(app_settings.curfew_enabled)
    return render(request, 'pages/settings.html',
                  {'email': email_settings, 'scanner_settings_form': scanner_settings_form,
                   'email_settings_form': email_settings_form,
                   'discord_form': discord_form,
                   'lock_app_form': lock_app_form,
                   'curfew_form': curfew_form,
                   'auto_delete_form': auto_delete_form,
                   'telegram_form': telegram_config_form,
                   "logfile": logfile, 'update_available': update_check(), 'scanner_running': scanner_running,
                   "timezone": django_settings.TIME_ZONE})


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def start_scanner(request):
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
    scanner_config.scanner_enabled = True
    scanner_config.save()
    logger.warning("Scanner started. Scanning every minute.")
    return HttpResponseRedirect('/')


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def stop_scanner(request):
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
    scanner_config.scanner_enabled = False
    scanner_config.save()
    logger.warning("Scanner Stopped.")
    return HttpResponseRedirect('/')


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def update_page(request):
    changelog_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/CHANGELOG.md'
    r = requests.get(changelog_url)
    if r.status_code == 200:
        changelog = r.text
        changelog = changelog.split('\n')
    else:
        changelog = 'Unable to retrieve changelog.'

    context = {
        'current_version': django_settings.CURRENT_VERSION, 'update_available': update_check(),
        'github_version': get_github_version(), 'changelog': changelog
    }

    return render(request, 'whoishome/update.html', context)
