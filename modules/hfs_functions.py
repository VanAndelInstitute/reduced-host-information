import os
import sys
import requests
import pandas as pd
import host_functions

def get_some_curr_host_facts(host_names, response, host_no):

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

    host_names[host_no] = response['ansible_nodename']
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

def get_some_host_facts(host_names, host_nums, headers):
    interfaces = []
    reduced_ifs = []

    #iterate through all hosts
    for host_no in host_nums:

        api_queries = {}    #reset api_queries to empty
        server_mac_addresses = {}   #reset the server mac address dictionary

        #get URL for specific host
        url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
        r = requests.get(url, headers=headers, verify=False)

        #check for valid http request, process querying for the mac addresses and API values
        if r.status_code == 200:
            r_json = r.json()

            #get facts for the current node
            api_queries = get_some_curr_host_facts(host_names, r_json, host_no)

            #get all interface names for current node
            interfaces = r_json['ansible_interfaces']

            #filter out the virtual and docker interfaces
            reduced_ifs = host_functions.reduce_interfaces(interfaces)

            #get the server interfaces and final reduced interfaces
            host_functions.query_interfaces(server_mac_addresses, reduced_ifs, r_json)

            #FIXME: APPEND DATA TO A CSV FILE

        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)
            
    print(f'\nNumber of hosts saved: {count_hosts}')