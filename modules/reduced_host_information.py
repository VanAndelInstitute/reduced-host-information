import modules.host_functions as host_functions
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

    #GOOD
    #initialize list of all hosts numbers
    def get_host_nums(self, url):
        #check if status code is good, retrieve all host numbers. exit if otherwise
        r = requests.get(url, headers=self.headers, verify=False)
        if r.status_code == 200:
            r_json = r.json()
            self.get_curr_page_hosts(response = r_json)

        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)

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
        else:
            if self.all_flag == 1:
                host_functions.get_all_host_facts()
            else:
                host_functions.get_some_host_facts()

    #FIXME: FIX THE FORMATTING. AND APPEND THE INFORMATION IN THE END. THIS IS LAST PRIORITY 
    def get_curr_host_facts(self, response, csv_file, host_no):

        self.host_names[host_no] = response['ansible_nodename']
        df = pd.json_normalize(response, sep=' ')

        #add hostname to each column of information, then trans
        server = f'{self.host_names[host_no]}'
        host_nodename = [server] * len(df.columns)  #to add a host nodename each row of information
        df.loc[-1] = host_nodename 
        df.index += 1
        df.sort_index()
        df = df.T

        df.to_csv(csv_file, mode='a')
        print(f"Successfully saved {server} data to {csv_file}")
        count_hosts += 1

    
    def get_some_curr_host_facts(self, response, host_no):

        api_queries = {'ansible_nodename':'',      
            'ansible_product_serial':'',
            'ansible_chassis_serial':'',
            'ansible_product_name':'',
            'ansible_chassis_vendor':'',
            'ansible_system_vendor':'',
            "ansible_memory_mb":'',
            'ansible_processor':'',
            'ansible_processor_cores':'',
            'ansible_processor_count':''}

        #get current host name
        self.host_names[host_no] = response['ansible_nodename']
        for k in api_queries.keys():
            try:
                if k == 'ansible_memory_mb':
                    api_queries[k] = response[k]['real']['total']
                elif k == "ansible_processor":
                    api_queries[k] = response[k][2]
                else:
                    api_queries[k] = response[k]
            except:
                print("Error: " + k)

        return api_queries

    
    def get_all_host_facts(self):
        count_hosts = 0
        csv_file = 'host_information_all.csv'
        host_functions.check_file(csv_file)

        #retrieving information for each host
        for host_no in self.host_nums:
            #create URL based on host number and request the information
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            #convert response object to json
            if r.status_code == 200:
                r_json = r.json()
                try:
                    self.get_curr_host_facts(self, response=r_json, csv_file=csv_file, host_no=host_no)
                except:
                    print("Error: Couldn't save host information")
            else:
                print(f"\nError: {r.status_code}). Exiting program...\n")
                sys.exit(1)
                
        print(f'\nNumber of hosts saved: {count_hosts}')

    def get_some_host_facts(self):
        count_hosts = 0
        csv_file = 'host_information_some.csv'
        host_functions.check_file(csv_file)

        interfaces = []
        reduced_ifs = []
        column_labels = ['Server Name',
                        'Product Serial',
                        'Chassis Serial',
                        'Model',
                        'Chassis Vendor',
                        'System Vendor',
                        'Memory',
                        'Processor (CPU)',
                        'Processor Cores',
                        'Processor Count']


        #iterate through all hosts
        for host_no in self.host_nums:

            api_queries = {}

            #get URL for specific host
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            #check for valid http request, process querying for the mac addresses and API values
            if r.status_code == 200:
                r_json = r.json()

                #get the facts listed in the api_queries for the current node
                api_queries = self.get_some_curr_host_facts(r_json, host_no)

                server_mac_addresses = {}   #reset the server mac address dictionary

                #retrieve all the interface names
                interfaces = r_json['ansible_interfaces']

                #filter out the virtual and docker interfaces
                reduced_ifs = host_functions.reduce_interfaces(interfaces)

                #get the server interfaces and final reduced interfaces
                valid_ifs = host_functions.query_interfaces(server_mac_addresses, reduced_ifs, r_json)


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

signal.signal(signal.SIGINT, signal_handler)

#suppress warnings and load environment variables
urllib3.disable_warnings()
load_dotenv()


TOKEN = host_functions.check_token()
data = host_functions.init_api_data_structure(token=TOKEN, API_data_var=API_data)
url = 'https://ansible.vai.org:8043/api/v2/hosts/'

print("\nProcess Starting...\n")
data.get_host_nums(url = url)
print('Process Ended Successfully\n')
