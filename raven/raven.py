import os
import logging
import datetime
import sys
import traceback
from typing import Optional, Dict
from slack_sdk import WebClient

logging.basicConfig(
    level=logging.DEBUG,
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
            mkdown = Raven.get_markdown(
                message=message,
                env=environment,
                service=service,
            )
            client = Raven._get_client(token=token, client_type=client_type)
            Raven._send_log(client, channel_id, mkdown)
        except Exception as e:
            logger.debug(e)

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
                cloudwatch = cloudwatch + Raven._get_pod_info()
            mkdown = Raven.get_error_markdown(
                env=environment,
                service=service,
                cloudwatch=cloudwatch,
                custom_fields=custom_fields,
            )
            client = Raven._get_client(token=token, client_type=client_type)
            Raven._send_error_log(client, channel_id, mkdown)
        except Exception as e:
            logger.debug(e)

    # client provider, this would always contain a map of functions that can be passed a token to initialize a client
    @staticmethod
    def _get_client_mappings(client_type):
        client_dict = {"slack": WebClient}
        if client_type in client_dict:
            return client_dict[client_type]
        else:
            return client_dict["slack"]

    @staticmethod
    def _get_pod_info():
        pod_name = os.environ["HOSTNAME"]
        return pod_name

    @staticmethod
    def _get_client(token: Optional[str], client_type: str):
        if not token:
            raise Exception("Please check presence of your token")
        Raven.client_type = client_type
        client = Raven._get_client_mappings(client_type=client_type)
        if not Raven.client:
            Raven.client = client(token=token)
        return Raven.client

    @staticmethod
    def _send_error_log(client: WebClient, channel_id: Optional[str], msg: str):
        if channel_id:
            if Raven.client_type == "slack":
                _ = client.chat_postMessage(
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
            client.chat_postMessage(
                channel=channel_id,
                text="Generaic Message",
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": msg}}],
            )
        else:
            raise Exception("Please enter a channel_id")

    @staticmethod
    def get_markdown(
        message: str,
        env: Optional[str],
        service: Optional[str],
    ):
        t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        t = t.strftime("%m/%d/%Y, %H:%M:%S")
        return f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Message*: ```Traceback: {message}\n```"

    @staticmethod
    def get_error_markdown(
        env: Optional[str],
        service: Optional[str],
        cloudwatch: Optional[str],
        custom_fields: Dict = {},
    ):
        t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        t = t.strftime("%m/%d/%Y, %H:%M:%S")
        type, value, _ = sys.exc_info()
        trace = str(traceback.format_exc())
        if len(trace) >= 2000:
            trace = trace[-2000:]
        if not cloudwatch:
            return (
                f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {trace}\nError: {value}\n```"
                + (
                    f"\n*Custom Fields*:\n```{custom_fields}\n```"
                    if len(custom_fields.keys()) > 0
                    else ""
                )
            )
        else:
            return (
                f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {trace}\nError: {value}\n```\n*Cloudwatch*: {cloudwatch}\n"
                + (
                    f"\n*Custom Fields*:\n```{custom_fields}\n```"
                    if len(custom_fields.keys()) > 0
                    else ""
                )
            )
