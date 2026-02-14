def location(location_json):
    type = location_json["type"]
    offline_address = location_json["offline_address"]
    online_link = location_json["online_link"]
    if type == "Unknown" or type == "International" or type == "Bundesweit":
        return type
    elif type == "Online":
        return online_link if online_link else "Unknown"
    elif type == "Offline":
        return offline_address if offline_address else "Unknown"
    elif type == "Regional":
        return location_json["regional_region"]
    elif type == "Hybrid":
        return f"Hybrid: {offline_address} | {online_link}"
