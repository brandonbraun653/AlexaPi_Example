import os
import json
import time
import requests

server_url = 'http://10.194.240.42:3000'
server_header = {"items": "Content-Type:application/json"}
server_function = {"light":        "/updateLight",
                   "allLights":    "/updateAllLight",
                   "mode":         "/updateMode",
                   "setTemp":      "/updateSetTemp",
                   "currentTemp":  "/updateCurrTemp"}

server_payload = {"light":         {"light": "<light_name>",    "state": ""},
                  "allLights":     {"light": "lights",          "state": ""},
                  "mode":          {"room": "home",             "mode": ""},
                  "setTemp":       {"room": "home",             "setTemp": 0},
                  "currentTemp":   {"room": "home",             "currTemp": 0}}

if __name__ == "__main__":

    # ----------------------
    # SET TEMPERATURE
    # ----------------------
    print("Attempting to set the temperature")

    # First configure the payload with the desired value
    server_payload["setTemp"]["setTemp"] = 30

    # Assign the url and payload data
    url = server_url + server_function["setTemp"]
    payload = server_payload["setTemp"]

    # Post
    res = requests.post(url, data=payload, headers=server_header)
    print("Done")
    time.sleep(0.5)

    # ----------------------
    # ALL LIGHTS ON
    # ----------------------
    print("Attempting to turn on all lights")
    server_payload["allLights"]["state"] = "on"
    url = server_url + server_function["allLights"]
    payload = server_payload["allLights"]
    requests.post(url, data=payload, headers=server_header)
    print("Done")
    time.sleep(0.5)

    # ----------------------
    # ALL LIGHTS OFF
    # ----------------------
    print("Attempting to turn off all lights")
    server_payload["allLights"]["state"] = "off"
    url = server_url + server_function["allLights"]
    payload = server_payload["allLights"]
    requests.post(url, data=payload, headers=server_header)
    print("Done")
    time.sleep(0.5)

    # ----------------------
    # CHANGE HOUSE MODE
    # Can be: "auto", "heat", "cool"
    # TODO: currently does not trigger the web-page
    # ----------------------
    print("Attempting to turn on the AC")
    server_payload["mode"]["mode"] = "auto"
    url = server_url + server_function["mode"]
    payload = server_payload["mode"]
    requests.post(url, data=payload, headers=server_header)
    print("Done")
    time.sleep(0.5)

    # ----------------------
    # CYCLE EACH LIGHT ON/OFF
    # TODO: Testing...not sure what the keyword for each light needs to be\
    # INCOMPLETE
    # ----------------------
    print("Cycling through all lights")
    server_payload["light"]["light"] = "Patio Light"
    server_payload["light"]["state"] = "on"

    url = server_url + server_function["light"]
    payload = server_payload["light"]

    #requests.post(url, data=payload, headers=server_header)
    print("Done")
    time.sleep(0.5)
