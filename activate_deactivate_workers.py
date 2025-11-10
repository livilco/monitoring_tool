import requests
import json
import slack
import os
from dotenv import load_dotenv
import logging
import time
import argparse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="ico_runpod_activate_deactivate.log",
    filemode="a",
)

api_key = os.environ.get("API_KEY")
slack_channel = "runpod_mia_alerts"
slack_runpod_alert_token = os.environ.get("SLACK_RUNPOD_ALERT_TOKEN")

client = slack.WebClient(slack_runpod_alert_token)
url = f"https://api.runpod.io/graphql?api_key={api_key}"
headers = {"content-type": "application/json"}

# Read the variable as a JSON string
target_endpoints_str = os.getenv("TARGET_ENDPOINTS")

# Parse JSON into a Python list
target_endpoints = json.loads(target_endpoints_str)
print(target_endpoints)

get_endpoint_query = {
    "query": """
    query Endpoints {
        myself {
            endpoints {
                gpuIds
                gpuCount
                allowedCudaVersions
                id
                idleTimeout
                locations
                name
                networkVolumeId
                scalerType
                scalerValue
                templateId
                workersMax
                workersMin
                executionTimeoutMs
            }
        }
    }
    """
}


def send_slack_notification(message):
    try:
        client.chat_postMessage(channel=slack_channel, text=message)
    except slack.errors.SlackApiError as e:
        if e.response["error"] == "not_in_channel":
            # Attempt to join the channel first
            try:
                client.conversations_join(channel=slack_channel)
                client.chat_postMessage(channel=slack_channel, text=message)
            except slack.errors.SlackApiError as join_error:
                print(
                    f"Failed to join and send message: {join_error.response['error']}"
                )
        else:
            print(f"Slack API Error: {e.response['error']}")


def send_post_request_to_runpod(query):
    result = {"data": None, "error_message": ""}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(query))
        response.raise_for_status()

        if response.status_code == 200:
            result["data"] = response.json()

        return result

    except requests.exceptions.HTTPError as e:
        logging.critical(f"HTTP Error happend: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.ConnectionError as e:
        logging.critical(f"HTTP Connection error happend: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.Timeout as e:
        logging.critical(f"Timeout error happend: {str(e)}")
        result["error_message"] = str(e)
        return result

    except requests.exceptions.RequestException as e:
        logging.critical(f"Timeout error happend: {str(e)}")
        result["error_message"] = str(e)
        return result


def get_data():
    result = send_post_request_to_runpod(get_endpoint_query)
    # print(result)

    if result["data"]:
        endpoints = result["data"]["data"]["myself"]["endpoints"]
        return endpoints
    else:
        error_message = result["error_message"]
        error_message = (
            "Error during getting endpoints data for activating the endpoints: "
            + error_message
        )
        send_slack_notification(error_message)
        logging.critical(error_message)
        print(error_message)


def update_workers(action, workersMin):
    endpoints = get_data()

    for endpoint in endpoints:
        endpoint_name = endpoint.get("name", "")
        if endpoint_name in target_endpoints:
            endpoint_gpuids = endpoint.get("gpuIds")
            endpoint_gpucount = endpoint.get("gpuCount")
            endpoint_allowedcudaversions = endpoint.get("allowedCudaVersions")
            endpoint_id = endpoint.get("id")
            endpoint_idletimeout = endpoint.get("idleTimeout")
            endpoint_locations = endpoint.get("locations")
            endpoint_networkvolumeid = endpoint.get("networkVolumeId")
            endpoint_scalertype = endpoint.get("scalerType")
            endpoint_scalervalue = endpoint.get("scalerValue")
            endpoint_templateid = endpoint.get("templateId")
            endpoint_workersmax = endpoint.get("workersMax")
            endpoint_executiontimeoutms = endpoint.get("executionTimeoutMs")

            update_query = {
                "operationName": "saveEndpoint",
                "variables": {
                    "input": {
                        "gpuIds": endpoint_gpuids,
                        "gpuCount": endpoint_gpucount,
                        "allowedCudaVersions": endpoint_allowedcudaversions,
                        "id": endpoint_id,
                        "idleTimeout": endpoint_idletimeout,
                        "locations": endpoint_locations,
                        "name": endpoint_name,
                        "networkVolumeId": endpoint_networkvolumeid,
                        "scalerType": endpoint_scalertype,
                        "scalerValue": endpoint_scalervalue,
                        "workersMax": endpoint_workersmax,
                        "workersMin": workersMin,
                        "executionTimeoutMs": endpoint_executiontimeoutms,
                    }
                },
                "query": """
                    mutation saveEndpoint($input: EndpointInput!) {
                        saveEndpoint(input: $input) {
                            gpuIds
                            id
                            idleTimeout
                            locations
                            name
                            networkVolumeId
                            scalerType
                            scalerValue
                            templateId
                            userId
                            workersMax
                            workersMin
                            gpuCount
                            __typename
                        }
                    }
                """,
            }

            result = send_post_request_to_runpod(update_query)
            print(result)

            if result["data"]:
                message = f"*{action}*: Active worker set to `{workersMin}` for the endpoint: `{endpoint_name}`"
                send_slack_notification(message)
                logging.info(message)

            else:
                error_message = result["error_message"]
                error_message = (
                    f"*{action}*: Failed during the setting active worker to `{workersMin}` for `{endpoint_name}`: "
                    + error_message
                )
                send_slack_notification(error_message)
                logging.critical(error_message)


if __name__ == "__main__":
    try:
        # Create the parser
        parser = argparse.ArgumentParser(
            description="Script to activate or deactivate workers."
        )

        # Add the 'action' argument
        parser.add_argument(
            "action",
            choices=["activate", "deactivate"],  # Restrict to valid choices
            help="The action to perform. Choose 'activate' to activate workers or 'deactivate' to deactivate them.",
        )

        # Parse the arguments
        args = parser.parse_args()

        if args.action == "activate":
            workersMin = 1
        elif args.action == "deactivate":
            workersMin = 0
        else:
            raise RuntimeError(f"Unknown action: {args.action}")

        update_workers(args.action, workersMin)

    except Exception as e:
        message = f"An unexpected error occurred during: {e}"
        print(message)
        logging.critical(message)
