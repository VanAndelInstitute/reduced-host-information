#possibly need to run pip install pandas, openpyxl, python-dotenv
import requests
import urllib3
import json
import os
import pandas as pd
from dotenv import load_dotenv

class API_data:
    def __init__(self, TOKEN):
        self.host_nums = []
        self.host_names = {}
        self.headers = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }

    #add host numbers to host_nums from each page of the API
    def get_hosts(self, url):
        r = requests.get(url, headers=self.headers, verify=False)
        if r.status_code == 200:
            r_json = r.json()
            df = pd.json_normalize(r_json['results']) #flatten the data to pull the host ids
            hosts = df['id']
            for host_no in hosts:
                self.host_nums.append(host_no)
            
            #if there is a next page, recurse with the url held in the 'next' field
            if r_json['next']:
                next_url = 'https://ansible.vai.org:8043' + r_json['next']
                self.get_hosts(next_url)
            else:
                self.get_facts()














    #retrieves the information of every host and appends it to a file called host_information.csv
    def get_facts(self):
        count_hosts = 0
        col_num = 0

        #delete old host_facts file if it exists
        csv_file = 'host_information.csv'
        if os.path.exists(csv_file) and os.path.isfile(csv_file):
            print("'host_information.csv' already exists. This file will be removed and a new one will be generated.\n")
            os.remove(csv_file)
            print("Generating new file: 'host_information.csv'\n")
        else:
            print("'host_information.csv' does not exist. Generating new file: 'host_information.csv'\n")
        
        #retrieving information for each host
        for host_no in self.host_nums:

            #create URL based on host number and request the information
            url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
            r = requests.get(url, headers=self.headers, verify=False)

            #check if status code is good for retrieval
            if r.status_code == 200:
                r_json = r.json()   #convert response object to json
                print(json.dumps(r_json, indent=2))

                #collect reduced information from the json response
                
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
                print(f"Successfully saved {server} data to host_information.csv")
                count_hosts += 1
        print(f'\nNumber of hosts saved: {count_hosts}')
















#suppress warnings and load environment variables
urllib3.disable_warnings()
load_dotenv()

#check if environmental variable called 'TOKEN' exists. 
if 'TOKEN' in os.environ:
    TOKEN = os.getenv('TOKEN')
    print("Process Starting...\n")
    data = API_data(TOKEN=TOKEN)
    data.get_hosts( url = 'https://ansible.vai.org:8043/api/v2/hosts/')
    print('Process Ended Successfully\n')
else:
    print("'TOKEN' does not exist as an evironment variable.")
    print("Initialize an environmental variable called 'TOKEN' with your bearer token. Rerun the script upon completion.\n")

#