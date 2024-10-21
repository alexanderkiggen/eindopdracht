import sys
import json
from processen import settings, get_city_coordinaten, get_directions

filename = 'app_database.json'

class Validator:

    def validate_title(self):
        """
        Validates the title of the trip.
        Ensures it's between 3 and 60 characters long and alphanumeric.
        """
        while True:
            try:
                title = input("Voer de titel van de reis in (minimaal 3 en maximaal 60 tekens, alfanumeriek): ").strip()

                if len(title) < 3:
                    print(f"Fout: Titel moet minimaal 3 tekens bevatten. Probeer het opnieuw. ({len(title)})")
                    continue

                if len(title) > 60:
                    print(f"Fout: Titel mag maximaal 60 tekens bevatten. Probeer het opnieuw. ({len(title)})")
                    continue

                if not any(char.isalpha() for char in title):
                    print("Fout: Titel moet ten minste één letter bevatten. Probeer het opnieuw.")
                    continue

                return title

            except Exception as e:
                print(f"Er is een fout opgetreden: {e}. Probeer het opnieuw.")

    def validate_temperature_unit(self):
        """
        Validates the temperature unit (metric/imperial/units).
        """
        while True:
            try:
                request_value = input("Enter new temperature unit (metric/imperial/units): ").lower()

                if request_value not in settings["temperature_unit"][1]:
                    print(f"Fout: Ongeldige temperatuur-eenheid '{request_value}'. Probeer het opnieuw.")
                    continue

                return request_value

            except KeyError:
                print(f"Fout: Ongeldige temperatuur-eenheid '{request_value}'. Probeer het opnieuw.")
            except Exception as e:
                print(f"Er is een fout opgetreden: {e}. Probeer het opnieuw.")

    def validate_distance_unit(self):
        """
        Validates the distance unit (kilometers/miles).
        """
        while True:
            try:
                request_value = input("Enter new distance unit (kilometers/miles): ").lower()

                if request_value not in settings["distance_unit"][1]:
                    print(f"Fout: Ongeldige afstandseenheid '{request_value}'. Probeer het opnieuw.")
                    continue

                return request_value

            except KeyError:
                print(f"Fout: Ongeldige afstandseenheid '{request_value}'. Probeer het opnieuw.")
            except Exception as e:
                print(f"Er is een fout opgetreden: {e}. Probeer het opnieuw.")

    def validate_fuel_cost(self):
        """
        Validates the fuel cost input, ensuring it's a positive number.
        """
        while True:
            try:
                message = input("Voer een brandstofprijs in per liter: ").strip()

                fuel_cost = float(message)

                if fuel_cost <= 0:
                    print(f"Fout: Ongeldige waarde, getal moet groter zijn dan 0. Probeer het opnieuw.")
                    continue

                return fuel_cost

            except ValueError:
                print(f"Fout: Ongeldige waarde, geen geldig getal '{message}'. Probeer het opnieuw.")
            except Exception as e:
                print(f"Er is een fout opgetreden: {e}. Probeer het opnieuw.")

    def validate_fuel_consumption(self):
        """
        Validates fuel consumption (liters per 100km), ensuring it's between 0 and 100.
        """
        while True:
            try:
                message = input("Enter new fuel consumption (liters per 100km): ").strip()

                fuel_consumption = float(message)

                if fuel_consumption <= 0:
                    print(f"Fout: Ongeldige waarde, brandstofverbruik moet groter zijn dan 0. Probeer het opnieuw.")
                    continue

                if fuel_consumption > 100:
                    print(f"Fout: Ongeldige waarde, brandstofverbruik moet kleiner zijn dan 100 L/100km. Probeer het opnieuw.")
                    continue

                return fuel_consumption

            except ValueError:
                print(f"Fout: Ongeldige waarde, geen geldig getal '{message}'. Probeer het opnieuw.")
            except Exception as e:
                print(f"Er is een fout opgetreden: {e}. Probeer het opnieuw.")

    def validate_city(self, city_type):
        """
        Validates whether the entered city is a valid city in Europe.
        The city_type argument determines whether it's for the start or end city.
        """
        while True:
            city = input(f"Selecteer een {city_type} stad: ").lower()
            city_status = get_city_coordinaten(city)

            if city_status is None:
                print(f"Error: '{city}' is not a valid {city_type} city in Europe. Please try again.", file=sys.stderr)
                continue

            return city

def load_data():
    """
    Load data from the JSON file.
    If the file does not exist, return an empty 'trips' list.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'trips': []}

def save_data(data):
    """
    Save the provided data to the JSON file.
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def print_trips():
    """
    Generate a formatted string of all trips.
    Returns a message if no trips are available or if data is invalid.
    """
    data = load_data()
    if not data.get('trips'):
        return "No trips available."

    message = ""
    for index, trip in enumerate(data['trips']):
        message += f"""
        Reis {index + 1}: {trip['Title']}
          |  Vertrekpunt: {trip['start_city']} -> Bestemming: {trip['end_city']}
          |  Eenheden: Afstand: {trip['distance_unit']} | Temperatuur: {trip['temperature_unit']}
          |  Brandstofkosten per liter: €{trip['fuel_cost']} | Verbruik: {trip['fuel_consumption']} liter per 100 kilometer
        """
    return message

def remove_trip_by_index():
    """
    Remove a trip by its index (input by user).
    Returns a success or error message based on the input and data status.
    """
    data = load_data()
    trips = data.get('trips', [])
    if not trips:
        return "No trips available to remove."

    try:
        index = int(input("Enter the trip number to remove: ")) - 1
    except ValueError:
        return "Invalid input. Please enter a number."

    if 0 <= index < len(trips):
        removed_trip = trips.pop(index)  # Remove the trip
        save_data(data)  # Save the updated data
        return f"Removed: {removed_trip['Title']} (ID: {removed_trip['ID']})"
    else:
        return "Invalid index. No trip removed."

def add_trip():
    """
    Add a new trip with predefined details and validate that the end city is within 8 hours of the start city.
    If not, prompt the user to enter a new end city or return to the main menu.
    """
    validator = Validator()
    data = load_data()

    if data['trips']:
        last_trip_id = int(data['trips'][-1]['ID'])
        new_id = last_trip_id + 1
    else:
        new_id = 1

    start_city = validator.validate_city("begin")

    while True:
        end_city = validator.validate_city("eind")

        directions_info = get_directions(start_city=start_city, end_city=end_city)

        if not directions_info:
            return

        if directions_info["duration_time"] is None:
            print("Dit kan niet worden op geslagen, want deze rit is langer dan 8uur. Dit menu wordt afgesloten.")

        else:
            new_trip = {
                "Title": validator.validate_title(),
                "ID": int(new_id),
                "start_city": start_city,
                "end_city": end_city,
                "temperature_unit": validator.validate_temperature_unit(),
                "distance_unit": validator.validate_distance_unit(),
                "fuel_cost": validator.validate_fuel_cost(),
                "fuel_consumption": validator.validate_fuel_consumption(),
            }

            data['trips'].append(new_trip)
            save_data(data)
            return f"Nieuwe reis '{new_trip['Title']}' is toegevoegd. Totale reistijd: {new_trip['travel_time']}."
