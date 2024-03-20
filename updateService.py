import subprocess
from os.path import dirname, abspath
import os
import time

def is_branch_behind():
    
    try:
        file_directory = dirname(abspath(__file__))
        os.chdir(file_directory)
        
        output = subprocess.check_output(['git', 'fetch'])

        # Run the git status command
        output = subprocess.check_output(['git', 'status'])
        
        # Decode the output from bytes to string
        decoded_output = output.decode("utf-8")

        # Check if the output contains the phrase indicating the branch is behind
        if "Your branch is behind" in decoded_output:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing git command:", e)
        return False

def git_pull():
    try:
        # Run the git pull command
        output = subprocess.check_output(['git', 'pull'], stderr=subprocess.STDOUT)
        
        # Decode the output from bytes to string
        decoded_output = output.decode("utf-8")
        print(decoded_output)

    except subprocess.CalledProcessError as e:
        # If an error occurs, print the output and return False
        print("An error occurred while executing git pull:", e.output.decode("utf-8"))
        return False

    return True
