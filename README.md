# reduced-host-information Documentation
## Overview
Originally created as a separate project, the reduced-host-information terminal program builds on the functionality of the original host-information repository while also adding modularity for ease of modification in the future. The reduced_host_information.py is a run-all terminal program that allows for the user to pull either all host information or a reduced amount of host information from the Ansible Tower API. The information from the CSV created by the program can be parsed for different attributes to be used at the owners disgression.

### User Guide / Instructions
1. Before running the program, the user will need to set their TOKEN environment variable to their authorization token as outlined below.
2. The user can run the terminal program with the following command 'python/python3 reduced_host_information.py'.
3. The program will check for the TOKEN in the user's path and ask the user if they want to retrieve all host information.
   - If the user only wants to retrieve a limited amount of information, the default values that will be retrieved are displayed to the user, and the user will be prompted if they want to retrieve more attributes (Refer to the getting more attributes section).
   - it is not always guaranteed an added attribute will be held within a cetain host's API. The code will check for it's existence and will assign the value with 'N/A' if none is found.
4. Once the above selections are made and any added data is input into the program, the program will retrieve the requested information and output it to an appropriately named CSV file. 
   - All host information --> all_host_information.csv. Some host information --> some_host_information.csv.
   - These files will be placed in a folder called 'csv-files' which can be found in the same folder as the repository. The program automatically check for its existence and automatically creates a new one if none exists.
5. The program will automatically check for files containing the same name within the csv-files folder. If a certain file name already exists, the program creates a copy of the files with an appended copy number attached to it.
   - all_host_information.csv exists --> all_host_information.csv(1) will be created.
  

### Dependencies
1. An updated version of python
2. An authorization token from the Rest API set to the environment variable 'TOKEN'
3. Installation of packages listed in the requirements.txt

## Token / Dependency / Modification / Attribute Information

### Authorization Token
If you are an authorized party, you can generate an authorization token from the ansible tower website (https://ansible.vai.org:8043/#/home at the time of creation).

An authorization token can be set to the token environment variable by running 'export TOKEN="<your_auth_token>"'. This will set the environment variable for the lifespan of the terminal. If you wish for this token to be set permanently and used for all terminal instances, add this varaible to your ~/.bashrc or ~/.bash_profile. 

### Python Version and Dependency Installation
Python version 3.12.4 and pip version 25.0.1 was used within a virtual environmnent to develop the program, so these versions or later versions will be necessary to run and or develop new features for the program. This repository contains the requirements.txt and requirements-dev.txt file. Only the packages listed in the requirements.txt is needed to run the program, but both sets of packages will be needed to modify the program.

It is recommended to install dependencies in a virtual environment or container to avoid package conflicts. To install listed dependencies, run 'pip install -r requirements.txt' and or 'pip install -r requirements-dev.txt' depending on your needs as a user.

### Code Modification
The program is designed with modularity in mind so users are free to fork the repository for their own needs. The program has been split across four modules for ease of reading and modification: one to run the code, one to handle gathering some host facts, one to handle generating all host facts, and one to define functions used by all other modules. It is recommended to create a virtual environment for development. Note that in this instance, all packages from both requirements.txt and requirements-dev.txt will be needed for development.

### Getting More Attributes (reduced host information)
If the user wants to retrieve more than the default attributes as defined by the program, they can add another attribute within the first level of a nested API structure. For instance, if a structure is nested as attribute[first level][second level][third level], the user can only add another query for attribute[first level].

Example for multi-leveled attribute 'ansible_host[A1][B1][B3]':
  - Add another attribute? (y/n):   y
  - Type attribute name (press enter to cancel):   ansible_host[A1]

For this example, we have an attribute 'ansible_host' with 3 levels of nesting in its structure: [A1], [B1], [C1]. Because the program is limited to only the first level of nesting, we only write 'asible_host[A1]' as our new query.


## Module Information

### reduced_host_information.py functions
This module acts as the run-all file and determines the behavior for the rest of the program. It will first disable unnecessary warnings make a call to the check_token function and read the user's TOKEN environment variable. If successful, the program then initialized the data structure with that token an prompt the user if they wish to retrieve all information about the hosts. The program will then create a csv-files folder if it doesn't exist, and make a call to either the get_some_host_facts() or the get_all_host_facts() function depending on if the all_flag was set to 0 or 1.

### host_functions.
host_functions.py houses the functions that are used by reduced_host_information.py, hfa_functions.py, and hfs_functions.py to improve modularity and reduce repeated code. It does not make any calls to other functions stored in the file.

### hfa_functions.py functions
hfa_functions is short for "Host Facts All Functions." This module gets called when the API_data.all_flag is set to 1. reduced_host_information.py passes the host names, host numbers, and headers as arguments to the get_all_host_facts() function. hfa_functions.py will then create a new csv file, iterate through each host number and make a request to that host's url, and append the retrieved data to the newly created file. 

### hfs_functions.py functions
hfa_functions is short for "Host Facts Some Functions". This module gets called when the API_data.all_flag is set to 0. reduced_host_information.py passes the host names, host numbers, and headers as arguments to the get_some_host_facts() function. hfs_functions.py will then create a new csv file and make a call to check_new_queries() to both dislpay which attributes get retrieved from the API and to allow the user to input any new queries. Once any new queries are retrieved (or skipped), the module will then iterate through each of the host numbers, retrieve the response data for the queries, retrieve and filter out the interfaces for that specific host number, and then append the information to the newly created csv. 














