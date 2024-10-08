settings = {
    "temperature_unit": ["celcius", ("celcius", "fahrenheit", "kelvin")],
    "distance_unit": ["kilometers", ("kilometers", "miles")],
    "fuel_cost": [1.820, (1.820,)],
    "fuel_consumption": [7.0, (7.0,)]
}

def settings_menu(request_value=None, request_item=None):
    """
    Beheer de instellingen van het systeem.

    Deze functie stelt de gebruiker in staat om instellingen te wijzigen,
    waaronder temperatuur-, afstands-, brandstofkosten en brandstofverbruik.
    Het biedt ook de mogelijkheid om standaardwaarden te herstellen.

    Parameters:
    request_value (str): De naam van de instelling die moet worden gewijzigd,
                         zoals 'temperature_unit', 'distance_unit',
                         'fuel_cost', 'fuel_consumption', of 'restore_defaults'.
    request_item (str or float): De nieuwe waarde voor de opgegeven instelling.
                                  Dit kan een string zijn voor eenheid wijzigingen
                                  of een float voor kosten en verbruik.

    Returns:
    str: Een foutmelding als de invoer ongeldig is of niet kan worden verwerkt.
    """
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

def reis_planner_menu():
    pass

def weer_menu():
    pass

def optimaliseer_menu():
    pass