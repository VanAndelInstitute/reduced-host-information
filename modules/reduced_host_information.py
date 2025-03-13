import host_functions
import os
import sys
import csv
import signal
import requests
import urllib3
import json
import pandas as pd
from dotenv import load_dotenv

############################################################################################################

#signal hander for keyboard interrupts
def signal_handler(sig, frame):
    print('\nInterupt Caught. Exiting program...\n')
    sys.exit(0)


class API_data:
    #constructor
    def __init__(self, TOKEN):
        self.all_flag = 1
        self.host_nums = []
        self.host_names = {}
        self.headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

######################################################################################

    #GOOD
    #initialize list of all hosts numbers
    def get_host_nums(self):
        #check if status code is good, retrieve all host numbers. exit if otherwise
        url = 'https://ansible.vai.org:8043/api/v2/hosts/'
        r = requests.get(url, headers=self.headers, verify=False)
        if r.status_code == 200:
            r_json = r.json()
            self.get_curr_page_hosts(response = r_json)
        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)

#######################################################################################

    #GOOD
    #get all the hosts from the curretly "visible" page
    def get_curr_page_hosts(self, response):
        hosts_curr_page = [host['id'] for host in response['results']]
        for hn in hosts_curr_page:
            self.host_nums.append(hn)

        self.check_next_page(response)

    #GOOD
    #if there is a next page, recurse with the url held in the 'next' field
    def check_next_page(self, response):
        if response['next']:
            next_url = 'https://ansible.vai.org:8043' + response['next']
            self.get_host_nums(next_url)

#######################################################################################


    def get_some_host_facts(self):
        count_hosts = 0
        interfaces = []
        reduced_ifs = []

        #iterate through all hosts
        for host_no in self.host_nums:

            api_queries = {}    #reset api_queries to empty
            server_mac_addresses = {}   #reset the server mac address dictionary

            #get URL for specific host
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            #check for valid http request, process querying for the mac addresses and API values
            if r.status_code == 200:
                r_json = r.json()

                #get facts for the current node
                api_queries = host_functions.get_some_curr_host_facts(self.host_names, r_json, host_no)

                #get all interface names for current node
                interfaces = r_json['ansible_interfaces']

                #filter out the virtual and docker interfaces
                reduced_ifs = host_functions.reduce_interfaces(interfaces)

                #get the server interfaces and final reduced interfaces
                host_functions.query_interfaces(server_mac_addresses, reduced_ifs, r_json)


            #print statements for server information
                if server_mac_addresses:
                    for k,v in server_mac_addresses.items():
                        api_queries[k] = v

                for k,v in api_queries.items():
                    print(f"{k}: {v}")
                print("\n\n")

                count_hosts += 1

            else:
                print(f"\nError: {r.status_code}). Exiting program...\n")
                sys.exit(1)
                
        print(f'\nNumber of hosts saved: {count_hosts}')


############################################################################################################

#initialize signal handler and supress warnings
signal.signal(signal.SIGINT, signal_handler)
urllib3.disable_warnings()
load_dotenv()

#retrieve API token and initialize API_data data structure with token
TOKEN = host_functions.check_token()
data = host_functions.init_api_data_structure(token=TOKEN, API_data_var=API_data)

#let user know process is starting
print("\nProcess Starting...\n")

#get every host number from the API
data.get_host_nums()
if data.all_flag == 1:
    host_functions.get_all_host_facts()
else:
    host_functions.get_some_host_facts()

#if here then process was successful
print('Process Ended Successfully\n')
