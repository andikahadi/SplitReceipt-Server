from __future__ import print_function

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email
import base64
import arrow


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_message(service, user_id, msg_id):
    try:
        # message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        #
        # msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        #
        # msg_str = email.message_from_bytes(msg_raw)
        # content_type = msg_str.get_content_maintype()
        #
        # if content_type == "multipart":
        #     part1, part2 = msg_str.get_payload()
        #     html_msg = part2.get_payload()
        #     return html_msg
        # else:
        #     return msg_str.get_payload()

        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()
        msgs = message['payload']['parts'][1]['body']['data']
        html_msg = base64.urlsafe_b64decode(msgs).decode('utf-8')
        return html_msg


    except HttpError as error:
        print(f"An error occured: {error}")


def search_messages(service, user_id, search_string):
    try:
        search_id = service.users().messages().list(userId=user_id, q=search_string).execute()

        number_results = search_id['resultSizeEstimate']

        final_list = []
        if number_results > 0:
            message_ids = search_id['messages']

            for ids in message_ids:
                final_list.append(ids['id'])

            return final_list

        else:
            print('There were 0 results for that search string, returning an empty string')
            return ""

    except HttpError as error:
        print(f"An error occured: {error}")


def get_service(google_access_token):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # if os.path.exists('token.json'):
    #     creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             'credentials.json', SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     # Save the credentials for the next run
    #     with open('token_without_refresh.json', 'w') as token:
    #         token.write(creds.to_json())
    time = arrow.utcnow().shift(hours=1).format('YYYY-MM-DDTHH:mm:ss.SSSSSS')
    creds = Credentials.from_authorized_user_info({
        "token": google_access_token,
        "refresh_token": "",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "1021304219474-kffnfs7t3c0hh09g6sbs4kq1fg8djr43.apps.googleusercontent.com",
        "client_secret": "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",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"], "expiry": time
    }, SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    return service


