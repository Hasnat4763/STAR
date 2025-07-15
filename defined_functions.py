import os
import requests
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv(".env")

ny2o_api_token = os.environ["ny2o_token"]
ninja_api_token = os.environ["NINJA_API"]
nasa_api_token = os.environ["NASA_API"]


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
def radio_pass_scan(satellite_id,lat,lon,days, min_elevation):
    url = f"https://api.n2yo.com/rest/v1/satellite/radiopasses/{satellite_id}/{lat}/{lon}/0/{days}/{min_elevation}?apiKey={ny2o_api_token}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()

    return data['passes']

def get_info_ninja(planet):
    url = f"https://api.api-ninjas.com/v1/planets?name={planet}"
    headers = {
        "X-Api-Key": ninja_api_token
    }
    result = requests.get(url, headers=headers)
    if result.status_code != 200:
        return None
    data = result.json()
    if not data:
        return None
    return data[0]

def APOD():
    url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_token}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    blocks = []

    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*{data['title']}* \n_{data['date']}_\n\n{data['explanation'][:700]}..."}
    })

    if data["media_type"] == "image":
        blocks.append({
            "type": "image",
            "title": {"type": "plain_text", "text": "NASA Astronomy Picture of the Day"},
            "image_url": data["url"],
            "alt_text": "APOD Image"
        })
    else:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"[Click to view media]({data['url']})"}
        })
    return blocks