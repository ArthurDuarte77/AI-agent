import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/gmail.readonly"
]


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {
        'raw': raw_message
    }


def send_message(service, user_id, message):
    """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')


def read_emails(max_results=10):
    """Reads emails from the user's Gmail inbox and returns a list of dictionaries.

    Args:
        max_results: The maximum number of emails to read (default is 10).

    Returns:
        A list of dictionaries, where each dictionary represents an email
        and contains the following keys: 'sender', 'subject', 'body'.
        Returns an empty list if there are no emails or if an error occurs.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        email_list = []
        if messages:
            for message in messages:
                msg = (
                    service.users()
                    .messages()
                    .get(userId="me", id=message["id"], format="full")
                    .execute()
                )
                payload = msg["payload"]
                headers = payload["headers"]
                sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
                body = ""
                if 'parts' in payload:
                    parts = payload["parts"]
                    for part in parts:
                        if part['mimeType'] == "text/plain":
                            body += base64.urlsafe_b64decode(part['body']['data']).decode()
                        elif part['mimeType'] == "text/html":
                            body += base64.urlsafe_b64decode(part['body']['data']).decode()
                else:
                  if payload["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(payload["body"]["data"]).decode()

                email_list.append({"sender": sender, "subject": subject})

        return email_list

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []

def main():
  emails = read_emails(5)
  print(emails)
  # if emails:
  #     for email in emails:
  #         print(f"From: {email['sender']}")
  #         print(f"Subject: {email['subject']}")
  #         print(f"Body: {email['body']}")
  #         print("-" * 20)
  # else:
  #     print("No emails found.")

if __name__ == "__main__":
    main()