from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow # Import from correct location

def create_and_populate_doc(document_title, text_to_add, credentials_file='credentials.json', token_file='token.pickle'):
    """Creates a new Google Doc and adds text to it.

    Args:
        document_title (str): The title of the new Google Doc.
        text_to_add (str): The text to insert into the document.
        credentials_file (str, optional): Path to the credentials JSON file. Defaults to 'credentials.json'.
        token_file (str, optional): Path to store the authentication token. Defaults to 'token.pickle'.
    """

    SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/tasks",
            'https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive'
        ]
    
    creds = None

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(  # Use from google_auth_oauthlib
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)

        # Create a new document
        document = service.documents().create(body={'title': document_title}).execute()
        document_id = document.get('documentId')

        # Add text to the document
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1
                    },
                    'text': text_to_add
                }
            }
        ]
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        # Open the document's sharing settings to make it accessible to all
        file_metadata = {
            'role': 'reader',
            'type': 'anyone'
        }
        drive_service.permissions().create(fileId=document_id, body=file_metadata).execute()

        print(f'Document created with ID: {document_id} and has been shared.')

        return document_id
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

if __name__ == '__main__':
    doc_title = 'My Python Created Doc'
    text_content = """Hello world! This is some text added by a Python script to my google doc.
This is another line of text.
    """

    document_id = create_and_populate_doc(doc_title, text_content)

    if document_id:
        print(f'You can access your document here: https://docs.google.com/document/d/{document_id}/edit')