import host_functions
import hfs_functions
import hfa_functions
import sys
import signal
import requests
import urllib3
import time
from dotenv import load_dotenv

#signal hander for keyboard interrupts
def signal_handler(sig, frame):
    time.sleep(0.1)
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
        #initialize the host_names and host_nums
        for host in response['results']:
            self.host_names[f"{host['id']}"] = host['name']
            self.host_nums.append(host['id'])

        #sort all the host numbers
        self.host_nums.sort()

        #check next page of hosts
        self.check_next_page(response)

    #if there is a next page, recurse with the url held in the 'next' field
    def check_next_page(self, response):
        if response['next']:
            next_url = 'https://ansible.vai.org:8043' + response['next']
            self.get_host_nums(next_url)


if __name__ == "__main__":

    #initialize signal handler and supress warnings
    signal.signal(signal.SIGINT, signal_handler)
    urllib3.disable_warnings()
    load_dotenv()

    #retrieve API token and initialize url, and API_data data structure with token
    TOKEN = host_functions.check_token()
    data = host_functions.init_api_data_structure(token=TOKEN, API_data_var=API_data)
    url = 'https://ansible.vai.org:8043/api/v2/hosts/'

    #let user know process is starting
    print("\nProcess Starting...\n")

    #check if the csv-files folder exists
    host_functions.check_folders()

    #get every host number from the API
    data.get_host_nums(url)

    #get host facts based on if user wants some or all facts
    if data.all_flag == 1:
        hfa_functions.get_all_host_facts(data.host_names, data.host_nums, data.headers)
    else:
        hfs_functions.get_some_host_facts(data.host_names, data.host_nums, data.headers)

    #if here then process was successful
    print('Shutting Down Process...')