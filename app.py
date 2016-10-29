from flask import Flask, render_template, request, flash, redirect, url_for
from flask_pymongo import PyMongo
from twilio.rest import TwilioRestClient
from flask_mail import Mail, Message
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
	return render_template('emergency')

@ask.intent('AlertIntent', mapping={'city': 'City'})
def alert():
	return statement("Your city is " + city);

# send emergency email
# TODO deal w/ invalid email addresses
def send_emergency_email(address, msg_body):
	print("EMAILING", file=sys.stderr)
	print("ADDRESS:", address, file=sys.stderr)
	msg = Message('Emergency', sender = gmail_username, recipients = [address])
	msg.body = msg_body
	mail.send(msg)

def getNaturalAlerts():
	for event in events:
		eventLat, eventLon = [float(i) for i in event[2].split(' , ')]
		if calculateDistance(eventLat, eventLon, userLat, userLon) < 5000000:
			pass

if __name__ == '__main__':
	app.run()
