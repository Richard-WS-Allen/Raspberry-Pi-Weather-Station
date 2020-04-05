'''
## License

The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import time
import grovepi
import math
import datetime
import json
import csv
import requests
from grove_rgb_lcd import *


# Connect the Grove LED to digital port D5, 2, and 6
led_blue = 5
led_red = 2
led_green = 6

# Connect the Grove Light Sensor to analog port A0
light_sensor = 0

grovepi.pinMode(light_sensor,"INPUT")
grovepi.pinMode(led_blue,"OUTPUT")
grovepi.pinMode(led_red,"OUTPUT")
grovepi.pinMode(led_green,"OUTPUT")

# Open weather api call setup
open_weather_api = "Your Key Here" # key to make api calls
zip_code = "29485" # Summerville sc
open_weather_url = "http://api.openweathermap.org/data/2.5/weather?" # Base url
complete_url = open_weather_url + "zip=" + zip_code + "&appid=" + open_weather_api


# Convert kelvin to farenheit
def to_farenheit(kelvin):
    return ((kelvin - 273.15) * (9 / 5)) + 32


# Make api call to return weather data
def get_weather():
    global complete_url
    
    response = requests.get(complete_url) # GET request

    weather_data = response.json() # Json object of response

    if weather_data["cod"] != "404":
        temperature = to_farenheit(weather_data["main"]["temp"]) # api response in kelvin
        weather_description = weather_data["weather"][0]["description"]
	    humidity = weather_data["main"]["humidity"]
		
	else:
		temperature = False
		weather_description = False
		humidity = False
        
    return temperature, weather_description, humidity
	
	
# Changed to write to csv. Keep better formatted log of weather data to view in excel if desired
# Allow appending to csv
def write_to_csv(data):
	with open('weather_data.csv', 'a+', newline='') as csvfile:
		cw = csv.writer(csvfile)
		cw.writerow(data)
		csvfile.close()


threshold = 100
while True:
    try:
        # Get sensor value
        sensor_value = grovepi.analogRead(light_sensor)
        
		if sensor_value < threshold:
            # continue to poll until > threshold
            continue
		
		# Get weather data with api call
		temperature, description, humidity = get_weather()
		
        # Set all leds to off
        grovepi.digitalWrite(led_blue,0)
        grovepi.digitalWrite(led_red,0)
        grovepi.digitalWrite(led_green,0)
		
        # Check for valid results
        if temperature and humidity and description:
			
			write_to_csv([datetime.datetime.now(), temperature, humidity, description])
            
            # Condititions to turn on LED
            if temperature > 60 and temperature < 85 and humidity < 80:
                # Green Led
                grovepi.digitalWrite(led_green,1)
            elif temperature > 85 and temperature < 95 and humidity < 80:
                # Blue Led
                grovepi.digitalWrite(led_blue,1)
            elif temperature > 95:
                # Red Led
                grovepi.digitalWrite(led_red,1)
            
            if humidity > 80:
                # Green and Blue LED
                grovepi.digitalWrite(led_green,1)
                grovepi.digitalWrite(led_blue,1)
		
		else:
		    # Set all leds to off
			grovepi.digitalWrite(led_blue,0)
			grovepi.digitalWrite(led_red,0)
			grovepi.digitalWrite(led_green,0)
			break
        
		# Write to LCD display
		setText("%.02f F\n%s"%(temperature, description))

        # Sleep for 30 minutes to limit writing
        time.sleep(1800)

    except IOError:
        print ("Error")
	
    #keyboard interrupt
    except KeyboardInterrupt:
        grovepi.digitalWrite(led_blue,0)
        grovepi.digitalWrite(led_green,0)
        grovepi.digitalWrite(led_red,0)

        print('Interrupted')
        break