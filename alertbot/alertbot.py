from typing import Tuple
from slack_sdk import WebClient
from typing import Dict
import os
import logging
import datetime
import sys
import traceback
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s -- [%(module)s:%(lineno)s - %(levelname)s] -- %(message)s",
)
logger = logging.getLogger(__name__)


class Alertbot:
    def __init__(
        self,
        channels: Dict,
        token: str = None,
        service: str = "",
        enviroment: str = "dev",
        client_type="slack",
        cloudwatch: str = None,
        custom_fields: Dict = None,
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
            logger.info(f"Initializing alertbot at {Alertbot._get_pod_info()}")
            self.cloudwatch = cloudwatch + Alertbot._get_pod_info()
        self.token = token
        self.channels = channels
        self.client_type = client_type
        self.client = Alertbot._get_client(self.token, self.client_type)
        self.env = enviroment
        self.service = service
        self.custom_fields = custom_fields

    @staticmethod
    def send_error_logs(
        channels: Dict,
        channel: str,
        error: Exception,
        token: str = None,
        service: str = "",
        enviroment: str = "dev",
        client_type="slack",
        cloudwatch: str = None,
        custom_fields: Dict = None,
    ):
        try:
            channel_id = channels[channel]
            cloudwatch = None
            if cloudwatch and "HOSTNAME" in os.environ:
                cloudwatch = cloudwatch + Alertbot._get_pod_info()
            mkdown = Alertbot.get_error_markdown(
                env=enviroment,
                service=service,
                cloudwatch=cloudwatch,
                custom_fields=custom_fields,
                error=error,
            )
            client = Alertbot._get_client(token=token, client_type=client_type)
            err, res = Alertbot._send_log(client, channel_id, mkdown)
            if err:
                logger.debug(err)
                print(err)
        except Exception as e:
            print(e)
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
    def _get_client(token: str, client_type: str):
        client = Alertbot._get_client_mappings(client_type=client_type)
        return client(token=token)

    @staticmethod
    def get_alertbot_instance(
        channels: Dict,
        token: str = None,
        service: str = "",
        enviroment: str = "dev",
        client_type="slack",
        cloudwatch=False,
        custom_fields=None,
    ):
        bot_instance = Alertbot(
            channels=channels,
            service=service,
            token=token,
            enviroment=enviroment,
            client_type=client_type,
            cloudwatch=cloudwatch,
            custom_fields=custom_fields,
        )
        return bot_instance

    @staticmethod
    def _send_log(client: WebClient, channel_id: str, msg: str) -> Tuple:
        try:
            res = client.chat_postMessage(
                channel=channel_id,
                text="Error Message",
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": msg}}],
            )
            return None, res
        except Exception as e:
            return e, None

    @staticmethod
    def get_error_markdown(
        env: str, service: str, cloudwatch: Any, custom_fields: Dict, error: Exception
    ):
        t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        t = t.strftime("%m/%d/%Y, %H:%M:%S")
        type, value, tb = sys.exc_info()
        if not cloudwatch:
            return (
                f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {traceback.format_exc()}\nError: {value}\n```"
                + (
                    f"\n*Custom Fields*:\n```{custom_fields}\n```"
                    if len(custom_fields.keys()) > 0
                    else ""
                )
            )
        else:
            return (
                f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {traceback.format_exc()}\nError: {value}\n```\n*Cloudwatch*: {cloudwatch}\n"
                + (
                    f"\n*Custom Fields*:\n```{custom_fields}\n```"
                    if len(custom_fields.keys()) > 0
                    else ""
                )
            )

    def send_generic_log(self, channel: str, msg: str) -> None:
        try:
            channel_id = self.channels[channel]
            err, res = self._send_log(channel_id, msg)
            if err:
                logger.debug(err)
        except Exception as e:
            logger.debug(e)

    def send_error_log(self, channel: str, error: Exception) -> None:
        """
        `channel`: Channel name of the channel to send the alert to. \n
        `error`: An exception raised by the application.
        """
        try:
            channel_id = self.channels[channel]
            mkdown = Alertbot.get_error_markdown(
                self.env, self.service, self.cloudwatch, self.custom_fields, error
            )
            err, res = Alertbot._send_log(self.client, channel_id, mkdown)
            if err:
                print(err)
                logger.debug(err)
        except Exception as e:
            print(e)
            logger.debug(e)
