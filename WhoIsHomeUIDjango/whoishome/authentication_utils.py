from django.contrib.auth.models import User

from whoishome.models import AppSettings


def user_logged_in_if_locked(user: User):
    app_settings, created_bool = AppSettings.objects.get_or_create(pk=1)
    return not app_settings.login_required or user.is_authenticated
