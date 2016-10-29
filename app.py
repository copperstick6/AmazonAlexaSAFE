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
def launch():
	print('launching', file=sys.stderr)
	#print("EMERGENCY", file=sys.stderr)
	#result = getNaturalAlerts()
	#return statement("\n".join(result))
	#return statement('emergency')

@ask.intent('AlertIntent')
def alert():
	print("Alert", file=sys.stderr)
	result = getNaturalAlerts()
	print(result, file=sys.stderr)
	return statement("alerting")
	#return statement("\n".join(getNaturalAlerts()))
	#return statement("Your city is " + city);

def getNaturalAlerts():
	eventList = []
	events = getNaturalEvents()
	for event in events:
		eventLat, eventLon = [float(i) for i in event[2].split(' , ')]
		# dummy userLat and userLon values
		userLat = -4.7155
		userLon = 153.1534
		if calculateDistance(eventLat, eventLon, userLat, userLon) <= 100:
			# appends the titles of the natural events
			eventList.append(event[0])
	return eventList

if __name__ == '__main__':
	app.run()
