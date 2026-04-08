import os
import tempfile
from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = "credentials/token.json"


class CalendarClient:
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        token_json = os.getenv("GOOGLE_TOKEN_JSON")

        if token_json:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                f.write(token_json)
                tmp_path = f.name
            creds = Credentials.from_authorized_user_file(tmp_path, SCOPES)
            os.unlink(tmp_path)
        elif os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds:
            raise RuntimeError("Google 인증 정보가 없습니다. GOOGLE_TOKEN_JSON 환경변수를 설정하세요.")

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def get_events(self, days: int = 14) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()

        result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=now,
                timeMax=end,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for e in result.get("items", []):
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            end_time = e["end"].get("dateTime", e["end"].get("date", ""))
            events.append({
                "id": e["id"],
                "title": e.get("summary", "제목 없음"),
                "start": start,
                "end": end_time,
            })
        return events

    def create_event(self, title: str, start_time: str, end_time: str) -> bool:
        event = {
            "summary": title,
            "start": {"dateTime": start_time, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Seoul"},
        }
        try:
            self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
            return True
        except Exception as e:
            print(f"[create_event 오류] {e}")
            return False

    def delete_event(self, event_id: str) -> bool:
        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
            return True
        except Exception as e:
            print(f"[delete_event 오류] {e}")
            return False

    def update_event(self, event_id: str, title: str, start_time: str, end_time: str) -> bool:
        event = {
            "summary": title,
            "start": {"dateTime": start_time, "timeZone": "Asia/Seoul"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Seoul"},
        }
        try:
            self.service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event).execute()
            return True
        except Exception as e:
            print(f"[update_event 오류] {e}")
            return False
