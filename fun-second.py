import jenkins
import csv
import os
import json
from pprint import pprint
from Queue import Queue
import threading
import time
import requests

queue = Queue()

THREADS_COUNT = 10
TIMEOUT = 1000
# Jenkins username from docker environment
USERNAME = os.getenv('USERNAME')

# Jenkins password from docker environment
PASSWORD = os.getenv('PASSWORD')

# Jenkins API token from environment
API_TOKEN = os.getenv('API_TOKEN')

# Jenkins depth from environment
# default value = 4
FOLDER_DEPTH = os.getenv('FOLDER_DEPTH', 4)

# Jenkins URL from environment
URL = os.getenv('URL')

# Count of Console Output
LAST_BYTES = os.getenv('LAST_BYTES', 400)

# Meeting function for checking connection
def start():
    user = server.get_whoami()
    print('2. Hello %s from Jenkins' % (user['fullName']))

def make_queue(current_service, services_dict, service_params):
    if current_service in services_dict:
        service_info = services_dict[current_service]
        print("Service info: ", service_info)
        build_list.append([
            service_info[0], #job name
            service_info[1], #job URL
            service_info[2], #service
            current_service,
            service_params,
            service_info[3] #service name
        ])
    else:
        error_list.append([current_service, "Not found"])


def start_all():
    for issue in build_list:
        params_dict = issue[4]
        params_dict[issue[2]] = issue[3]
        print("ISSUE", issue)

        command_result = 'Error'
        try:
            build_number = server.build_job(name=issue[0], parameters=params_dict, token=API_TOKEN)
            print ('JOB NUMBER: %', build_number)
            console_url = '{0}{1}/consoleText'.format(issue[1], build_number)
            issue.append(build_number)
            queue.put(
                {
                    'fullname': issue[0],
                    'build_number': build_number,
                    'url': issue[1],
                    'console_url': console_url,
                    'service_name': issue[5]

                }
            )
            list_to_result.append(build_number)

        except jenkins.JenkinsException:
            print("Failed build a job", issue[0])

def worker():
    global queue
    try:
        target_job = queue.get_nowait()
    except:
        return

    print ('Build number:', target_job['build_number'], 'in process..')

    idx = 0
    while idx < TIMEOUT:
        time.sleep(1)
        try:
            command_result = server.get_build_console_output(
                name=target_job['fullname'], number=target_job['build_number']
            )
            print ('Build number: ', target_job['build_number'], '.   ', command_result, target_job['console_url'])
            dict_to_result[target_job['build_number']] = [
                target_job['fullname'],
                target_job['url'],
                target_job['build_number'],
                target_job['console_url']
            ]
            jenkins_request(target_job['console_url'], target_job['build_number'], target_job['service_name'])
            return
        except jenkins.JenkinsException:
            idx += 1
            continue
    if idx >= TIMEOUT:
        print('Something wrong with:', target_job['build_number'])


def jenkins_request(output_url, build_number, service):
    url = output_url
    auth = (USERNAME, PASSWORD)
    r = requests.get(url, auth=auth, stream=True)
    result_row = ""
    for chunk in r.iter_content(chunk_size=LAST_BYTES):
        if chunk:  # filter out keep-alive new chunks
            prev_row = result_row
            result_row = chunk
    if len(result_row) < LAST_BYTES:
        to_stream = prev_row[-(LAST_BYTES - len(result_row) + 1):-1] + result_row
    else:
        to_stream = result_row
    print("LAST_OUTPUT:{0}".format(to_stream))
    os.mkdir("/temp/output/{0}_{1}".format(service, build_number))
    file_result = open('/temp/output/{0}_{1}/output'.format(service, build_number), 'wb')
    file_result.write(to_stream)
    file_result.close()
    service_file = open('/temp/output/{0}_{1}/service'.format(service, build_number), 'wb')
    service_file.write(service)
    service_file.close()
    service_file = open('/temp/found_info', 'wb')
    service_file.write(" ")
    service_file.close()



##
# START MAIN FUNCTION
##
print('HELLO')
print('1. Create connection...')
try:
    server = jenkins.Jenkins(url=URL, username=USERNAME, password=PASSWORD)
except:
    print("Connection isn't create!")

start()

print('3. Get all services from data.json')
jobs_data_file = open('/opt/data.json')
services_dict = json.load(jobs_data_file)

pprint(services_dict)

#
#
jobs_data_file = open('/opt/build.json')
build_data = json.load(jobs_data_file)
#
build_list = []
error_list = []
for service in build_data:
    make_queue(service['service'], services_dict, service['params'])

dict_to_result = {}
list_to_result = []
start_all()

for _ in xrange(10):
    thread_ = threading.Thread(target=worker)
    thread_.start()

while threading.active_count() > 1:
    time.sleep(1)

print "FINISHED"

#
file_result = open('/temp/queue.csv', 'wb')
writer = csv.writer(file_result, delimiter=',')
writer.writerow(['JOB', 'JOB URL', 'SERVICE TYPE', 'SERVICE NAME', 'PARAMS', 'BUILD NUMBER'])
for rows in build_list:
    writer.writerow(rows)
file_result.close()

file_result = open('/temp/error.csv', 'wb')
writer = csv.writer(file_result, delimiter=',')
writer.writerow(['SERVICE NAME', 'RESULT'])
for rows in error_list:
    writer.writerow(rows)
file_result.close()

file_result = open('/temp/result.csv', 'wb')
writer = csv.writer(file_result, delimiter=',')

writer.writerow(['JOB', 'JOB URL', 'BUILD NUMBER', 'RESULT OUTPUT'])
for number in list_to_result:
    if number in dict_to_result:
        writer.writerow(dict_to_result[number])
file_result.close()
