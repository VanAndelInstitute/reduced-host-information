


def query_interfaces(infs, r_json):
    mac_addresses = {}
    for inf in infs:                    
        mac_query = f'ansible_{inf}'
        try:
            mac_address = r_json[mac_query]['macaddress']
            mac_addresses[inf] = mac_address
        except:
            infs.remove(inf)
            continue
    return mac_addresses





def get_some_host_facts(self):
    count_hosts = 0
    csv_file = 'host_information_some.csv'
    check_file(csv_file)

    #FIXME index the processor to only show the first item. ansible_processor[0] = CPU name
    #create a list of column names and query dict values
    interfaces = []
    column_labels = ['Server Name', 'Product Serial', 'Chassis Serial', 'Model', 'Chassis Vendor', 'System Vendor', 'Memory', 'Processor (CPU)', 'Processor Cores', 'Processor Count']
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

        #
        if r.status_code == 200:
            server_mac_addresses = {}   #reset the server mac address dict
            r_json = r.json()           #convert the response into a json object
            interfaces = r_json['ansible_interfaces']       #retrieve all the interface names

            filtered_ifs = reduce_interfaces(interfaces)      #filter out the virtual and docker interfaces
            server_mac_addresses = query_interfaces(infs=filtered_ifs, r_json=r_json)   #create a map with all the server affresses
        
            if server_mac_addresses:           
                print(r_json['ansible_nodename'])
                for k,v in server_mac_addresses.items():
                    print(f"{k}: {v}")
            

            for key in api_queries:
                try:
                    api_queries[key] = r_json[key]
                except KeyError:
                    api_queries[key] = 'N/A'

            count_hosts += 1

        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)
            
    print(f'\nNumber of hosts saved: {count_hosts}')
