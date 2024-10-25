import sys
import json_processen
import re
import processen
from json_processen import print_trips, add_trip, remove_trip_by_index, select_trip_by_index, change_settings_by_index

header = "===== De ultieme reis app ====="

def main():
    """
    Het hoofdmenu van de reisapp. Gebruikers kunnen kiezen om een nieuwe reis te plannen,
    vooraf ingestelde bestemmingen te gebruiken, instellingen te wijzigen, hulp te raadplegen
    of het programma te beëindigen.
    """
    while True:
        layout = f"""
        {header}
               --- Home Page ---

        1. New       // Start met het plannen van je volgende reis
        2. PreSets   // Laad of maak een bestemming pre-set van een bestand.
        3. Settings  // Wijzig instellingen voor de huidige sessie.
        4. Help      // Een gids.
        5. Quit      // Stop het programma.
        """
        print(layout)

        choice = input("Maak een keuze (1-5): ").lower()

        if choice == '1' or choice == 'new':
            new()
        elif choice == '2' or choice == 'presets':
            pre_set()
        elif choice == '3' or choice == 'settings':
            settings()
        elif choice == '4' or choice == 'help':
            help_program()
        elif choice == '5' or choice == 'quit':
            quit_program()
        else:
            print(f"\033[91mOngeldige keuze. Selecteer een geldig nummer uit het menu.\033[0m")

def new(pre_set_start_city=None, pre_set_end_city=None):
    """
    Plan een nieuwe reis door een beginstad en eindstad te selecteren.
    Indien presets aanwezig zijn, kunnen deze ook gebruikt worden om
    steden vooraf in te vullen.

    Parameters:
    pre_set_start_city (str): Vooraf ingestelde beginstad (optioneel).
    pre_set_end_city (str): Vooraf ingestelde eindstad (optioneel).
    """
    if pre_set_start_city is None or pre_set_end_city is None:
        start_city = input("Selecteer een beginstad: ").lower()
        start_coords = processen.get_city_coordinates(start_city)

        while start_coords is None or (isinstance(start_coords, str) and re.search(r'\d', start_coords)):
            print(f"\033[91mFout: '{start_city}' is geen geldige stad in Europa. Probeer het opnieuw.\033[0m")
            start_city = input("Selecteer een geldige beginstad: ").lower()
            start_coords = processen.get_city_coordinates(start_city)

        end_city = input("Selecteer een eindstad: ").lower()
        end_coords = processen.get_city_coordinates(end_city)

        while end_coords is None or (isinstance(end_coords, str) and re.search(r'\d', end_coords)):
            print(f"\033[91mFout: '{end_city}' is geen geldige stad in Europa. Probeer het opnieuw.\033[0m")
            end_city = input("Selecteer een geldige eindstad: ").lower()
            end_coords = processen.get_city_coordinates(end_city)

        directions = processen.get_directions(start_city=start_city, end_city=end_city)

    else:
        start_city = str(pre_set_start_city).lower()
        end_city = str(pre_set_end_city).lower()
        directions = processen.get_directions(start_city=start_city, end_city=end_city)

    while True:
        if directions is None:
            break

        distance = directions['total_distance']
        duration = directions['duration_time']
        fuel_price = directions['fuel_price']
        sunset_info = directions['time_until_sun_up_or_down'][1]
        temp_end_city = directions['temp_end_city']
        weather_desc_end_city = directions['weather_desc_end_city']

        distance_unit = "kilometers" if processen.settings["distance_unit"][0] == "kilometers" else "mijl"
        temperature_unit = (
            "°C" if processen.settings["temperature_unit"][0] == "metric"
            else "°F" if processen.settings["temperature_unit"][0] == "imperial"
            else "K"
        )

        arrival_time, arrival_context = processen.parse_duration_and_calculate_arrival(duration)

        if arrival_time is None:
            continue

        printer(
            start_city, end_city, distance, distance_unit, duration,
            arrival_context, arrival_time, sunset_info, temp_end_city,
            temperature_unit, weather_desc_end_city, fuel_price
        )

        while True:
            continue_question = input("Wilt u terug naar het vorige menu (y): ").lower()
            if continue_question == "y":
                main()
            else:
                print(f"\033[91mOngeldige waarde, probeer het opnieuw\033[0m")

