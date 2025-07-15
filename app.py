from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
import time
from math import ceil
load_dotenv(".env")

from defined_functions import coordinates, sat_scan, visible_scan, radio_pass_scan, get_info_ninja, APOD
from meme_fetcher import fetch_memes_from_reddit
from formatter import format_to_block, format_planet

bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]


app = App(token=bot_token)
client = WebClient(token=bot_token)


@app.command("/star_scan")
def handle_scan(ack, respond, command):
    ack()
    parts = command["text"].strip().split()
    if len(parts) < 2:
        city = parts[0]
        number = 5
    elif len(parts) == 2:
        city = parts[0]
        number = parts[1]
    else:
        respond("Invalid command format. Use `/star_scan <city> <number>`.")
        return
    if not city:
        respond("Please give a city name.")
        return
    lat,lon = coordinates(city)
    if lat is None or lon is None:
        respond(f"Could not find coordinates for {city}. Please check the city name.")
        return
    respond(f"You are located at {lat}, {lon}. \n Scanning satellites over {city}... ")
    satellites = sat_scan(lat, lon)
    if not satellites:
        respond(f"No satellites found over {city}.")
        return
    list_of_sats = "\n".join([f"- {sat['satname']} (ID: {sat['satid']})" for sat in satellites[:int(number)]])
    respond(f"Satellites currently visible: \n{list_of_sats}")
    


@app.command("/star_visible_pass")
def handle_eye_command(ack, respond, command):
    ack()
    parts = command["text"].strip().split()
    if len(parts) == 3:
        satellite_id = int(parts[0])
        city = parts[1]
        days = int(parts[2])
    else:
        respond("Invalid command format. Use `/star_visible_pass <satellite_id> <city> <days>`.")
        return
    if not city:
        respond("Please give a city name.")
        return
    lat,lon = coordinates(city)
    if lat is None or lon is None:
        respond(f"Could not find coordinates for {city}. Please check the city name.")
        return
    respond(f"You are located at {lat}, {lon}. \n Finding when it will appear over {city} again... ")
    passes = visible_scan(satellite_id, lat, lon, days, 20)
    if not passes:
        respond("No visible passes found")
        return
    else:
        list_of_passes = format_to_block(passes, "visible")
        respond(blocks=list_of_passes)

@app.command("/star_radiopasses")
def handle_radio_command(ack, respond, command):
    ack()
    parts = command["text"].strip().split()
    if len(parts) == 3:
        satellite_id = int(parts[0])
        city = parts[1]
        days = int(parts[2])
    else:
        respond("Invalid command format. Use `/star_visible_pass <satellite_id> <city> <days>`.")
        return
    if not city:
        respond("Please give a city name.")
        return
    lat,lon = coordinates(city)
    if lat is None or lon is None:
        respond(f"Could not find coordinates for {city}. Please check the city name.")
        return
    respond(f"You are located at {lat}, {lon}. \n Finding when it will appear on your radio again... ")
    passes = radio_pass_scan(satellite_id, lat, lon, days, 10)
    if not passes:
        respond("No radio passes found")
        return
    else:
        list_of_passes = format_to_block(passes, "Radio")
        respond(blocks=list_of_passes)

@app.command("/star_notify")
def handle_notify_command(ack, respond, command):
    ack()
    parts = command["text"].strip().split()
    if len(parts) != 3:
        respond("Invalid command format. Use `/star_notify <satellite_id> <city>`.")
        return
    else:
        sat_id = int(parts[0])
        city = parts[1]
        type = parts[2]
        user = command["user_id"]
    lat, lon = coordinates(city)
    if lat is None or lon is None:
        respond(f"Could not find coordinates for {city}. Please check the city name.")
        return
    respond(f"You are located at {lat}, {lon}. \n You will be notified when it will appear over {city} again... ")
    if type == "radio":
        passes = radio_pass_scan(sat_id, lat, lon, 7, 20)
    else:
        passes = visible_scan(sat_id, lat, lon, 7, 20)
    if not passes:
        respond(f"No {type} passes found")
        return
    pass1= passes[0]
    next_pass = {
        "starUTC" : datetime.fromtimestamp(pass1["startUTC"], tz=timezone.utc),
        "endUTC" : datetime.fromtimestamp(pass1["endUTC"], tz=timezone.utc),
        "satellite_id" : sat_id,
        "city" : city,
    }
    next_pass = "\n".join(next_pass)
    
    dm_channel_setup = client.conversations_open(users=user)
    if dm_channel_setup and dm_channel_setup.get("ok") and "channel" in dm_channel_setup:
        dm_channel = dm_channel_setup["channel"]["id"]
    else:
        respond("Could not open a direct message channel.")
        return
    start_time = datetime.fromtimestamp(pass1["startUTC"], tz=timezone.utc)
    delay = ceil((start_time - datetime.now(timezone.utc)).total_seconds())
    if delay < 10:
        respond("The next pass is already started can't give notification.")
        return
    
    post_the_message_at = int(time.time()) + delay
    client.chat_scheduleMessage(channel=dm_channel, text=f"We are notifying you about a pass of the satellite with ID {sat_id} \n{next_pass}", post_at=post_the_message_at)
@app.command("/star_memes")
def handle_memes_command(ack, respond, command):
    ack()
    parts = command["channel_id"].strip()
    respond("Fetching memes from r/astronomymemes...")
    fetch_memes_from_reddit(parts)

@app.command("/star_iss")
def handle_iss_command(ack, respond, command):
    ack()
    parts = command["text"].strip().split()
    if len(parts) != 1:
        respond("Invalid command format. Use `/star_iss <city>`.")
        return
    city = parts[0]
    lat, lon = coordinates(city)
    if lat is None or lon is None:
        respond(f"Could not find coordinates for {city}. Please check the city name.")
        return
    respond(f"You are located at {lat}, {lon}. \n Finding when ISS will appear over {city} again... ")
    visible_passes = visible_scan(25544, lat, lon, 7, 20)
    radio_passes = radio_pass_scan(25544, lat, lon, 7, 10)
    if not visible_passes:
        respond("No visible passes found for ISS.")
        return
    list_of_passes = format_to_block(visible_passes, "visible")
    respond(blocks=list_of_passes)
    if not radio_passes:
        respond("No radio passes found for ISS.")
        return
    list_of_radio_passes = format_to_block(radio_passes[:5], "radio")
    respond(blocks=list_of_radio_passes)
@app.command("/star_facts")
def handle_facts_command(ack, respond, command):
    ack()
    planet = command["text"].strip()
    data = get_info_ninja(planet)
    if not data:
        respond(f"Could not find information about {planet}. Please check the planet name.")
        return
    infos = format_planet(data)
    respond(blocks=infos)
@app.command("/star_astronomy_photo")
def handle_astronomy(ack, respond, command):
    ack()
    data = APOD()
    respond(blocks=data)

if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()