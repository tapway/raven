from typing import Tuple
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


class Alertbot:
    def __init__(
        self,
        channels: Dict,
        token: str = None,
        service: str = "",
        enviroment: str = "dev",
        client_type="slack",
        cloudwatch: str = None,
        custom_fields: Dict = None
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
            logger.info(f"Initializing alertbot at {self._get_pod_info()}")
            self.cloudwatch = cloudwatch + self._get_pod_info()
        self.token = token
        self.channels = channels
        self.client_type = client_type
        self.client = self._get_client()
        self.env = enviroment
        self.service = service
        self.custom_fields = custom_fields

    def _get_client_mappings(self):
        client_dict = {"slack": WebClient}
        if self.client_type in client_dict:
            return client_dict[self.client_type]
        else:
            return client_dict["slack"]

    def _get_pod_info(self):
        pod_name = os.environ["HOSTNAME"]
        return pod_name

    def _get_client(self):
        client = self._get_client_mappings()
        return client(token=self.token)

    @staticmethod
    def get_alertbot_instance(
        channels: Dict,
        token: str = None,
        service: str = "",
        enviroment: str = "dev",
        client_type="slack",
        cloudwatch=False,
        custom_fields=None
    ):
        bot_instance = Alertbot(
                channels=channels,
                service=service,
                token=token,
                enviroment=enviroment,
                client_type=client_type,
                cloudwatch=cloudwatch,
                custom_fields=custom_fields
            )
        return bot_instance

    def _send_log(self, channel_id: str, msg: str) -> Tuple:
        try:
            res = self.client.chat_postMessage(
                channel=channel_id,
                text="Error Message",
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": msg}}],
            )
            return None, res
        except Exception as e:
            logger.log(e)
            return e, None

    def _get_error_markdown(self, error: Exception):
        t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        t = t.strftime("%m/%d/%Y, %H:%M:%S")
        type, value, tb = sys.exc_info()
        custom_fields = [f"*{key}*: {value}\n" for key, value in self.custom_fields]
        if not self.cloudwatch:
            mkdown = f"*Time*: `{t}`\n*Environment*: `{self.env}`\n*Service*: `{self.service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {traceback.format_exc()}\nError: {value}\n```"
            for item in custom_fields:
                mkdown += item
            return mkdown
        else:
            mkdown = f"*Time*: `{t}`\n*Environment*: `{self.env}`\n*Service*: `{self.service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {traceback.format_exc()}\nError: {value}\n```\n*Cloudwatch*: {self.cloudwatch}\n"
            for item in custom_fields:
                mkdown += item
            return mkdown

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
            mkdown = self._get_error_markdown(error)
            err, res = self._send_log(channel_id, mkdown)
            if err:
                logger.log(err)
        except Exception as e:
            logger.log(e)