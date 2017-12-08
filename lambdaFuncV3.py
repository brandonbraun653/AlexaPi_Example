import logging
import boto3
import json
import time
import uuid

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iot-data')

SMART_HOME_APPLIANCES = [
    {
        'applianceId': 'Thermostat',
        'friendlyName': 'Thermostat',
        'friendlyDescription': 'The thermostat controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff',
            'setTargetTemperature',
            'incrementTargetTemperature',
            'decrementTargetTemperature'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Thermostat',
        'version': '1'
    },
    {
        'applianceId': 'F1_DiningLight',
        'friendlyName': 'Dining Room Light',
        'friendlyDescription': 'The dining room light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F1_KitchenLight',
        'friendlyName': 'Kitchen Light',
        'friendlyDescription': 'The kitchen light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F1_HallLight',
        'friendlyName': 'Hall Light',
        'friendlyDescription': 'The hall light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F1_PatioLight',
        'friendlyName': 'Patio Light',
        'friendlyDescription': 'The patio light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F2_RestRoomLight',
        'friendlyName': 'Bathroom Light',
        'friendlyDescription': 'The bathroom light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F2_BedRoomLight',
        'friendlyName': 'Bedroom Light',
        'friendlyDescription': 'The bedroom light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F2_LivingRoomLight',
        'friendlyName': 'Living Room Light',
        'friendlyDescription': 'The living room light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    },
    {
        'applianceId': 'F3_AtticLight',
        'friendlyName': 'Attic Light',
        'friendlyDescription': 'The attic light controlled by AlexaPi',
        'actions': [
            'turnOn',
            'turnOff'
        ],
        'additionalApplianceDetails': {},
        'isReachable': True,
        'manufacturerName': 'SmartHome',
        'modelName': 'Smart Light',
        'version': '1'
    }
]


def lambda_handler(request, context):
    try:
        logger.info("Directive:")
        logger.info(json.dumps(request, indent=4, sort_keys=True))

        version = get_directive_version(request)

        if version == "3":
            logger.info("Received V3 Directive!")
            if request["directive"]["header"]["name"] == "Discover":
                response = handle_discovery_v3(request)
            else:
                response = handle_non_discovery_v3(request)

        logger.info("Response:")
        logger.info(json.dumps(response, indent=4, sort_keys=True))

        return response

    except ValueError as error:
        logger.error(error)
        raise


# V3 Handlers
def handle_discovery_v3(request):
    endpoints = []
    for appliance in SMART_HOME_APPLIANCES:
        endpoints.append(get_endpoint_from_v2_appliance(appliance))

    response = {
        "event": {
            "header": {
                "namespace": "Alexa.Discovery",
                "name": "Discover.Response",
                "payloadVersion": "3",
                "messageId": get_uuid()
            },
            "payload": {
                "endpoints": endpoints
            }
        }
    }

    return response


def handle_non_discovery_v3(request):
    request_namespace = request["directive"]["header"]["namespace"]
    request_name = request["directive"]["header"]["name"]

    if request_namespace == "Alexa.PowerController":
        if request_name == "TurnOn":
            value = "ON"
            light_state = True
        else:
            value = "OFF"
            light_state = False

        # Update the thing shadow
        client.update_thing_shadow(
            thingName=request["directive"]["endpoint"]["endpointId"],
            payload=json.dumps({'state': {'desired': {'light': light_state}}}))

        response = {
            "context": {
                "properties": [
                    {
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": value,
                        "timeOfSample": get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 500
                    },
                    {
                        "namespace": "Alexa.EndpointHealth",
                        "name": "connectivity",
                        "value": {
                            "value": "OK"
                        },
                        "timeOfSample": get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 200
                    }
                ]
            },
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "Response",
                    "payloadVersion": "3",
                    "messageId": get_uuid(),
                    "correlationToken": request["directive"]["header"]["correlationToken"]
                },
                "endpoint": {
                    "scope": {
                        "type": "BearerToken",
                        "token": "access-token-from-Amazon"
                    },
                    "endpointId": request["directive"]["endpoint"]["endpointId"]
                },
                "payload": {}
            }
        }
        return response

    elif request_namespace == "Alexa.ThermostatController":

        if request_name == "SetTargetTemperature":
            # Using this accessing nomenclature will become problematic if dual
            # mode is used to set the thermostat. Check documenation API
            target_temp = request["directive"]["payload"]["targetSetpoint"]["value"]
            target_scale = request["directive"]["payload"]["targetSetpoint"]["scale"]

            # Update the thing shadow
            client.update_thing_shadow(
                thingName=request["directive"]["endpoint"]["endpointId"],
                payload=json.dumps({
                    'state': {
                        'desired': {
                            'value': target_temp,
                            'scale': target_scale
                        }
                    }
                })
            )

            response = {
                "context": {
                    "properties": [
                        {
                            "namespace": "Alexa.ThermostatController",
                            "name": "targetSetpoint",
                            "value": {
                                "value": target_temp,
                                "scale": target_scale
                            },
                            "timeOfSample": get_utc_timestamp(),
                            "uncertaintyInMilliseconds": 500
                        },
                        {
                            "namespace": "Alexa.EndpointHealth",
                            "name": "connectivity",
                            "value": {
                                "value": "OK"
                            },
                            "timeOfSample": get_utc_timestamp(),
                            "uncertaintyInMilliseconds": 200
                        }
                    ]
                },
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "Response",
                        "payloadVersion": "3",
                        "messageId": request["directive"]["header"]["messageId"],
                        "correlationToken": request["directive"]["header"]["correlationToken"]
                    },
                    "endpoint": {
                        "endpointId": request["directive"]["endpoint"]["endpointId"]
                    },
                    "payload": {}
                }
            }
            return response

        elif request_name == "AdjustTargetTemperature":
            target_delta_temp = request["directive"]["payload"]["targetSetpointDelta"]["value"]
            target_delta_scale = request["directive"]["payload"]["targetSetpointDelta"]["scale"]

            stream_obj = client.get_thing_shadow(thingName=request["directive"]["endpoint"]["endpointId"])
            current_thing_state = json.loads(stream_obj["payload"].read())

            current_thing_temp = current_thing_state["state"]["desired"]["value"]
            new_temp = current_thing_temp + target_delta_temp

            # Update the thing shadow
            client.update_thing_shadow(
                thingName=request["directive"]["endpoint"]["endpointId"],
                payload=json.dumps({
                    'state': {
                        'desired': {
                            'value': new_temp,
                            'scale': target_delta_scale
                        }
                    }
                })
            )

            response = {
                "context": {
                    "properties": [
                        {
                            "namespace": "Alexa.ThermostatController",
                            "name": "targetSetpoint",
                            "value": {
                                "value": new_temp,
                                "scale": target_delta_scale
                            },
                            "timeOfSample": get_utc_timestamp(),
                            "uncertaintyInMilliseconds": 500
                        },
                        {
                            "namespace": "Alexa.EndpointHealth",
                            "name": "connectivity",
                            "value": {
                                "value": "OK"
                            },
                            "timeOfSample": get_utc_timestamp(),
                            "uncertaintyInMilliseconds": 200
                        }
                    ]
                },
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "Response",
                        "payloadVersion": "3",
                        "messageId": request["directive"]["header"]["messageId"],
                        "correlationToken": request["directive"]["header"]["correlationToken"]
                    },
                    "endpoint": {
                        "endpointId": request["directive"]["endpoint"]["endpointId"]
                    },
                    "payload": {}
                }
            }
            return response

        elif request_name == "SetThermostatMode":
            target_mode = request["directive"]["payload"]["thermostatMode"]["value"]

            # Update the thing shadow
            client.update_thing_shadow(
                thingName=request["directive"]["endpoint"]["endpointId"],
                payload=json.dumps({
                    'state': {
                        'desired': {
                            'mode': target_mode
                        }
                    }
                })
            )

            response = {
                "context": {
                    "properties": [
                        {
                            "namespace": "Alexa.ThermostatController",
                            "name": "thermostatMode",
                            "value": target_mode,
                            "timeOfSample": get_utc_timestamp(),
                            "uncertaintyInMilliseconds": 500
                        },
                        {
                            "namespace": "Alexa.EndpointHealth",
                            "name": "connectivity",
                            "value": {
                                "value": "OK"
                            },
                            "timeOfSample": get_utc_timestamp(),
                            "uncertaintyInMilliseconds": 200
                        }
                    ]
                },
                "event": {
                    "header": {
                        "namespace": "Alexa",
                        "name": "Response",
                        "payloadVersion": "3",
                        "messageId": request["directive"]["header"]["messageId"],
                        "correlationToken": request["directive"]["header"]["correlationToken"]
                    },
                    "endpoint": {
                        "endpointId": request["directive"]["endpoint"]["endpointId"]
                    },
                    "payload": {}
                }
            }
            return response


