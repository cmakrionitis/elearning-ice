import hashlib
import requests
from urllib.parse import urlencode
from django.conf import settings
import requests
import xml.etree.ElementTree as ET


class BigBlueButtonService:
    def __init__(self):
        self.base_url = settings.BBB_SERVER_URL.rstrip("/") + "/"
        self.secret = settings.BBB_SECRET

    def _checksum(self, action, query_string):
        raw = f"{action}{query_string}{self.secret}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def _url(self, action, params):
        query_string = urlencode(params)
        checksum = self._checksum(action, query_string)
        return f"{self.base_url}{action}?{query_string}&checksum={checksum}"

    def create_meeting(self, meeting):
        params = {
            "name": meeting.title,
            "meetingID": meeting.meeting_id,
            "moderatorPW": meeting.moderator_pw,
            "attendeePW": meeting.attendee_pw,
            "record": "true",
            "duration": 60,
        }

        url = self._url("create", params)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def join_url(self, meeting, full_name, user_id, role="attendee"):
        password = meeting.moderator_pw if role == "moderator" else meeting.attendee_pw

        params = {
            "meetingID": meeting.meeting_id,
            "fullName": full_name,
            "password": password,
            "userID": user_id,
            "redirect": "true",
        }

        return self._url("join", params)
    
    def is_meeting_running(self, meeting_id):
        action = "isMeetingRunning"

        params = {
            "meetingID": meeting_id
        }

        url = self._url(action, params)

        try:
            response = requests.get(url, timeout=5)

            print("BBB URL:", url)
            print("BBB STATUS:", response.status_code)
            print("BBB RESPONSE:", response.text)

            response.raise_for_status()

            root = ET.fromstring(response.content)

            returncode = root.findtext("returncode")
            running = root.findtext("running")

            return returncode == "SUCCESS" and running == "true"

        except Exception as e:
            print("BBB isMeetingRunning ERROR:", e)
            return False