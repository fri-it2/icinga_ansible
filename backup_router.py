#!/usr/bin/env python3

# Nagios check command to verify, if oxidized successfully make a backup of the configuration from the device


__version__ = 'v1.0'

import requests
import json
import logging
from datetime import datetime

from pynag.Plugins import PluginHelper, ok, warning, critical, unknown
import urllib3
urllib3.disable_warnings()

helper = PluginHelper()
helper.parser.add_option("--url", help="Url of device to connect to connect to", dest="url")
helper.parser.add_option("-l", help="Username to login with", dest="username")
helper.parser.add_option("-p", help="Password to login with", dest="password")
helper.parser.add_option('-c', help='Time in second from last backup: status of service in CRITICAL state', dest='critical_state',  default='36000')
helper.parser.add_option('-w', help='Time in second from last backup: status of service in WARNING state', dest='warning_state',  default='18000')
helper.parse_arguments()
url = helper.options.url
username = helper.options.username
password = helper.options.password
if url is None:
    helper.parser.error('-H argument is required')
if username is None:
    helper.parser.error('-l argument is required')
if password is None:
    helper.parser.error('-p argument is required')

if helper.options.show_debug:
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.disable(logging.ERROR)

try:
    response = requests.get(url, auth=(username, password), verify=False, timeout=20)
except requests.exceptions.Timeout as e:
    logging.debug(e, exc_info=1)
    helper.add_summary('Could not establish connection')
    helper.add_long_output(str(e))
    helper.status(critical)
except requests.exceptions.ConnectionError as e:
    logging.debug(e, exc_info=1)

    helper.add_summary('Connection error')
    helper.add_long_output('Connection error'+str(e))
    helper.status(critical)
except requests.exceptions.HTTPError as e:
    logging.debug(e, exc_info=1)
    helper.add_summary('HTTP error')

    helper.add_long_output(str(e))
    helper.status(critical)
except requests.exceptions.RequestException as e:
    logging.debug(e, exc_info=1)
    helper.add_summary('Unknown error')
    helper.add_long_output(str(e))
    helper.status(critical)
except Exception as e:
    logging.debug(e, exc_info=1)
    helper.add_summary('Unknown error')
    helper.add_long_output(str(e))
    helper.status(critical)

else:
    try:
        json_response = json.loads(response.text)
    except Exception as e:
        logging.debug(e, exc_info=1)
        helper.add_summary('JSON error')
        helper.add_long_output(str(e))
        helper.status(critical)
    else:
        last_start = json_response.get('last').get('start')
        last_status = json_response.get('last').get('status')
        # čas '2020-05-07 09:05:54 UTC'
        # datetime.datetime(2020, 5, 7, 9, 5, 54)
        year = int(last_start[0:4])
        month = int(last_start[5:7])
        day = int(last_start[8:10])
        hour = int(last_start[11:13])
        minute = int(last_start[14:16])
        second = int(last_start[17:19])
        date_last_start = datetime(year, month, day, hour, minute, second)
        # datetime(int(last_start[0:4]), int(last_start[5:7]), int(last_start[8:10]),int(last_start[11:13]), int(last_start[14:16]), int(last_start[17:19]))
        time_difference = datetime.utcnow() - date_last_start
        duration = time_difference.total_seconds()
        if last_status != 'success':
            helper.add_summary('Configuration not saved OK')
            helper.add_long_output('time=%s status=%s' % (last_start, last_status))
            helper.status(critical)
        elif int(helper.options.warning_state) < duration < int(helper.options.critical_state):
            helper.add_summary('Configuration not saved in time')
            helper.add_long_output('time=%s status=%s' % (last_start, last_status))
            helper.status(warning)
        elif duration > int(helper.options.critical_state):
            helper.add_summary('Configuration not saved in time')
            helper.add_long_output('time=%s status=%s' % (last_start, last_status))
            helper.status(critical)
        else:
            helper.add_summary('Configuration saved OK')
            helper.status(ok)
            helper.add_long_output('time=%s status=%s' % (last_start, last_status))

helper.check_all_metrics()
helper.exit()
