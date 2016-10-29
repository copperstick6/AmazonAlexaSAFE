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

# set up the login manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# mongo setup
app.config['MONGO_DBNAME'] = 'safe_db'
mongo = PyMongo(app)

# email stuff
gmail_username = 'safe2faconfirm@gmail.com'
# TODO turn off DEBUG when in production
app.config.update(
	DEBUG = True,
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USE_SSL = True,
	MAIL_USERNAME = gmail_username,
	MAIL_PASSWORD = keys.gmail_password()
	)
mail = Mail(app)

#@ask.intent('EmergencyIntent')
@ask.launch
def emergency():
	return render_template('emergency')

@ask.intent('AlertIntent', mapping={'city': 'City'})
def alert():
	return statement("Your city is " + city);

# send emergency text
# TODO deal w/ missing number
def send_emergency_text(address, msg_body):
	print("TEXTING", file=sys.stderr)
	client = TwilioRestClient(keys.twilioSSIDKey(), keys.twilioAuth())
	message = client.messages.create(body = msg_body,
		to = address,
		from_ = keys.phoneNumber())

# send emergency email
# TODO deal w/ invalid email addresses
def send_emergency_email(address, msg_body):
	print("EMAILING", file=sys.stderr)
	print("ADDRESS:", address, file=sys.stderr)
	msg = Message('Emergency', sender = gmail_username, recipients = [address])
	msg.body = msg_body
	mail.send(msg)

def getNaturalAlerts()
	for event in events:
		eventLat, eventLon = [float(i) for i in event[2].split(' , ')]
		if calculateDistance(eventLat, eventLon, userLat, userLon) < 5000000:

if __name__ == '__main__':
	app.run()
