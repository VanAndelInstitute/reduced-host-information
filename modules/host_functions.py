import os
import sys
import requests

#check if environmental variable called 'TOKEN' exists. 
def check_token():
    if 'TOKEN' in os.environ:
        return os.getenv('TOKEN')
    else:
        print("'TOKEN' does not exist as an evironment variable.")
        print("Initialize an environmental variable called 'TOKEN' with your bearer token. Rerun the script upon completion.")
        print("Exiting program...\n")
        exit(1)


def check_file(filepath):
    if os.path.exists(filepath) and os.path.isfile(filepath):
        print(f"{filepath} already exists. This file will be removed and a new one will be generated.\n")
        os.remove(filepath)
        print(f"Generating new file: '{filepath}\n")
    else:
        print(f"{filepath} does not exist. Generating new file: {filepath}\n")


def init_api_data_structure(token, API_data_var):
    all_flag = input("Do you want to retrieve all host information? (y/n): ")
    data = API_data_var(TOKEN=token)

    if all_flag.lower() == 'n':
        data.all_flag = 0
    else:
        data.all_flag = 1

    return data


def reduce_interfaces(interfaces):
    skip_lst = ['v', 'd']

    for interface in interfaces:
        if interface[0] in skip_lst:
            interfaces.remove(interface)
        else:
            print(interface[0])

    return interfaces


def query_interfaces(server_mac_addresses, reduced_ifs, r_json):
    for intf in reduced_ifs:                    
        mac_query = f'ansible_{intf}'
        try:
            mac_address = r_json[mac_query]['macaddress']
            server_mac_addresses[intf] = mac_address
        except:
            continue

####################################################################################

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


def create_csv():
    csv_file = 'host_information_some.csv'
    check_file(csv_file)
    column_labels = ['Server Name', 'Product Serial', 'Chassis Serial', 'Model', 'Chassis Vendor', 'System Vendor', 'Memory', 'Processor (CPU)', 'Processor Cores', 'Processor Count']
