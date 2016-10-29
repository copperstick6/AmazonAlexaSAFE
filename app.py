from flask import Flask, render_template, request, flash, redirect, url_for
import flask_login
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FieldList, FormField, validators, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import TwilioRestClient
from flask_mail import Mail, Message
from flask_security import login_required
import random
import keys
import sys
from googleMapsDistance import *
from latLonCalc import *
from EventsFinder import *
import threading

# method to check if the email is unique
def unique_email(form, field):
	print(field.data, file=sys.stderr)
	result = mongo.db.users.find_one({'email': field.data})
	if result is not None:
		raise ValidationError('Email already exists')

# validator to check if phone number is required
def required_if_using_text(form, field):
	if dict([('email', 'Email'), ('text', 'Text Message')]).get(form.verify_method.data) == 'text':
		return validators.DataRequired('Phone Number is required')

# The signup form
# feel free to change the string values to something better
# TODO check about .data vs w/ out in selectfield
class RegisterForm(FlaskForm):
	# the verifcation method choices
	verify_choices = [('email', 'Email'), ('text', 'Text Message')]
	# all the fields
	first_name = StringField('First Name', [validators.DataRequired('First Name is required')])
	last_name = StringField('Last Name', [validators.DataRequired('Last Name is required')])
	email = StringField('Email', [validators.DataRequired('Email is required'), validators.Email(), unique_email])
	password = PasswordField('Password', [validators.DataRequired('Password is required'),
		validators.EqualTo('repeat_password', 'Passwords are not the same')])
	address = StringField('Address', [validators.DataRequired('Address is required')])
	repeat_password = PasswordField('Repeat Password', [validators.DataRequired('Must repeat password')])
	verify_method = SelectField('Chose Verification Method', choices=verify_choices)
	phone_number = StringField('Phone Number', [required_if_using_text])
	submit = SubmitField('Sign Up')

# The signup form
# Again, feel free to change the label values
class LoginForm(FlaskForm):
	email = StringField('Email', [validators.DataRequired('Email is required')])
	password = PasswordField('Password', [validators.DataRequired('Password is required')])
	submit = SubmitField('Login')

# The verification number form
class VerifyForm(FlaskForm):
	number = IntegerField('Verification Number', [validators.DataRequired('Verification Number is required and must be numeric')])
	submit = SubmitField('Verify')

# The form for one contact
class ContactForm(FlaskForm):
	name = StringField('Name', [validators.DataRequired('Name is required')])
	phone_number = StringField('Phone Number', [])
	email_field = StringField('Email', [validators.Email])

# The form for multiple contacts
class MultiContactForm(FlaskForm):
	all_contacts = FieldList(FormField(ContactForm), min_entries=1)
	submit = SubmitField('Update Contacts')
	def validate(self, **kwargs):
		if not super().validate():
			self.all_contacts.errors += (super().errors, 'super not validated')
			return False

# User class (used for logging in)
class User(flask_login.UserMixin):
	pass

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

# flashes form errors
def flash_errors(form):
	for field, errors in form.errors.items():
		for err in errors:
			flash("Error in the %s field: %s" % (getattr(form, field).label.text, err))

# the home page
@app.route('/')
def index():
	return render_template('index.html')

# the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		email = request.form['email']
		first = request.form['first_name']
		last = request.form['last_name']
		phone_number = request.form['phone_number']
		address = request.form['address']
		default_lat, default_long = [float(i) for i in getUnFormattedLongLat(address)]
		passwordHash = generate_password_hash(request.form['password'])
		verify_method = form['verify_method'].data
		print("VERIFICATION METHOD:", verify_method)
		unique_code = random.randint(10000, 99999)
		
		# send verification msg
		if verify_method == 'email':
			try:
				send_verification_email(unique_code, email)
			except:
				print(sys.exc_info(), file=sys.stderr)
				flash('Can\'t send email. Make sure email address is valid')
				return render_template('signup.html', form = form), 401
		elif verify_method == 'text':
			try:
				send_verification_text(unique_code, phone_number)
			except:
				flash('Can\'t send text. Make sure phone number is valid')
				return render_template('signup.html', form = form), 401
		#place user in database
		mongo.db.users.insert_one({'email': email, 'password': passwordHash, 'verify_code': unique_code,
			'first': first, 'last': last, 'contacts': [], 'lat': default_lat, 'long': default_long})
		user = load_user(email)
		flask_login.login_user(user)
		return redirect(url_for('verify'))
	elif request.method == 'POST':
		flash_errors(form)
		return render_template('signup.html', form = form), 401
	return render_template('signup.html', form = form)

# send verification text
# TODO deal w/ missing number
def send_verification_text(unique_code, address):
	print("TEXTING", file=sys.stderr)
	client = TwilioRestClient(keys.twilioSSIDKey(), keys.twilioAuth())
	msg_body = "Your verification code is: " + str(unique_code)
	message = client.messages.create(body = msg_body,
		to = address,
		from_ = keys.phoneNumber())

