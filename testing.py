from datetime import datetime, timedelta


def timestamp_converter(sunrise_time=None, sunset_time=None, arrival_time=None):
    # Convert Unix timestamps to datetime objects
    sunrise_datetime = datetime.fromtimestamp(sunrise_time)
    sunset_datetime = datetime.fromtimestamp(sunset_time)
    arrival_datetime = arrival_time

    print(f"Sunrise: {sunrise_datetime}")
    print(f"Sunset: {sunset_datetime}")
    print(f"Arrival: {arrival_datetime}")

    # Case 1: Arrival is before sunrise (night time)
    if arrival_datetime < sunrise_datetime:
        time_difference = sunrise_datetime - arrival_datetime
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunrise"}, f"{hours} hours and {minutes} minutes until sunrise"]

    # Case 2: Arrival is during the day (before sunset)
    elif arrival_datetime < sunset_datetime:
        time_difference = sunset_datetime - arrival_datetime
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunset"}, f"{hours} hours and {minutes} minutes until sunset"]

    # Case 3: Arrival is after sunset (evening or night time)
    else:
        # Add 24 hours to calculate time until the next day's sunrise
        next_day_sunrise = sunrise_datetime + timedelta(days=1)
        time_difference = next_day_sunrise - arrival_datetime
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes = remainder // 60
        return [{"next_event": "sunrise"}, f"{hours} hours and {minutes} minutes until next sunrise"]


# Example usage:
sunrise_time = 1697362800  # Example Unix timestamp for sunrise (2023-10-15 06:00:00 UTC)
sunset_time = 1697406000  # Example Unix timestamp for sunset (2023-10-15 18:00:00 UTC)
arrival_time = datetime(2023, 10, 15, 10, 10, 0)  # Arrival time (2023-10-15 10:10:00)

result = timestamp_converter(sunrise_time=sunrise_time, sunset_time=sunset_time, arrival_time=arrival_time)
print(result)
