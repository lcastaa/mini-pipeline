# This Python file is used to house the helper functions the main.py needs
import os
import json
import time
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp')


# ---------[ Preflight Methods ]-----------
# Helper Method One: Check for the temp dir
def check_for_temp_dir(main_file_path):
    print('[ Checking for Temp Dir ] \n')
    # Get the directory of the main.py file
    main_dir = os.path.dirname(main_file_path)
    temp_dir_path = os.path.join(main_dir, 'temp')

    # Check if the temp directory exists
    if not os.path.exists(temp_dir_path):
        print('[!!] No Temp Directory Found...Now Creating \n')
        time.sleep(2)
        os.mkdir(temp_dir_path)
        print('[oo] Temp Directory Created! Moving to next check... \n')
    else:
        print('[oo] Temp Directory Was Found! Moving to next check... \n')
    return True


# Helper Method Two : Check for Git is installed in the system
def check_for_git():
    print('[ Checking for Git ] \n')
    os.system('sudo git --version > buffer.log')
    with open('buffer.log', 'r') as output:
        if not output.read().__contains__('git version'):
            print('[!!] Git is NOT INSTALLED! \n')
            os.remove('buffer.log')
            return False
        else:
            print('[oo] Git is is INSTALLED! Moving to next check... \n')
            os.remove('buffer.log')
            return True


# Helper Method Three : Check for Docker is installed in the system
def check_for_docker():
    print('[ Checking for Docker ] \n')
    os.system('sudo docker -v > buffer.log')
    with open('buffer.log', 'r') as output:
        if not output.read().__contains__('Docker version'):
            print('[!!] Docker is NOT INSTALLED! \n')
            os.remove('buffer.log')
            return False
        else:
            print('[oo] Docker is INSTALLED! Moving to next check... \n')
            os.remove('buffer.log')
            return True


# Helper Method Four : Check for Java is installed in the system
def check_for_java():
    print('[ Checking for Java ] \n')
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True, check=True)
        output = result.stderr  # Java version info is typically in stderr
        if 'java version' in output or 'openjdk version' in output:
            print('[oo] JAVA is INSTALLED! Moving to next check... \n')
            return True
        else:
            print('[!!] JAVA is NOT INSTALLED! \n')
            return False
    except subprocess.CalledProcessError:
        print('[!!] JAVA is NOT INSTALLED! \n')
        return False


# ---------[ Pipeline Helper Methods ]----------

# Helper Method Five : Checks for Files within a directory
def check_for_file(filename, path):
    files = os.listdir(path)
    for file in files:
        if file == filename:
            return True
    return False


# Helper Method Six : Fetches Parameters found in the minipipeline.conf file
def return_config_param(config_file):
    with open(config_file, 'r', encoding='UTF-8') as file_data:
        config_data = json.loads(file_data.read())
        return config_data


# Helper Method Seven : Removes Docker image with image name from minipipeline.conf
def remove_docker_image(image_name):
    os.system('sudo docker image rm -f ' + image_name)


# Helper Method Eight : Removes Docker container with container id
def remove_docker_container(container_id):
    os.system('sudo docker container rm -f ' + container_id)


# Helper Method Nine : Checks for running containers using the image
def check_running_containers(image_name):
    # Run the Docker command and output to a temp file
    os.system('sudo docker ps -a > temp.txt')
    with open('temp.txt', 'r') as file_data:
        # Check each line for the image name
        for line in file_data:
            if image_name in line:
                os.remove('temp.txt')
                return True
    os.remove('temp.txt')
    return False


# Checks for if image exists
def check_for_docker_image(image_name):
    os.system('sudo docker image ls | grep "' + image_name + '" > temp.txt')
    with open('temp.txt', 'r') as file_data:
        image = file_data.read()
    if len(image) > 0:
        os.remove('temp.txt')
        return True
    else:
        os.remove('temp.txt')
        return False


# Helper Method Ten : Returns the container id from the running container using the image name
def get_container_id_using_image_name(image_name):
    os.system('sudo docker ps -a --filter "ancestor=' + image_name + '" | awk \'NR > 1 {print $1}\' > temp.txt')
    with open('temp.txt', 'r') as file_data:
        print(file_data)
        for line in file_data:
            container_id = line
            os.remove('temp.txt')
            return container_id
            
