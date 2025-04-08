# reduced-host-information Documentation
## Overview
Originally created as a separate project, reduced-host-information terminal program builds on the functionality of the original host-information repository while also adding modularity for ease of modification. This program allows for a user to pull either some or all of the host information from the Ansible Tower API and save that information to a CSV file. The information from the CSV file can be parsed for different host attributes, which can then be used at the user's disgression.

**Note:** because this repository replaces the original host-information reposity, the reduced-host-information repository is the only one that should be used.

### Dependencies
1. Python 3.12.4 or greater
2. An authorization token from the Rest API set to the environment variable 'TOKEN'
3. Installation of packages listed in the requirements.txt

### User Guide / Instructions
1. Before running the program, the user will need to set their TOKEN environment variable to their Ansible Tower API authorization token as outlined in the "Authorization Token" section.
   
2. The user can run the terminal program on their local machine, a custom virtual environment, or a docker container created from the dockerfile (recommended)
   - To run the program on a local machine or in a venv, run: "python path/to/reduced_host_information.py"
     
   - To run the program in a docker container, see the "Running the Program in a Docker Container" section
3. The program will check for the TOKEN in the user's path and ask the user if they want to retrieve all host information.
   - If the user only wants to retrieve a limited amount of information, the default values that are retrieved will be displayed to the user, and the user gets prompted if they want to retrieve more attributes (Refer to the "Getting More Attributes" section).
4. Once the above selections are made and any added data is input into the program, the program will retrieve the requested information and output it to an appropriately named CSV file.
   - It's not always guaranteed that a specifically named attribute is held within a certain host's API. The code will still check for it's existence and assign the value with 'N/A' if no attribute of that name was found. This is done to prevent the program from exiting over typos or invalid attributes.
     
   - File name example: All host information --> all_host_information.csv. Some host information --> some_host_information.csv.
     
   - These files will be placed in a folder called 'csv-files' which can be found in the same folder as the repository. The program checks for this folder's existence and automatically creates a new one if it doesn't exists.
6. The program will automatically check for files containing the same name within the csv-files folder. If a certain file name already exists, the program creates a copy of the files with an appended copy number attached to it.
   - Copy Example: all_host_information.csv exists --> all_host_information.csv(1) will be created.

