garmin-activities
=================

A simple Python module that allows you to log into Garmin Connect and get activity data.

#### Requirements
* mechanize
* cookielib
* simplejson


#### Classes

    class activities
     |  A simple Python class that allows you to log into Garmin Connect and get
     |  activity data
     |  
     |  Methods defined here:
     |  
     |  __init__(self, username, password)
     |      Create a mechanize browser and then call the login function with the
     |      supplied credentials
     |  
     |  get_all(self)
     |      Return a list of instances of the activity class
     |  
     |  get_latest(self)
     |      Return an instance of the activity class for the latest activity
     |  
     |  get_week(self, week=None)
     |      Return a list of instances of the activity class for the week
     |      (Monday - Sunday). Optionally takes the week of the year to get
    
    class activity
     |  A class that represents a Garmin Connect activity
     |  
     |  Methods defined here:
     |  
     |  __init__(self, json)
     |  
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |  
     |  pace_calculator(duration_seconds, distance)
     |      Returns the pace as a datetime.datetime instance. Takes the duration
     |      in seconds and distance as arguments
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  datetime
     |      Returns the date and time that the run started as an instance of
     |      datetime.datetime
     |  
     |  distance
     |      Returns the distance of the activity as a float
     |  
     |  distance_short
     |      Returns the distance of the activity as a decimal.Decimal
     |  
     |  duration
     |      Returns an instance of datetime.time for the duration of the
     |      activity
     |  
     |  duration_seconds
     |      Returns an int of the duration of the activity in seconds
     |  
     |  json
     |      A dictionary that represents the JSON data of the activity
     |  
     |  name
     |      The name of the activity
     |  
     |  pace
     |      Returns the pace as a datetime.datetime instance
     |  
     |  pace_unit
     |      Returns an abbreviation of the unit in pace form
     |  
     |  short_unit
     |      Returns an abbreviation of the unit
     |  
     |  unit
     |      Returns the unit of measurement for the activity. Either 'mile' or
     |      'kilomiter'