# send verification email
# TODO deal w/ invalid email addresses
def send_verification_email(unique_code, address):
	print("EMAILING", file=sys.stderr)
	print("ADDRESS:", address, file=sys.stderr)
	msg_body = "Your verification code is: " + str(unique_code)
	msg = Message('Verification Code', sender = gmail_username, recipients = [address])
	msg.body = msg_body
	mail.send(msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm(request.form)
	if request.method == 'POST' and form.validate():
		email = request.form['email']
		userRecord = mongo.db.users.find_one({'email': email})
		if userRecord is not None:
			user = User()
			user.id = email
			flask_login.login_user(user)
			return redirect(url_for('index'))
		else:
			flash('Invalid Login')
	elif request.method == 'POST':
		flash_errors(form)
		return render_template('login.html', form = form), 401
	return render_template('login.html', form = form)

@login_manager.user_loader
def load_user(email):
	emailRecord = mongo.db.users.find_one({'email': email})
	# if no user w/ this email exists, return None
	if emailRecord is None:
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	email = request.form.get('email')
	userRecord = mongo.db.users.find_one({'email': email})
	#print("USER RECORD IN REQ_LOADER:", userRecord, file=sys.stderr)
	# if no user w/ this email exists, return None
	if userRecord is None or 'email' not in request.form:
		return
	user = User()
	user.id = email
	print(request.form, file=sys.stderr)
	#request.form['password']
	passwordHash = request.form['password']
	user.is_authenticated = check_password_hash(passwordHash, password)
	return user

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	email = flask_login.current_user.id
	userRecord =  mongo.db.users.find_one({'email': email})
	verify_code = userRecord['verify_code']
	if verify_code != None:
		return redirect(url_for('verify'))
	contacts = userRecord['contacts']
	print(contacts, file=sys.stderr)
	for i in contacts:
		print(i, file=sys.stderr)
	form = MultiContactForm(request.form)
	print(form.all_contacts, file=sys.stderr)
	all_contacts = form.all_contacts
	to_add = []
	if request.method == 'POST':
		while len(all_contacts) > 0:
			cf = all_contacts.pop_entry()
			#if cf['name'].validate() and cf['phone_number'].validate() and cf['email_field'].validate():
			to_add.append({'name': cf['name'].data, 'phone_number': cf['phone_number'].data,'email_field': cf['email_field'].data})
			print(to_add, file=sys.stderr)
			#else:
			#	flash_errors(cf)
			#	return render_template('settings.html', form = form)
			#print(cf, file=sys.stderr)
		mongo.db.users.update_one({'email': email}, {'$set': {'contacts': to_add}})
	return render_template('settings.html', form = form)
	

@app.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
	email = flask_login.current_user.id
	userRecord = mongo.db.users.find_one({'email': email})
	verify_code = userRecord['verify_code']
	#password = userRecord['password']
	if verify_code == None:
		redirect(url_for('index'))
	form = VerifyForm(request.form)
	user_response = form['number'].data
	print(user_response, file=sys.stderr)
	if request.method == 'POST' and form.validate():
		if user_response != verify_code:
			flash('Invalid Verification Code')
			return render_template('verify.html', form = form), 401
		else:
			mongo.db.users.update_one({'email': email}, {'$set': {'verify_code': None} }, upsert=False)
			return redirect(url_for('index'))
	elif request.method == 'POST':
		flash_errors(form)
	return render_template('verify.html', form = form), 401

events = []
seen = set()
def send_alerts():
	global events
	global seen
	
	with app.app_context():
		try:
			# change value later
			threading.Timer(100, send_alerts).start()
			print('BEFORE QUERY', file=sys.stderr)
			all_users = mongo.db.users.find()
			print('AFTER QUERY', file=sys.stderr)
			events = getNaturalEvents(events)
			#events2 = set(events2) - set(events)
			print('EVENTS:', events, file=sys.stderr)
			print('GOT EVENTS', file=sys.stderr)
			#coords = [(float(j) for j in i[2].split(' , ')) for i in events]
			for user in all_users:
				for event in events:
					if event in seen:
						pass
					seen.add(event)
					print('USER, EVENT PAIR', file=sys.stderr)
					eventLat, eventLon = [float(i) for i in event[2].split(' , ')]
					userLat = user['lat']
					userLon = user['long']
					msg_body = user['first'] + ' ' + user['last'] + ' is near ' + event[0]
					if calculateDistance(eventLat, eventLon, userLat, userLon) < 5000000:
						print('IN DISTANCE', file=sys.stderr)
						ppl = user['contacts']
						for person in ppl:
							print('SENDING MSG', file=sys.stderr)
							if person.get('phone_number') != '':
								send_emergency_text(person.get('phone_number'), msg_body)
							if person.get('email') != '':
								send_emergency_email(person.get('phone_number'), msg_body)
		except:
			pass
		

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

if __name__ == '__main__':
	#some facebook test code
	#graph = facebook.GraphAPI(access_token = 'EAACEdEose0cBAMp0ENf0vQV9jZBlP72fjL8udks97VOFh7cNHF3J9OcdVN6ZAgxwJ292x5AAHErrumpv3yOsonUurVgt80su5F3s6PFqFeku721CYQGJIgXEa1ywtbDaJyWLJkYRPuZAVk20sTNyCmrxVMetkIDSA8CkM6TYGOSv9NlVkkh')
	#friends = graph.get_connections(id='me', connection_name='friends')
	#print(friends)
	send_alerts()
	app.run()
