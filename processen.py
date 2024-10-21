import re
import requests
from datetime import datetime, timedelta

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

        if hours >= 8:
            return None, "De reistijd is langer dan 8 uur. Het programma wordt afgebroken."
        else:
            return f"{int(hours)} uur en {int(minutes)} minuten", None

def get_city_coordinaten(city_name=None):
    params = {
        'api_key': api_key_transport,
        'text': city_name
    }

    response = requests.get(geocode_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['features']:
            if data['features'][0]['properties']['continent'].lower() == "europe":
                return data['features'][0]['geometry']['coordinates']
            else:
                return None
        else:
            return None
    else:
        print(f"Error fetching coordinates for {city_name}: {response.status_code}")
        return None

def get_directions(start_city=None, end_city=None):
    start_coords = get_city_coordinaten(start_city)
    end_coords = get_city_coordinaten(end_city)

    if start_city and end_coords:
        payload = {
            'coordinates': [start_coords, end_coords],
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
            total_time, error_message = convert_unit("duration", duration_s)

            if total_time is None:
                print(error_message)
                return None

            total_price = total_distance / settings["fuel_consumption"][0] * settings["fuel_cost"][0]

            departure_time = datetime.now()
            arrival_time = departure_time + timedelta(seconds=duration_s)

            formatted_start_time = departure_time.strftime("%H:%M")
            formatted_end_time = arrival_time.strftime("%H:%M")

            weather = get_weather(city=end_city)
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
        "units": settings["temperature_unit"][0]
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
    sunrise_datetime = datetime.fromtimestamp(sunrise_time)
    sunset_datetime = datetime.fromtimestamp(sunset_time)

    if arrival_time < sunrise_datetime:
        time_difference = sunrise_datetime - arrival_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunrise"}, f"{hours} uur en {minutes} minuten tot zonsopkomst"]

    elif arrival_time < sunset_datetime:
        time_difference = sunset_datetime - arrival_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunset"}, f"{hours} uur en {minutes} minuten tot zonsondergang"]

    else:
        next_day_sunrise = sunrise_datetime + timedelta(days=1)
        time_difference = next_day_sunrise - arrival_time
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunrise"}, f"{hours} uur en {minutes} minuten tot de volgende zonsopkomst"]

def parse_duration_and_calculate_arrival(duration):
    print(f"Duration returned: {duration}")

    match = re.search(r'(?:(\d+)\s*uur)?\s*(?:(\d+)\s*minuten)?', duration)

    if match:
        duration_hours = int(match.group(1)) if match.group(1) else 0
        duration_minutes = int(match.group(2)) if match.group(2) else 0
    else:
        return None, "Error: Unable to parse duration"

    total_duration_hours = duration_hours + duration_minutes / 60

    arrival_time, arrival_context = calculate_arrival_time(total_duration_hours)

    return arrival_time, arrival_context

def calculate_arrival_time(total_duration_hours):
    current_time = datetime.now()
    arrival_time = current_time + timedelta(hours=total_duration_hours)

    if arrival_time.date() == current_time.date():
        arrival_context = "vandaag"
    elif arrival_time.date() == (current_time + timedelta(days=1)).date():
        arrival_context = "morgen"
    elif arrival_time.date() == (current_time + timedelta(days=2)).date():
        arrival_context = "overmorgen"
    else:
        arrival_context = "later"

    return arrival_time, arrival_context

def printer(
        start_city, end_city, distance, distance_unit, duration,
        arrival_context, arrival_time, sunset_info, temp_end_city,
        temperature_unit, weather_desc_end_city, fuel_price
):
    message = f"""
    De route van {start_city.capitalize()} naar {end_city.capitalize()} bedraagt 
    {distance:.1f} {distance_unit} en zal ongeveer {duration} duren in een auto. 
    Als je nu begint met rijden, ben je er {arrival_context} om {arrival_time.strftime("%H:%M")} (zonder tussentijdse pauzes). 
    Dan heb je nog {sunset_info}. 
    De temperatuur in {end_city.capitalize()} is momenteel {temp_end_city:.2f}{temperature_unit} en het weer is {weather_desc_end_city}. 
    De geschatte brandstofprijs voor de rit bedraagt €{fuel_price:.2f}.
    Veel succes en een veilige reis!
    """

    print(message)