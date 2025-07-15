from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv(".env")

from defined_functions import coordinates, sat_scan, visible_scan

bot_token = os.environ["SLACK_BOT_TOKEN"]
app_token = os.environ["SLACK_APP_TOKEN"]


app = App(token=bot_token)

@app.command("/aurabot_scan")
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
    


@app.command("/aurabot_visible_pass")
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

if __name__ == "__main__":
    SocketModeHandler(app, app_token).start()