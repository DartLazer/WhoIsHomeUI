import requests
from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from whoishome.forms import ScannerSettingsForm, EmailSettingsForm, DiscordNotificationsForm, AppSettingsForm, \
    TelegramNotificationsConfigForm
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
        scanner_settings_form = ScannerSettingsForm(request.POST, instance=scanner_config)
        if scanner_settings_form.is_valid():
            scanner_settings_form.save()
            messages.success(request, 'Scanner settings saved')
            logger.warning('Scanner settings updated.')
            return redirect('settings')

    elif 'update_email_settings' in request.POST:
        email_settings_form = EmailSettingsForm(request.POST, instance=email_settings)
        if email_settings_form.is_valid():
            email_settings_form.save()
            messages.success(request, 'Email settings saved!')
            logger.warning('Email settings updated.')
            return redirect('settings')

    elif 'update_discord_settings' in request.POST:
        discord_form = DiscordNotificationsForm(request.POST, instance=discord_config)
        if discord_form.is_valid():
            discord_config = discord_form.save()
            messages.success(request, 'Discord settings saved & test message sent!')
            discord_test_message(discord_config)
            logger.warning('Discord settings updated and test message sent.')
        return redirect('settings')

    elif 'app_settings' in request.POST:
        app_settings_form = AppSettingsForm(request.POST, instance=app_settings)
        if app_settings_form.is_valid():
            app_settings = app_settings_form.save()

            # Handle user password logic after the form is validated
            if app_settings_form.cleaned_data['login_required']:
                password = app_settings_form.cleaned_data['password']
                if User.objects.filter(username='login_user').exists():
                    user = User.objects.get(username='login_user')
                    user.set_password(password)
                    user.save()
                else:
                    User.objects.create_user(username='login_user', password=password)
                messages.success(request, 'Password set')
            else:
                messages.success(request, 'App settings saved!')
        else:
            messages.error(request, 'Settings not saved, missing password?')

    elif 'update_telegram_config' in request.POST:
        form = TelegramNotificationsConfigForm(request.POST, instance=telegram_config)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO,
                                 'Auto delete setting saved!',
                                 extra_tags='Saved!')
            logger.warning('Auto delete setting updated.')

    with open('logfile.log') as file:
        logfile = file.readlines()
        if len(logfile) > 30:
            logfile = logfile[-30:]

    scanner_settings_form = ScannerSettingsForm(instance=scanner_config)
    email_settings_form = EmailSettingsForm(instance=email_settings)
    discord_form = DiscordNotificationsForm(instance=discord_config)
    telegram_form = TelegramNotificationsConfigForm(instance=telegram_config)
    app_settings_form = AppSettingsForm(instance=app_settings)
    return render(request, 'pages/settings/settings.html',
                  {'email': email_settings, 'scanner_settings_form': scanner_settings_form,
                   'email_settings_form': email_settings_form,
                   'discord_form': discord_form,
                   'app_settings_form': app_settings_form,
                   'telegram_form': telegram_form,
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

    return render(request, 'pages/settings/update.html', context)
