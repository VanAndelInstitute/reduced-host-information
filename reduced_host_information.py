#possibly need to run pip install pandas, openpyxl, python-dotenv
import os
import sys
import csv
import signal
import requests
import urllib3
import pandas as pd
from dotenv import load_dotenv


def signal_handler(sig, frame):

    print('\nInterupt Caught. Exiting program...\n')

    sys.exit(0)

def check_file(filepath):

    if os.path.exists(filepath) and os.path.isfile(filepath):
        print(f"{filepath} already exists. This file will be removed and a new one will be generated.\n")
        os.remove(filepath)
        print(f"Generating new file: '{filepath}\n")
    else:
        print(f"{filepath} does not exist. Generating new file: {filepath}\n")

def reduce_interfaces(interfaces):
    skip_lst = ['v','d']

    for interface in interfaces:
        if interface[0] in skip_lst:
            interfaces.remove(interface)

    return interfaces

def query_interfaces(server_mac_addresses, reduced_ifs, r_json):
    valid_ifs = []

    for inf in reduced_ifs:                    
        mac_query = f'ansible_{inf}'
        try:
            mac_address = r_json[mac_query]['macaddress']
            server_mac_addresses[inf] = mac_address
            valid_ifs.append(inf)
        except:
            continue
    
    return valid_ifs

############################################################################################################

class API_data:

    def __init__(self, TOKEN):
        self.all_flag = 1
        self.host_nums = []
        self.host_names = {}
        self.headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

    def get_host_nums(self, url):
        #check if status code is good, retrieve all host numbers. exit if otherwise
        r = requests.get(url, headers=self.headers, verify=False)
        if r.status_code == 200:
            r_json = r.json()
            hosts_curr_page = [host['id'] for host in r_json['results']]
            for hn in hosts_curr_page:
                self.host_nums.append(hn)

            #if there is a next page, recurse with the url held in the 'next' field
            if r_json['next']:
                next_url = 'https://ansible.vai.org:8043' + r_json['next']
                self.get_host_nums(next_url)
            else:
                if self.all_flag == 1:
                    self.get_all_host_facts()
                else:
                    self.get_some_host_facts()

        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)

##############################################################
    
    def get_some_host_facts(self):
        count_hosts = 0
        csv_file = 'host_information_some.csv'
        check_file(csv_file)

        #FIXME index the processor to only show the first item. ansible_processor[0] = CPU name
        #create a list of column names and query dict values
        interfaces = []
        reduced_ifs = []
        column_labels = ['Server Name', 'Product Serial', 'Chassis Serial', 'Model', 'Chassis Vendor', 'System Vendor', 'Memory', 'Processor (CPU)', 'Processor Cores', 'Processor Count']
        api_queries = {'ansible_nodename':'',      
                      'ansible_product_serial':'',
                      'ansible_chassis_serial':'',
                      'ansible_product_name':'',
                      'ansible_chassis_vendor':'',
                      'ansible_system_vendor':'',
                      'ansible_memory_mb':'',
                      'ansible_processor[0]':'',
                      'ansible_processor_cores':'',
                      'ansible_processor_count':''}
        
        #iterate through all hosts
        for host_no in self.host_nums:
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            #
            if r.status_code == 200:
                server_mac_addresses = {}   #reset the server mac address dict
                r_json = r.json()           #convert the response into a json object
                interfaces = r_json['ansible_interfaces']       #retrieve all the interface names
                reduced_ifs = reduce_interfaces(interfaces)      #filter out the virtual and docker interfaces

                #get the server interfaces and final reduced interfaces
                valid_ifs = query_interfaces(server_mac_addresses, reduced_ifs, r_json)
            
                if server_mac_addresses:
                    print(r_json['ansible_nodename'])
                    for k,v in server_mac_addresses.items():
                        print(f"{k}: {v}")
                

                for key in api_queries:
                    try:
                        api_queries[key] = r_json[key]
                    except KeyError:
                        api_queries[key] = 'N/A'

                count_hosts += 1

            else:
                print(f"\nError: {r.status_code}). Exiting program...\n")
                sys.exit(1)
                
        print(f'\nNumber of hosts saved: {count_hosts}')

##############################################################
        
    def get_all_host_facts(self):
        count_hosts = 0
        csv_file = 'host_information_all.csv'
        check_file(csv_file)
        

        #retrieving information for each host
        for host_no in self.host_nums:
            #create URL based on host number and request the information
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            #convert response object to json
            if r.status_code == 200:
                r_json = r.json()
                self.host_names[host_no] = r_json['ansible_nodename']
                df = pd.json_normalize(r_json, sep=' ')

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

            else:
                print(f"\nError: {r.status_code}). Exiting program...\n")
                sys.exit(1)
                
        print(f'\nNumber of hosts saved: {count_hosts}')

############################################################################################################

signal.signal(signal.SIGINT, signal_handler)

#suppress warnings and load environment variables
urllib3.disable_warnings()
load_dotenv()

#check if environmental variable called 'TOKEN' exists. 
if 'TOKEN' in os.environ:
    TOKEN = os.getenv('TOKEN')

    all_flag = input("Do you want to retrieve all host information? (y/n): ")
    if all_flag.lower() == 'n':
        data = API_data(TOKEN=TOKEN)
        data.all_flag = 0
    else:
        data = API_data(TOKEN=TOKEN)
        data.all_flag = 1

    print("\nProcess Starting...\n")
    data.get_host_nums( url = 'https://ansible.vai.org:8043/api/v2/hosts/')
    print('Process Ended Successfully\n')
else:
    print("'TOKEN' does not exist as an evironment variable.")
    print("Initialize an environmental variable called 'TOKEN' with your bearer token. Rerun the script upon completion.\n")
