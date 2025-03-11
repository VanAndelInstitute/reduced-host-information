#possibly need to run pip install pandas, openpyxl, python-dotenv
import os
import sys
import csv
import signal
import requests
import urllib3
import pandas as pd
from dotenv import load_dotenv

#signal hander for keyboard interrupts
def signal_handler(sig, frame):
    print('\nInterupt Caught. Exiting program...\n')
    sys.exit(0)

############################################################################################################

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

    #get all the hosts from the curretly "visible" page
    def get_curr_page_hosts(self, response):
        hosts_curr_page = [host['id'] for host in response['results']]
        for hn in hosts_curr_page:
            self.host_nums.append(hn)

        self.check_next_page(response)

    #if there is a next page, recurse with the url held in the 'next' field
    def check_next_page(self, response):
        if response['next']:
            next_url = 'https://ansible.vai.org:8043' + response['next']
            self.get_host_nums(next_url)
        else:
            if self.all_flag == 1:
                self.get_all_host_facts()
            else:
                self.get_some_host_facts()

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
        check_file(csv_file)

        #FIXME index the processor to only show the first item. ansible_processor[0] = CPU name
        #create a list of column names and query dict values
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

            #check for valid http request, process querying for the mac addresses and API values
            if r.status_code == 200:
                server_mac_addresses = {}   #reset the server mac address dict
                r_json = r.json()           #convert the response into a json object

                #retrieve all the interface names
                interfaces = r_json['ansible_interfaces']

                #filter out the virtual and docker interfaces
                reduced_ifs = reduce_interfaces(interfaces)

                #get the server interfaces and final reduced interfaces
                valid_ifs = query_interfaces(server_mac_addresses, reduced_ifs, r_json)

                #map the api queries to their corresponding values in the RESTAPI
                map_api_queries(api_queries, r_json)

                #open csv file and create writer object
                with open(csv_file, mode='a', newline=' ') as file:
                    writer = csv.writer(file)

                #write headers
                writer.writerow(column_labels)

            #print statements for server information
                if server_mac_addresses:
                    print("\n" + r_json['ansible_nodename'])
                    for k,v in server_mac_addresses.items():
                        print(f"{k}: {v}")

                if api_queries:
                    print("\n" + "api queries:")
                    for k, v in api_queries.items():
                        print(f"{k}: {v}")

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

TOKEN = check_token()
data = init_api_data_structure(token=TOKEN)
url = 'https://ansible.vai.org:8043/api/v2/hosts/'

print("\nProcess Starting...\n")
data.get_host_nums(url = url)
print('Process Ended Successfully\n')
