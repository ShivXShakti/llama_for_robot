import requests

url = "http://127.0.0.1:5000/generate"

payload = {
    "prompt": "Move the right arm to pick up the cup."
}

try:
    resp = requests.post(url, json=payload, timeout=10)

    print("Status code:", resp.status_code)
    print("Raw response:", resp.text)

    if resp.status_code == 200:
        data = resp.json()

        action = data.get("action", "none")
        obj = data.get("object", "none")
        place_location = data.get("place_location", "none")

        print("\nParsed Command:")
        print("  Action:", action)
        print("  Object:", obj)
        print("  Place Location:", place_location)

        # ---- ROBOT EXECUTION LOGIC ----
        if action == "pick":
            print(f"➡ Pick {obj}")
            if place_location != "none":
                print(f"➡ Then place {obj} at {place_location}")

        elif action == "place":
            print(f"➡ Place {obj} at {place_location}")

        elif action == "hold":
            print("➡ Hold current position")

        else:
            print("➡ No valid task detected")

    else:
        print("❌ Server returned error")

except requests.exceptions.RequestException as e:
    print("❌ Request failed:", e)
