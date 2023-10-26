from typing import Optional, Tuple
from slack_sdk import WebClient
from typing import Dict
import os
import logging
import datetime
import sys
import traceback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s",
)
logger = logging.getLogger(__name__)


class Raven:
    def __init__(
        self,
        channels: Dict,
        token: Optional[str] = None,
        service: Optional[str] = "",
        environment: str = "dev",
        client_type="slack",
        cloudwatch: Optional[str] = None,
        custom_fields: Dict = {},
    ) -> None:
        """
        `channels`: Dictionary containing `channel_name` and `channel_id` \n
        `token`: Token for clients, if the value is not passed, we look for BOT_TOKEN variable in .env file \n
        `service`: Service that the bot is running on \n
        `environment`: Environment the service is running on, default is dev \n
        `client_type`: Client to be used to send alerts. By default it is Slack, its the only available client right now.
        """
        self.cloudwatch = None
        if cloudwatch and "HOSTNAME" in os.environ:
            logger.info(f"Initializing alertbot at {Raven._get_pod_info()}")
            self.cloudwatch = cloudwatch + Raven._get_pod_info()
        self.token = token
        self.channels = channels
        self.client_type = client_type
        self.client = Raven._get_client(self.token, self.client_type)
        self.env = environment
        self.service = service
        self.custom_fields = custom_fields

    @staticmethod
    def send_error_logs(
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
            err, _ = Raven._send_log(client, channel_id, mkdown)
            if err:
                logger.debug(err)
                print(err)
        except Exception as e:
            logger.debug(e)

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
        client = Raven._get_client_mappings(client_type=client_type)
        return client(token=token)

    @staticmethod
    def get_alertbot_instance(
        channels: Dict,
        token: Optional[str] = None,
        service: str = "",
        environment: str = "dev",
        client_type: str = "slack",
        cloudwatch: Optional[str] = None,
        custom_fields: Dict = {},
    ):
        bot_instance = Raven(
            channels=channels,
            service=service,
            token=token,
            environment=environment,
            client_type=client_type,
            cloudwatch=cloudwatch,
            custom_fields=custom_fields,
        )
        return bot_instance

    @staticmethod
    def _send_log(client: WebClient, channel_id: Optional[str], msg: str) -> Tuple:
        if channel_id:
            try:
                res = client.chat_postMessage(
                    channel=channel_id,
                    text="Error Message",
                    blocks=[
                        {"type": "section", "text": {"type": "mrkdwn", "text": msg}}
                    ],
                )
                return None, res
            except Exception as e:
                return e, None
        else:
            raise Exception("Please enter a channel_id")

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
        trace = str(traceback.format_exc())[-2800:]

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

    def send_generic_log(
        self, channels: Dict, channel: Optional[str] = None, msg: str = ""
    ) -> None:
        try:
            channel_id = (
                channels[list(channels.keys())[0]] if not channel else channels[channel]
            )
            err, _ = self._send_log(self.client, channel_id, msg)
            if err:
                logger.debug(err)
        except Exception as e:
            logger.debug(e)

    def send_error_log(self, channel_id: str) -> None:
        """
        `channel`: Channel name of the channel to send the alert to. \n
        `error`: An exception raised by the application.
        """
        try:
            mkdown = Raven.get_error_markdown(
                self.env, self.service, self.cloudwatch, self.custom_fields
            )
            err, _ = Raven._send_log(self.client, channel_id, mkdown)
            if err:
                print(err)
                logger.debug(err)
        except Exception as e:
            print(e)
            logger.debug(e)
