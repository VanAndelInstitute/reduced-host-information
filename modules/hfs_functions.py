import sys
import csv
import requests
import host_functions

def write_to_csv(query_map, filepath):

    with open(filepath, 'a+') as csvfile:
        csvwriter = csv.writer(csvfile)

        rows = []
        for k,v in query_map.items():
            rows.append([k, v])
        rows.append("\n")

        csvwriter.writerows(rows)
        csvwriter.writerow(["\n"])

def check_answer(another_query=''):

    valid_answers = ['y','n']
    while another_query.lower() not in valid_answers:
        another_query = input("\nAdd another attribute? (y/n):  ")

    return another_query


def check_new_queries():
    queries = {}
    attr_names = ['ansible_nodename', 'ansible_product_serial', 'ansible_chassis_serial', 'ansible_product_name', 'ansible_chassis_vendor',
                  'ansible_system_vendor', 'ansible_memory_mb', 'ansible_processor', 'ansible_processor_cores', 'ansible_processor_count']

    print("The values of these attribute names from the Anisble Tower APi will be retrieved:")
    for a in attr_names:
        print(a)

    #initialize another_query
    another_query = check_answer()

    #get the attribute name if another_query = yes
    while another_query.lower() == 'y':
        attr_name = input("Type attribute name: ")
        queries[attr_name] = ''
        
        #reset and check for another attribute and reloop if yes
        another_query = check_answer()

    return queries

def current_host_facts(host_names, added_queries, response, host_no):

    host_names[host_no] = response['ansible_nodename']
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

    for k, v in added_queries.items():
        api_queries[k] = v

    for k in api_queries.keys():
        try:
            if k == 'ansible_memory_mb':
                api_queries[k] = response[k]['real']['total']
            elif k == "ansible_processor":
                api_queries[k] = response[k][2]
            else:
                api_queries[k] = response[k]
        except:
            api_queries[k] = 'N/A'

    return api_queries

def get_some_host_facts(host_names, host_nums, headers):
    interfaces = []
    reduced_ifs = []

    #initialize filename for csv
    filename = "some_host_information.csv"

    #create the filepath and change the filename if needed
    filepath = host_functions.check_filepath(filename)

    #initialize default queries
    added_queries = check_new_queries()

    #iterate through all hosts
    progress = 0
    for host_no in host_nums:

        server_mac_addresses = {}   #reset the server mac address dictionary

        #get URL for specific host
        url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
        r = requests.get(url, headers=headers, verify=False)

        #check for valid http request, process querying for the mac addresses and API values
        if r.status_code == 200:
            r_json = r.json()

            #get facts for the current node
            api_queries = current_host_facts(host_names, added_queries, r_json, host_no)

            #get all interface names for current node
            interfaces = r_json['ansible_interfaces']

            #filter out the virtual and docker interfaces
            reduced_ifs = host_functions.reduce_interfaces(interfaces)

            #get the server interfaces and final reduced interfaces
            host_functions.query_interfaces(server_mac_addresses, reduced_ifs, r_json)

            #add interfaces to api_queries
            for k,v in server_mac_addresses.items():
                api_queries[k] = v

            #append the reduced information to host_information.csv
            write_to_csv(query_map=api_queries, filepath=filepath)

            progress += 1
            host_functions.progress_bar(progress, len(host_nums))

        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)
