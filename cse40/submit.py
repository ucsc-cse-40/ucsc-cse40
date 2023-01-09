"""
Handles submission of student code to the autograder.
"""

import argparse
import json
import sys
import urllib.request

import cse40.assignment
import cse40.code

ENCODING = 'utf-8'
DEFAULT_CONFIG_PATH = 'config.json'
DEFAULT_SUBMISSION_PATH = 'assignment.ipynb'
DEFAULT_AUTOGRADER_URL = 'http://sozopol.soe.ucsc.edu:12345'

def submit_notebook(config_path = DEFAULT_CONFIG_PATH, submission_path = DEFAULT_SUBMISSION_PATH,
        autograde_url = DEFAULT_AUTOGRADER_URL):
    source_code = cse40.code.extract_code(submission_path)

    with open(config_path, 'r') as file:
        config = json.load(file)

    config['task'] = 'grade'
    config['code'] = source_code

    payload = bytes(json.dumps(config), ENCODING)
    raw_response = urllib.request.urlopen(autograde_url, data = payload)

    status = raw_response.status
    if (status != 200):
        print("Got a failure status from the autograding server: %s." % (status))
        return None

    body = json.loads(raw_response.read().decode(encoding = ENCODING))

    if (body['status'] != 'success'):
        return (False, body['message'])

    return (True, cse40.assignment.Assignment.from_dict(body['assignment']))

def main(arguments):
    (success, result) = submit_notebook(arguments.config_path, arguments.submission_path,
            arguments.server)

    if (not success):
        print('The autograder failed to grade your assignment.')
        print('Message from the autograder: ' + result)
        sys.exit(1)

    print('The autograder successfully graded your assignment.')
    print(result.report())
    sys.exit(0)

def _load_args(args):
    parser = argparse.ArgumentParser(description = 'Submit a notebook to the autograding server.')

    parser.add_argument('--config', dest = 'config_path',
        action = 'store', type = str, default = DEFAULT_CONFIG_PATH,
        help = 'The JSON config file with your authentication details.')

    parser.add_argument('--submission', dest = 'submission_path',
        action = 'store', type = str, default = DEFAULT_SUBMISSION_PATH,
        help = 'Your submission.')

    parser.add_argument('--server', dest = 'server',
        action = 'store', type = str, default = DEFAULT_AUTOGRADER_URL,
        help = 'The URL of the server to submit to.')

    return parser.parse_args()

if (__name__ == '__main__'):
    main(_load_args(sys.argv))
