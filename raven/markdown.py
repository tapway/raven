import datetime
import traceback
import sys
from typing import Optional, Dict

def get_markdown(
    message: str,
    env: Optional[str],
    service: Optional[str],
):
    t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    t = t.strftime("%m/%d/%Y, %H:%M:%S")
    return f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Message*: ```Traceback: {message}\n```"

def get_error_markdown(
    env: Optional[str],
    service: Optional[str],
    cloudwatch: Optional[str],
    custom_fields: Dict = {},
):
    t = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    t = t.strftime("%m/%d/%Y, %H:%M:%S")
    type, value, _ = sys.exc_info()
    trace = str(traceback.format_exc())
    if len(trace) >= 2000:
        trace = trace[-2000:]
    if not cloudwatch:
        return (
            f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {trace}\nError: {value}\n```"
            + (
                f"\n*Custom Fields*:\n```{custom_fields}\n```"
                if len(custom_fields.keys()) > 0
                else ""
            )
        )
    else:
        return (
            f"*Time*: `{t}`\n*Environment*: `{env}`\n*Service*: `{service}`\n*Stack Trace*: ```Type: {type}\nTraceback: {trace}\nError: {value}\n```\n*Cloudwatch*: {cloudwatch}\n"
            + (
                f"\n*Custom Fields*:\n```{custom_fields}\n```"
                if len(custom_fields.keys()) > 0
                else ""
            )
        )
