settings = {
    "temperature_unit": ["fahrenheit", ("celcius", "fahrenheit", "kelvin")],
    "distance_unit": ["kilometers", ("kilometers", "miles")],
    "fuel_consumption": ["7/100", ("7/100",)],
    "fuel_cost": [1.820, (1.820,)]
}


def settings_menu(request_value="", request_item=""):
    if request_value in settings:
        try:
            if request_value == "fuel_cost":
                item_to_compare = float(request_item)
            else:
                item_to_compare = request_item.lower()

            if item_to_compare in settings[request_value][1]:
                settings[request_value][0] = item_to_compare
            else:
                raise ValueError(f"{request_item} is not part of {request_value}")

        except ValueError:
            return "Probeer het opnieuw"

    return settings

# Test the function
print(settings_menu(request_value="distance_unit", request_item="miles"))
print(settings_menu(request_value="fuel_cost", request_item="1.820"))