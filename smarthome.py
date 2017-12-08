#!/usr/bin/env/python

import os
import json
import time
import requests

# This is a dependency not native to the basic RPI install
# It can be found here: https://pypi.python.org/pypi/AWSIoTPythonSDK/1.0.0
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

# NAMING CONVENTIONS FOR VARIOUS LIGHTS
# switch1a - patio light
# switch1b - hall light
# switch1c - kitchen light
# switch1d - dining light
# switch2a - living room
# switch2b - bedroom
# switch2c - restroom
# switch3a - attic

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


class OnOffLightType:
    def __init__(self, name, friendly_name, iot, server_name):
        """
        Creates the shadow handler for the object and initializes
        it to the default state.
        :param name: Name of the thing as specified on the IoT dashboard
        :param iot: Object of type returned from createIoT()
        """
        self.name = name
        self.server_thing_name = server_name
        self.friendlyName = friendly_name
        self.shadow = iot.createShadowHandlerWithName(self.name, True)

        # Register a function to run when the shadow is updated online
        self.shadow.shadowRegisterDeltaCallback(self.shadowDeltaCallback)

        # Initialize the device to OFF
        self.set(False)

    # CALLBACK FUNCTION
    def shadowDeltaCallback(self, payload, responseStatus, token):
        # Why does this need to be ['state']['light']???
        new_state = json.loads(payload)['state']['light']

        if new_state:
            print(str(self.friendlyName) + " received a turn ON request")
        else:
            print(str(self.friendlyName) + " received a turn OFF request")

        # Inform the shadow of the new state
        self.set(new_state)

        # Update the Server API
        self.thing_action(new_state)

    # SHADOW UPDATE ACTION FUNCTION
    def set(self, state):
        # Update the shadow handler with the new state
        self.shadow.shadowUpdate(json.dumps({
            'state': {
                'reported': {
                    'light': state
                }
            }
        }
        ), None, 5)

        if state:
            print(str(self.friendlyName) + " ON")
        else:
            print(str(self.friendlyName) + " OFF")

    def thing_action(self, state):
        if state:
            temp = "on"
        else:
            temp = "off"

        server_payload["light"]["light"] = self.server_thing_name
        server_payload["light"]["state"] = temp

        url = server_url + server_function["light"]
        payload = server_payload["light"]

        requests.post(url, data=payload, headers=server_header)
        time.sleep(0.5)


class ThermostatType:
    def __init__(self, name, friendly_name, iot, server_name):
        self.name = name
        self.server_thing_name = server_name
        self.friendlyName = friendly_name
        self.shadow = iot.createShadowHandlerWithName(self.name, True)

        # Register a function to run when the shadow is updated online
        self.shadow.shadowRegisterDeltaCallback(self.shadow_delta_callback)

    def shadow_delta_callback(self, payload, responseStatus, token):
        json_data = json.loads(payload)

        # Sort through the possible Delta keys we are looking for
        if 'value' in json_data["state"]:
            new_temp = json_data["state"]["value"]
            print(str(self.friendlyName) + " requested updated temp of " + str(new_temp))
        else:
            new_temp = ""

        if 'mode' in json_data["state"]:
            new_mode = json_data["state"]["mode"]
            print(str(self.friendlyName) + " requested updated mode of " + str(new_mode))
        else:
            new_mode = ""

        if 'scale' in json_data["state"]:
            new_scale = json_data["state"]["scale"]
            print(str(self.friendlyName) + " requested updated scale of " + str(new_scale))
        else:
            new_scale = ""

        # Inform the shadow of the new state
        self.update_shadow(new_temp, new_mode, new_scale)

        # Update the Server API
        self.update_server(new_mode, new_temp)

    def update_shadow(self, value, mode, scale):
        update_response = {'state': {'reported': {}}}

        if value != "":
            update_response["state"]["reported"]["value"] = value

        if mode != "":
            update_response["state"]["reported"]["mode"] = mode

        if scale != "":
            update_response["state"]["reported"]["scale"] = scale

        self.shadow.shadowUpdate(json.dumps(update_response), None, 5)

    def update_server(self, mode, temp):
        # New AC Mode Update
        if mode != "":
            if mode == "COOL":
                new_mode = "mode3"
            elif mode == "HEAT":
                new_mode = "mode2"
            elif mode == "OFF":
                new_mode = "mode1"
            else:
                new_mode = "mode1"

            server_payload["mode"]["mode"] = new_mode

            url = server_url + server_function["mode"]
            payload = server_payload["mode"]

            requests.post(url, data=payload, headers=server_header)
            time.sleep(0.5)

        # New Temperature Update
        if temp != "":
            server_payload["setTemp"]["setTemp"] = temp

            url = server_url + server_function["setTemp"]
            payload = server_payload["setTemp"]

            requests.post(url, data=payload, headers=server_header)
            time.sleep(0.5)


def create_iot(endpoint='', credentials='rootCA.pem'):
    """
    Creates a connection to a Thing in the user's IoT dashboard.

    :param endpoint: HTTPS link to the thing. Can be found under the
        "Interact" tab of the Thing in the developer dashboard.
    :param credentials: filename for the credentials of this thing
    :return: iot object
    """
    # Can the 'AlexaPi' be arbitrary?
    iot_thing = AWSIoTMQTTShadowClient('AlexaPi', useWebsocket=True)

    iot_thing.configureEndpoint(endpoint, 443)
    iot_thing.configureCredentials(os.path.join(os.path.dirname(os.path.realpath(__file__)), credentials))
    iot_thing.configureConnectDisconnectTimeout(10)
    iot_thing.configureMQTTOperationTimeout(5)
    iot_thing.connect()
    return iot_thing


if __name__ == "__main__":
    # In this case the endpoint for ALL the devices are the same. Perhaps
    # it is because they share a common security profile? Not too sure why.
    print("Connecting all the things...")
    iot_ap = create_iot(endpoint='atnox9aalr8w3.iot.us-east-1.amazonaws.com')
    print("Done!")

    print("Initializing all devices...")
    ThermostatType('Thermostat', 'Thermostat', iot_ap, 'n/a')
    OnOffLightType('F1_DiningLight', 'Dining Room Light', iot_ap, "switch1d")
    OnOffLightType('F1_KitchenLight', 'Kitchen Light', iot_ap, "switch1c")
    OnOffLightType('F1_HallLight', 'Hall Light', iot_ap, "switch1b")
    OnOffLightType('F1_PatioLight', 'Patio Light', iot_ap, "switch1a")
    OnOffLightType('F2_RestRoomLight', 'Rest Room Light', iot_ap, "switch2c")
    OnOffLightType('F2_BedRoomLight', 'Bed Room Light', iot_ap, "switch2b")
    OnOffLightType('F2_LivingRoomLight', 'Living Room Light', iot_ap, "switch2a")
    OnOffLightType('F3_AtticLight', 'Attic Light', iot_ap, "switch3a")
    print("Done!")
    time.sleep(1)
    print('Listening...')

    while True:
        time.sleep(0.2)
