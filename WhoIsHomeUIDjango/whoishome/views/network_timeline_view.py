from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from whoishome.models import LogData
from whoishome.update_checker import update_check
from whoishome.authentication_utils import user_logged_in_if_locked


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def network_timeline(request):
    log_data_query = LogData.objects.filter().order_by('-time_saved')
    if len(log_data_query) > 50:
        log_data_query = log_data_query[:50]
    log_dict = {}
    sort_log = {}
    x = 0
    for log in log_data_query:
        if log.check_out:
            log_dict[x] = {"time": log.check_out, 'arrival': False, 'host': log.host, 'logdata': log}
            sort_log[x] = log.check_out
            x += 1
        log_dict[x] = {"time": log.check_in, 'arrival': True, 'host': log.host, 'logdata': log}
        sort_log[x] = log.check_in
        x += 1

    sorted_log_list = sorted(sort_log, key=sort_log.get, reverse=True)
    sorted_log_dict = {}
    x = 0

    for sorted_index in sorted_log_list:
        sorted_log_dict[x] = log_dict[sorted_index]
        x += 1

    context = {'logdata_query': log_data_query, 'sorted_log_dict': sorted_log_dict, 'update_available': update_check()}

    return render(request, 'whoishome/network_timeline.html', context)
