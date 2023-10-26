import os
import logging
from typing import Optional, Dict

from slack_sdk import WebClient

from raven.kubernetes import get_pod_info
from raven.markdown import get_error_markdown, get_markdown
from raven.providers import client_provider

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s",
)
logger = logging.getLogger(__name__)


class Raven:
    client = None

    def __init__(self) -> None:
        # the purpose of the class is to encapsulate related implementations and caching clients
        pass

    @staticmethod
    def send_generic_log(
        message: str,
        channel_id: Optional[str] = None,
        token: Optional[str] = None,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        client_type="slack",
    ):
        try:
            mkdown = get_markdown(
                message=message,
                env=environment,
                service=service,
            )
            client = Raven._get_client(token=token, client_type=client_type)
            Raven._send_log(client, channel_id, mkdown)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def send_error_log(
        channel_id: Optional[str] = None,
        token: Optional[str] = None,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        client_type="slack",
        cloudwatch: Optional[str] = None,
        custom_fields: Dict = {},
    ):
        try:
            if cloudwatch and "HOSTNAME" in os.environ:
                cloudwatch = cloudwatch + get_pod_info()
            mkdown = get_error_markdown(
                env=environment,
                service=service,
                cloudwatch=cloudwatch,
                custom_fields=custom_fields,
            )
            client = Raven._get_client(token=token, client_type=client_type)
            Raven._send_error_log(client, channel_id, mkdown)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def _get_client(token: Optional[str], client_type: str):
        if not token:
            raise Exception("Please check presence of your token")
        Raven.client_type = client_type
        client = client_provider(client_type=client_type)
        if not Raven.client:
            Raven.client = client(token=token)
        return Raven.client

    @staticmethod
    def _send_error_log(client: WebClient, channel_id: Optional[str], msg: str):
        if channel_id:
            if Raven.client_type == "slack":
                client.chat_postMessage(
                    channel=channel_id,
                    text="Error Message",
                    blocks=[
                        {"type": "section", "text": {"type": "mrkdwn", "text": msg}}
                    ],
                )
        else:
            raise Exception("Please enter a channel_id")

    @staticmethod
    def _send_log(client: WebClient, channel_id: Optional[str], msg: str):
        if channel_id:
            if Raven.client_type == "slack":
                client.chat_postMessage(
                    channel=channel_id,
                    text="Generaic Message",
                    blocks=[
                        {"type": "section", "text": {"type": "mrkdwn", "text": msg}}
                    ],
                )
        else:
            raise Exception("Please enter a channel_id")
