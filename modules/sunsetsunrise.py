from astral import LocationInfo, moon
from astral.sun import sun, golden_hour, blue_hour, twilight, night, daylight, time_at_elevation
import datetime

def get_sun_times(
    latitude: float = 54.8985,
    longitude: float = 23.9036,
    name: str = "Lithuania",
    region: str = "Kaunas",
    timezone: str = "Europe/Vilnius",
    date: datetime.date = None
):
    """
    Calculate various sun and moon related times and information for a given location and date.

    Args:
        latitude (float): Latitude of the location. Defaults to 54.8985.
        longitude (float): Longitude of the location. Defaults to 23.9036.
        name (str): Name of the location. Defaults to "Lithuania".
        region (str): Region of the location. Defaults to "Kaunas".
        timezone (str): Timezone of the location. Defaults to "Europe/Vilnius".
        date (datetime.date, optional): Date for which to calculate the times. Defaults to None (today's date).

    Returns:
        dict: A dictionary containing various sun and moon related information.
    """

    location = LocationInfo(name, region, timezone, latitude, longitude)
    if date is None:
        date = datetime.date.today()

    # Get sun information
    s = sun(location.observer, date=date)

    # Calculate moon information
    m = moon(location.observer, date)

    # ... rest of the function remains the same ...

    # Prepare the result dictionary
    result = {
        # ... other keys remain the same ...
        'moonrise': m.rise.strftime('%H:%M:%S') if m.rise else None,
        'moonset': m.set.strftime('%H:%M:%S') if m.set else None,
        'moon_azimuth': round(m.azimuth, 2),
        'moon_zenith': round(90 - m.elevation, 2),
        'moon_phase': round(m.fraction, 2)
    }

    return result

print(get_sun_times())