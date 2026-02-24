from datetime import datetime,timedelta,timezone
import webbrowser
import time
import logging
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def getService():

    creds = None
    # if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json',SCOPES)

    # if logging in first time
    if not creds or not creds.valid:
        # if credentials are expired request for new ones
        if creds and creds.expired and creds.refresh_token:
            print("creds expired")
            creds.refresh(Request())

        # creds are not expired
        else:   
            print("creds not expired\n")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json',SCOPES)
            creds = flow.run_local_server(port=0) 

        
        with open('token.json',mode = 'w') as token:
            print("to token\n")
            token.write(creds.to_json())
    service = build('calendar','v3',credentials=creds)
  
    return service


def checkMeeting():

    service = getService()
    now = datetime.now(timezone.utc)
    # will get meetings scheduled in next five minutes
    five_minutes = now + timedelta(minutes=5)
    events_result = service.events().list(
        calendarId = 'primary',
        timeMin = now.isoformat(),
        timeMax = five_minutes.isoformat(), 
        singleEvents = True,
        orderBy = 'startTime'
    ).execute()

    events = events_result.get('items',[])
    print(events[0])
    if not events:
        return None

    return events[0]

    

def main():
    already_joined = set()

    while True:
        try:
            meeting = checkMeeting()
            if meeting:
                id=meeting.get('id')
                url = meeting.get('hangoutLink')
                status = meeting.get('status')
                start_str = meeting.get('start').get('dateTime')
                start_time = datetime.fromisoformat(start_str)
                start_time = start_time.astimezone(timezone.utc)
                join_now = datetime.now(timezone.utc) + timedelta(minutes=1)

                if start_time<=join_now and id not in already_joined:
                    if status != "cancelled":
                        logging.info("Joining meeting")
                        webbrowser.open(url)
                        
                        already_joined.add(id)
            time.sleep(30)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
