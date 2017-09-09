
import json
import requests

from cfg.config import (
    CI_STAGES,
    DEPLOY_STAGES,
    VERSION_CONTROL_TYPE
)


def send_to_slack(body, webhook_url):
    requests.post(webhook_url, data=json.dumps(body))


def message_builder(gocd_details, changeset, dashboard_url):

    if VERSION_CONTROL_TYPE == 'GIT':
        changesetLabel = 'Commit'
    else:
        changesetLabel = 'Changeset'

    pipeline = gocd_details['pipeline']
    stage = gocd_details['stage']
    status = gocd_details['status']

    pipeline_url = get_pipeline_url(dashboard_url, pipeline)

    if status in ['passed', 'is fixed']:
        icon = ':white_check_mark:'
    elif status in ['failed', 'is broken']:
        icon = ':x:'
    else:
        return

    body = {'username': 'go build status - {0}'.format(status),
            'icon_emoji': icon,
            'text': '<{0}|{1}>'.format(pipeline_url, pipeline)}

    if stage in CI_STAGES:
        body['text'] += ('\n{0}: <{1}|{2}> - {3}: {4}'
                         ''.format(changesetLabel,
                                   changeset['url'],
                                   changeset['id'],
                                   changeset['author'],
                                   changeset['comment']))

    if status in ['failed', 'is broken']:
        body['text'] += '\nStage: ' + stage

    return body


def message_builder_multiple_changesets(gocd_details, changesets, dashboard_url):

    if VERSION_CONTROL_TYPE == 'GIT':
        changesetLabel = 'Commit'
    else:
        changesetLabel = 'Changeset'

    pipeline = gocd_details['pipeline']
    stage = gocd_details['stage']
    status = gocd_details['status']

    pipeline_url = get_pipeline_url(dashboard_url, pipeline)

    if status in ['passed', 'is fixed']:
        icon = ':white_check_mark:'
    elif status in ['failed', 'is broken']:
        icon = ':x:'
    else:
        return

    body = {'username': 'go build status - {0}'.format(status),
            'icon_emoji': icon,
            'text': '<{0}|{1}>'.format(pipeline_url, pipeline)}

    max_changesets = 3
    max_comment_length = 100
    if stage in CI_STAGES:
        index = 1
        for changeset in changesets[:max_changesets]:
            # Cap comment at 100 chars max
            comment = changeset['comment']
            if len(comment) > max_comment_length:
                comment = comment[:max_comment_length] + "..."
            body['text'] += ('\n• {0}: <{1}|{2}> - *{3}*: {4}'
                             ''.format(changesetLabel,
                                       changeset['url'],
                                       changeset['id'],
                                       changeset['author'],
                                       comment))
            index = index + 1
        if len(changesets) > max_changesets:
            remaining_changesets = len(changesets) - max_changesets
            body['text'] += ('\n_And {0} more {1}(s)_'
                             ''.format(remaining_changesets,
                                       changesetLabel.lower()))

    if status in ['failed', 'is broken']:
        body['text'] += '\nStage: ' + stage

    return body


def is_matching_send_rule(gocd_details):
    if gocd_details['status'] in ['failed', 'is broken']:
        return True
    if gocd_details['status'] in ['passed', 'is fixed']:
        if gocd_details['stage'] in ['Package', 'package'] + DEPLOY_STAGES:
            return True
    else:
        return False


def get_pipeline_url(gocd_dash_root_url, pipeline):
    return gocd_dash_root_url + '/tab/pipeline/history/' + pipeline
