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
    """
    Behandelt wijzigingen in de instellingen voor temperatuur, afstand, brandstofkosten en verbruik.
    Ook mogelijk om standaardwaarden te herstellen.

    Parameters:
    request_value (str): De instelling die aangepast moet worden.
    request_item (str/float/int): De nieuwe waarde voor de instelling.

    Returns:
    str: Foutmelding als de invoer onjuist is, anders None.
    """
    if request_value in settings:
        try:
            if request_value == "temperature_unit" or request_value == "distance_unit":
                if request_item.lower() in settings[request_value][1]:
                    settings[request_value][0] = request_item.lower()
                else:
                    return f"\033[91m'{request_item}' is geen geldige optie voor '{request_value}'.\033[0m"
            elif request_value == "fuel_cost":
                try:
                    settings[request_value][0] = float(request_item)
                except ValueError:
                    return f"\033[91m'{request_item}' kan niet worden omgezet naar een getal.\033[0m"
            elif request_value == "fuel_consumption":
                try:
                    consumption_value = float(request_item)
                    if consumption_value <= 100:
                        settings[request_value][0] = consumption_value
                    else:
                        return f"\033[91m'{request_item}' is hoger dan 100. Dit lijkt onrealistisch.\033[0m"
                except ValueError:
                    return f"\033[91m'{request_item}' kan niet worden omgezet naar een getal.\033[0m"
        except ValueError:
            return f"\033[91mOngeldige invoer. Probeer het opnieuw.\033[0m"
    elif request_value == "restore_defaults":
        for key, value in settings.items():
            if isinstance(value[1], tuple):
                settings[key][0] = value[1][0]
    else:
        return f"\033[91m'{request_value}' is geen geldige optie.\033[0m"

def convert_unit(unit=None, amount=None):
    """
    Converteert afstanden of tijden naar de juiste eenheden (kilometers/mijlen en uren/minuten).

    Parameters:
    unit (str): Type eenheid (bv. 'distance_unit' of 'duration').
    amount (float/int): De te converteren waarde (bijv. afstand in meters of duur in seconden).

    Returns:
    float/str: De geconverteerde afstand of tijd. Geeft None terug als de duur te lang is.
    """
    try:
        if unit == "distance_unit":
            if settings["distance_unit"][0] == "kilometers":
                return amount / 1000
            elif settings["distance_unit"][0] == "miles":
                return amount / 1000 * 0.621371192
            else:
                raise ValueError(f"\033[91mOngeldige afstandseenheid in instellingen.\033[0m")
        elif unit == "duration":
            hours = amount // 3600
            minutes = (amount % 3600) // 60
            if hours >= 8:
                return None, f"\033[91mDe reistijd is langer dan 8 uur. De reis wordt afgebroken.\033[0m"
            else:
                return f"{int(hours)} uur en {int(minutes)} minuten", None
        else:
            raise ValueError(f"\033[91mOngeldige eenheid opgegeven.\033[0m")

    except TypeError as e:
        return None, f"\033[91mFout: onjuiste datatype - {e}\033[0m"
    except ValueError as e:
        return None, f"\033[91mFout: {e}"
    except Exception as e:
        return None, f"\033[91mEen onverwachte fout is opgetreden: {e}\033[0m"

def get_city_coordinates (city_name=None):
    """
    Haalt de geografische coördinaten van een opgegeven stad op via een API.

    Parameters:
    city_name (str): De naam van de stad waarvan de coördinaten worden opgehaald.

    Returns:
    list/None: Lijst met lengte- en breedtegraad van de stad, of None als de stad niet wordt gevonden.
    """
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
        print(f"\033[91mFout bij het ophalen van coördinaten voor {city_name}: {response.status_code}\033[0m")
        return None

def get_directions(start_city=None, end_city=None):
    """
    Haalt routegegevens op tussen twee steden, inclusief afstand, reistijd en brandstofkosten.

    Parameters:
    start_city (str): De naam van de vertrekstad.
    end_city (str): De naam van de aankomststad.

    Returns:
    dict/str: Woordenboek met route-informatie of foutmelding bij mislukking.
    """
    start_coords = get_city_coordinates(start_city)
    end_coords = get_city_coordinates(end_city)

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
            return f"Fout bij het ophalen van de route: {response.status_code} - {response.text}"
    else:
        return "Kon de coördinaten van een of beide steden niet ophalen."

