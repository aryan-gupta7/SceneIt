# SceneIt: Campus Event Discovery Platform

## Overview

SceneIt is an innovative solution designed to address the common problem of information overload and missed opportunities in campus environments. With numerous events happening simultaneously across campus, it's easy for students to miss out on events that align with their interests. SceneIt aims to streamline event discovery and notification, ensuring that students never miss out on events they care about.

## Problem Statement

In a bustling campus environment, students often face the following challenges:
1. Information overload from multiple event announcements
2. Difficulty in tracking events relevant to their interests
3. Missing out on interesting events due to lack of awareness or forgetfulness

## Solution

SceneIt provides a centralized platform for event management and discovery. The key features include:

1. **Event Aggregation**: Collects event information from various campus sources into a single database.
2. **User Profiles**: Allows students to create profiles and specify their interests.
3. **Smart Filtering**: Matches events to user interests, providing personalized event recommendations.
4. **Notification System**: Sends timely reminders about upcoming events of interest.
5. **Interactive Calendar**: Offers a visual representation of all campus events, with the ability to filter and search.

## How SceneIt Works

1. **Event Input**: Campus organizations and departments input their event details into SceneIt.
2. **User Registration**: Students create SceneIt accounts and set up their interest profiles.
3. **Matching Algorithm**: SceneIt continuously matches upcoming events with user profiles.
4. **Notifications**: Users receive notifications about events that match their interests.
5. **Event Discovery**: Users can also browse the full calendar of events and apply filters as needed.

## Technologies Used

1. Flask Framework(Python)
2. SQLAlchemy(Python)
3. WTForms(Python)
4. Gmail API
5. Google Calendar API
6. Javascript
7. HTML/CSS
8. GROQ LLAMA 3.1 70b


## Setup and Installation


### 1. Clone this repo or install zip.
`git clone https://github.com/aryan-gupta7/SceneIt`
### 2. Install the required libraries by
`pip install -r requirements.txt`
### 3. Get credentials.json and keys.json
`credentials.json` is a json file that has creds that are used to fetch mails using Gmail API and Add events using Calendar API. This can be found in the Google Clound Console Setup for a project and `keys.json` is a json file that has GROQ API for LLAMA Model which can be easily obtained by logging into GROQ's website
### 4. Setup Database
Make sure your system has a database system install, may it be MySQL, SQLite or PostgreSQL. After setting up, add the DATABASE_URI to the `main.py`.
### 5. You are good to go.
While running for the first time, you can go to localhost:port/update_events to fetch the events.


## Usage

SceneIt provides an intuitive interface for students to discover and engage with campus events. Here's how to use the main features of the application:

### 1. User Registration and Login

- Navigate to the login page ([url]).
- If you're a new user, click on the registration link to create an account.
- Fill in your details on the registration page ([url]).
- Once registered or if you're an existing user, log in with your credentials.

### 2. Home Page

After logging in, you'll be directed to the home page ([url]), which displays:

- A navigation bar with the SceneIt logo and your user profile.
- Three main sections:
  - Upcoming Events
  - Ongoing Events
  - Feedback (for past events)

### 3. Exploring Events

- Scroll through the rows of event cards in each section.
- Each event card displays:
  - Event title
  - Date and time
  - Tags or categories
  - Number of attendees

### 4. Event Details

- Click on an event card to view more details.
- In the expanded view, you'll see:
  - Full event description
  - Exact date and time
  - Event ID
  - Option to mark interest

### 5. Showing Interest

- Click the "I'm interested!" button on an event to add it to your interested events list.
- This helps SceneIt provide better recommendations in the future.

### 6. Calendar Integration

- Some events may have a calendar button.
- Clicking this will add the event to your Google Calendar (requires Google account integration).

### 7. Notifications

- SceneIt will send notifications about events matching your interests.
- Make sure to enable notifications in your account settings or browser to receive these alerts.



