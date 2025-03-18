import os
import sys
import csv
import requests
import pandas as pd
import host_functions

def write_to_csv(host_page_df):
    filename = "all_host_information.csv"
    filepath = os.path.join("csv-files",filename)

    filenum = 0
    while os.path.exists(filepath):
        filenum += 1
        filepath = os.path.join("csv-files",f"{filename}({filenum})")

    host_page_df.to_csv(filepath, index=False)

def current_host_facts(response):

    #convert the response to a dataframe to flatten the data
    host_page_df = pd.json_normalize(response, sep=' ')

    #create a list of hostnames = in length to the number of colums to associate with the value
    new_top_row = pd.DataFrame([response['ansible_nodename'] * len(host_page_df.columns)])
    host_page_df = pd.concat([new_top_row, host_page_df]).reset_index(drop=True)
    
    #write to a new csv file
    write_to_csv(host_page_df)

#FIXME: dynamically get the host numbers to be used for the getting the data
def get_all_host_facts(host_nums, headers):

    #retrieving information for each host
    progress = 0
    for host_no in host_nums:
        #create URL based on host number and request the information
        url = f'https://ansible.vai.org:8043/api/v2/hosts/{host_no}/ansible_facts'
        r = requests.get(url, headers=headers, verify=False)

        #convert response object to json
        if r.status_code == 200:
            r_json = r.json()
            try:
                current_host_facts(response=r_json)
                progress += 1

                #FIXME: make sure there is numbers passed into this function
                host_functions.progress_bar(progress, len(host_nums))
            except:
                print("Error: Couldn't save host information")
        else:
            print(f"\nError: {r.status_code}). Exiting program...\n")
            sys.exit(1)

