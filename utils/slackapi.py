import slack
from utils.aws import secrets

secret_key = 'gh-pipelines/gb-notifications-token'


def send_message(channel: str, message: str) -> slack.web.slack_response.SlackResponse:
    ''' Send mesasge to specific slack channel '''
    token = secrets.fetch_secret(secret_key)['token']
    client = slack.WebClient(token=token)

    resp = client.chat_postMessage(
        channel=channel,
        text=message
    )

    return resp
