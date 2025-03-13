import os
import sys
import requests
import pandas as pd
import host_functions

def get_all_host_facts(host_names, host_nums, headers):

    #retrieving information for each host
    for host_no in host_nums:
        #create URL based on host number and request the information
        url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
        r = requests.get(url, headers=headers, verify=False)

        #convert response object to json
        if r.status_code == 200:
            r_json = r.json()
            try:
                get_curr_host_facts(host_names=host_names, host_no=host_no, response=r_json)
            except:
                print("Error: Couldn't save host information")
        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)


def get_curr_host_facts(host_names, host_no, response):

    host_names[host_no] = response['ansible_nodename']
    df = pd.json_normalize(response, sep=' ')
    print(df)

