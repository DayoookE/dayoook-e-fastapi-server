# app/services/google_meet_service.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2
import os
import logging

logger = logging.getLogger(__name__)


class GoogleMeetService:
    SCOPES = ['https://www.googleapis.com/auth/meetings.space.created']

    def __init__(self):
        self.creds = None

    async def get_credentials(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        return self.creds

    async def create_meeting(self):
        try:
            credentials = await self.get_credentials()
            client = meet_v2.SpacesServiceClient(credentials=credentials)
            request = meet_v2.CreateSpaceRequest()
            response = client.create_space(request=request)

            return {
                "meeting_uri": response.meeting_uri
            }
        except Exception as e:
            logger.error(f"Failed to create meeting: {e}")
            raise Exception(f"Failed to create meeting: {str(e)}")