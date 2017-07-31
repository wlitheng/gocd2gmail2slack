import base64
import re
import pdb

GOCD_PATTERN = (r"Stage\s*\[(\S*)\/\d*\/(\S*)\/\d*\]\s*"
                r"(passed|failed|is fixed|is broken)")
                
BASE_GIT_SSH_PATTERN = r"Git: (ssh:\/\/.*?)\\r"

REVISION_PATTERN = (r"revision: (\w+), "
                    r"modified by \w+\\\\(\w+) "
                    r"\<(.*?)\> "
                    r"on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+)\s*"
                    r"([\s\S]*)\s*modified")
        
def get_subject(message):
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            return header['value']

def get_timestamp(message):
    return message['internalDate']


def get_id(message):
    return message['id']

def get_body(message):
    encoded = message['payload']['body']['data']
    return str(base64.urlsafe_b64decode(encoded))

def get_changeset_info(body):
    result = {'id': get_changeset_id(body),
              'author': get_changeset_author(body),
              'comment': get_changeset_comment(body),
              'url': get_changeset_url(body)}
    return result

def get_changeset_url(body):
    match = re.search(BASE_GIT_SSH_PATTERN, body)
    if match:
        base_url = match.group(1)
        #replace ssh with https
        base_url = base_url.replace("ssh:", "https:")
        #replace :22 with nothing
        base_url = base_url.replace(":22", "")
        return base_url + "/commit/" + get_changeset_id(body) 

def get_changeset_id(body):
    match = re.search(REVISION_PATTERN, body)
    if match:
        return match.group(1)
    
def get_changeset_comment(body):
    match = re.search(REVISION_PATTERN, body)
    if match:
        first_pass = match.group(5)
        second_pass = first_pass.split('modified $/', 1)[0]
        third_pass = second_pass.replace("\\n", "").replace("\\r", "")
        return third_pass.strip()

def get_changeset_author(body):
    match = re.search(REVISION_PATTERN, body)
    if match:
        return match.group(2)