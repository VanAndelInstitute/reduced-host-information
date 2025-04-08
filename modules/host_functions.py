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

def check_folders():
    folder_name = "csv-files"

    if not os.path.exists(folder_name):
        try:
            os.mkdir(folder_name)
        except Exception as e:
            print(e)


def check_filepath(filename):
    #initialize filename for csv
    filepath = os.path.join("csv-files",filename)
    filenum = 0

    while os.path.exists(filepath):
        filenum += 1
        filepath = os.path.join("csv-files",f"{filename}({filenum})")

    return filepath

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

    return interfaces


def query_interfaces(server_mac_addresses, reduced_ifs, r_json):
    for intf in reduced_ifs:                    
        mac_query = f'ansible_{intf}'
        try:
            mac_address = r_json[mac_query]['macaddress']
            server_mac_addresses[intf] = mac_address
        except:
            continue


def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '#' * int(percent) + '-' * (100 - int(percent))
    print(f"\r[{bar}] {percent:.2f}%", end="\r")