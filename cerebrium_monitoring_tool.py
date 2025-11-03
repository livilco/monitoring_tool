import requests
from requests.auth import HTTPBasicAuth
import logging
from var import (
    summary_input,
    # pickup_intent_input,
    smart_reply_input,
    # email_smart_reply_input,
    # message_generation_input,
    message_improvisation_input,
    # email_generation_input,
    email_improvisation_input,
    command_interpreter_input,
    content_importance_input,
)
import time
import slack
import os
from dotenv import load_dotenv
import json

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="cerebrium_app.log",
    filemode="a",
)

timeout = 120
# url = "https://mia-staging.livil.co"
url = "https://mia.livil.co"
slack_channel = "cerebrium-monitoring"
slack_lfmh_alert_token = os.environ.get("SLACK_ALERT_TOKEN")
username = os.environ.get("USER_NAME")
password = os.environ.get("PASSWORD")
jwt_token = os.environ.get("JWT_TOKEN")

client = slack.WebClient(slack_lfmh_alert_token)


def send_request_to_cerebrium(
    data,
    task: str,
):
    endpoint = ""
    if task == "content-importance":
        endpoint = "/content_importance_ico"
    elif task == "command-interpreter":
        endpoint = "/command_interpreter_ico"
    else:
        endpoint = "/insights_ico"

    full_url = url + endpoint
    result = {"is_success": False, "error_message": "Default"}

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
        "X-provider": "cerebrium",
    }

    try:
        response = requests.post(full_url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        response_dict = response.json()
        error = response_dict["res_jobs"][0]["error"]

        if response.status_code == 200:
            logging.info(f"Cerebrium Response: {response_dict}")
            print(f"Cerebrium Response: {response_dict}")
            result["is_success"] = True
            result["error_message"] = ""
            return result
        else:
            logging.info(f"Cerebrium Response: {response_dict}")
            print(f"Cerebrium Response: {response_dict}")
            result["is_success"] = False
            result["error_message"] = error
            return result

    except requests.exceptions.HTTPError as e:
        logging.critical(f"HTTP Error happend for {task} and exception {str(e)}")
        result["is_success"] = False
        result["error_message"] = str(e)
        return result

    except requests.exceptions.ConnectionError as e:
        logging.critical(
            f"HTTP Connection error happend for {task} and exception {str(e)}"
        )
        result["is_success"] = False
        result["error_message"] = str(e)
        return result

    except requests.exceptions.Timeout as e:
        logging.critical(f"Timeout error happend for {task} and exception {str(e)}")
        result["is_success"] = False
        result["error_message"] = str(e)
        return result

    except requests.exceptions.RequestException as e:
        logging.critical(f"Timeout error happend for {task} and exception {str(e)}")
        result["is_success"] = False
        result["error_message"] = str(e)
        return result


def check_summarization(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {"id": req_id, "input_text": summary_input, "model": model, "task": task}
        ]
    }

    return send_request_to_cerebrium(data, task)


# def check_pickup_intent(model, task):
#    req_id = 1
#    data = {
#        "req_jobs": [
#            {
#                "id": req_id,
#                "input_text": pickup_intent_input,
#                "model": model,
#                "task": task,
#            }
#        ]
#    }
#
#    return send_request_to_cerebrium(data, task)
#


def check_smart_reply(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": smart_reply_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_cerebrium(data, task)


#
# def check_email_smart_reply(model, task):
#    req_id = 1
#    data = {
#        "req_jobs": [
#            {
#                "id": req_id,
#                "input_text": email_smart_reply_input,
#                "model": model,
#                "task": task,
#            }
#        ]
#    }
#
#    return send_request_to_cerebrium(data, task)
#
# def check_message_generation(model, task):
#    req_id = 1
#    data = {
#        "req_jobs": [
#            {
#                "id": req_id,
#                "input_text": message_generation_input,
#                "model": model,
#                "task": task,
#            }
#        ]
#    }
#
#    return send_request_to_cerebrium(data, task)
#
#


def check_message_improvisation(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": message_improvisation_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_cerebrium(data, task)


#
#
# def check_email_generation(model, task):
#    req_id = 1
#    data = {
#        "req_jobs": [
#            {
#                "id": req_id,
#                "input_text": email_generation_input,
#                "model": model,
#                "task": task,
#            }
#        ]
#    }
#
#    return send_request_to_cerebrium(data, task)
#


def check_email_improvisation(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": email_improvisation_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_cerebrium(data, task)


def check_command_interpreter(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": command_interpreter_input,
                "model": model,
                "task": task,
            }
        ]
    }

    return send_request_to_cerebrium(data, task)


def check_content_importance(model, task):
    req_id = 1
    data = {
        "req_jobs": [
            {
                "id": req_id,
                "input_text": content_importance_input,
                "model": model,
                "task": task,
                "subject_line_signals": True,
                "is_sender_a_known_contact": False,
                "is_attachment_present": False,
                "thread_depth": 5,
                "frequency_of_interaction_with_sender": "low",
                "user_defined_keywords_or_phrases": "project deadline, milestone",
                "is_sender_in_priority_contacts": True,
                "message_type_preference_list": "Legal, Compliance",
                "language": "en"
            }
        ]
    }

    return send_request_to_cerebrium(data, task)


def send_slack_notification(error_message):
    try:
        client.chat_postMessage(channel=slack_channel, text=error_message)
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

        result = check_command_interpreter("jupiter-2", "command-interpreter")
        if not result["is_success"]:
            message = f"Command interpreter is not working: {result['error_message']} "
            send_slack_notification(message)
        time.sleep(sleep)

        result = check_content_importance("jupiter-2", "content-importance")
        if not result["is_success"]:
            message = f"Content importance is not working: {result['error_message']} "
            send_slack_notification(message)
        time.sleep(sleep)

        result = check_summarization("jupiter-1", "summarization")
        if not result["is_success"]:
            message = (
                f"Cerebrium summarization is not working: {result['error_message']} "
            )
            send_slack_notification(message)

        time.sleep(sleep)

        result = check_smart_reply("jupiter-2", "smart-reply")
        if not result["is_success"]:
            message = f"Smart reply is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)

        # result = check_pickup_intent("jupiter-2", "pickup-intent")
        # if not result["is_success"]:
        #    message = f"Pickup-intent is not working: {result['error_message']} "
        #    send_slack_notification(message)

        # time.sleep(sleep)

        # result = check_email_smart_reply("jupiter-2", "email-smart-reply")
        # if not result["is_success"]:
        #    message = f"Email smart reply is not working: {result['error_message']} "
        #    send_slack_notification(message)

        # time.sleep(sleep)

        # result = check_message_generation("jupiter-2", "message-generation")
        # if not result["is_success"]:
        #    message = f"Message generation is not working: {result['error_message']} "
        #    send_slack_notification(message)

        # time.sleep(sleep)

        result = check_message_improvisation("jupiter-2", "message-improvisation")
        if not result["is_success"]:
            message = (
                f"Message improvisation is not working: {result['error_message']} "
            )
            send_slack_notification(message)

        time.sleep(sleep)

        # result = check_email_generation("jupiter-2", "email-generation")
        # if not result["is_success"]:
        #    message = f"Email generation is not working: {result['error_message']} "
        #    send_slack_notification(message)

        # time.sleep(sleep)

        result = check_email_improvisation("jupiter-2", "email-improvisation")
        if not result["is_success"]:
            message = f"Email improvisation is not working: {result['error_message']} "
            send_slack_notification(message)

        time.sleep(sleep)


# send_slack_notification("This is a test message")

start_monitoring(300)
