#possibly need to run pip install pandas, openpyxl, python-dotenv
import sys
import signal
import requests
import urllib3
import xlsxwriter
import os
import pandas as pd
from dotenv import load_dotenv


#signal handler for interupts
def signal_handler(sig, frame):
    print('\nInterupt Caught. Exiting program...\n')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#check for csv files existence. delete if file exists and generate new file
def check_file(filepath):
    if os.path.exists(filepath) and os.path.isfile(filepath):
        print("'host_information.csv' already exists. This file will be removed and a new one will be generated.\n")
        os.remove(filepath)
        print("Generating new file: 'host_information.csv'\n")
    else:
        print("'host_information.csv' does not exist. Generating new file: 'host_information.csv'\n")

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

    
    def get_some_host_facts(self):
        count_hosts = 0
        csv_file = 'host_information_some.csv'
        self.check_file(csv_file)

        #FIXME index the processor to only show the first item. ansible_processor[0] = CPU name

        server_mac_addresses = []
        column_labels = ['Server Name', 'Product Serial', 'Chassis Serial', 'Model', 'Chassis Vendor', 'System Vendor', 'Memory', 'Processor (CPU)', 'Processor Cores', 'Processor Count']
        api_queries = {'ansible_nodename':'',      
                      'ansible_product_serial':'',
                      'ansible_chassis_serial':'',
                      'ansible_product_name':'',
                      'ansible_chassis_vendor':'',
                      'ansible_system_vendor':'',
                      'ansible_memory_mb':'',
                      'ansible_processor':'',
                      'ansible_processor_cores':'',
                      'ansible_processor_count':''}
        
        """
        row, col = 0, 0
        workbook = xlsxwriter.Workbook('host_information_some.xlsx')
        worksheet = workbook.add_worksheet()
        for label in column_labels:
            worksheet.write(row, col, label)
            col += 1

        

        for host_no in self.host_nums:
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            if r.status_code == 200:
                r_json = r.json()
                for key in api_queries:
                    try:
                        api_queries[key] = r_json[key]
                    except KeyError:
                        api_queries[key] = 'N/A'

                count_hosts += 1

            else:
                print(f"\nError: {r.status_code}). Exiting program...\n")
                sys.exit(1)
                
        print(f'\nNumber of hosts saved: {count_hosts}')"""

        
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
