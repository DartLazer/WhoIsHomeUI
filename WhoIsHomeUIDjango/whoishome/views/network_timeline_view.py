from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from whoishome.models import LogData
from whoishome.update_checker import update_check
from whoishome.authentication_utils import user_logged_in_if_locked


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def network_timeline(request):
    # Fetch and limit log data to 50 entries if more are present
    log_data_query = LogData.objects.all().order_by('-time_saved')[:50]

    log_dict = {}
    sort_log = {}

    # Populate log_dict and sort_log with log data entries
    for index, log in enumerate(log_data_query):
        if log.check_out:
            log_dict[index] = {
                "time": log.check_out,
                "arrival": False,
                "host": log.host,
                "logdata": log
            }
            sort_log[index] = log.check_out
            index += 1

        log_dict[index] = {
            "time": log.check_in,
            "arrival": True,
            "host": log.host,
            "logdata": log
        }
        sort_log[index] = log.check_in

    # Sort log entries by time in descending order
    sorted_log_list = sorted(sort_log, key=sort_log.get, reverse=True)
    sorted_log_dict = {idx: log_dict[sorted_index] for idx, sorted_index in enumerate(sorted_log_list)}

    context = {
        'logdata_query': log_data_query,
        'sorted_log_dict': sorted_log_dict,
        'update_available': update_check()
    }

    return render(request, 'pages/network_timeline.html', context)
