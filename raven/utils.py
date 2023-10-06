import boto3
from botocore.exceptions import ClientError
import json
from typing import Dict, Optional, Callable, List
import yaml
from pathlib import Path
import functools
from .raven import Raven


def alert(
    config_path: Optional[str] = None,
    service: Optional[str] = None,
    environment: Optional[str] = None,
    channel: Optional[str] = None,
    channel_id: Optional[str] = None,
    params: Optional[bool] = False,
    token: Optional[str] = None,
    callbacks: Optional[List[Callable]] = None,
):
    def _alert(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:
                if config_path and token:
                    send_alert_with_config(
                        config_path=config_path,
                        environment=environment,
                        channel=channel,
                        token=token,
                        kwargs=kwargs,
                    )
                elif config_path:
                    send_alert_with_config(
                        config_path=config_path,
                        environment=environment,
                        channel=channel,
                        kwargs=kwargs,
                    )
                elif token and channel_id:
                    send_alert(
                        service=service,
                        environment=environment,
                        additional_body_params=(kwargs if params else {}),
                        token=token,
                        channel_id=channel_id,
                    )
                else:
                    raise Exception(
                        "Please ensure you have either config file or the token and channel_id present in the decorator."
                    )
                if callbacks:
                    for callback in callbacks:
                        # running arbitrary callbacks
                        try:
                            callback()
                        except Exception as e:
                            print(f"Callback failed {e}")

        return wrapper

    return _alert


def send_alert_with_config(
    config_path, channel=None, environment=None, token=None, kwargs={}
):
    """
    `path`: absolute path of an yaml file containing channel names and ids
    """
    p = Path(config_path)
    with p.open("r") as f:
        config: Dict = yaml.safe_load(f)
        # load variables
        channels: Optional[Dict] = config.get("channels", None)
        secret_name: Optional[str] = config.get("aws_sm_secret", None)
        service: Optional[str] = config.get("service", None)
        cloudwatch: Optional[str] = config.get("cloudwatch", None)
        additional_body_params: Optional[str] = config.get("params", False)
        aws_region: Optional[str] = config.get("aws_region", None)

        if secret_name and not token:
            token = _load_secret_from_aws_sm(secret_name, aws_region)

        if not token:
            raise Exception(
                "Please input either aws_secret in config file or pass in the bot token"
            )

        if channels:
            # load channels
            channel_id = (
                channels[list(channels.keys())[0]]
                if not channel
                else channels.get(channel, None)
            )

            if not channel_id:
                raise Exception(
                    "Please include channels or input the correct channel_name"
                )

            try:
                Raven.send_error_logs(
                    token=token,
                    service=service,
                    channel_id=channel_id,
                    environment=environment,
                    cloudwatch=cloudwatch,
                    custom_fields=(kwargs if additional_body_params else {}),
                )
            except Exception:
                raise Exception("Something went wrong in config file, please check.")
        else:
            raise Exception("Please include channels in your config file")


def send_alert(
    service: Optional[str] = None,
    environment: Optional[str] = None,
    channel_id: Optional[str] = None,
    additional_body_params: Dict = {},
    token: Optional[str] = None,
):
    Raven.send_error_logs(
        channel_id=channel_id,
        token=token,
        service=service,
        environment=environment,
        custom_fields=(additional_body_params if additional_body_params else {}),
    )


def _load_secret_from_aws_sm(secret_name: str, region_name: Optional[str] = None):
    if not secret_name or not region_name:
        raise Exception(
            "Please ensure presence of secret_name and region_name in config file"
        )
    session = boto3.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response["SecretString"])
        return secret["BOT_TOKEN"]
    except ClientError as e:
        raise e
