from flask import Flask, request, jsonify
import os
import time
import threading
import core_methods
import components.printer as printer
import components.helper_methods as helper


app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def github_webhook():

    # Loads settings.conf and gets the target branch
    data = helper.return_config_param(config_file_path)
    target_branch = data.get('target_branch')

    if request.headers.get('X-GitHub-Event') == 'ping':
        return jsonify({'message': 'Received Ping Event !! Pipeline is listening...'}), 202
    if request.headers.get('X-GitHub-Event') == 'push':
        payload = request.json
        if payload['ref'] == 'refs/heads/' + target_branch:
            threading.Thread(target=pipeline, args=(payload['repository']['html_url'], target_branch)).start()
            return jsonify({'message': 'Received Push Event !! Now Executing Pipeline...'}), 200
        else:
            return jsonify({'message': 'Branch Specified in the settings doesnt match the ref branch'}), 500
    else:
        return jsonify({'message': 'Unknown GitHub event !! Error: No action has been created to handle GitHub Event: ' + request.headers.get('X-GitHub-Event')}), 500


def pipeline(github_repo, branch):
    core_methods.pre_fight_check()

    cloned_repo = core_methods.stage_one(github_repo, branch)

    core_methods.stage_two(config_file_path)

    with_secrets = core_methods.stage_three(cloned_repo)

    config_data = core_methods.stage_four()

    core_methods.stage_five(config_data)

    if not with_secrets:
        core_methods.stage_six(config_data)
    else:
        core_methods.stage_six_with_secrets(config_data)

    core_methods.clean_up(cloned_repo)


# Start the flask application that will listen for the webhooks
def launch_flask():
    app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)


# This is the main menu where you will be able to start the pipeline, edit settings, or exit program
def main_menu():
    choice = printer.print_menu(["Start Pipeline", "Edit Settings", "Exit Program"], "Main Menu")
    if choice == 1:
        launch_flask()
    if choice == 2:
        create_set_up(config_file_path)
    if choice == 3:
        exit(1)


# This will create the setting.config file it also allows you to customize the pipeline after the file is created.
def create_set_up(set_up_file):
    if os.path.isfile(set_up_file):
        print(border)
        print(printer.colorize("    Your Current Settings ", 'yellow'))
        print(border)
        printer.print_file_data(set_up_file)
        print(border)
    print("")
    with (open(set_up_file, 'w+') as file):
        pipeline_name = input(printer.colorize("Please enter the name of the pipeline: ", "magenta"))
        run_with_tests = printer.get_boolean_from_prompt("Want to run this pipeline with tests?")
        target_branch = input(printer.colorize("Enter the branch name you want to build from: ", "magenta"))
        pipeline_settings = ("{\"pipeline_name\":" + "\"" + pipeline_name + "\"," 
                             "\"run_with_tests\":" + "\"" + run_with_tests + "\","
                             "\"target_branch\":" + "\"" + target_branch + "\"}")
        file.write(pipeline_settings)
        file.close()
        time.sleep(2)
        print(printer.colorize("Set up is complete!",  "yellow"))
        main_menu()


if __name__ == '__main__':

    border = "-------------------------------"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_dir, 'settings.conf')

    if os.path.isfile(config_file_path):
        print(printer.colorize("Config file was found", 'green'))
        main_menu()
    else:
        print("NO config file was found")
        print("")
        print("Starting Set-up")
        create_set_up(config_file_path)

