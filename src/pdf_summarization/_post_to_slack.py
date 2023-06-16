import json
import os
import subprocess
from typing import List

from ._schema import SlackMessageData


def post_to_slack(message_data: List[SlackMessageData]) -> None:
    """
    Post the summary to Slack.

    Parameters
    ----------
    message_data : List[SlackMessageData]
        The list of SlackMessageData objects containing the title,
        URL, and summary of the research paper.
    """

    for message_datum in message_data:
        payload = {
            "attachments": [
                {
                    "color": "#36a64f",
                    "fields": [
                        {
                            "title": "Title",
                            "value": message_datum.title,
                            "short": False,
                        },
                    ],
                },
                {
                    "color": "#f2c744",
                    "fields": [
                        {
                            "title": "URL",
                            "value": message_datum.url,
                            "short": False,
                        },
                    ],
                },
                {
                    "color": "#f24436",
                    "fields": [
                        {
                            "title": "Summary",
                            "value": message_datum.summary,
                            "short": False,
                        },
                    ],
                },
            ]
        }

        subprocess.run(
            [
                "curl",
                "-X",
                "POST",
                "-H",
                "Content-type: application/json",
                "--data",
                json.dumps(payload),
                os.environ.get("SLACK_INCOMING_WEBHOOK_URL"),
            ]
        )
