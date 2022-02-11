from django.apps import AppConfig
import os


class WhoishomeConfig(AppConfig):
    name = 'whoishome'
    
    def ready(self):
        background_scheduler_running = os.popen(
            'ps -ef | grep "process_tasks" | grep -v grep').read()  # checks if the process_tasks is started which is required for background tasks.
        if not background_scheduler_running:
            print('Starting background scheduler...')
            os.system('python /mysite/mysite/manage.py process_tasks > /dev/null 2>&1 &')
            background_check = os.popen('ps -ef | grep "process_tasks" | grep -v grep').read()
            if background_check:
                print('Background scheduler successfully started :)')
