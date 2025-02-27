import slack
import os
from dotenv import load_dotenv
import json
import requests
from requests.auth import HTTPBasicAuth
import logging
import time

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="billing_alerts.log",
    filemode="a",
)

api_key = os.environ.get("API_KEY")
slack_channel = "runpod_mia_alerts"
slack_runpod_alert_token = os.environ.get("SLACK_RUNPOD_ALERT_TOKEN")
runpod_balance_threshold = float(os.environ.get("RUNPOD_BALANCE_THRESHOLD"))

client = slack.WebClient(slack_runpod_alert_token)

url = f"https://api.runpod.io/graphql?api_key={api_key}"
headers = {"content-type": "application/json"}

query = {
    "operationName": "myPods",
    "variables": {},
    "query": """query myPods {
      myself {
        id
        clientBalance
        savingsPlans {
          startTime
          endTime
          gpuTypeId
          podId
          costPerHr
          __typename
        }
        pods {
          savingsPlans {
            gpuTypeId
            endTime
            costPerHr
            __typename
          }
          clusterId
          containerDiskInGb
          containerRegistryAuthId
          costPerHr
          adjustedCostPerHr
          desiredStatus
          dockerArgs
          dockerId
          env
          gpuCount
          id
          imageName
          lastStatusChange
          locked
          machineId
          memoryInGb
          name
          networkVolume {
            id
            name
            size
            __typename
          }
          ipAddress {
            address
            __typename
          }
          cpuFlavorId
          machineType
          cpuFlavor {
            groupName
            displayName
            __typename
          }
          podType
          port
          ports
          templateId
          uptimeSeconds
          vcpuCount
          version
          volumeEncrypted
          volumeInGb
          volumeMountPath
          machine {
            costPerHr
            currentPricePerGpu
            diskMBps
            gpuAvailable
            gpuDisplayName
            location
            maintenanceEnd
            maintenanceNote
            maintenanceStart
            minPodGpuCount
            maxDownloadSpeedMbps
            maxUploadSpeedMbps
            note
            podHostId
            secureCloud
            supportPublicIp
            gpuTypeId
            globalNetwork
            gpuType {
              secureSpotPrice
              communitySpotPrice
              oneMonthPrice
              threeMonthPrice
              sixMonthPrice
              __typename
            }
            __typename
          }
          __typename
        }
        __typename
      }
    }"""
}
target_endpoints = [
    "US-NNA-Summarization -fb",
    "US-NNA-Smart-reply -fb",
    "US-NNA-Pickup-intent -fb",
    "EU-LFMH-Summarization -fb",
    "EU-LFMH-Pickup-intent -fb",
    "EU-LFMH-Pickup-intent -fb",
]

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

def get_endpoints_data():
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
    endpoints = get_endpoints_data()

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

            else:
                error_message = result["error_message"]
                error_message = (
                    f"*{action}*: Failed during the setting active worker to `{workersMin}` for `{endpoint_name}`: "
                    + error_message
                )
                send_slack_notification(error_message)
                logging.critical(error_message)

def send_slack_notification(message):
    try:
        client.chat_postMessage(channel=slack_channel, text=message)
    except slack.errors.SlackApiError as e:
        if e.response["error"] == "not_in_channel":
            # Attempt to join the channel first
            try:
                client.conversations_join(channel=slack_channel)
                client.chat_postMessage(channel=slack_channel, text=error_message)
            except slack.errors.SlackApiError as join_error:
                print(
                    f"Failed to join and send message: {join_error.response['error']}"
                )
        else:
            print(f"Slack API Error: {e.response['error']}")

def start_monitoring(sleep):

    while True:
        result = send_post_request_to_runpod(query)

        if result["data"]:
            current_balance = result['data']['data']['myself']['clientBalance']

            if current_balance < runpod_balance_threshold:
                alert_msg = f"Testing billing alerts: *ALERT!! ALERT!! ALERT!!* \nCurrent runpod balance `${current_balance}` is less than the threshold `${runpod_balance_threshold}`"
                send_slack_notification(alert_msg)
                logging.critical(alert_msg)
                update_workers("deactivate", 0)

        else:
            error_message = result["error_message"]
            send_slack_notification(error_message)
            logging.critical(error_message)
            print(error_message)

        # sleep for 5 mins.
        time.sleep(sleep)


start_monitoring(30)
#data = get_endpoints_data()
#import json
#print(json.dumps(data, indent=4))
