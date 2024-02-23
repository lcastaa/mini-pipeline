# Core Stage Methods for the Pipeline
from components import helper_methods
from components import printer
import os
import time
import shutil


# Is responsible for checking the environment before executing the pipeline
def pre_fight_check():
    time.sleep(5)
    print(printer.colorize('---------- [ Running Preflight Check ] ---------- \n', "yellow"))
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
    print(printer.colorize('---------- [Stage One: Clone Repository ] ---------- \n', "yellow"))
    time.sleep(4)
    print(printer.colorize('[oo] Cloning Repo: ' + github_repo + "\n", "green"))
    os.chdir("./temp")
    os.system("git clone -b" + branch + " " + github_repo)
    print('\n[oo] Moving into cloned repository... \n')
    items_in_directory = os.listdir(os.getcwd())
    directories = [item for item in items_in_directory if os.path.isdir(item)]
    if directories:
        cloned_repo = directories[0]
    else:
        # Handle the case where no directories are found
        print(printer.colorize("No repository directory found.", 'red'))
        exit(1)
    os.chdir(cloned_repo)
    return cloned_repo


# Stage Two: Build Project with MVMW Script Stage
def stage_two(settings_file):

    # Loads settings data to see if we want to run with tests
    data = helper_methods.return_config_param(settings_file)
    trigger = data.get('run_with_tests')

    print('Trigger is: ' + trigger)

    print(printer.colorize('---------- [Stage Two: Build Project ] ---------- \n', "yellow"))
    for file in os.listdir(os.getcwd()):
        # If the file name equal mvnw which is the build script
        if file == 'mvnw':
            if trigger == 'False':
                # Execute the build script without tests
                os.system('bash ./' + file + ' install -DskipTests')
            elif trigger == "True":
                os.system('bash ./' + file + ' install')
            else:
                print(printer.colorize('No testing trigger was found, exiting...', 'red'))
    print(printer.colorize('\n[oo] Project Successfully build with MVNW Script...', 'green'))
    print(printer.colorize('[oo] Proceeding to next stage...\n', 'magenta'))
    pass


# Stage Three: Check for Pipeline Files Stage
def stage_three(cloned_repo):
    print(printer.colorize('---------- [Stage Three: Checking for Required Files in repository ] ---------- \n','yellow'))
    if helper_methods.check_for_file('minipipe.json', os.getcwd()):
        print(printer.colorize('[oo] minipipe.json FOUND...', 'green'))
        pass
    if helper_methods.check_for_file('dockerfile', os.getcwd()):
        print(printer.colorize('[oo] dockerfile FOUND...', 'green'))
        pass
        # Else abort the pipeline build and clean up temp dir
    else:
        print(printer.colorize('[!!] No minipipe or dockerfile FOUND ABORTING build...', 'red'))
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
        print(printer.colorize("[oo] A Secret was found... \n", 'green'))
        os.chdir(cloned_repo)
        print(printer.colorize('[oo] All Files Found Proceeding to next stage...\n', 'magenta'))
        return True
    # if secrets not found go back into the cloned repo and return false
    print(printer.colorize("[oo] No Secret was found... \n", 'red'))
    os.chdir(cloned_repo)
    print(printer.colorize('[oo] All Files Found Proceeding to next stage...\n', 'magenta'))
    return False


# Stage Four: Locate Output Build File and Move
def stage_four():
    print(printer.colorize('---------- [Stage Four: Locate Output Build File and Move] ---------- \n', 'yellow'))
    config_data = helper_methods.return_config_param('minipipe.json')
    output_jar = config_data.get('output_filename')
    print(printer.colorize('[oo] Moving into target directory...', 'cyan'))
    os.chdir('target')
    print('[oo] Looking for output file: ' + output_jar)
    for file in os.listdir():
        if file == output_jar + '.jar':
            print(printer.colorize('[oo] Output File was Located...', 'green'))
            shutil.copy(file, '../' + output_jar + '.jar')
            print(printer.colorize('[oo] Output File was Moved to Root Directory...', 'cyan'))
    # Move back to the root of the cloned repo
    print(printer.colorize('[oo] Moving Back to Root Directory...', 'cyan'))
    print(printer.colorize('[oo] Proceeding to next stage...\n', 'magenta'))
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    return config_data


# Stage Five: Docker Image Construction Stage
def stage_five(config_data):
    print(printer.colorize('---------- [ Stage Five: Docker Image Construction Stage ] ---------- \n', 'yellow'))
    image_name = config_data.get('image_name')
    # Find Docker Containers with img name
    print(printer.colorize('[oo] Looking for Containers Using Image: ' + image_name, "cyan"))
    if helper_methods.check_running_containers(image_name):
        # If there is containers remove them then remove image
        container_id = helper_methods.get_container_id_using_image_name(image_name)
        print(printer.colorize('[oo] Container with ID: ' + container_id + ' was FOUND...', 'green'))
        print(printer.colorize('[oo] Now Removing Container...', 'cyan'))
        helper_methods.remove_docker_container(container_id)
        print(printer.colorize('[oo] Container Removed...', 'cyan'))
        print(printer.colorize('[oo] Now Removing Image...', 'cyan'))
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
    print(printer.colorize('[oo] Image built proceeding to the next stage...\n', 'magenta'))
    pass


# Stage Six: Docker Container Deployment Stage without environment variable
def stage_six(config_data):
    container_name = config_data.get('container_name')
    image_name = config_data.get('image_name')
    args = config_data.get('args')
    print(printer.colorize('---------- [ Stage Six: Docker Container Deployment Stage ] ---------- \n', 'yellow'))
    time.sleep(2)
    print(printer.colorize('[oo] Now Deploying Containers...', 'cyan'))
    time.sleep(2)
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    os.system('sudo docker run ' + args + ' --name ' + container_name + ' ' + image_name)
    print(printer.colorize("[oo] Container has been deployed...", 'green'))
    print(printer.colorize("[oo] Proceeding to clean up...\n", 'yellow'))
    pass


# Stage Six: Docker Container Deployment Stage if you have environment variable
def stage_six_with_secrets(config_data):
    container_name = config_data.get('container_name')
    image_name = config_data.get('image_name')
    args = config_data.get('args')
    print(printer.colorize('---------- [ Stage Six: Docker Container Deployment Stage ] ---------- \n', 'yellow'))
    time.sleep(2)
    print(printer.colorize('[oo] Now Deploying Containers...', 'cyan'))
    time.sleep(2)
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    secret_data = helper_methods.return_config_param('secrets.json')
    secret = secret_data.get('KEY')
    os.system('sudo docker run -e \'KEY=' + secret + '\' ' + args + ' --name ' + container_name + ' ' + image_name)
    print(printer.colorize("[oo] Container has been deployed...", 'green'))
    print(printer.colorize("[oo] Proceeding to clean up...\n", 'yellow'))
    pass


# Is Responsible for cleaning up after pipeline
def clean_up(cloned_repo):
    print(printer.colorize('---------- [ Cleaning up ] ---------- \n', 'yellow'))
    shutil.rmtree(cloned_repo)
    print(printer.colorize('[oo] Clean Complete...', "green"))
    print(printer.colorize('[oo] Ready for next build...\n', 'yellow'))
    os.chdir(os.path.join(os.getcwd(), os.pardir))
    print(os.getcwd())
    pass
