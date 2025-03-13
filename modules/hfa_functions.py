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
