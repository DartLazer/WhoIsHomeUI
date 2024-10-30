import datetime
import requests
from django.utils.timezone import localtime
from .models import Host, EmailConfig, DiscordNotificationsConfig, TelegramNotificationsConfig
import smtplib
import logging
import discord

logger = logging.getLogger('log_to_file')


def telegram_notify(host: Host, telegram_config: TelegramNotificationsConfig, notification_type: str):
    print('Telegram!')
    target = getattr(host, 'name')
    arrival_time = localtime(getattr(host, 'arrival_time')).strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = localtime(getattr(host, 'departure_time')).strftime("last seen at: %H:%M:%S on %d-%b-%Y ")

    time_home = getattr(host, 'departure_time') - getattr(host, 'arrival_time')
    time_home = format_time_delta_object(time_home)

    time_away = getattr(host, 'arrival_time') - getattr(host, 'departure_time')
    time_away = format_time_delta_object(time_away)

    if notification_type == 'arrival':
        body = getattr(telegram_config, 'arrival_message').format(target=target, arrival_time=arrival_time,
                                                                  departure_time=departure_time, time_away=time_away,
                                                                  time_home=time_home)
    elif notification_type == 'departure':
        body = getattr(telegram_config, 'departure_message').format(target=target, departure_time=departure_time,
                                                                    arrival_time=arrival_time, time_away=time_away,
                                                                    time_home=time_home)
    elif notification_type == 'new':
        body = getattr(telegram_config, 'new_connection_message').format(target=target, departure_time=departure_time,
                                                                         arrival_time=arrival_time, time_away=time_away,
                                                                         time_home=time_home, mac=host.mac, ip=host.ip,
                                                                         name=host.name)
    elif notification_type == 'curfew':
        body = getattr(telegram_config, 'curfew_message').format(target=target, departure_time=departure_time,
                                                                 arrival_time=arrival_time, time_away=time_away,
                                                                 time_home=time_home, mac=host.mac, ip=host.ip,
                                                                 name=host.name)
    else:
        logger.error('Invalid notification type for Telegram')
        return

    url = f"https://api.telegram.org/bot{telegram_config.bot_token}/sendMessage?chat_id={telegram_config.chat_id}&text={body}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Failed to send Telegram notification. Status code: {response.status_code}")


def discord_notify(host: Host, discord_config: DiscordNotificationsConfig, notification_type: str):
    print('Discord notify')
    webhook = discord.SyncWebhook.from_url(discord_config.webhook_url)
    target = getattr(host, 'name')
    arrival_time = localtime(getattr(host, 'arrival_time')).strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = localtime(getattr(host, 'departure_time')).strftime("last seen at: %H:%M:%S on %d-%b-%Y ")

    time_home = getattr(host, 'departure_time') - getattr(host, 'arrival_time')
    time_home = format_time_delta_object(time_home)

    time_away = getattr(host, 'arrival_time') - getattr(host, 'departure_time')
    time_away = format_time_delta_object(time_away)

    if notification_type == 'arrival':
        body = getattr(discord_config, 'arrival_message').format(target=target, arrival_time=arrival_time,
                                                                 departure_time=departure_time, time_away=time_away,
                                                                 time_home=time_home)
    elif notification_type == 'departure':
        body = getattr(discord_config, 'departure_message').format(target=target, departure_time=departure_time,
                                                                   arrival_time=arrival_time, time_away=time_away,
                                                                   time_home=time_home)
    elif notification_type == 'new':
        body = getattr(discord_config, 'new_connection_message').format(target=target, departure_time=departure_time,
                                                                        arrival_time=arrival_time, time_away=time_away,
                                                                        time_home=time_home, mac=host.mac, ip=host.ip,
                                                                        name=host.name)
    elif notification_type == 'curfew':
        body = getattr(discord_config, 'curfew_message').format(target=target, departure_time=departure_time,
                                                                arrival_time=arrival_time, time_away=time_away,
                                                                time_home=time_home, mac=host.mac, ip=host.ip,
                                                                name=host.name)
    else:
        logger.error('Invalid notification type')
        return

    webhook.send(body)