def settings():
    """
    Beheer de instellingen van de reisapp, inclusief temperatuur eenheden, afstand eenheden,
    brandstofprijs en brandstofverbruik. Gebruikers kunnen ook alle instellingen bekijken of
    herstellen naar de standaardinstellingen.
    """
    while True:
        layout = f"""
        {header}
            --- Instellingen Pagina ---

        1. Temp      // Verander standaardtemperatuureenheid
        2. Dist      // Verander standaardeenheid voor afstand
        3. Fuel      // Verander standaard brandstofprijs per liter
        4. Cons      // Verander standaard brandstofverbruik
        --------------------------------------------------------
        5. Show      // Toon alle huidige instellingen
        6. Restore   // Herstel standaardinstellingen
        7. Back      // Terug naar het hoofdmenu.
        """

        while True:
            print(layout)
            choice = input("Maak een keuze (1-7): ").lower()

            if choice == '1' or choice == 'temp':
                new_temp = input("Voer nieuwe temperatuur eenheid in (metric/imperial/units): ").lower()
                result = processen.settings_menu("temperature_unit", new_temp)
                print(result if result else "Temperatuureenheid succesvol bijgewerkt.")

            elif choice == '2' or choice == 'dist':
                new_dist = input("Voer nieuwe afstandseenheid in (kilometers/miles): ").lower()
                result = processen.settings_menu("distance_unit", new_dist)
                print(result if result else "Afstandseenheid succesvol bijgewerkt.")
            elif choice == '3' or choice == 'fuel':
                new_fuel_cost = input("Voer nieuwe brandstofprijs per liter in: ")
                result = processen.settings_menu("fuel_cost", new_fuel_cost)
                print(result if result else "Brandstofprijs succesvol bijgewerkt.")
            elif choice == '4' or choice == 'cons':
                new_fuel_cons = input("Voer nieuw brandstofverbruik in (liters per 100km): ")
                result = processen.settings_menu("fuel_consumption", new_fuel_cons)
                print(result if result else "Brandstofverbruik succesvol bijgewerkt.")
            elif choice == '5' or choice == 'show':
                print("\nHuidige instellingen:")
                for key, value in processen.settings.items():
                    print(f"{key.replace('_', ' ').capitalize()}: {value[0]}")
            elif choice == '6' or choice == 'restore':
                processen.settings_menu("restore_defaults")
                print("Alle instellingen zijn hersteld naar de standaardwaarden.")
            elif choice == '7' or choice == 'back':
                main()
            else:
                print(f"\033[91mOngeldige keuze. Selecteer een geldig nummer uit het menu.\033[0m")

        continue_question = None

        while continue_question != "y" or continue_question != "n":
            continue_question = input("Wilt u nog een instelling aanpassen of bekijken (y/n): ").lower()
            if continue_question == "y":
                break
            elif continue_question == "n":
                main()
            else:
                print(f"\033[91mOngeldige waarde, probeer het opnieuw\033[0m")

def help_program():
    """
    Toon de help pagina met uitleg en informatie over hoe het programma werkt.
    """
    layout = f"""
    {header}
        --- Help Pagina ---

    Welkom bij de ultieme reis app! Dit programma helpt je bij het plannen van je volgende reis door informatie te verstrekken over
    afstanden, reistijden en weersomstandigheden. Je kunt een begin- en eindstad invoeren om een gedetailleerde routebeschrijving
    te krijgen, inclusief geschatte brandstofkosten en temperatuur in de eindstad.

    Functionaliteiten van de app:
    1. **Nieuwe Reis**: Start met het plannen van je reis door een begin- en eindstad te selecteren.
    2. **Preset**: Laad of maak een bestemming preset van een bestand.
    3. **Instellingen**: Pas de instellingen aan, zoals temperatuur- en afstandseenheden.
    4. **Help**: Toegang tot deze helpsectie voor ondersteuning en uitleg.
    5. **Afsluiten**: Stop het programma.

    Je kunt zowel cijfers als de Engelse commando's gebruiken om een keuze te maken. Bijvoorbeeld, je kunt '1' of 'new' invoeren om een nieuwe reis te starten.

    Bedankt voor het gebruik van de ultieme reis app! We hopen dat je een veilige en plezierige reis hebt.

    """
    print(layout)
    continue_question = None

    while continue_question != "y":
        continue_question = input("Wilt u terug naar het hoofdmenu (y): ").lower()
        if continue_question == "y":
            break
        else:
            print(f"\033[91mOngeldige waarde, probeer het opnieuw\033[0m")

