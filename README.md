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


    class activity
     |  A class that represents a Garmin Connect activity
     |  
     |  Methods defined here:
     |  
     |  __init__(self, json)
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  distance
     |      Returns the distance of the activity as a float
     |  
     |  duration
     |      Returns an instance of datetime.timedelta for the duration of the
     |      activity
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
     |  unit
     |      Returns the unit of measurement for the activity. Either 'mile' or
     |      'kilomiter'
