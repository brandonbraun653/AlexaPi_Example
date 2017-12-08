import logging
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('iot-data')


def lambda_handler(event, context):
    logger.info('got event{}'.format(event))
    access_token = event['payload']['accessToken']

    if (event['header']['namespace'] == 'Alexa.ConnectedHome.Discovery' and
                event['header']['name'] == 'DiscoverAppliancesRequest'):
        return handleDiscovery(context, event)

    elif event['header']['namespace'] == 'Alexa.ConnectedHome.Control':
        return handleControl(context, event)


def handleDiscovery(context, event):
    return {
        'header': {
            'messageId': event['header']['messageId'],
            'name': 'DiscoverAppliancesResponse',
            'namespace': 'Alexa.ConnectedHome.Discovery',
            'payloadVersion': '2'
        },
        'payload': {
            'discoveredAppliances': [
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
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
                    'modelName': '1',
                    'version': '1'
                }
            ]
        }
    }


def handleControl(context, event):
    device_id = event['payload']['appliance']['applianceId']
    requestType = event['header']['name']

    if requestType == 'TurnOnRequest':
        name = 'TurnOnConfirmation'
        light = True

    elif requestType == 'TurnOffRequest':
        name = 'TurnOffConfirmation'
        light = False

    # elif requestType == 'SetTargetTemperatureRequest':
    # name = ''

    logger.info('turning %s %s' % ('on' if light else 'off', device_id))

    response = client.update_thing_shadow(
        thingName=device_id,
        payload=json.dumps({
            'state': {
                'desired': {
                    'light': light
                }
            }
        })
    )

    logger.info('received {}'.format(response))

    return {
        'header': {
            "messageId": event['header']['messageId'],
            "name": name,
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"
        },
        'payload': {}
    }