def discord_test_message(discord_config):
    webhook = discord.SyncWebhook.from_url(discord_config.webhook_url)  # Use SyncWebhook for synchronous calls
    webhook.send("Test message from WhoIsHomeUI!")


def email_sender(host, notification_type):  # sends arrival/departure emails
    print('Sending email')

    email = EmailConfig.objects.get(pk=1)
    target = getattr(host, 'name')
    arrival_time = localtime(getattr(host, 'arrival_time')).strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = localtime(getattr(host, 'departure_time')).strftime("last seen at: %H:%M:%S on %d-%b-%Y ")

    time_home = getattr(host, 'departure_time') - getattr(host, 'arrival_time')
    time_home = format_time_delta_object(time_home)

    time_away = getattr(host, 'arrival_time') - getattr(host, 'departure_time')
    time_away = format_time_delta_object(time_away)

    sender_address = getattr(email, 'sender_address')
    receiver_address = getattr(email, 'to_address')
    account_password = getattr(email, 'your_password')
    smtp_domain = getattr(email, 'smtp_domain')
    smtp_port = getattr(email, 'smtp_port')

    if notification_type == 'arrival':  # if target is home formats the string according to the arrival email.
        # Else departure email

        subject = getattr(email, 'arrival_mail_suject').format(target=target, arrival_time=arrival_time,
                                                               depature_time=departure_time, time_away=time_away,
                                                               time_home=time_home)
        body = getattr(email, 'arrival_mail_body').format(target=target, arrival_time=arrival_time,
                                                          departure_time=departure_time, time_away=time_away,
                                                          time_home=time_home)
    elif notification_type == 'departure':
        subject = getattr(email, 'departure_mail_subject').format(target=target, departure_time=departure_time,
                                                                  time_away=time_away,
                                                                  time_home=time_home)
        body = getattr(email, 'departure_mail_body').format(target=target, departure_time=departure_time,
                                                            arrival_time=arrival_time, time_away=time_away,
                                                            time_home=time_home)
    elif notification_type == 'new':
        subject = getattr(email, 'new_connection_mail_subject').format(target=target, departure_time=departure_time,
                                                                       arrival_time=arrival_time, time_away=time_away,
                                                                       time_home=time_home, mac=host.mac, ip=host.ip,
                                                                       name=host.name)
        body = getattr(email, 'new_connection_mail_body').format(target=target, departure_time=departure_time,
                                                                 arrival_time=arrival_time, time_away=time_away,
                                                                 time_home=time_home, mac=host.mac, ip=host.ip,
                                                                 name=host.name)
    elif notification_type == 'curfew':
        subject = getattr(email, 'curfew_subject').format(target=target, departure_time=departure_time,
                                                          arrival_time=arrival_time, time_away=time_away,
                                                          time_home=time_home, mac=host.mac, ip=host.ip,
                                                          name=host.name)
        body = getattr(email, 'curfew_message').format(target=target, departure_time=departure_time,
                                                       arrival_time=arrival_time, time_away=time_away,
                                                       time_home=time_home, mac=host.mac, ip=host.ip,
                                                       name=host.name)
    else:
        logger.error('Invalid notification type')

    smtp_server = smtplib.SMTP_SSL(smtp_domain, int(smtp_port))
    try:
        smtp_server.login(sender_address, account_password)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f'Email Error during authentication. Make sure email setup is correct.\n: {e}')
        return

    message = f"Subject: {subject}\n\n{body}"
    try:
        smtp_server.sendmail(sender_address, receiver_address, message)
    except smtplib.SMTPException as e:
        logger.error(f'Unknown email error. Printing out:\n {e}')

    smtp_server.close()


def strfdelta(tdelta: datetime.timedelta, fmt: str):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def format_time_delta_object(time_delta: datetime.timedelta):
    if time_delta.days >= 1:
        time_delta = strfdelta(time_delta, '{days} days {hours}:{minutes}:{seconds}')
    elif time_delta.seconds > 3600:
        time_delta = strfdelta(time_delta, '{hours} hours and {minutes} minutes.')
    else:
        time_delta = strfdelta(time_delta, '{minutes} minutes.')

    return time_delta