def get_weather(city=None):
    """
    Haalt de huidige weersinformatie van een opgegeven stad op via een API.

    Parameters:
    city (str): De naam van de stad.

    Returns:
    dict/str: Woordenboek met temperatuur, weeromschrijving, zonsopkomst en zonsondergangstijden of foutmelding.
    """
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
        return f"\033[91mFout: {response.status_code}\033[0m"

def timestamp_converter(sunrise_time=None, sunset_time=None, arrival_time=None):
    """
    Berekent de tijd tot zonsopkomst of zonsondergang gebaseerd op de aankomsttijd.

    Parameters:
    sunrise_time (int): Tijdstempel voor zonsopkomst.
    sunset_time (int): Tijdstempel voor zonsondergang.
    arrival_time (datetime): Verwachte aankomsttijd.

    Returns:
    list: Informatie over het volgende zonne-event en de tijd tot dat moment.
    """
    try:
        # Converteer tijdstempels naar datetime-objecten
        sunrise_datetime = datetime.fromtimestamp(sunrise_time)
        sunset_datetime = datetime.fromtimestamp(sunset_time)

        if arrival_time < sunrise_datetime:
            time_difference = sunrise_datetime - arrival_time
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes = remainder // 60
            return [{"next_event": "zonsopkomst"}, f"{hours} uur en {minutes} minuten tot zonsopkomst"]

        elif arrival_time < sunset_datetime:
            time_difference = sunset_datetime - arrival_time
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes = remainder // 60
            return [{"next_event": "zonsondergang"}, f"{hours} uur en {minutes} minuten tot zonsondergang"]

        else:
            next_day_sunrise = sunrise_datetime + timedelta(days=1)
            time_difference = next_day_sunrise - arrival_time
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes = remainder // 60
            return [{"next_event": "zonsopkomst"}, f"{hours} uur en {minutes} minuten tot de volgende zonsopkomst"]

    except TypeError as e:
        return [None, f"\033[91mFout: onjuiste datatype - {e}\033[0m"]
    except ValueError as e:
        return [None, f"\033[91mFout: {e}\033[0m"]
    except Exception as e:
        return [None, f"\033[91mEen onverwachte fout is opgetreden: {e}\033[0m"]

def parse_duration_and_calculate_arrival(duration=None):
    """
    Parseert de duur van de reis en berekent de verwachte aankomsttijd.

    Parameters:
    duration (str): De duur van de reis in uren en minuten.

    Returns:
    tuple: De verwachte aankomsttijd en context (vandaag/morgen/etc.), of een foutmelding.
    """
    print(f"Teruggegeven duur: {duration}")

    match = re.search(r'(?:(\d+)\s*uur)?\s*(?:(\d+)\s*minuten)?', duration)

    if match:
        duration_hours = int(match.group(1)) if match.group(1) else 0
        duration_minutes = int(match.group(2)) if match.group(2) else 0
    else:
        return None, f"\033[91mFout: kan de duur niet verwerken.\033[0m"

    total_duration_hours = duration_hours + duration_minutes / 60

    arrival_time, arrival_context = calculate_arrival_time(total_duration_hours)

    return arrival_time, arrival_context

def calculate_arrival_time(total_duration_hours=None):
    """
    Berekent de aankomsttijd op basis van de verstreken reistijd.

    Parameters:
    total_duration_hours (float): De totale reistijd in uren.

    Returns:
    tuple: Aankomsttijd (datetime) en context (vandaag/morgen/overmorgen/etc.).
    """
    try:
        if total_duration_hours is None:
            raise ValueError(f"\033[91mDe totale reistijd mag niet None zijn.\033[0m")

        total_duration_hours = float(total_duration_hours)

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

    except ValueError as e:
        print(f"\033[91mFout: {e}\033[0m")
    except TypeError as e:
        print(f"\033[91mFout: onjuiste datatype - {e}\033[0m")
    except Exception as e:
        print(f"\033[91mEen onverwachte fout is opgetreden: {e}\033[0m")

