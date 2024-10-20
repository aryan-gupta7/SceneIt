import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events","https://www.googleapis.com/auth/calendar"]
# SCOPES = []  # Changed to allow write access

# Define a fixed time interval (in minutes) for events without an end time
FIXED_TIME = 60  # 1 hour

def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

def put_event(service, event_name, start_time, end_time=None):
    # Convert start_time to datetime object if it's a string
    if isinstance(start_time, str):
        start_time = datetime.datetime.fromisoformat(start_time)

    # If end_time is not provided, use FIXED_TIME to calculate it
    if end_time is None:
        end_time = start_time + datetime.timedelta(minutes=FIXED_TIME)
    elif isinstance(end_time, str):
        end_time = datetime.datetime.fromisoformat(end_time)

    event = {
        'summary': event_name,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',  # Replace with your timezone, e.g., 'America/New_York'
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',  # Replace with your timezone
        },
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
        return event
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def main():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Example usage of put_event function
    # put_event(service, "Team Meeting", "2024-03-15T10:00:00")
    # put_event(service, "Conference Call", "2024-03-16T14:00:00", "2024-03-16T15:30:00")
    put_event(service, "Test Event With Time", "2024-10-19T10:00:00","2024-10-20T10:00:00")
    put_event(service, "Test Event Without end time", "2024-10-19T09:00:00")


    # Original code to list events
    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        print("Getting the upcoming 10 events")
        events_result = service.events().list(calendarId="primary", timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy="startTime").execute()
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")
    

if __name__ == "__main__":
    main()
