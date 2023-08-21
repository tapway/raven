# Alertbot

[![Python package](https://github.com/tapway/alertbot/actions/workflows/python-package.yml/badge.svg)](https://github.com/tapway/alertbot/actions/workflows/python-package.yml)

## Installation
```shell
pip install git+ssh://git@github.com/tapway/alertbot.git
```

## Usage
Here is a basic example, with yaml config for channel names. (Use absolute path)
```python
from alertbot.alertbot import Alertbot

# you can just manually use a dictionary instead
# use absolute path
channels = Alertbot.get_channels_from_yaml("config.yaml") 
Alertbot(channels=channels, service="test_service", token=load_secret_from_aws_sm(secret_name=<YOUR_SECRET_NAME>))

try:
    f = 1/0
except Exception as e:
    bot.send_error_log("test_channel", e)
```

Example without yaml file,
```python
from alertbot.alertbot import Alertbot
channels = {test_channel: "CXXXXXXXXXX"}
Alertbot(channels=channels, service="test_service", token=load_secret_from_aws_sm(secret_name=<YOUR_SECRET_NAME>))

try:
    f = 1/0
except Exception as e:
    bot.send_error_log("test_channel", e)
```
Example yaml file,

```yaml
channles:
    test_channel: "CXXXXXXXXXX"
```