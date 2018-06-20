
import json
import requests

from cfg.config import (
    CI_STAGES,
    DEPLOY_STAGES,
    VERSION_CONTROL_TYPE
)

def failed_icon():
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABQUlEQVRYhe2XsU7DMBCGP1s8QMWEOqAIMfICTNCxr4B4O8SK2IqY6Ix4hTYCCWUrOxLHYEcqaRTnDrdZcpKVxPb5/2yf7IsjYQKnwAKYpvo27BOYO3hX+v0VF1gLiLGs4wQGEbdDZBTXQ+xBvBPCNcWBJVAkOFfAS6PuGjhL+JXAVWtgKmd+3+J/Z1kJr5x5DiuAZQ3hDyy+A+EJh8whxbchFh79CZfTpn5AcSAG4QgwAowAQ9qR0W8icNGoO7YM5AQ2wMQI8l/7GnwLPFAZfR+By1gejGNUCBSGFOxNtgJYwrX+akjRCu9CmjQjPPvas4Of+iO+Pyn8S2DmoPRxAC1EW+53rhXfaVFsx7fArQQfBG5iXa9l78RTxsRHLL33vNcaGQMzj/geIPTiGSGS4q6rsYYgZM4nSv6K8HtednX6BZgU/SE2MPZ5AAAAAElFTkSuQmCC'


def passed_icon():
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAALiIAAC4iAari3ZIAAAAZdEVYdFNvZnR3YXJlAHBhaW50Lm5ldCA0LjAuMjHxIGmVAAADGUlEQVRYR7VXS08TURTu2keiICGQMtPEBVhQo0h06S9whQl3SgV8ILojcenKtQuMkrhCKLqQhXaGR2mIca8JgiRtJTUGlWhiH1SMxQgdzxluk85w5o0f+ZIy997zfffeM/eeCThF84tovShL/aIiTQiKtCzIrAS/VWAFf2vPFGm8Re7pCz7vruPD/AMCtoPIUwj+hwvaUpClLVFmMSEeCfMw7hF+ffkQBHkEAbeNAi64DTEeNCZ7D/KwzoDOYcYfiICeCCuSDiUirTy8NUQ5cgFcF6hAvihL+aAS6eIyNHZnzopkgP2gzPKhuMlKtMYvHYalWiUH7iNha1NkToD4KDXgP3GEy+4iON3bAQ/9ZLs7ytJfUWFtXB5nz56RHX2wK3lbvZ+eUkNKhGwHExOaeJPCjrk5ZJwQxbOb6ypi8tMCaQKSvSzMSEcDsBQDxkY/7EzeAvGvmngV5iakKBqYNDZ4JYqv/vzCZfW4txLb0x8SfwwOHrZibPDCzuSQqfibXFoNzw7sGQMrsIiv36axoZZts/3k81qenR9SM6XPXE6Pt/mMGp67So7DExe2gGjgvPhqWF3//UMdXhwl25GexZEy2zE1gOLfynkt0E5lhzRxZv6mmi6taX2MsBXXCAaoLagVr8JoAsVTJuKLhVW1fe6aLiZJbQuIJLzz7rFagT8jqiZOJwYtxTuciAO1JAQDMarx7vKYqYm1X9/5f3q4EUfuvoYWB5GZCQpLhawrcaQgR3oDzQvRequj2IkJFD+ZuE6ONyPcP2XxZd8R7T6wu4ysTHgR5xzXxBG88rW8jikT74sfvYkbr2MEJCNWwPQAzloTKH4qcYPsZ0dIPn1BgmiAMhxywbYSRhPLxawPcZZqUgYPcFk9sCjFw4EaWMvj01HyuT1ZzrQorSIU7znvxIR7slxLvOccl7GGOBM9ARVLhg7knrC1KduZG9EwBZ9mivQQ6L1Y1bJdGmmMufw0qwV/RSchc7d0wS0IiYZ9J/a8an4QnO+uC8GnNwQehyXFT/ENmGEFCeY2QHQJtu1JS5xd0YpNRwgE/gE+cOhD+QmRdgAAAABJRU5ErkJggg=='


def send_to_teams(body, webhook_url):
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
        icon = passed_icon()
    elif status in ['failed', 'is broken']:
        icon = failed_icon()
    else:
        return

    body_text = ''
    if stage in CI_STAGES:
         body_text += ('\n{0}: <{1}|{2}> - {3}: {4}'
                       ''.format(changesetLabel,
                                 changeset['url'],
                                 changeset['id'],
                                 changeset['author'],
                                 changeset['comment']))

    if status in ['failed', 'is broken']:
         body_text += '\nStage: ' + stage

    body = {'@context': 'http://schema.org/extensions',
            '@type': 'MessageCard',
            'themeColor': 'ff0000',
            'summary': 'Workflow15.CI',
            'sections': [{'activityTitle': 'go build status - {0} (stage={1})'.format(status, stage),
                          'activitySubtitle': pipeline,
                          'activityImage': icon,
                          'text': body_text }],
            'potentialAction': [{'@type': 'OpenUri',
                                 'name': 'Open Pipeline',
                                 'targets': [{'os': 'default',
                                              'uri': '{0}'.format(pipeline_url)}]}]}
 
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
        icon = passed_icon()
    elif status in ['failed', 'is broken']:
        icon = failed_icon()
    else:
        return

    max_changesets = 5
    max_comment_length = 100
    body_text = ''
    if stage in CI_STAGES:
        index = 1
        for changeset in changesets[:max_changesets]:
            # Cap comment at 100 chars max
            comment = changeset['comment']
            if len(comment) > max_comment_length:
                comment = comment[:max_comment_length] + "..."
            body_text += ('\n• {0}: <{1}|{2}> - {3}: {4}'
                          ''.format(changesetLabel,
                                    changeset['url'],
                                    changeset['id'],
                                    changeset['author'],
                                    comment))
            index = index + 1
        if len(changesets) > max_changesets:
            remaining_changesets = len(changesets) - max_changesets
            body_text += ('\n_And {0} more {1}(s)_'
                          ''.format(remaining_changesets,
                                    changesetLabel.lower()))

    body = {'@context': 'http://schema.org/extensions',
            '@type': 'MessageCard',
            'themeColor': 'ff0000',
            'summary': 'Workflow15.CI',
            'sections': [{'activityTitle': 'go build status - {0} (stage={1})'.format(status, stage),
                          'activitySubtitle': pipeline,
                          'activityImage': icon,
                          'text': body_text }],
            'potentialAction': [{'@type': 'OpenUri',
                                 'name': 'Open Pipeline',
                                 'targets': [{'os': 'default',
                                              'uri': '{0}'.format(pipeline_url)}]}]}
    
    return body


def is_matching_send_rule(gocd_details):
    if gocd_details['status'] in ['failed', 'is broken']:
        return True
    if gocd_details['status'] in ['passed']:
        if gocd_details['stage'] in ['Package', 'package'] + DEPLOY_STAGES:
            return True
    if gocd_details['status'] in ['is fixed']:
        if gocd_details['stage'] in ['Package', 'package', 'AcceptanceTest'] + DEPLOY_STAGES:
            return True
    else:
        return False


def get_pipeline_url(gocd_dash_root_url, pipeline):
    return gocd_dash_root_url + '/tab/pipeline/history/' + pipeline
