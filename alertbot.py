from typing import Tuple
from slack_sdk import WebClient
import yaml
from pathlib import Path
import logging as logger
import sys
import os
from dotenv import dotenv_values


class Alertbot:
    def __init__(
        self,
        token: str = None,
        service: str = "test_service",
        enviroment: str = "dev",
        client_type="slack",
    ) -> None:
        self.token = token
        self.channels = self._get_channels_from_yaml()
        self.token = token
        self.client_type = client_type
        self.client = self._get_client()
        self.env = enviroment
        self.service = service

    def _get_client(self):
        if self.token is None:
            # read from .env
            config = dotenv_values(".env")
            self.token = config["BOT_TOKEN"]
        if self.client_type == "slack":
            return WebClient(token=self.token)
        else:
            return WebClient(token=self.token)

    def _get_channels_from_yaml(self):
        p = Path(__file__).with_name("config.yaml")
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
        try:
            channel_id = self.channels[channel]
            mkdown = self._get_error_markdown(error)
            err, res = self._send_log(channel_id, mkdown)
            if err:
                logger.debug(e)
        except Exception as e:
            logger.debug(e)
