from typing import Tuple
from slack_sdk import WebClient
import yaml
from pathlib import Path
import logging as logger
from dotenv import dotenv_values
from typing import Dict

class Alertbot:
    def __init__(
        self,
        channels: Dict,
        token: str = None,
        service: str = "",
        enviroment: str = "dev",
        client_type="slack",
    ) -> None:
        """
        `channels`: Dictionary containing `channel_name` and `channel_id` \n
        `token`: Token for clients, if the value is not passed, we look for BOT_TOKEN variable in .env file \n
        `service`: Service that the bot is running on \n
        `environment`: Environment the service is running on, default is dev \n
        `client_type`: Client to be used to send alerts. By default it is Slack, its the only available client right now.
        """
        self.token = token
        self.channels = channels
        self.client_type = client_type
        self.client = self._get_client()
        self.env = enviroment
        self.service = service

    def _get_client_mappings(self):
        client_dict = {
            "slack": WebClient
        }
        if self.client_type in client_dict:
            return client_dict[self.client_type]
        else:
            return client_dict["slack"]

    def _get_client(self):
        if self.token is None:
            # read from .env
            config = dotenv_values(".env")
            self.token = config["BOT_TOKEN"]
        client = self._get_client_mappings()
        self.client = client(token=self.token)

    @staticmethod
    def get_channels_from_yaml(path: str) -> Dict:
        """
        `path`: absolute path of an yaml file containing channel names and ids
        """
        p = Path(path)
        with p.open("r") as f:
            config = yaml.safe_load(f)
            return config["channels"]

    def _send_log(
        self, channel_id: str, msg: str
    ) -> Tuple[Exception | None, str | None]:
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text="Error Message",
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": msg}}],
            )
            return None, "Successfully sent message"
        except Exception as e:
            return e, None

    def _get_error_markdown(self, error: Exception):
        filename = error.__traceback__.tb_frame.f_code.co_filename
        return f"*Environment*: {self.env},\n*Service*: {self.service}\n*Stack Trace*: ```Error Class: {error.__class__}\nFilename: {filename}\nLine No: {error.__traceback__.tb_lineno}\nError: {error}\n```"

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
                logger.debug(e)
        except Exception as e:
            logger.debug(e)