import sys
import requests
import pandas as pd
import host_functions

def write_to_csv(host_page_df, filepath):
    host_page_df.to_csv(filepath, mode='a')
    

def current_host_facts(host_name, r_json, filepath):

    #convert the response to a dataframe to flatten the data
    host_page_df = pd.json_normalize(r_json, sep=':  ', max_level=8)
    host_name_labels = [':   ' + host_name] * len(host_page_df.columns)

    #insert the names of the servers for every line
    host_page_df.loc[1] = host_name_labels

    #sort the labels and transpose columns to rows of data
    host_page_df = host_page_df.T

    #write to a new csv file
    write_to_csv(host_page_df, filepath)


def get_all_host_facts(host_names, host_nums, headers):

    #initialize filename for csv
    filename = "all_host_information.csv"

    #create a filepath and change the filename if needed
    filepath = host_functions.check_filepath(filename)

    #retrieving information for each host
    progress = 0
    for host_no in host_nums:
        #create URL based on host number and request the information
        url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
        r = requests.get(url, headers=headers, verify=False)
        host_name = host_names[str(host_no)]

        #convert response object to json
        if r.status_code == 200:
            r_json = r.json()
            try:
                current_host_facts(host_name=host_name, r_json=r_json, filepath=filepath)
                progress += 1

                host_functions.progress_bar(progress, len(host_nums))
            except Exception as e:
                print(e)
        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)

    print(f"\n\nFile saved as: {filepath}\n")