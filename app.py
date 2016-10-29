from flask import Flask, render_template, request, flash, redirect, url_for
from flask_ask import Ask, statement, question
import keys
import sys
from googleMapsDistance import *
from latLonCalc import *
from EventsFinder import *

# set up the app
app = Flask(__name__)
app.secret_key = keys.app_secret()

# setup alexa stuff
ask = Ask(app, "/")

#@ask.intent('EmergencyIntent')
@ask.launch
def emergency():
	print("EMERGENCY", file=sys.stderr)
	return statement("\n".join(getNaturalAlerts()))
	#return statement('emergency')

@ask.intent('AlertIntent')
def alert():
	print("Alert", file=sys.stderr)
	return statement("\n".join(getNaturalAlerts()))
	#return statement("Your city is " + city);

def getNaturalAlerts():
	eventList = []
	events = getNaturalEvents()
	for event in events:
		eventLat, eventLon = [float(i) for i in event[2].split(' , ')]
		# dummy userLat and userLon values
		userLat = 30.27
		userLon = 97.74
		if calculateDistance(eventLat, eventLon, userLat, userLon) < 5000000:
			# appends the titles of the natural events
			eventList.append(event[0])
	return eventList

if __name__ == '__main__':
	app.run()
