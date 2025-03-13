import os

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
    valid_ifs = []

    for intf in reduced_ifs:                    
        mac_query = f'ansible_{intf}'
        try:
            mac_address = r_json[mac_query]['macaddress']
            server_mac_addresses[intf] = mac_address
            valid_ifs.append(intf)
        except:
            continue

    return valid_ifs

