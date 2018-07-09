import jenkins
import csv
import os
import json
from pprint import pprint

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


# Meeting function for checking connection
def start():
    user = server.get_whoami()
    print('DOCKER 1.1. Hello %s from Jenkins' % (user['fullName']))


##
# Sending Jenkins API request to get jobs info and saving data in a list of dictionary
#
# Format:
# FULLNAME (string), JOB URL (string), JOB PARAMS (dictionary)
##
def get_data(jobs):
    # Iterative process. Looking for jobs and job's parameters
    for job in jobs:
        # Data structure for a csv file (row)
        fullname = job['fullname']
        print('DOCKER 1.5. Get info for', fullname)
        job_url = job['url']

        list_to_result = [fullname, job_url]

        dictionary_to_write = {'other': []}
        jenkins_job_actions = server.get_job_info(name=fullname, depth=FOLDER_DEPTH)['actions']
        ##
        # If jenkins job has any action
        ##
        if jenkins_job_actions > 0:
            # Listing all actions
            for action in jenkins_job_actions:
                # Looking for a parameter
                for action_param in action:
                    ##
                    # If jenkins job action is field with parameter
                    ##
                    if action_param == 'parameterDefinitions' and action['parameterDefinitions'] > 0:
                        job_params = action['parameterDefinitions']
                        print ('DOCKER 1.6. Job params:', job_params)
                        for parameter in job_params:
                            parameter_dict = {}
                            if 'type' in parameter and parameter['type'] == 'ChoiceParameterDefinition':
                                parameter_dict['type'] = parameter['type']
                                parameter_dict['name'] = parameter['name']
                                parameter_dict['choices'] = parameter['choices']
                                parameter_dict['default_value'] = parameter['defaultParameterValue']['value']

                                if parameter_dict['name'] == 'action':
                                    dictionary_to_write['actions'] = parameter_dict

                                elif parameter_dict['name'] == 'service':
                                    dictionary_to_write['services'] = parameter_dict

                                    for choice in parameter_dict['choices']:
                                        services_dict[choice] = [
                                            fullname,
                                            job_url,
                                            parameter_dict['name'],
                                            parameter_dict['default_value']
                                        ]

                                else:
                                    dictionary_to_write['other'].append(parameter_dict)

                            elif 'type' in parameter and parameter['type'] == 'StringParameterDefinition':
                                parameter_dict['type'] = parameter['type']
                                parameter_dict['name'] = parameter['name']
                                parameter_dict['default_value'] = parameter['defaultParameterValue']['value']

                                if parameter_dict['name'] == 'version':
                                    dictionary_to_write['versions'] = parameter_dict

                                elif parameter_dict['name'] == 'profile':
                                    dictionary_to_write['profiles'] = parameter_dict

                                else:
                                    dictionary_to_write['other'].append(parameter_dict)

        flag_is_leaf = False
        if 'services' in dictionary_to_write:
            flag_is_leaf = True
            list_to_result.append(dictionary_to_write['services'])
        else:
            list_to_result.append('None')

        if 'actions' in dictionary_to_write:
            flag_is_leaf = True
            list_to_result.append(dictionary_to_write['actions'])
        else:
            list_to_result.append('None')

        if 'versions' in dictionary_to_write:
            flag_is_leaf = True
            list_to_result.append(dictionary_to_write['versions'])
        else:
            list_to_result.append('None')

        if 'profiles' in dictionary_to_write:
            flag_is_leaf = True
            list_to_result.append(dictionary_to_write['profiles'])
        else:
            list_to_result.append('None')

        if len(dictionary_to_write['other']) > 0:
            flag_is_leaf = True
            list_to_result.append(dictionary_to_write['other'])
        else:
            list_to_result.append('None')

        if flag_is_leaf:
            result.append(list_to_result)

##
#  START
##

print("URL:", URL)

print('DOCKER 1.2. Create connection...')
try:
    server = jenkins.Jenkins(url=URL, username=USERNAME, password=PASSWORD)
except jenkins.JenkinsException:
    print("DOCKER 1. Connection isn't create!")

start()

print('DOCKER 1.3. Get all jobs from the server')
jenkins_jobs = server.get_all_jobs(FOLDER_DEPTH)
result = []
services_dict = {}
actions_dict = {}
versions_dict = {}
profiles_dict = {}
other_params_dict = {}

print('DOCKER 1.4. Get all services from jobs')
get_data(jenkins_jobs)

print('DOCKER 1.7. Write .csv file ')
file_result = open('/temp/mycsvfile.csv', 'wb')
file_result = open('/opt/mycsvfile.csv', 'wb')

csv_writer = csv.writer(file_result, delimiter=',')
csv_writer.writerow(['FULLNAME', 'JOB URL', 'SERVICES', 'ACTIONS', 'VERSIONS', 'PROFILES', 'OTHER'])
for rows in result:
    print('DOCKER 1.8 Add a new job', rows)
    csv_writer.writerow([rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6]])

file_result.close()
print('DOCKER 1.9. Write .json file ')
json.dump(services_dict, open('/temp/data.json', 'wb'))

json.dump(services_dict, open('/opt/data.json', 'wb'))