# V3 Utility Functions
def get_uuid():
    return str(uuid.uuid4())


def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))


def get_endpoint_from_v2_appliance(appliance):
    endpoint = {"endpointId": appliance["applianceId"],
                "manufacturerName": appliance["manufacturerName"],
                "friendlyName": appliance["friendlyName"],
                "description": appliance["friendlyDescription"],
                "displayCategories": get_display_categories_from_v2_appliance(appliance),
                "cookie": appliance["additionalApplianceDetails"],
                "capabilities": get_capabilities_from_v2_appliance(appliance)}
    return endpoint


def get_directive_version(request):
    try:
        return request["directive"]["header"]["payloadVersion"]
    except:
        try:
            return request["header"]["payloadVersion"]
        except:
            return "-1"


def get_display_categories_from_v2_appliance(appliance):
    model_name = appliance["modelName"]

    if model_name == "Smart Light":
        display_categories = ["LIGHT"]

    elif model_name == "Smart Thermostat":
        display_categories = ["THERMOSTAT"]

    else:
        display_categories = ["OTHER"]

    return display_categories


def get_capabilities_from_v2_appliance(appliance):
    model_name = appliance["modelName"]

    if model_name == "Smart Light":
        capabilities = [
            {
                "type": "AlexaInterface",
                "interface": "Alexa.PowerController",
                "version": "3",
                "properties": {
                    "supported": [
                        {"name": "powerState"}
                    ],
                    "proactivelyReported": True,
                    "retrievable": True
                }
            }
        ]

    elif model_name == "Smart Thermostat":
        capabilities = [
            {
                "type": "AlexaInterface",
                "interface": "Alexa.ThermostatController",
                "version": "3",
                "properties": {
                    "supported": [
                        {"name": "targetSetpoint"},
                        {"name": "thermostatMode"}
                    ],
                    "proactivelyReported": True,
                    "retrievable": True
                }
            },
            {
                "type": "AlexaInterface",
                "interface": "Alexa.TemperatureSensor",
                "version": "3",
                "properties": {
                    "supported": [
                        {"name": "temperature"}
                    ],
                    "proactivelyReported": True,
                    "retrievable": True
                }
            }
        ]

    else:
        # in this example, just return simple on/off capability
        capabilities = [
            {
                "type": "AlexaInterface",
                "interface": "Alexa.PowerController",
                "version": "3",
                "properties": {
                    "supported": [
                        {"name": "powerState"}
                    ],
                    "proactivelyReported": True,
                    "retrievable": True
                }
            }
        ]

    # additional capabilities that are required for each endpoint
    endpoint_health_capability = {
        "type": "AlexaInterface",
        "interface": "Alexa.EndpointHealth",
        "version": "3",
        "properties": {
            "supported": [
                {"name": "connectivity"}
            ],
            "proactivelyReported": True,
            "retrievable": True
        }
    }
    alexa_interface_capability = {
        "type": "AlexaInterface",
        "interface": "Alexa",
        "version": "3"
    }
    capabilities.append(endpoint_health_capability)
    capabilities.append(alexa_interface_capability)
    return capabilities
