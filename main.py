from flask import Flask, request, jsonify
import core_methods
import threading


app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def github_webhook():

    if request.headers.get('X-GitHub-Event') == 'ping':
        return jsonify({'message': 'Received Ping Event !! Pipeline is listening...'}), 202

    if request.headers.get('X-GitHub-Event') == 'push':
        payload = request.json
        threading.Thread(target=pipeline, args=(payload['repository']['html_url'],)).start()
        return jsonify({'message': 'Received Push Event !! Now Executing Pipeline...'}), 200

    else:
        return jsonify({'message': 'Unknown GitHub event !! Error: No action has been created to handle GitHub Event: ' + request.headers.>


# This is the actual Pipeline You can add stages in the core_methods
def pipeline(github_repo):
    core_methods.pre_fight_check()
    cloned_repo = core_methods.stage_one(github_repo)
    core_methods.stage_two()
    with_secrets = core_methods.stage_three(cloned_repo)
    config_data = core_methods.stage_four()
    core_methods.stage_five(config_data)
    if not with_secrets:
        core_methods.stage_six(config_data)
    else:
        core_methods.stage_six_with_secrets(config_data)
    core_methods.clean_up(cloned_repo)


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=3000, debug=False, use_reloader=False)