def quit_program():
    """
    Verlaat het programma na bevestiging van de gebruiker.
    """
    while True:
        choice = input("Weet u zeker dat u het programma wilt afsluiten? (y/n): ").lower()
        if choice == 'y' or choice == 'yes':
            print("Oké, tot ziens.")
            exit()
        elif choice == 'n' or choice == 'no':
            print("Oké, ik breng u terug naar het hoofdmenu.")
            main()
        else:
            print(f"\033[91mOngeldige keuze. Selecteer een geldige optie uit het menu.\033[0m")
            continue

def pre_set():
    """
    Laad en beheer presets van reizen. Biedt opties om reizen te tonen, te laden,
    te creëren of te verwijderen.
    """
    while True:
        layout = f"""
                {header}
                    --- Preset Page ---

                1. Show      // Toon beschikbare reizen                   
                2. Back      // Terug naar het hoofdmenu
                """
        print(layout)

        choice = input("Maak een keuze (1-2): ").lower()

        if choice == '1' or choice == 'show':
            print(print_trips())
            tool_menu()
        elif choice == '2' or choice == 'back':
            main()
        else:
            print(f"\033[91mOngeldige keuze. Selecteer een geldig nummer uit het menu.\033[0m")

def tool_menu():
    """
    Biedt een menu aan voor het beheren van reis presets. Gebruikers kunnen reizen laden,
    nieuwe reizen creëren of bestaande reizen verwijderen.
    """
    layout = f"""
                    --- Preset Page ---

                    1. Load      // Laad reisgegevens
                    2. Create    // Maak een nieuwe reis
                    3. Remove    // Verwijder een bestaande reis
                    4. Back      // Terug naar het hoofdmenu
                """
    print(layout)

    choice = input("Maak een keuze (1-4): ").lower()

    if choice == '1' or choice == 'load':
        selected_trip = select_trip_by_index()
        change_settings_by_index(selected_trip)

        start_city = selected_trip.get('start_city')
        end_city = selected_trip.get('end_city')

        new(pre_set_start_city=start_city, pre_set_end_city=end_city)

    elif choice == '2' or choice == 'create':
        print(add_trip())
    elif choice == '3' or choice == 'remove':
        print(remove_trip_by_index())
    elif choice == '4' or choice == 'back':
        main()
    else:
        print(f"\033[91mOngeldige keuze. Selecteer een geldig nummer uit het menu.\033[0m")

def printer(
        start_city=None, end_city=None, distance=None, distance_unit=None, duration=None,
        arrival_context=None, arrival_time=None, sunset_info=None, temp_end_city=None,
        temperature_unit=None, weather_desc_end_city=None, fuel_price=None
):
    """
    Print een samenvatting van de route inclusief afstand, duur, aankomsttijd, weer en brandstofkosten.

    Parameters:
    start_city (str): Vertrekstad.
    end_city (str): Bestemming.
    distance (float): Afstand tussen de twee steden.
    distance_unit (str): Eenheid van de afstand (kilometers/mijlen).
    duration (str): Duur van de reis.
    arrival_context (str): Tijdsaanduiding van aankomst (vandaag/morgen/etc.).
    arrival_time (datetime): Verwachte aankomsttijd.
    sunset_info (str): Tijd tot zonsopkomst of zonsondergang.
    temp_end_city (float): Temperatuur in de aankomststad.
    temperature_unit (str): Eenheid van temperatuur (°C/°F).
    weather_desc_end_city (str): Weersomstandigheden in de aankomststad.
    fuel_price (float): Geschatte brandstofkosten voor de reis.

    Returns:
    None: Drukt een routebeschrijving af.
    """
    message = f"""
                De route van {start_city.capitalize()} naar {end_city.capitalize()} bedraagt 
                {distance:.1f} {distance_unit} en zal ongeveer {duration} duren in een auto. 
                Als je nu begint met rijden, ben je er {arrival_context} om {arrival_time.strftime("%H:%M")} (zonder tussenstops). 
                Dan heb je nog {sunset_info}. 
                De temperatuur in {end_city.capitalize()} is momenteel {temp_end_city:.2f}{temperature_unit} en het weer is {weather_desc_end_city}. 
                De geschatte brandstofkosten voor de reis bedragen €{fuel_price:.2f}.
                Veel succes en een veilige reis!
                """
    print(message)


if __name__ == '__main__':
    main()
