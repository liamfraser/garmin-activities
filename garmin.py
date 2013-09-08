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
from datetime import datetime, timedelta

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
        """Returns an instance of datetime.timedelta for the duration of the
        activity"""
        
        time_string = self.json['sumDuration']['display']
        split = time_string.split(':')
        hours = int(split[0])
        minutes = int(split[1])
        seconds = int(split[2])
        return timedelta(hours = hours, minutes = minutes, seconds = seconds)

    @property
    def distance(self):
        """Returns the distance of the activity as a float"""

        dist_string = self.json['sumDistance']['value']
        return float(dist_string)

    @property
    def unit(self):
        """Returns the unit of measurement for the activity. Either 'mile' or
        'kilomiter'"""

        return self.json['sumDistance']['uom']

    @property
    def pace(self):
        """Returns the pace as a datetime.datetime instance"""

        duration_seconds = int(self.duration.total_seconds())
        seconds_per_distance = duration_seconds / self.distance

        # Convert the seconds back to minutes and seconds
        pace_td = timedelta(seconds = seconds_per_distance)
        pace_d = datetime(1,1,1) + pace_td

        return pace_d
        

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
            json = self._api_request(i)
            
            # Find out how many activities we have on Garmin Connect            
            try:
                total = json['results']['search']['totalFound']
            except KeyError:
                # Bad data from API
                return []

            # Add the number of activities we got to i
            try:
                i += len(json['results']['activities'])
            except KeyError:
                # We have no more activities
                break

            # Add the new json to the collection
            jsons.append(json)

        # Turn the json into a collection of activities we can return
        activities = []

        for j in jsons:
            for a in json['results']['activities']:
                activities.append(activity(a))

        return activities