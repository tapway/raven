import os


def get_pod_info():
    pod_name = os.environ["HOSTNAME"]
    return pod_name
