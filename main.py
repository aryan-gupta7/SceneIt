from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from wtforms import StringField, PasswordField, SubmitField
from werkzeug.security import generate_password_hash, check_password_hash
import mail_scraper
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta, time, date
import analyse
import re
import os
from sqlalchemy.sql import func

import quickstart
creds = quickstart.get_credentials()
service = quickstart.build("calendar", "v3", credentials=creds)




app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/www'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CSRFProtect(app)

db = SQLAlchemy(app)

user_event_interest = db.Table('user_event_interest',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True)
)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False, default="Location to be decided")
    timing = db.Column(db.Time, nullable=False, default=time(18, 0))  # Default to 6:00 PM
    duration = db.Column(db.Integer, nullable=False, default=60)  # Default duration: 1 hour (60 minutes)
    type_ = db.Column(db.String(100), nullable=False, default="Not specified")
    tag = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False, default="No description available")
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    interested_users = db.relationship('User', secondary=user_event_interest, back_populates='interested_events')

    def __repr__(self):
        return f'<Event {self.name}>'
    
    @property
    def interest_count(self):
        return len(self.interested_users)

    def to_dict(self):
        today = date.today()
        return {
            'id': self.id,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'timing': self.timing.isoformat() if self.timing else None,
            'duration': self.duration,
            'type_': self.type_,
            'description': self.description,
            'interest_count': self.interest_count,
            'tag': self.tag,
            'is_past_event': self.date < today if self.date else False
        }
    
    @property
    def interest_count(self):
        return len(self.interested_users)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(8), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    interested_events = db.relationship('Event', secondary=user_event_interest, back_populates='interested_users')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class LoginForm(FlaskForm):
    roll_no = StringField('Roll Number', validators=[DataRequired(), Length(min=8, max=8)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    roll_no = StringField('Username', validators=[DataRequired(), Length(min=8, max=8, message="Username must be exactly 8 digits")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_roll_no(self, roll_no):
        if not re.match(r'^\d{8}$', roll_no.data):
            raise ValidationError('Username must be exactly 8 digits.')
        user = User.query.filter_by(username=roll_no.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_password(self, password):
        if not re.search("[a-z]", password.data):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search("[A-Z]", password.data):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search("[0-9]", password.data):
            raise ValidationError("Password must contain at least one number.")

def process_and_add_events():
    emails = mail_scraper.get_mail_content(max_results=100)
    for email in emails:
        analysis = analyse.analyse_email(email)
        if analysis and not analysis.startswith("No output"):
            event_data = parse_event_data(analysis)
            if event_data:
                add_event_to_database(event_data)
        else:
            print(f"Skipping email. Subject: {email['subject']}")

def parse_event_data(analysis):
    lines = analysis.split('\n')
    event_data = {}
    current_key = None
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            if key in ['event_name', 'event_date', 'event_location', 'event_timing', 'event_type', 'event_description', 'event_tag']:
                current_key = key
                event_data[key] = value
        elif current_key and line.strip():
            event_data[current_key] += ' ' + line.strip()

    # Handle missing fields
    required_fields = ['event_name', 'event_date', 'event_location', 'event_timing', 'event_type', 'event_description', 'event_tag']
    for field in required_fields:
        if field not in event_data:
            event_data[field] = 'Not specified'

    # Clean up data
    event_data['event_date'] = event_data['event_date'].replace('(Not specified in the mail)', 'Not specified')
    event_data['event_location'] = event_data['event_location'].replace('(Not specified in the mail)', 'Not specified')
    event_data['event_timing'] = event_data['event_timing'].replace('(Not specified in the mail)', 'Not specified')

    return event_data if event_data else None

def parse_date(date_str):
    date_formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d']
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def parse_time(time_str):
    time_formats = ['%H:%M', '%I:%M %p', '%H:%M:%S']
    for fmt in time_formats:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    return None

def add_event_to_database(event_data):
    # Check if event_date is provided
    if 'event_date' not in event_data or not event_data['event_date']:
        print(f"Event date not provided for event: {event_data.get('event_name', 'Unknown event')}. Skipping.")
        return False

    parsed_date = parse_date(event_data['event_date'])
    if not parsed_date:
        print(f"Invalid date format for event: {event_data.get('event_name', 'Unknown event')}. Skipping.")
        return False

    parsed_time = parse_time(event_data.get('event_timing', ''))
    if not parsed_time:
        parsed_time = time(18, 0)  # Default to 6:00 PM if time is not provided or invalid

    existing_event = Event.query.filter_by(name=event_data['event_name'], date=parsed_date).first()
    
    if existing_event:
        existing_event.location = event_data.get('event_location', existing_event.location)
        existing_event.timing = parsed_time
        existing_event.type_ = event_data.get('event_type', existing_event.type_)
        existing_event.description = event_data.get('event_description', existing_event.description)
        existing_event.tag = event_data.get('event_tag', existing_event.tag)
        existing_event.duration = event_data.get('event_duration', existing_event.duration)
        print(f"Event '{existing_event.name}' updated.")
    else:
        new_event = Event(
            name=event_data['event_name'],
            date=parsed_date,
            location=event_data.get('event_location', "Location to be decided"),
            timing=parsed_time,
            type_=event_data.get('event_type', 'Not specified'),
            description=event_data.get('event_description', 'No description available'),
            tag=event_data.get('event_tag'),
            duration=event_data.get('event_duration', 60)  # Default duration: 1 hour (60 minutes)
        )
        db.session.add(new_event)
        print(f"New event '{new_event.name}' added.")
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error adding/updating event: {str(e)}")
        return False



@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.roll_no.data).first()
        if user:
            if user.check_password(form.password.data):
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('User does not exist. Please check your roll number or Register.', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(fullname=form.full_name.data, username=form.roll_no.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    now = datetime.now()
    today = now.date()
    current_time = now.time()

    upcoming_events = Event.query.filter(Event.date > today).order_by(Event.date, Event.timing).all()
    ongoing_events = Event.query.filter(
        (Event.date == today) & 
        (Event.timing <= current_time)
    ).order_by(Event.timing).limit(6).all()

    feedback_items = Event.query.filter(Event.date < today).order_by(Event.date.desc()).all()

    def serialize_event(event):
        event_dict = event.to_dict()
        event_dict['is_interested'] = event in user.interested_events
        return event_dict

    upcoming_events_serialized = [serialize_event(event) for event in upcoming_events]
    ongoing_events_serialized = [serialize_event(event) for event in ongoing_events]
    feedback_items_serialized = [serialize_event(event) for event in feedback_items]

    return render_template('index.html', 
                           user=user, 
                           upcoming_events=upcoming_events_serialized, 
                           ongoing_events=ongoing_events_serialized, 
                           feedback_items=feedback_items_serialized)


@app.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    
    # Clear any existing flash messages
    _ = get_flashed_messages()
    
    # Set the logout flash message
    flash('You have been logged out successfully.', 'info')
    
    return redirect(url_for('login'))


@app.route('/mark_interest/<int:event_id>', methods=['POST'])
def mark_interest(event_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in to mark interest.'}), 401

    user = User.query.get(session['user_id'])
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Event not found.'}), 404
    if event in user.interested_events:
        user.interested_events.remove(event)
        interested = False
        message = "You are no longer interested in this event."
    else:
        user.interested_events.append(event)
        interested = True
        message = "You are now interested in this event."

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'interested': interested,
            'interest_count': event.interest_count,
            'message': message
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500


@app.route('/update_events')
def update_events():
    process_and_add_events()
    flash('Events have been updated from emails.', 'success')
    return redirect(url_for('home'))

# @app.route('/get_upcoming_events')
# def get_upcoming_events():
#     upcoming_events = Event.query.filter(Event.date >= datetime.now().date()).order_by(Event.date).limit(7).all()
#     return jsonify([event.to_dict() for event in upcoming_events])

# @app.route('/get_ongoing_events')
# def get_ongoing_events():
#     ongoing_events = Event.query.filter(Event.type_ == 'Ongoing').limit(6).all()
#     return jsonify([event.to_dict() for event in ongoing_events])

# @app.route('/get_feedback')
# def get_feedback():
#     # Implement this when you have feedback data
#     return jsonify([])

@app.route('/add_to_calendar', methods=['POST'])
def add_to_calendar():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in to add events to your calendar.'}), 401

    data = request.json
    event_id = data.get('event_id')
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Event not found.'}), 404

    try:
        start_time = datetime.combine(event.date, event.timing or time(0, 0))
        end_time = start_time + timedelta(minutes=event.duration or 60)

        formatted_start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        formatted_end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        creds = quickstart.get_credentials()
        service = quickstart.build("calendar", "v3", credentials=creds)

        calendar_event = quickstart.put_event(service, event.name, formatted_start_time, formatted_end_time)

        if calendar_event:
            return jsonify({'success': True, 'message': 'Event added to calendar successfully.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add event to calendar.'}), 500

    except Exception as e:
        print(f"Error adding event to calendar: {str(e)}")
        return jsonify({'success': False, 'message': f'An error occurred while adding the event to the calendar: {str(e)}'}), 500

@app.route('/check_username')
def check_username():
    username = request.args.get('username', '')
    if not username.isdigit():
        return jsonify({'available': False, 'message': 'Username must contain only numbers'})
    user = User.query.filter_by(username=username).first()
    return jsonify({'available': user is None})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # app.run(host = "0.0.0.0", debug=True)
    app.run(host = "0.0.0.0", debug=True)















