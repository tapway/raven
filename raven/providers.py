from slack_sdk import WebClient

def client_provider(client_type):
    client_dict = {"slack": WebClient}
    if client_type in client_dict:
        return client_dict[client_type]
    else:
        return client_dict["slack"]
