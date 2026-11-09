"""
Gmail client for fetching Google Alerts emails
"""

import os
import base64
from typing import List, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailClient:
    """Client for interacting with Gmail API to fetch Google Alerts"""

    def __init__(self, credentials_path: str = 'credentials.json'):
        """
        Initialize Gmail client

        Args:
            credentials_path: Path to Google OAuth credentials JSON file
        """
        self.credentials_path = credentials_path
        self.service = None

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def get_google_alerts(self, max_results: int = 10) -> List[Dict]:
        """
        Fetch Google Alerts emails from Gmail

        Args:
            max_results: Maximum number of emails to fetch

        Returns:
            List of email message dictionaries
        """
        if not self.service:
            self.authenticate()

        # Search for Google Alerts emails
        query = 'from:googlealerts-noreply@google.com'

        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])

        email_data = []
        for message in messages:
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            email_data.append(msg)

        return email_data

    def extract_message_body(self, message: Dict) -> str:
        """
        Extract the body content from a Gmail message

        Args:
            message: Gmail message dictionary

        Returns:
            Decoded message body as string
        """
        if 'payload' not in message:
            return ""

        payload = message['payload']

        # Handle multipart messages
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    data = part['body'].get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')

        # Handle simple messages
        if 'body' in payload and 'data' in payload['body']:
            data = payload['body']['data']
            return base64.urlsafe_b64decode(data).decode('utf-8')

        return ""
