# Core Stage Methods for the Pipeline
from components import helper_methods
import os
import time
import shutil


# Is responsible for checking the environment before executing the pipeline
def pre_fight_check():
    time.sleep(5)
    print('---------- [ Running Preflight Check ] ---------- \n')
    if not helper_methods.check_for_temp_dir(os.path.dirname(os.path.abspath(__file__))):
        print('A Fatal Error Occurred...')
        exit(100)
    if not helper_methods.check_for_git():
        exit(101)
    if not helper_methods.check_for_java():
        exit(102)
    if not helper_methods.check_for_docker():
        exit(103)
    pass


# Stage One: Clone Repository Stage
def stage_one(github_repo, branch):
    print('---------- [Stage One: Clone Repository ] ---------- \n')
    time.sleep(4)
    print('[oo] Cloning Repo: ' + github_repo + "\n")
    os.chdir("./temp")
    os.system("git clone -b" + branch + " " + github_repo)
    print('\n[oo] Moving into cloned repository... \n')
    items_in_directory = os.listdir(os.getcwd())
    directories = [item for item in items_in_directory if os.path.isdir(item)]
    if directories:
        cloned_repo = directories[0]
    else:
        # Handle the case where no directories are found
        print("No repository directory found.")
        exit(1)
    os.chdir(cloned_repo)
    return cloned_repo


# Stage Two: Build Project with MVMW Script Stage
def stage_two():
    print('---------- [Stage Two: Build Project ] ---------- \n')
    for file in os.listdir(os.getcwd()):
        # If the file name equal mvnw which is the build script
        if file == 'mvnw':
            # Execute the build script without tests
            os.system('bash ./' + file + ' install -DskipTests')
    print('\n[oo] Project Successfully build with MVNW Script...')
    print('[oo] Proceeding to next stage...\n')
    pass


# Stage Three: Check for Pipeline Files Stage
def stage_three(cloned_repo):
    print('---------- [Stage Three: Checking for Required Files in repository ] ---------- \n')
    if helper_methods.check_for_file('minipipe.json', os.getcwd()):
        print('[oo] minipipe.json FOUND...')
        pass
    if helper_methods.check_for_file('dockerfile', os.getcwd()):
        print('[oo] dockerfile FOUND...')
        pass
        # Else abort the pipeline build and clean up temp dir
    else:
        print('[!!] No minipipe or dockerfile FOUND ABORTING build...')
        time.sleep(2)
        print('[!!] Removing temp files...')
        # Change to the prent directory
        os.chdir(os.path.join(os.getcwd(), os.pardir))
        shutil.rmtree(cloned_repo)
        print('[!!] Exiting process...\n')
        exit(201)
    # Goes out to from inside the cloned repo to the temp folder
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    # Checks for secrets
    print("[oo] Now checking for secrets... \n")
    if helper_methods.check_for_file('secrets.json', os.getcwd()):
        # if secrets found go back into the cloned repo and return true
        print("[oo] A Secret was found... \n")
        os.chdir(cloned_repo)
        print('[oo] All Files Found Proceeding to next stage...\n')
        return True
    # if secrets not found go back into the cloned repo and return false
    print("[oo] No Secret was found... \n")
    os.chdir(cloned_repo)
    print('[oo] All Files Found Proceeding to next stage...\n')
    return False


# Stage Four: Locate Output Build File and Move
def stage_four():
    print('---------- [Stage Four: Locate Output Build File and Move] ---------- \n')
    config_data = helper_methods.return_config_param('minipipe.json')
    output_jar = config_data.get('output_filename')
    print('[oo] Moving into target directory...')
    os.chdir('target')
    print('[oo] Looking for output file: ' + output_jar)
    for file in os.listdir():
        if file == output_jar + '.jar':
            print('[oo] Output File was Located...')
            shutil.copy(file, '../' + output_jar + '.jar')
            print('[oo] Output File was Moved to Root Directory...')
    # Move back to the root of the cloned repo
    print('[oo] Moving Back to Root Directory...')
    print('[oo] Proceeding to next stage...\n')
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    return config_data


# Stage Five: Docker Image Construction Stage
def stage_five(config_data):
    print('---------- [ Stage Five: Docker Image Construction Stage ] ---------- \n')
    image_name = config_data.get('image_name')
    # Find Docker Containers with img name
    print('[oo] Looking for Containers Using Image: ' + image_name)
    if helper_methods.check_running_containers(image_name):
        # If there is containers remove them then remove image
        container_id = helper_methods.get_container_id_using_image_name(image_name)
        print('[oo] Container with ID: ' + container_id + ' was FOUND...')
        print('[oo] Now Removing Container...')
        helper_methods.remove_docker_container(container_id)
        print('[oo] Container Removed...')
        print('[oo] Now Removing Image...')
        helper_methods.remove_docker_image(image_name)
        pass
    # If no containers are found then remove image
    else:
        print('[oo] No Containers were Using Image: ' + image_name)
        helper_methods.remove_docker_image(image_name)
    # then build the image
    print('[oo] Now Building Image...')
    time.sleep(2)
    os.system('sudo docker build --no-cache -t ' + image_name + ' .')
    print('[oo] Image built proceeding to the next stage...\n')
    pass


# Stage Six: Docker Container Deployment Stage without environment variable
def stage_six(config_data):
    container_name = config_data.get('container_name')
    image_name = config_data.get('image_name')
    args = config_data.get('args')
    print('---------- [ Stage Six: Docker Container Deployment Stage ] ---------- \n')
    time.sleep(2)
    print('[oo] Now Deploying Containers...')
    time.sleep(2)
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    os.system('sudo docker run ' + args + ' --name ' + container_name + ' ' + image_name)
    print("[oo] Container has been deployed...")
    print("[oo] Proceeding to clean up...\n")
    pass


# Stage Six: Docker Container Deployment Stage if you have environment variabl=-0r
def stage_six_with_secrets(config_data):
    container_name = config_data.get('container_name')
    image_name = config_data.get('image_name')
    args = config_data.get('args')
    print('---------- [ Stage Six: Docker Container Deployment Stage ] ---------- \n')
    time.sleep(2)
    print('[oo] Now Deploying Containers...')
    time.sleep(2)
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    secret_data = helper_methods.return_config_param('secrets.json')
    secret = secret_data.get('KEY')
    os.system('sudo docker run -e \'KEY=' + secret + '\' ' + args + ' --name ' + container_name + ' ' + image_name)
    print("[oo] Container has been deployed...")
    print("[oo] Proceeding to clean up...\n")
    pass


# Is Responsible for cleaning up after pipeline
def clean_up(cloned_repo):
    print('---------- [ Cleaning up ] ---------- \n')
    shutil.rmtree(cloned_repo)
    print('[oo] Clean Complete...')
    print('[oo] Ready for next build...\n')
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    print(os.getcwd())
    pass
