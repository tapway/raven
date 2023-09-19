# Alertbot

[![Python package](https://github.com/tapway/alertbot/actions/workflows/python-package.yml/badge.svg)](https://github.com/tapway/alertbot/actions/workflows/python-package.yml) <br>
A rather opinionated utility bot to raise alerts in comms in case of runtime exceptions.

## Installation

```shell
pip install git+ssh://git@github.com/tapway/alertbot.git
```

## Usage

Before using the package -

1. Create a secret in AWS secret manager with BOT_TOKEN variable in the secret
1. Make sure the machine/pod/container has appropriate permissions to get secrets from AWS Secrets Manager
1. You have your config yaml file in correct directory

Example yaml file,

```yaml
channels:
  alert_channel: CXXXXXXXXXX # can be obtained from slack channel settings
cloudwatch: <YOUR CLOUDWATCH PREFIX URL>
aws_sm_secret: <YOUR SECRET NAME>
```

Note: For cloudwatch link to work, your app should be running in a kubernetes cluster, otherwise, it will skip sending the cloudwatch link.

# Usage

## Automatic alert

Sends alert to the first channel in the yaml file,

```python
from alertbot.utils import alert

@alert(
    config="alertbot_config.yaml",
    enviroment=os.environ.get("CURRENT_ENV", "dev"),
    service="example_service",
    send_params=True,
)
def example_func():
    x = 1/0 # this raises error, do not catch the error
```

Sends alert to specified channel in the yaml file,

```python
from alertbot.utils import alert

@alert(
    config="alertbot_config.yaml",
    enviroment=os.environ.get("CURRENT_ENV", "dev"),
    service="example_service",
    send_params=True,
    channel="alert_channel"
)
def example_func():
    x = 1/0 # this raises error, do not catch the error
```

## Manual alert in try-catch

```python
from alertbot.utils import send_alert

def example_func():
    try:
        x = 1/0
    except Exception:
        # for alertbot to catch this error
        send_alert(
            config="config.yaml",
            enviroment=os.environ.get("CURRENT_ENV", "dev"),
            service="launcher.listen",
            additional_body_params=message,
        )
```
