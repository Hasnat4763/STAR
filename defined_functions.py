import os
import requests
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv(".env")

ny2o_api_token = os.environ["ny2o_token"]


def coordinates(city):
    locator = Nominatim(user_agent="star")
    location = locator.geocode(city)
    if location:
        latitude = location.latitude
        longitude = location.longitude
        return float(latitude), float(longitude)
    return None, None

def sat_scan(lat,lon, altitude=0, radius=90, category=0):
    url = f"https://api.n2yo.com/rest/v1/satellite/above/{lat}/{lon}/{altitude}/{radius}/{category}/&apiKey={ny2o_api_token}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data.get("above", [])
    
def visible_scan(satellite_id,lat,lon,days, min_elevation):
    url = f"https://api.n2yo.com/rest/v1/satellite/visualpasses/{satellite_id}/{lat}/{lon}/0/{days}/{min_elevation}?apiKey={ny2o_api_token}"

    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    return data['passes']
