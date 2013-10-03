# Copyright (c) 2013, Liam Fraser <liam@liamfraser.co.uk>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import mechanize
import cookielib
import simplejson
import re
import time
import datetime
from decimal import *

class activity:
    """A class that represents a Garmin Connect activity"""

    def __init__(self, json):
        self._json = json

    @property
    def json(self):
        """A dictionary that represents the JSON data of the activity"""
        
        return self._json['activity']

    @property
    def name(self):
        """The name of the activity"""
        
        return self.json['activityName']['value']

    @property
    def duration(self):
        """Returns an instance of datetime.time for the duration of the
        activity"""
        
        time_string = self.json['sumDuration']['display']
        split = time_string.split(':')
        hours = int(split[0])
        minutes = int(split[1])
        seconds = int(split[2])
        return datetime.time(hour = hours, minute = minutes, second = seconds)

    @property
    def duration_seconds(self):
        """Returns an int of the duration of the activity in seconds"""

        seconds = self.duration.hour * 60 * 60
        seconds += self.duration.minute * 60
        seconds += self.duration.second
        return seconds

    @property
    def distance(self):
        """Returns the distance of the activity as a float"""

        dist_string = self.json['sumDistance']['value']
        return float(dist_string)

    @property
    def distance_short(self):
        """Returns the distance of the activity as a decimal.Decimal"""

        d = Decimal(self.distance).quantize(Decimal('.01'), rounding=ROUND_UP)
        return d

    @property
    def unit(self):
        """Returns the unit of measurement for the activity. Either 'mile' or
        'kilomiter'"""

        return self.json['sumDistance']['uom']

    @property
    def short_unit(self):
        """Returns an abbreviation of the unit"""

        unit_map = {"mile" : "Mi",
                    "kilomiter" : "Km"}

        return unit_map[self.unit]
    
    @property
    def pace_unit(self):
        """Returns an abbreviation of the unit in pace form"""

        unit_map = {"mile" : "Min/Mi",
                    "kilomiter" : "Min/Km"}

        return unit_map[self.unit]


    @property
    def pace(self):
        """Returns the pace as a datetime.datetime instance"""

        return self.pace_calculator(self.duration_seconds, self.distance)

    @staticmethod
    def pace_calculator(duration_seconds, distance):
        """Returns the pace as a datetime.datetime instance. Takes the duration
        in seconds and distance as arguments"""

        seconds_per_distance = float(duration_seconds / distance)

        # Convert the seconds back to minutes and seconds
        pace_td = datetime.timedelta(seconds = seconds_per_distance)
        pace_d = datetime.datetime(1,1,1) + pace_td

        return pace_d

    @property
    def datetime(self):
        """Returns the date and time that the run started as an instance of
        datetime.datetime"""

        start_time = self.json['beginTimestamp']['display']
        # We need to convert a string in the form:
        # Wed, Sep 25, 2013 19:09
        # To an instance of datetime

        t_match = re.match('(\w+), (\w+) (\d+), (\d+) (\d+):(\d+)',
                           start_time)
        t_day_str = t_match.group(1)
        t_month_str = t_match.group(2)
        t_day_of_month = t_match.group(3)
        # For year, we only want the last 2 digits
        t_year_str = t_match.group(4)[-2:]
        t_hours = t_match.group(5)
        t_minutes = t_match.group(6)
        
        # Convert this to a string that can be parsed with strptime
        t_str = "{0} {1} {2} {3} {4}".format(t_day_of_month,
                                             t_month_str,
                                             t_year_str,
                                             t_hours,
                                             t_minutes)
        start_time = time.strptime(t_str, "%d %b %y %H %M")

        # Now turn the struct_time object into a datetime object
        start_time = datetime.datetime.fromtimestamp(time.mktime(start_time))

        return start_time

class activities:
    """A simple Python class that allows you to log into Garmin Connect and get
    activity data"""

    def __init__(self, username, password):
        """Create a mechanize browser and then call the login function with the
        supplied credentials"""
        
        self._username = username
        self._password = password
       
        # Initialize the mechanize stuff that we'll use to talk to the API
        self._m = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        self._m.set_cookiejar(cj)
        # Pretend that we're firefox
        self._m.addheaders = [('User-agent',
                              'Mozilla/5.0 (X11; Linux x86_64; rv:22.0)'
                              ' Gecko/20100101 Firefox/22.0')]

        self._login()

    def _login(self):
        """Authenticate with garmin connect"""

        self._m.open('https://connect.garmin.com/signin')
        self._m.select_form('login')
        self._m.form['login:loginUsernameField'] = self._username
        self._m.form['login:password'] = self._password
        r = self._m.submit()

        # We should now be logged in. Lets check if there were any error messages
        if 'errorMessage' in r.read():
            raise Exception("Authentication Error!")

    def _api_request(self, url):
        """Do an API request. If it fails try logging in again and do it
        again""" 

        try_count = 0
        tries = 2
        while try_count < tries:
            r = self._m.open(url)
            if r.code == 200:
                # Success
                return r.read()
            else:
                # Log in and we'll try again on the next loop
                self.login()
                
            try_count += 1

        raise Exception("API Error!")   
 
    def _get_activity_page(self, start = 0):
        """Return a dicitionary representing the JSON data from a page of
        activities""" 
        
        url = ('http://connect.garmin.com/proxy/activity-search-service-1.0/'
               'json/activities?start={0}'.format(start))
        json = simplejson.loads(self._api_request(url))
        return json['results']

    def get_latest(self):
        """Return an instance of the activity class for the latest activity"""
        json = self._get_activity_page()['activities']
        return activity(json[0])

    def get_all(self):
        """Return a list of instances of the activity class"""

        jsons = []
        i = 0
        total = 0

        while i < total or total == 0:
            json = self._get_activity_page(i)
            
            # Find out how many activities we have on Garmin Connect            
            try:
                total = json['search']['totalFound']
            except KeyError as error:
                # Bad data from API
                print "Key Error: "   + error.message
                return []

            # Add the number of activities we got to i
            try:
                i += len(json['activities'])
            except KeyError:
                # We have no more activities
                break

            # Add the new json to the collection
            jsons.append(json)

        # Turn the json into a collection of activities we can return
        activities = []

        for json in jsons:
            for a in json['activities']:
                activities.append(activity(a))

        return activities

    def get_week(self, week = None):
        """Return a list of instances of the activity class for the week
        (Monday - Sunday). Optionally takes the week of the year to get"""

        # We're going to be lazy about this and filter the results from the
        # the get_all function because we won't be making api requests
        # frequently

        all_activities = self.get_all()
        week_activities = []

        # Get the week number of this week
        week_num = None
        if week == None:
            now = datetime.datetime.now()
            year, week_now, day_of_week = now.isocalendar()
            week_num = week_now
        else:
            week_num = week

        # Loop through each activity and add it to the collection if it's in
        # this week
        for a in all_activities:
            a_year, a_week, a_day_of_week = a.datetime.isocalendar()
            if a_week == week_num:
                week_activities.append(a)
        
        return week_activities
