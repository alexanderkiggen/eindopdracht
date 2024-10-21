from http.client import responses

import json_processen
import processen
import pprint as pp
import sys
import json_processen
from json_processen import print_trips, add_trip, remove_trip_by_index

header = "===== De ultieme reis app ====="

def main():
    while True:
        layout = f"""
        {header}
               --- Home Page ---

        1. New       // Start planning your next trip
        2. Load      // Load or create a destination pre-set from a file.
        3. Settings  // Change settings for current session.
        4. Help      // A guide.
        5. Quit      // Quit program.
        """
        print(layout)

        choice = input("Please select an option (1-5): ").lower()

        if choice == '1' or choice == 'new':
            new()
        elif choice == '2' or choice == 'load':
            load()
        elif choice == '3' or choice == 'settings':
            settings()
        elif choice == '4' or choice == 'help':
            help()
        elif choice == '5' or choice == 'quit':
            quit()
        else:
            print("Invalid option. Please select a valid number from the menu.")

def new():
    while True:
        start_city = input("Please select a starting city: ").lower()
        start_coords = processen.get_city_coordinaten(start_city)

        while start_coords is None:
            print(f"Error: City '{start_city}' is not a valid city in Europe. Please try again.", file=sys.stderr)
            start_city = input("Please select a valid starting city: ").lower()
            start_coords = processen.get_city_coordinaten(start_city)

        end_city = input("Please select an end city: ").lower()
        end_coords = processen.get_city_coordinaten(end_city)

        while end_coords is None:
            print(f"Error: City '{end_city}' is not a valid city in Europe. Please try again.", file=sys.stderr)
            end_city = input("Please select a valid end city: ").lower()
            end_coords = processen.get_city_coordinaten(end_city)

        directions = processen.get_directions(start_city=start_city, end_city=end_city)

        if directions is None:
            continue

        distance = directions['total_distance']
        duration = directions['duration_time']
        fuel_price = directions['fuel_price']
        sunset_info = directions['time_until_sun_up_or_down'][1]
        temp_end_city = directions['temp_end_city']
        weather_desc_end_city = directions['weather_desc_end_city']

        if processen.settings["distance_unit"][0] == "kilometers":
            distance_unit = "kilometers"
        else:
            distance_unit = "mijl"

        if processen.settings["temperature_unit"][0] == "metric":
            temperature_unit = "°C"
        elif processen.settings["temperature_unit"][0] == "imperial":
            temperature_unit = "°F"
        else:
            temperature_unit = "K"

        arrival_time, arrival_context = processen.parse_duration_and_calculate_arrival(duration)

        if arrival_time is None:
            continue

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

        continue_question = None

        while continue_question != "y" or continue_question != "n":
            continue_question = input("Wilt u nog een reis plannen (y/n): ").lower()
            if continue_question == "y":
                break
            elif continue_question == "n":
                main()
            else:
                print("Dat is geen geldige waarde, probeer het opnieuw", file=sys.stderr)

def settings():  # Renamed from settings to settings_menu
    while True:
        layout = f"""
        {header}
            --- Settings Page ---

        1. Temp      // Change default temperature unit
        2. Dist      // Change default distance unit
        3. Fuel      // Change default fuel cost price per liter
        4. Cons      // Change default fuel consumption
        --------------------------------------------------------
        5. Show      // Show all current settings
        6. Restore   // Restore default settings
        7. Back      // Back to home page.
        """

        while True:
            print(layout)
            choice = input("Please select an option (1-7): ").lower()

            if choice == '1' or choice == 'temp':
                new_temp = input("Enter new temperature unit (metric/imperial/units): ").lower()
                result = processen.settings_menu("temperature_unit", new_temp)
                print(result if result else "Temperature unit updated successfully.")

            elif choice == '2' or choice == 'dist':
                new_dist = input("Enter new distance unit (kilometers/miles): ").lower()
                result = processen.settings_menu("distance_unit", new_dist)
                print(result if result else "Distance unit updated successfully.")
            elif choice == '3' or choice == 'fuel':
                new_fuel_cost = input("Enter new fuel cost per liter: ")
                result = processen.settings_menu("fuel_cost", new_fuel_cost)
                print(result if result else "Fuel cost updated successfully.")
            elif choice == '4' or choice == 'cons':
                new_fuel_cons = input("Enter new fuel consumption (liters per 100km): ")
                result = processen.settings_menu("fuel_consumption", new_fuel_cons)
                print(result if result else "Fuel consumption updated successfully.")
            elif choice == '5' or choice == 'show':
                print("\nCurrent Settings:")
                for key, value in processen.settings.items():
                    print(f"{key.replace('_', ' ').capitalize()}: {value[0]}")
            elif choice == '6' or choice == 'restore':
                processen.settings_menu("restore_defaults")
                print("All settings have been restored to default values.")
            elif choice == '7' or choice == 'back':
                main()
            else:
                print("Invalid option. Please select a valid number from the menu.", file=sys.stderr)

            continue_question = None

            while continue_question != "y" or continue_question != "n":
                continue_question = input("Wilt u nog een instelling aanpassen of bekijken (y/n): ").lower()
                if continue_question == "y":
                    break
                elif continue_question == "n":
                    main()
                else:
                    print("Dat is geen geldige waarde, probeer het opnieuw", file=sys.stderr)

def help():
    layout = f"""
    {header}
        --- Help Page ---

    Credits menu bla bla bla bla bla bla bla bla bla
    bla bla bla bla bla bla bla bla bla bla bla bla
    bla bla bla bla bla bla bla bla bla bla bla bla
    bla bla bla bla bla bla bla bla bla bla bla bla
    """
    print(layout)
    continue_question = None

    while continue_question != "y":
        continue_question = input("Wilt u terug naar het hoofdmenu (y): ").lower()
        if continue_question == "y":
            break
        else:
            print("Dat is geen geldige waarde, probeer het opnieuw", file=sys.stderr)

def quit():
    while True:
        choice = input("Are you sure you want to quit the program? (y/n): ").lower()
        if choice == 'y' or choice == 'yes':
            print("Alright, good bye.")
            exit()
        elif choice == 'n' or choice == 'no':
            print("Alright, I will take you back to the main menu.")
            main()
        else:
            print("Invalid option. Please select a valid letter from the menu.", file=sys.stderr)
            continue

def load():
    while True:
        layout = f"""
                {header}
                    --- Preset Page ---

                1. Show      // Show available trips                
                2. Back      // Go back to the main menu
                """
        print(layout)

        choice = input("Please select an option (1-2): ").lower()

        if choice == '1' or choice == 'show':
            print(print_trips())
            tool_menu()
        elif choice == '2' or choice == 'back':
            main()
        else:
            print("Invalid option. Please select a valid number from the menu.")

def tool_menu():
    layout = f"""
            --- Preset Page ---

            1. Load      // Load trip data
            2. Create    // Create a new trip
            3. Remove    // Remove an existing trip
            4. Back      // Go back to the main menu
    """
    print(layout)

    choice = input("Please select an option (1-5): ").lower()

    if choice == '1' or choice == 'load':
        pass
    elif choice == '2' or choice == 'create':
        print(add_trip())
    elif choice == '3' or choice == 'remove':
        print(remove_trip_by_index())
    elif choice == '4' or choice == 'back':
        main()
    else:
        print("Invalid option. Please select a valid number from the menu.")


if __name__ == '__main__':
    main()
