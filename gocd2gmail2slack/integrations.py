
import gmail as Gm
import slack
import teams

from cfg.config import (
    WEBHOOK_URL,
    TEAMS_WEBHOOK_URL,
    GOCD_DASHBOARD_URL,
    VERSION_CONTROL_TYPE
)

if VERSION_CONTROL_TYPE == 'GIT':
    import messages_git as Msg
else:
    import messages as Msg


def main():
    try:
        service, labels, messages_details = initialize()
        process(service, labels, messages_details)
    except:
        pass


def initialize():
    service = Gm.get_service()
    labels = Gm.get_labels(service)
    initial_messages = Gm.get_messages(service, include_labels=['UNREAD'])
    messages_details = Gm.get_messages_details(service, initial_messages)
    return (service, labels, messages_details)


def process(service, labels, messages_details):
    process_teams(service, labels, messages_details)


def process_slack(service, labels, messages_details):
    for item in messages_details:
        subject = Msg.get_subject(item)

        if Msg.is_gocd_pattern(subject):
            gocd_details = Msg.get_gocd_details(subject)

            if slack.is_matching_send_rule(gocd_details):
                body = Msg.get_body(item)
                changesets = Msg.get_changeset_info_multiple(body)
                text = (slack
                        .message_builder_multiple_changesets(gocd_details,
                                                             changesets,
                                                             GOCD_DASHBOARD_URL))

                slack.send_to_slack(text, WEBHOOK_URL)

                Gm.add_label(service, Msg.get_id(item),
                             'SENT_TO_SLACK', labels)

        Gm.remove_label(service, Msg.get_id(item),
                        'UNREAD', labels)


def process_teams(service, labels, messages_details):
    for item in messages_details:
        subject = Msg.get_subject(item)

        if Msg.is_gocd_pattern(subject):
            gocd_details = Msg.get_gocd_details(subject)

            if teams.is_matching_send_rule(gocd_details):
                body = Msg.get_body(item)
                changesets = Msg.get_changeset_info_multiple(body)
                text = (teams
                        .message_builder_multiple_changesets(gocd_details,
                                                             changesets,
                                                             GOCD_DASHBOARD_URL))

                teams.send_to_teams(text, TEAMS_WEBHOOK_URL)

                Gm.add_label(service, Msg.get_id(item),
                             'SENT_TO_SLACK', labels)

        Gm.remove_label(service, Msg.get_id(item),
                        'UNREAD', labels)
                        
if __name__ == "__main__":
    main()
