from datetime import datetime, timezone

def format_to_block(passes, type):
    blocks=[]
    if not passes:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "No visible passes found."
            }
        })
        return blocks

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"Upcoming {type} passes for the satellite you request:*"
        }
        })
    blocks.append({"type": "divider"})
    for i in passes:
        start = datetime.fromtimestamp(i['startUTC'], tz=timezone.utc).strftime('%Y-%m-%d %I:%M %p UTC')
        end = datetime.fromtimestamp(i['endUTC'], tz=timezone.utc).strftime('%Y-%m-%d %I:%M %p UTC')
        duration_seconds = int(i['endUTC']) - int(i['startUTC'])
        duration = duration_seconds // 60

        max_el = i.get('maxEl', 'N/A')
        
        pass_infos = (
        f"*Start:* {start}\n"
        f"*End:* {end}\n"
        f"*Duration:* {duration} minutes\n"
        f"*Max Elevation:* {max_el}°"
    )
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": pass_infos
            }
        })
        blocks.append({"type": "divider"})
    return blocks

def format_planet(data):
    blocks = []

    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"🌌 Facts about {data['name']}",
            "emoji": True
        }
    })

    blocks.append({"type": "divider"})

    facts = (
        f"*Mass:* {data['mass']:.2e} kg\n"
        f"*Radius:* {data['radius']} km\n"
        f"*Orbital Period:* {data['period']} Earth days\n"
        f"*Semi-Major Axis:* {data['semi_major_axis']} million km\n"
        f"*Avg. Temperature:* {data['temperature']} K\n"
        f"*Host Star Mass:* {data['host_star_mass']} M☉\n"
        f"*Host Star Temp:* {data['host_star_temperature']} K"
    )

    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": facts
        }
    })

    return blocks
