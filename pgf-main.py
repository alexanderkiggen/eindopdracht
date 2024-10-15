from pprint import pprint
import requests
from datetime import datetime, timedelta
import pprint as pp

api_key_transport = '5b3ce3597851110001cf6248a452ed53f6894f49b807209008176de1'
api_key_weather = '97b8bfd53453a164a52bd9bbf84a080d'
geocode_url = 'https://api.openrouteservice.org/geocode/search'
directions_url = 'https://api.openrouteservice.org/v2/directions/driving-car'
weather_url = 'http://api.openweathermap.org/data/2.5/weather'

settings = {
    "temperature_unit": ["metric", ("metric", "imperial", "units")],
    "distance_unit": ["kilometers", ("kilometers", "miles")],
    "fuel_cost": [1.820, (1.820,)],
    "fuel_consumption": [7.0, (7.0,)]
}


def settings_menu(request_value=None, request_item=None):
    if request_value in settings:
        try:
            if request_value == "temperature_unit" or request_value == "distance_unit":
                if request_item.lower() in settings[request_value][1]:
                    settings[request_value][0] = request_item.lower()
                else:
                    return f"{request_item} is not part of {request_value}"

            elif request_value == "fuel_cost":
                try:
                    settings[request_value][0] = float(request_item)
                except ValueError:
                    return f"{request_item} cannot be converted to a float."

            elif request_value == "fuel_consumption":
                try:
                    consumption_value = float(request_item)
                    if consumption_value <= 100:
                        settings[request_value][0] = consumption_value
                    else:
                        return f"{request_item} is higher than 100."
                except ValueError:
                    return f"{request_item} cannot be converted to a float."

        except ValueError:
            return "Probeer het opnieuw"

    elif request_value == "restore_defaults":
        for key, value in settings.items():
            if isinstance(value[1], tuple):
                new_first_item = value[1][0]
                value[0] = new_first_item
    else:
        return f"{request_value} is not a valid option."


def convert_unit(unit=None, amount=None):
    if unit == "temperature_unit":
        pass

    elif unit == "distance_unit":
        if settings["distance_unit"][0] == "kilometers":
            return amount / 1000
        elif settings["distance_unit"][0] == "miles":
            return amount / 1000 * 0.621371192

    elif unit == "duration":
        hours = amount // 3600
        minutes = (amount % 3600) // 60
        return f"{int(hours)}:{int(minutes)}"


def get_city_coordinaten(city_name=None):
    params = {
        'api_key': api_key_transport,
        'text': city_name
    }
    response = requests.get(geocode_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['features'][0]['properties']['continent'].lower() == "europe":
            return data['features'][0]['geometry']['coordinates']
        else:
            return f"Error: City ({city_name}) not in Europe."
    else:
        return f"Error fetching coordinates for {city_name}: {response.status_code}"


def get_directions(start_city=None, end_city=None):
    start_coords = get_city_coordinaten(start_city)
    end_coords = get_city_coordinaten(end_city)
    if start_coords and end_coords:
        payload = {
            'coordinates': [start_coords, end_coords]
        }
        response = requests.post(directions_url, headers={
            'Authorization': api_key_transport,
            'Content-Type': 'application/json'
        }, json=payload)

        if response.status_code == 200:
            route = response.json()
            distance_m = route['routes'][0]['summary']['distance']
            duration_s = route['routes'][0]['summary']['duration']

            total_distance = convert_unit("distance_unit", distance_m)
            total_price = total_distance / settings["fuel_consumption"][0] * settings["fuel_cost"][0]
            total_time = convert_unit("duration", duration_s)

            # Set the departure time to now
            departure_time = datetime.now()
            # Calculate the actual arrival time
            arrival_time = departure_time + timedelta(seconds=duration_s)

            formatted_start_time = departure_time.strftime("%H:%M")
            formatted_end_time = arrival_time.strftime("%H:%M")

            # Fetch weather for the end city
            weather = get_weather(city=end_city)
            # Calculate the time until sunrise or sunset based on arrival time
            time_until_sun_up_or_down = timestamp_converter(sunrise_time=weather["sunrise"],
                                                            sunset_time=weather["sunset"],
                                                            arrival_time=arrival_time)

            return {
                "total_distance": total_distance,
                "fuel_price": total_price,
                "duration_time": total_time,
                "departure_time": formatted_start_time,
                "arrival_time": formatted_end_time,
                "temp_end_city": weather["temp"],
                "weather_desc_end_city": weather["weather_desc"],
                "time_until_sun_up_or_down": time_until_sun_up_or_down
            }
        else:
            return f"Error fetching directions: {response.status_code} - {response.text}"
    else:
        return "Could not retrieve coordinates for one or both cities."


def get_weather(city=None):
    params = {
        "q": city,
        "appid": api_key_weather,
        "lang": "nl",
        "units": "metric",
    }

    response = requests.get(weather_url, params=params)

    if response.status_code == 200:
        data = response.json()

        return {
            "temp": data['main']['temp'],
            "weather_desc": data['weather'][0]['description'],
            "sunrise": data['sys']['sunrise'],
            "sunset": data['sys']['sunset']
        }
    else:
        return f"Error: {response.status_code}"


def timestamp_converter(sunrise_time=None, sunset_time=None, arrival_time=None):
    # Convert Unix timestamps to datetime objects
    sunrise_datetime = datetime.fromtimestamp(sunrise_time)
    sunset_datetime = datetime.fromtimestamp(sunset_time)

    if arrival_time < sunrise_datetime:
        time_difference = sunrise_datetime - arrival_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunrise"}, f"{hours} hours and {minutes} minutes until sunrise"]

    elif arrival_time < sunset_datetime:
        time_difference = sunset_datetime - arrival_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunset"}, f"{hours} hours and {minutes} minutes until sunset"]

    else:
        next_day_sunrise = sunrise_datetime + timedelta(days=1)
        time_difference = next_day_sunrise - arrival_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunrise"}, f"{hours} hours and {minutes} minutes until next sunrise"]


if __name__ == "__main__":
    pp.pprint(get_directions(start_city="Amsterdam", end_city="Berlijn"))
