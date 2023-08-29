# Alertbot
A rather opinionated utility bot to raise alerts in comms in case of runtime exceptions.
[![Python package](https://github.com/tapway/alertbot/actions/workflows/python-package.yml/badge.svg)](https://github.com/tapway/alertbot/actions/workflows/python-package.yml)

## Installation
```shell
pip install git+ssh://git@github.com/tapway/alertbot.git
```

## Usage

Before using the package -
1. Make sure the machine/pod/container has appropriate permissions to get secrets from AWS Secrets Manager
2. Make sure your github has access to the alertbot repository
3. You have your config yaml file in correct directory

Here is a basic example, with yaml config for channel names. (Use absolute path)
```python
from alertbot.alertbot import Alertbot
from alertbot.utils import load_secret_from_aws_sm, load_channels_from_yaml

bot = Alertbot.get_alertbot_instance(
    channels=load_channels_from_yaml(<CONFIG YAML FILE WITH CHANNELS>),
    token=load_secret_from_aws_sm(<AWS SECRET WHERE BOT_TOKEN VARIABLE IS STORED>),
    enviroment=<ENV>,
    client_type="slack",
    service="example",
    cloudwatch=False
)

@bot.error_alert(<YOUR CHANNEL NAME>)
def fn():
    return 1/0
```

Example without yaml file,
```python
from alertbot.alertbot import Alertbot
from alertbot.utils import load_secret_from_aws_sm

channels = {test_channel: "CXXXXXXXXXX"}

bot = Alertbot.get_alertbot_instance(
    channels=channels,
    token=load_secret_from_aws_sm(<AWS SECRET WHERE BOT_TOKEN VARIABLE IS STORED>),
    enviroment=<ENV>,
    client_type="slack",
    service="example",
    cloudwatch=False
)

@bot.error_alert(<YOUR CHANNEL NAME>)
def fn():
    return 1/0
```

Example yaml file,
```yaml
channles:
    test_channel: "CXXXXXXXXXX"
```