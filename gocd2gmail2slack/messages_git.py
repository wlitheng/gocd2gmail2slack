import base64
import re
import pdb

GOCD_PATTERN = (r"Stage\s*\[(\S*)\/\d*\/(\S*)\/\d*\]\s*"
                r"(passed|failed|is fixed|is broken)")
                
BASE_GIT_SSH_PATTERN = r"Git: ssh:\/\/(?:.*?@)?(.*?)\\r"

REVISION_PATTERN = (r"revision: (\w+), "
                    r"modified by (.*?) "
                    r"\<(.*?)\> "
                    r"on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+)\s*"
                    r"([\s\S]*?)\s*modified ")

GIT_PATTERN_MULTIPLE_COMMITS = (r"Git: ssh:\/\/(?:.*?@)?(.*?)\\r\\n"                    # URL
                                r"revision: (\w+), "                                    # Commit hash
                                r"modified by (.*?) "                                   # User
                                r"\<(.*?)\> "                                           # Email
                                r"on (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+)\s*"      # Date/time
                                r"([\s\S]*?)"                                           # Comment
                                r"(?=(?:Git:)|(?:Sent))")                               # Delimiter for next commit

def get_subject(message):
    for header in message['payload']['headers']:
        if header['name'] == 'Subject':
            return header['value']

def is_gocd_pattern(subject):
    match = re.search(GOCD_PATTERN, subject)
    if match:
        return True
    else:
        return False

def get_gocd_details(subject):
    match = re.search(GOCD_PATTERN, subject)
    result = {'pipeline': match.group(1),
              'stage': match.group(2),
              'status': match.group(3),
              }
    return result

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

def get_changeset_info_multiple(body):
    commits = []
    for match in re.finditer(GIT_PATTERN_MULTIPLE_COMMITS, body):
        id = match.group(2)
        shortid = id[:8]
        author = match.group(3)
        comment = clean_changeset_comment(match.group(6))
        url = format_commit_url(match.group(1), id) 
        result = {'id': shortid,
                  'author': author,
                  'comment': comment,
                  'url': url}
        commits.append(result)
    return commits

def get_changeset_url(body):
    match = re.search(BASE_GIT_SSH_PATTERN, body)
    if match:
        base_url = match.group(1)
        changeset_id = get_changeset_id(body)
        return format_commit_url(base_url, changeset_id)

def get_changeset_id(body):
    match = re.search(REVISION_PATTERN, body)
    if match:
        return match.group(1)

def get_changeset_comment(body):
    match = re.search(REVISION_PATTERN, body)
    if match:
        comment = match.group(5)
        return clean_changeset_comment(comment)

def clean_changeset_comment(comment):
    # For multiline comments, get the first non-blank line
    temp = comment.replace("\\n", "\n").replace("\\r", "\r").strip()
    lines = temp.splitlines()
    for line in lines:
        strippedLine = line.strip()
        if strippedLine:
            return strippedLine

def format_commit_url(base_url, changeset_id):
    #prepend https://
    base_url = "https://" + base_url
    #replace :22 with nothing
    base_url = base_url.replace(":22", "")
    return base_url + "/commit/" + changeset_id

def get_changeset_author(body):
    match = re.search(REVISION_PATTERN, body)
    if match:
        return match.group(2)