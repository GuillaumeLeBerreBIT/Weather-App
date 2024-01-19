import json, requests, re
from datetime import datetime

def city_names_to_lat_long(city_name):
    # Load in the API Key
    api_key = load_credentials('environment.json')
    
    # Number of locations in the API response
    limit = 1
    # The city name want to look up  
    city_name = city_name
    # Instead of formatting the string, set all the parameters in a dictionary and parse them into the request call
    params = {
        'q': city_name,
        'limit': limit,
        'appid': api_key
    }
    # Get the response call from the API
    response = requests.get(url = 'http://api.openweathermap.org/geo/1.0/direct', params = params)
    # Load in the information in a dictionary
    city_dictionary = response.json()
    # Get the latitude and longitude values
    lat, lon = city_dictionary[0]['lat'], city_dictionary[0]['lon']
    
    # What can do now, only need to call this function it will automatically call the function tog et the weather data >> Can now return again and is it in the front end
    current_weather_data, daily_forecast_data = fetch_weather_data(lat, lon, api_key)
    
    return current_weather_data, daily_forecast_data

def load_credentials(json_file):
    # Read in file with credentials
    json_cred_list = open(json_file)
    # Load in the json file
    dict_cred = json.load(json_cred_list)
    # Return the API key from my dictionary
    return dict_cred[0]['key']

def fetch_weather_data(lat, lon, api_key):
    # Formatted url string 
    current_weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}'
    # Read in the JSON format file from the API endpiont
    response = requests.get(url = current_weather_url).json()

    # Display the time
    dt_object = datetime.utcfromtimestamp(response['dt'])
    #print(dt_object.strftime('%Y-%m-%d %H:%M:'))
    
    if 'rain' in response:
        rain_fallen = response['rain']['rain.1h']
    else: 
        rain_fallen = 0

    current_weather_data = {
        'description': response['weather'][0]['description'],   # Weather description
        'icon': response['weather'][0]['icon'],                 # Weather Icon
        'current_temp': response['main']['temp'],               # Current Temp
        'min_temp': response['main']['temp_min'],               # Min Temp
        'max_temp': response['main']['temp_max'],               # Max Temp
        'wind_degree': response['wind']['deg'],                 # Wind Degree
        'wind_speed': response['wind']['speed'],                # Wind speed
        'visibility': response['visibility'],                   # Visibility
        'rain': rain_fallen                                     # Rain
    }

    # Format the URL link
    forecast_weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}'
    # Read in the JSON format from the API response object
    response = requests.get(url = forecast_weather_url).json()
    # Define an empty library on beforehand
    daily_forecast_data = {}
    # Since the list only has timestamps up to 5 days, we do not need to slice and can check only for specific hour to get the data
    for d in response['list']:
        # Only want the weather of the afternoon
        if re.search('12:00:00', d['dt_txt']):
            
            daily_forecast_data[d['dt_txt']] = {
                'description': d['weather'][0]['description'],   # Weather description
                'icon': d['weather'][0]['icon'],                 # Weather Icon
                'current_temp': d['main']['temp'],               # Current Temp
                'min_temp': d['main']['temp_min'],               # Min Temp
                'max_temp': d['main']['temp_max'],               # Max Temp
                'wind_degree': d['wind']['deg'],                 # Wind Degree
                'wind_speed': d['wind']['speed'],                # Wind speed
                'visibility': d['visibility']                    # Visibility
            }
    #print(daily_forecast_data)
    
    # Return a list of daily forecast data and current weather
    return current_weather_data, daily_forecast_data
