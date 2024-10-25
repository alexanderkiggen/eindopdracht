import sys
import json
from processen import settings, get_city_coordinates, get_directions, settings_menu

filename = 'app_database.json'

class Validator:
    def validate_title(self):
        """
        Valideert de titel van de reis.
        Zorgt ervoor dat deze tussen de 3 en 60 tekens lang is en alfanumeriek.
        Geeft een foutmelding als de titel niet voldoet aan de vereisten en vraagt om nieuwe invoer.
        """
        while True:
            try:
                title = input("Geef een titel voor de reis (minimaal 3 en maximaal 60 tekens, alleen letters en cijfers): ").strip()

                if len(title) < 3:
                    print(f"\033[91mFout: De titel moet minstens 3 tekens bevatten. Je hebt nu {len(title)} tekens ingevoerd.\033[0m")
                    continue

                if len(title) > 60:
                    print(f"\033[91mFout: De titel mag niet meer dan 60 tekens bevatten. Je hebt nu {len(title)} tekens ingevoerd.\033[0m")
                    continue

                if not any(char.isalpha() for char in title):
                    print(f"\033[91mFout: De titel moet minimaal één letter bevatten. Probeer het opnieuw.\033[0m")
                    continue

                return title

            except Exception as e:
                print(f"\033[91mEr is een fout opgetreden: {e}. Probeer het opnieuw.\033[0m")

    def validate_temperature_unit(self):
        """
        Valideert de temperatuur-eenheid (metric/imperial/units).
        Geeft een foutmelding bij een ongeldige invoer en vraagt om nieuwe invoer.
        """
        while True:
            request_value = None
            try:
                request_value = input("Kies een temperatuur-eenheid (metric/imperial/units): ").lower()

                if request_value not in settings["temperature_unit"][1]:
                    print(f"\033[91mFout: Ongeldige temperatuur-eenheid '{request_value}'. Voer een geldige optie in (metric/imperial/units).\033[0m")
                    continue

                return request_value

            except KeyError:
                print(f"\033[91mFout: Ongeldige temperatuur-eenheid '{request_value}'. Probeer het opnieuw.\033[0m")
            except Exception as e:
                print(f"\033[91mEr is een fout opgetreden: {e}. Probeer het opnieuw.\033[0m")

    def validate_distance_unit(self):
        """
        Valideert de afstandseenheid (kilometers/miles).
        Geeft een foutmelding bij ongeldige invoer en vraagt om nieuwe invoer.
        """
        while True:
            request_value = None
            try:
                request_value = input("Kies een afstandseenheid (kilometers/miles): ").lower()

                if request_value not in settings["distance_unit"][1]:
                    print(f"\033[91mFout: Ongeldige afstandseenheid '{request_value}'. Voer een geldige optie in (kilometers/miles).\033[0m")
                    continue

                return request_value

            except KeyError:
                print(f"\033[91mFout: Ongeldige afstandseenheid '{request_value}'. Probeer het opnieuw.\033[0m")
            except Exception as e:
                print(f"\033[91mEr is een fout opgetreden: {e}. Probeer het opnieuw.\033[0m")

    def validate_fuel_cost(self):
        """
        Valideert de ingevoerde brandstofprijs, waarbij het een positief getal moet zijn.
        Geeft een foutmelding bij ongeldige invoer en vraagt om nieuwe invoer.
        """
        while True:
            request_value = None
            try:
                request_value = input("Voer de brandstofprijs in per liter (bijvoorbeeld 1.82): ").strip()

                fuel_cost = float(request_value)

                if fuel_cost <= 0:
                    print(f"\033[91mFout: De prijs moet een positief getal zijn. Voer een waarde groter dan 0 in.\033[0m")
                    continue

                return fuel_cost

            except ValueError:
                print(f"\033[91mFout: Ongeldige invoer, '{request_value}' is geen geldig getal. Probeer het opnieuw.\033[0m")
            except Exception as e:
                print(f"\033[91mEr is een fout opgetreden: {e}. Probeer het opnieuw.\033[0m")

    def validate_fuel_consumption(self):
        """
        Valideert het brandstofverbruik (liters per 100km), moet tussen 0 en 100 liggen.
        Geeft een foutmelding bij ongeldige invoer en vraagt om nieuwe invoer.
        """
        while True:
            request_value = None
            try:
                request_value = input("Voer het brandstofverbruik in (liters per 100km, bijvoorbeeld 7.0): ").strip()

                fuel_consumption = float(request_value)

                if fuel_consumption <= 0:
                    print(f"\033[91mFout: Het brandstofverbruik moet een positief getal zijn. Voer een waarde groter dan 0 in.\033[0m")
                    continue

                if fuel_consumption > 100:
                    print(f"\033[91mFout: Ongeldige waarde, het brandstofverbruik moet minder dan 100 liter per 100 km zijn.\033[0m")
                    continue

                return fuel_consumption

            except ValueError:
                print(f"\033[91mFout: Ongeldige invoer, '{request_value}' is geen geldig getal. Probeer het opnieuw.\033[0m")
            except Exception as e:
                print(f"\033[91mEr is een fout opgetreden: {e}. Probeer het opnieuw.\033[0m")

    def validate_city(self, city_type=None):
        """
        Valideert of de ingevoerde stad een geldige Europese stad is.
        Het argument `city_type` geeft aan of het om de begin- of eindstad gaat.
        Geeft een foutmelding bij ongeldige invoer en vraagt om nieuwe invoer.
        """
        while True:
            city = input(f"Voer een {city_type}stad in: ").lower()
            city_status = get_city_coordinates(city)

            if city_status is None:
                print(f"\033[91mFout: '{city}' is geen geldige {city_type} stad in Europa. Probeer het opnieuw.\033[0m")
                continue

            return city