### Authorization Token
If you are an authorized party, you can generate an authorization token from the ansible tower website (https://ansible.vai.org:8043/#/home at the time of creation).

An authorization token can be set to the token environment variable by running the command: 'export TOKEN="<your_auth_token>"'. This will set the environment variable for the lifespan of the terminal. If you wish for this token to be set permanently and used for all terminal instances, add this varaible to your ~/.bashrc or ~/.bash_profile. 

Alternatively the access token may also be stored in an environment file (.env) since docker commands allow for reading environment variables from files. When choosing to do this, create a .env file and write inside of it: "TOKEN=<your_auth_token>" (without the quotations).

### Running the Program in a Docker Container
A dockerfile was created for this repository so users can run the program without having to worry about conflicting dependencies. You will need to set the TOKEN environment variable as shown above in order to use it. You will need to build the image and run the container from this file to use it. Because this program writes to a directory, we need to persist this data beyond the containers lifespan by creating a docker volume (outlined in the below).

#### Building the image:
To build the docker image, run the following command: "docker build -t <image_name> <location>"
  - "-t" allows you to name the image
  - <image_tag> can be replaced by whatever you wish to name the image
  - <location> is where the image will be created

#### Running a container and mounting a docker volume:
The program will require both terminal interaction and reading from the TOKEN environment variable, so you will need to enable both in the terminal.
After you set your TOKEN environment variable, we will create and mount a volume using one of the two following methods:

  - If using an exported TOKEN variable: "docker run -it --env TOKEN=$TOKEN -v ${PWD}/<new_directory_name|existing_directory_name>/:/code/csv-files <image_name>
  - Example: docker run -it --env TOKEN=$TOKEN -v ${PWD}/my_new_dir/:/code/csv-files my_docker_image
    - "--env TOKEN=$TOKEN" will create an environment variable named TOKEN wihtin the container and will assign it to the local TOKEN environment variable set by the user

  - If using a .env file: "docker run -it --env-file <your_env_file> -v ${PWD}/<new_directory_name|existing_directory_name>/:/code/csv-files <image_name>
  - Example: docker run -it --env-file docker.env -v ${PWD}/my_new_dir/:/code/csv-files my_docker_image
    - "--env-file <your_env_file> will read the "TOKEN=<your_auth_token>" line stored within the file (outlined in the Authorization Token section) and pass it to the docker container
  
  - "-it" will run the container with an interactive terminal to get the necessary inputs when running the program
  - "--env-file <your_env_file> will read 
  -v ${PWD}/<new_directory_name|existing_directory_name>/:/code/csv-files <image_name> can be broken down as follows:
    - -v will allow us to mount a volume to a specified directory
    - ${PWD} gets the current working directory of the repository
    - <new_directory_name|existing_directory_name>/ can be either the name of an existing or non-existing directory
    - :/code/csv-files/ is where the program ran within the docker container outputs CSV files to. The names in this part of the command does not change

## Dependency / Development / Attribute Information

### Python Version and Dependency Installation
Python version 3.12.4 and pip version 25.0.1 was used within a virtual environmnent to develop the program, so these versions or later versions will be necessary to develop new features for the program. This repository contains the requirements.txt and requirements-dev.txt file. Only the packages listed in the requirements.txt is needed to run the program, but both sets of packages will be needed to modify the program.

It is recommended to install dependencies in a virtual environment or container to avoid package conflicts. To install listed dependencies, run 'pip install -r requirements.txt' and or 'pip install -r requirements-dev.txt' depending on your needs as a user.

**Note:** To simply run the program, it is recommended to follow the instructions for running the docker container above as the commands will automatically install the correct dependencies.

### Code Development/Modification
The program is designed with modularity in mind so users are free to fork the repository for their own needs. The program has been split across four modules for ease of reading and modification: one to run the code, one to handle retrieving some host facts, one to handle retrieving all host facts, and one to define functions used by other modules. It is recommended to create a virtual environment for development. In this instance, all packages from both requirements.txt and requirements-dev.txt will be needed for development.

**Note:** For any code changes to take effect in a docker container, you will need to rebuild the image and rerun the container (as shown above).

### Getting More Attributes (reduced host information)
To retrieve more than the default reduced host attributes defined by the program, you can add another attribute name that is held within the first level of the host API's json structure. For instance, if a host API's json structure contains attribute_1[first level][second level][third level], and the user wants to query for the first level of attribute_2, they can add the query attribute_2[first_level] when prompted. However, if the user wants to query for the second level of attribute 2, say attribute_2[first_level][second_level], they will need to query for attribute_2[first_level] and parse the CSV themselves for the second attribute.

Example for multi-leveled attribute 'ansible_host[A1][B1][B3]':
  - Add another attribute? (y/n):   y
  - Type attribute name (press enter to cancel):   ansible_host[A1]

For this example, we have an attribute 'ansible_host' with 3 levels of nesting in its structure: [A1], [B1], [C1]. Because the program is limited to only the first level of nesting, we can only write 'asible_host[A1]' as our new query, and will need to parse through the CSV for [B1] and [C1].

## Module Information

### reduced_host_information.py functions
This module acts as the run-all file and determines the behavior for the rest of the program. It will first disable unnecessary warnings, make a call to the check_token function, and read the user's TOKEN environment variable. If successful, the program initializes the data structure with that token and prompt the user if they wish to retrieve all information about the hosts. The program will then create a csv-files folder if it doesn't exist and make a call to either the get_some_host_facts() or the get_all_host_facts() function depending on if the all_flag was set to 0 or 1.

### host_functions.py functions
host_functions.py houses the functions that are used by reduced_host_information.py, hfa_functions.py, and hfs_functions.py to improve modularity and reduce repeated code. Functions here do not call other functions defined in this file.

### hfa_functions.py functions
hfa_functions is short for "Host Facts All Functions." This module gets called when the API_data.all_flag is set to 1. reduced_host_information.py passes the host names, host numbers, and headers as arguments to the get_all_host_facts() function. hfa_functions.py will then create a brand new csv file, iterate through each host number, make a request to that host's url, and append the retrieved data to the newly created file. 

### hfs_functions.py functions
hfa_functions is short for "Host Facts Some Functions". This module gets called when the API_data.all_flag is set to 0. reduced_host_information.py passes the host names, host numbers, and headers as arguments to the get_some_host_facts() function. hfs_functions.py will then create a brand new csv file and make a call to check_new_queries(). This function will dislpay the default attributes to the terminal and allow the user to input any new queries they wish to retrieve. The program will then iterate through each of the host numbers, retrieve the response data for the queries, retrieve and filter out the interfaces for that specific host number, and then append the information to the newly created csv. 














