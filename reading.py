import json

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def edit_trip(data, title, new_fuel_consumption):
    for trip in data['trips']:
        if trip['Title'] == title:
            trip['fuel_consumption'] = new_fuel_consumption
            print(f"Fuel consumption updated for {title}.")
            return
    print(f"No trip found with the title '{title}'.")

def add_trip(data, new_trip):
    data['trips'].append(new_trip)
    print(f"New trip '{new_trip['Title']}' has been added.")

def delete_trip(data, title_to_remove):
    data['trips'] = [trip for trip in data['trips'] if trip['Title'] != title_to_remove]
    print(f"Record with title '{title_to_remove}' has been deleted.")


if __name__ == "__main__":
    file_path = 'app_database.json'

    data = read_json(file_path)

    edit_trip(data, 'Road Trip 1', 5.9)

    new_trip = {
        "Title": "Road Trip 4",
        "ID": "4",
        "temperature_unit": "Celsius",
        "distance_unit": "Kilometers",
        "fuel_cost": 2.10,
        "fuel_consumption": 8.0,
        "start_city": "Madrid",
        "end_city": "Lisbon"
    }

#     message = f"""
# Title: {new_trip['Title']}
#     Reis van: {new_trip['start_city']} --> naar {new_trip['end_city']}
#         Temperature unit: {new_trip['temperature_unit']}
#         Distance unit: {new_trip['distance_unit']}
#         Fuel cost: {new_trip['fuel_cost']}
#         Fuel consumption: {new_trip['fuel_consumption']}
# """
#     print(message)

    add_trip(data, new_trip)

    delete_trip(data, 'Road Trip 2')

    write_json(file_path, data)