def load_data():
    """
    Laadt gegevens uit het JSON-bestand.
    Als het bestand niet bestaat, wordt een lege lijst met 'trips' teruggegeven.
    """
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'trips': []}

def save_data(data=None):
    """
    Slaat de opgegeven gegevens op in het JSON-bestand.
    """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def print_trips():
    """
    Genereert een geformatteerde string van alle opgeslagen reizen.
    Geeft een melding als er geen reizen beschikbaar zijn of als de data onjuist is.
    """
    data = load_data()
    if not data.get('trips'):
        return f"\033[91mEr zijn geen reizen beschikbaar.\033[0m"

    message = ""
    for index, trip in enumerate(data['trips']):
        message += f"""
        ReisID: {index + 1}, {trip['Title']}
          |  Vertrekpunt: {trip['start_city']} -> Bestemming: {trip['end_city']}
          |  Eenheden: Afstand: {trip['distance_unit']} | Temperatuur: {trip['temperature_unit']}
          |  Brandstofkosten per liter: €{trip['fuel_cost']} | Verbruik: {trip['fuel_consumption']} liter per 100 kilometer
        """
    return message

def remove_trip_by_index():
    """
    Verwijdert een reis op basis van het door de gebruiker ingevoerde indexnummer.
    Geeft een succes- of foutmelding op basis van de invoer en de status van de data.
    """
    data = load_data()
    trips = data.get('trips', [])
    if not trips:
        return f"\033[91mEr zijn geen reizen beschikbaar om te verwijderen.\033[0m"

    try:
        index = int(input("Voer het reisnummer in dat je wilt verwijderen: ")) - 1
    except ValueError:
        return f"\033[91mOngeldige invoer. Voer een nummer in.\033[0m"

    if 0 <= index < len(trips):
        removed_trip = trips.pop(index)
        save_data(data)
        return f"\033[91mVerwijderd: {removed_trip['Title']} (ID: {removed_trip['ID']})\033[0m"
    else:
        return f"\033[91mOngeldig nummer. Geen reis verwijderd.\033[0m"

def select_trip_by_index():
    """
    Selecteert een reis op basis van het door de gebruiker ingevoerde indexnummer en haalt de route op.
    """
    data = load_data()
    trips = data.get('trips', [])

    if not trips:
        print(f"\033[91mEr zijn geen reizen beschikbaar om te selecteren.\033[0m")
        return

    while True:
        try:
            index = int(input("Voer het reisnummer in dat je wilt selecteren: ")) - 1

            if 0 <= index < len(trips):
                selected_trip = trips[index]
                return selected_trip
            else:
                print(f"\033[91mOngeldige invoer. Kies een nummer tussen 1 en {len(trips)}.\033[0m")

        except ValueError:
            print(f"\033[91mOngeldige invoer. Voer een geldig nummer (ID) in.\033[0m")


def change_settings_by_index(data=None):
    """
    Past de instellingen aan op basis van de doorgegeven gegevens (zoals eenheden, brandstofkosten en verbruik).
    """
    try:
        distance_unit = data.get('distance_unit')
        temperature_unit = data.get('temperature_unit')
        fuel_cost = data.get('fuel_cost')
        fuel_consumption = data.get('fuel_consumption')

        settings_menu(request_value="distance_unit", request_item=distance_unit)
        settings_menu(request_value="temperature_unit", request_item=temperature_unit)
        settings_menu(request_value="fuel_cost", request_item=fuel_cost)
        settings_menu(request_value="fuel_consumption", request_item=fuel_consumption)

    except AttributeError as e:
        print(f"\033[91mFout: een probleem met de gegevens - {e}\033[0m")
    except TypeError as e:
        print(f"\033[91mFout: onjuiste datatype - {e}")
    except Exception as e:
        print(f"\033[91mEen onverwachte fout is opgetreden: {e}\033[0m")

def add_trip():
    """
    Voegt een nieuwe reis toe met vooraf gedefinieerde gegevens en valideert dat de eindstad binnen 8 uur van de beginstad ligt.
    Als de reistijd langer is dan 8 uur, wordt de gebruiker gevraagd om een nieuwe eindstad in te voeren of terug te keren naar het hoofdmenu.
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
            return f"\033[91mDe reistijd is langer dan 8 uur. De reis kan niet worden opgeslagen.\033[0m"

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
                "travel_time": directions_info["duration_time"]
            }

            data['trips'].append(new_trip)
            save_data(data)

            return f"\033[92mNieuwe reis '{new_trip['Title']}' is toegevoegd.\033[0m"

