# Alertbot

## Installation
```shell
pip install git+ssh://git@github.com/tapway/alertbot.git
```

## Usage
Here is a basic example, with yaml config for channel names
```python
from alertbot.alertbot import Alertbot

# you can just manually use a dictionary instead
# use absolute path
channels = Alertbot.get_channels_from_yaml("/home/bashketchum/tests/config.yaml") 
bot = Alertbot(channels=channels)

try:
    f = 1/0
except Exception as e:
    bot.send_error_log("test_channel", e)
```
Example without yaml file,
from alertbot.alertbot import Alertbot

# you can just manually use a dictionary instead
# use absolute path
channels = {test_channel: "CXXXXXXXXXX"}
bot = Alertbot(channels=channels)

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

### Explicitely passing token (Not recommended)
You can explicitely pass the token for the bot. But it is recommended to just have a `.env` file with the `BOT_TOKEN` variable, Alertbot will automatically load it.

Example `.env` file,
```
BOT_TOKEN=xoxb-XXXXXXXXXX-XXXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXX
```