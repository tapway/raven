import boto3
from botocore.exceptions import ClientError
import json
from typing import Dict, Optional
import yaml
from pathlib import Path
import functools
from .alertbot import Alertbot


def alert(
    config_path: Optional[str] = None,
    service: Optional[str] = None,
    environment: Optional[str] = None,
    channel: Optional[str] = None,
    channel_id: Optional[str] = None,
    params: Optional[bool] = False,
    token: Optional[str] = None,
):
    def _alert(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:
                if config_path:
                    send_alert_with_config(
                        path=config_path,
                        environment=environment,
                        channel=channel,
                        kwargs=kwargs,
                    )
                elif token and channel_id:
                    send_alert(
                        service=service,
                        enviroment=environment,
                        additional_body_params=(kwargs if params else {}),
                        token=token,
                        channel_id=channel_id,
                    )
                else:
                    raise Exception(
                        "Please ensure you have either config file or the token and channel present in the decorator."
                    )

        return wrapper

    return _alert


def send_alert_with_config(path, channel, environment, kwargs):
    """
    `path`: absolute path of an yaml file containing channel names and ids
    """
    p = Path(path)
    with p.open("r") as f:
        config: Dict = yaml.safe_load(f)
        # load variables
        channels: Optional[Dict] = config.get("channels", None)
        secret_name: Optional[str] = config.get("aws_sm_secret", None)
        service: Optional[str] = config.get("service", None)
        cloudwatch: Optional[str] = config.get("cloudwatch", None)
        additional_body_params: Optional[str] = config.get("params", False)
        aws_region: Optional[str] = config.get("aws_region", None)

        # check if token exists
        token: Optional[str] = None
        if secret_name:
            token = _load_secret_from_aws_sm(secret_name, aws_region)
        else:
            token = config.get("bot_token", None)

        if not token:
            raise Exception(
                "Please input either aws_secret or bot_token in config file"
            )

        # load channels
        channel_id = (
            channels[list(channels.keys())[0]]
            if not channel
            else channels.get(channel, None)
        )

        if not channel_id:
            raise Exception("Please include channels or input the correct channel_name")

        try:
            Alertbot.send_error_logs(
                channels=channels,
                token=token,
                service=service,
                channel_id=channel_id,
                enviroment=environment,
                cloudwatch=cloudwatch,
                custom_fields=(kwargs if additional_body_params else {}),
            )
        except Exception:
            raise Exception("Something went wrong in config file, please check.")


def send_alert(
    service: Optional[str] = None,
    enviroment: Optional[str] = None,
    channel_id: Optional[str] = None,
    additional_body_params: Dict = None,
    token: str = None,
):
    Alertbot.send_error_logs(
        channel_id=channel_id,
        token=token,
        service=service,
        enviroment=enviroment,
        custom_fields=(additional_body_params if additional_body_params else {}),
    )


def _load_secret_from_aws_sm(secret_name, region_name="ap-southeast-1"):
    if not secret_name or region_name:
        raise Exception(
            "Please ensure presence of secret_name and region_name in config file"
        )
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response["SecretString"])
        return secret["BOT_TOKEN"]
    except ClientError as e:
        raise e
