#!/usr/bin/python
# jcaldav.py - add caledar eveents to google calendar
# Jeremy Tammik, Autodesk Inc, 2015-08-20

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

#SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'jcaldav'

def get_credentials():
  """Gets valid user credentials from storage.

  If nothing has been stored, or if the stored credentials
  are invalid, the OAuth2 flow is completed to obtain the
  new credentials.

  Returns:
    Credentials, the obtained credential.
  """
  home_dir = os.path.expanduser('~')
  credential_dir = os.path.join(home_dir, '.credentials')
  if not os.path.exists(credential_dir):
    os.makedirs(credential_dir)
  credential_path = os.path.join(credential_dir,
                   'calendar-quickstart.json')

  store = oauth2client.file.Storage(credential_path)
  credentials = store.get()
  if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
    flow.user_agent = APPLICATION_NAME
    if flags:
      credentials = tools.run_flow(flow, store, flags)
    else: # Needed only for compatability with Python 2.6
      credentials = tools.run(flow, store)
    print 'Storing credentials to ' + credential_path
  return credentials

def quickstart_sample_main():
  """Shows basic usage of the Google Calendar API.

  Creates a Google Calendar API service object and
  outputs a list of the next 10 events on the user's
  calendar.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)

  now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
  print 'Getting the upcoming 10 events'
  eventsResult = service.events().list(
    calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
    orderBy='startTime').execute()
  events = eventsResult.get('items', [])

  if not events:
    print 'No upcoming events found.'
  for event in events:
    #print event
    start = event['start'].get('dateTime', event['start'].get('date'))
    dt = dateutil.parser.parse(start)
    start = dt.strftime('%Y-%m-%d %H:%M')
    print start, event['summary']

def add_event_sample_main():
  """Add an event using the Google Calendar API.

  Creates a Google Calendar API service object
  and creates a new event on the user's calendar.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)

  #"start": { # The (inclusive) start time of the event. For a recurring event, this is the start time of the first instance.
  #  "timeZone": "Europe/Zurich", # The time zone in which the time is specified. (Formatted as an IANA Time Zone Database name, e.g. "Europe/Zurich".) For recurring events this field is required and specifies the time zone in which the recurrence is expanded. For single events this field is optional and indicates a custom time zone for the event start/end.
  #  "dateTime": "2015-08-19T10:00", # The time, as a combined date-time value (formatted according to RFC3339). A time zone offset is required unless a time zone is explicitly specified in timeZone.
  #},

  body = {
    u'status': u'confirmed',
    u'kind': u'calendar#event',
    #u'start': {u'dateTime': u'2015-08-19T10:00:00+02:00'},
    u'start': {u'dateTime': u'2015-08-19T10:00:00', u'timeZone': u'Europe/Zurich'}, # trailing seconds are required!
    #u'end': {u'dateTime': u'2015-08-19T10:50:00+02:00'},
    u'end': {u'dateTime': u'2015-08-19T10:50:00', u'timeZone': u'Europe/Zurich'},
    #u'endTimeUnspecified': True, # this causes an error saying 'Forbidden'. Whether the end time is actually unspecified. An end time is still provided for compatibility reasons, even if this attribute is set to True. The default is False.
    u'summary': u'jeremy test event summary',
    u'organizer': {u'self': True, u'displayName': u'Jeremy Tammik', u'email': u'jeremytammik@gmail.com'},
    u'creator': {u'self': True, u'displayName': u'Jeremy Tammik', u'email': u'jeremytammik@gmail.com'}
  }
  print service.events().insert( calendarId='primary', body=body).execute()

def clear_all_events_main():
  "Clear all GCal entries."
  # I did this manually instead:
  # https://productforums.google.com/forum/#!topic/calendar/HjyCdrZydEI
  # Google Calendar Help Forum
  # How do I delete all Google calendar entries in my primary calendar?

def clean_calendar_entry(s):
  "Clean up a calendar entry for publication."
  s = s.strip()
  i = s.find('#')
  if -1 < i: s = s[:i]
  n = 50
  if n < len(s): s = s[:n-3] + '...'
  return s.strip()

def get_calendar_entries(log):
  """Retrieve all event entries from
  the master text-based calendar file."""
  f = open('/j/doc/db/jcal/calendar.txt')
  entries = [clean_calendar_entry(x)
             for x in f.readlines()
             if x.startswith('20')]
  f.close()
  if log:
    for x in entries: print x
  return entries

def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def parse_calendar_entry(e, log):
  """Extract and return start time, end time
  and summary from calendar entry."""
  if log: print e
  i = e.find(' ')
  assert -1 < i
  (date,summary) = e.split( None, 1 )
  i = summary.find(' ')
  if -1 == i: time = None
  else: (time,summary) = summary.split( None, 1 )

  starttime = endtime = None

  if time:
    if time[0] in '0123456789':
      a = time.split('-')
      assert(len(a) in [1,2])
      starttime = a[0]
      if 1 < len(a): endtime = a[1]
      else: endtime = None
    else:
      summary = time + ' ' + summary

  if not starttime: starttime = '06:00'

  # switch to datetime objects

  starttime = datetime.datetime.strptime(
    date + 'T' + starttime, '%Y-%m-%dT%H:%M')

  if endtime:
    if endtime.endswith('+1'):
      endtime = endtime[:-2]
      next_day = starttime + relativedelta(days=+1)
      date = next_day.strftime('%Y-%m-%d')

    endtime = datetime.datetime.strptime(
      date + 'T' + endtime, '%Y-%m-%dT%H:%M')
  else:
    endtime = starttime + relativedelta(minutes=+10)

  # switch back to string representation;
  # Google Calendar API requires trailing seconds

  starttime = starttime.strftime('%Y-%m-%dT%H:%M:%S')
  endtime = endtime.strftime('%Y-%m-%dT%H:%M:%S')

  if log: print starttime, endtime, summary

  return (starttime, endtime, summary)

def add_calendar_event( service, starttime, endtime, summary, log ):
  "Add an event using the Google Calendar API."

  if log: print starttime, endtime, summary

  me = {u'self': True,
        u'displayName': u'Jeremy Tammik',
        u'email': u'jeremytammik@gmail.com'}

  body = {
    u'status': u'confirmed',
    u'kind': u'calendar#event',
    u'start': {u'dateTime': starttime, u'timeZone': u'Europe/Zurich'}, # trailing seconds are required!
    u'end': {u'dateTime': endtime, u'timeZone': u'Europe/Zurich'},
    u'summary': summary,
    u'organizer': me,
    u'creator': me
  }
  service.events().insert( calendarId='primary', body=body).execute()


def main():
  """Add event entries from the master text-based
  calendar file to the online GCal using the Google
  Calendar API.

  Create a Google Calendar API service object, parse
  the text file, extract all events, and add them to
  GCal one by one.
  """
  credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  service = discovery.build('calendar', 'v3', http=http)

  entries = get_calendar_entries( log=False )

  for e in entries:
    (starttime, endtime, summary) = parse_calendar_entry(e, False)
    add_calendar_event( service, starttime, endtime, summary, True )


if __name__ == '__main__':
  #main()
  #add_event()
  #parse_calendar()
  #add_event_sample_main()
  #clear_all_events_main()
  main()
