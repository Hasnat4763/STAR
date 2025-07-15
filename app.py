from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from dateutil import parser
import time
load_dotenv(".env")

from defined_functions import coordinates, sat_scan, visible_scan
from meme_fetcher import fetch_memes_from_reddit

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
        respond("Invalid command format. Use `/aurabot_scan <city> <number>`.")
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
        respond("Invalid command format. Use `/aurabot_visible_pass <satellite_id> <city> <days>`.")
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
        list_of_passes = "\n".join([f"- {datetime.fromtimestamp(p['startUTC'], tz=timezone.utc)} to {datetime.fromtimestamp(p['endUTC'], tz=timezone.utc)}" for p in passes])
        respond(f"Visible passes for satellite ID {satellite_id} over {city}:\n{list_of_passes}")

@app.command("/star_notify")
def handle_notify_command(ack, respond, command):
    ack()
    parts = command["text"].strip().split()
    if len(parts) != 2:
        respond("Invalid command format. Use `/star_notify <satellite_id> <city> <days>`.")
        return
    else:
        sat_id = int(parts[0])
        city = parts[1]
        user = command["user_id"]
    lat, lon = coordinates(city)
    if lat is None or lon is None:
        respond(f"Could not find coordinates for {city}. Please check the city name.")
        return
    respond(f"You are located at {lat}, {lon}. \n You will be notified when it will appear over {city} again... ")
    passes = visible_scan(sat_id, lat, lon, 7, 20)

    pass1= passes[0]
    next_pass = {
        "starUTC" : datetime.fromtimestamp(pass1["startUTC"]),
        "endUTC" : datetime.fromtimestamp(pass1["endUTC"]),
        "satellite_id" : sat_id,
        "city" : city,
    }
    next_pass = "\n".join(next_pass)
    dm_channel = client.conversations_open(users=user)["channel"]['id']
    
    start_time = parser.parse(pass1["startUTC"])
    delay = int((start_time - datetime.now()).total_seconds())
    post_the_message_at = int(time.time()) + max(5, delay)
    client.chat_postMessage(channel=dm_channel, text=next_pass, post_at=post_the_message_at)
    
    
@app.command("/star_memes")
def handle_memes_command(ack, respond, command):
    ack()
    parts = command["channel_id"].strip()
    respond("Fetching memes from r/astronomymemes...")
    fetch_memes_from_reddit(parts)
    

if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()