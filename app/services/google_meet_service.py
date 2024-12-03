# app/services/google_meet_service.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)


class GoogleMeetService:
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]

    def __init__(self):
        self.creds = None
        self.service = None

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

        self.service = build('calendar', 'v3', credentials=self.creds)
        return self.creds

    async def create_meeting(self, tutor_email: str):
        try:
            credentials = await self.get_credentials()

            start_time = datetime.now()
            end_time = start_time + timedelta(hours=1)

            event = {
                'summary': '튜터링 세션',
                'description': '1:1 튜터링 세션\n\n* 튜터님은 미팅 참여 후 "호스트 권한 요청"을 클릭하여 공동 호스트 권한을 얻을 수 있습니다.',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'Asia/Seoul',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'meeting_{hash(datetime.now())}',
                        'conferenceSolutionKey': {
                            'type': 'hangoutsMeet'
                        }
                    }
                },
                'attendees': [
                    {
                        'email': tutor_email,
                        'responseStatus': 'accepted'
                    }
                ],
                'guestsCanModify': True,
                'guestsCanInviteOthers': True,
                'anyoneCanAddSelf': False
            }

            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            conference_data = event.get('conferenceData', {})
            meet_link = conference_data.get('entryPoints', [{}])[0].get('uri', '')

            return {
                "meeting_uri": meet_link,
                "event_id": event['id']
            }

        except Exception as e:
            logger.error(f"Failed to create meeting: {e}")
            raise Exception(f"Failed to create meeting: {str(e)}")