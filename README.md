# reduced-host-information
Originally a separate project, the reduced-host-information repository builds on the functionality of the original host-information repository while also adding modularity for ease of modification in the future. The reduced_host_information.py is a run-all terminal program that allows for the user to pull either all host information or a reduced amount of host information from the Ansible Tower API. The information from the CSV can be parsed for different attributes to be used at the owners disgression.

# Dependencies
1 - An updated version of python
2 - An authorization token from the Rest API set to the environment variable TOKEN
3 - Installation of packages listed in the requirements.txt

# Authorization Token
If you are an authorized party, you can generate an authorization token from the ansible tower website (https://ansible.vai.org:8043/#/home at the time of creation).

An authorization token can be set to the token environment variable by running 'export TOKEN="<your_auth_token>"'. This will set the environment variable for the lifespan of the terminal. If you wish for the token to be set permanently and used for all terminal instances, add this varaible to your ~/.bashrc or ~/.bash_profile. 

# Python Version and Dependencies


# Proceedure

# User Guide

# reduced_host_information.py functions

# host_functions.py functions

# hfa_functions.py functions

# hfs_functions.py functions
