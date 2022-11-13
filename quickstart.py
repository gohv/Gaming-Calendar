from __future__ import print_function

import datetime
import os.path
import requests
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
GAME_CAL_ID = "ADD CALENDAR ID HERE"
GET_GAMES = "https://api.rawg.io/api/games?key=d430c2ba8e9146d7af53c78d27ba9a57&dates=2023-12-01,2024-12-30"

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    #get game
    game_request = requests.get(GET_GAMES)

    games_list_raw = json.loads(game_request.content.decode("utf-8"))
    game_results = games_list_raw.get("results")
    name = ""
    release_date = ""
    event = {}

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId=GAME_CAL_ID, timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        #Adds the game to the calendar
        for single_game in game_results:
            name = single_game["name"]
            release_date = single_game["released"]
            image = single_game["background_image"]
            slug = single_game["slug"]
            #Get single game details through slug
            game_details = requests.get(
                "https://api.rawg.io/api/games/" + slug + "?key=d430c2ba8e9146d7af53c78d27ba9a57")
            game_details_raw = json.loads(game_details.content.decode("utf-8"))
            description = game_details_raw["description"]
            url = game_details_raw["website"]
            event = {
                'summary': name,
                'location': url,
                'description': description,
                'start': {
                    'dateTime': release_date + 'T09:00:00-07:00',
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    'dateTime': release_date + 'T09:00:00-07:00',
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            event = service.events().insert(calendarId=GAME_CAL_ID, body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

        if not events:
            print('No upcoming events found.')
            return
        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print("HERE " + start, event['summary'])

    except HttpError as error:
                print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
