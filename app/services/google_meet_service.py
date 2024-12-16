# app/services/google_meet_service.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import pickle
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
        self.token_path = 'token.pickle'

    async def get_credentials(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('calendar', 'v3', credentials=self.creds)
        return self.creds

    async def create_meeting(self, tutor_email: str, tutee_email: str):
        try:
            credentials = await self.get_credentials()

            start_time = datetime.now()
            end_time = start_time + timedelta(hours=1)

            event = {
                'summary': '다육이 1:1 튜터링',
                'description': '다육이 1:1 튜터링',
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
                    },
                    {
                        'email': tutee_email,
                        'responseStatus': 'accepted'
                    }
                ],
                # 모든 참가자가 수정할 수 있도록 설정
                'guestsCanModify': True,
                'guestsCanInviteOthers': True,
                'anyoneCanAddSelf': True,
                # 기본 알림 설정 사용
                'reminders': {
                    'useDefault': True
                }
            }

            # 이벤트 생성
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