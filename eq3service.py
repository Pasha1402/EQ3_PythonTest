#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import time
from eq3bt import Thermostat
from eq3bt import Mode
import logging
import logging.handlers as handlers
import sys

sys.path.append('/home/pasha')

logger = logging.getLogger('my_app')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logHandler = handlers.RotatingFileHandler('app.log', maxBytes=20000, backupCount=1)
logHandler.setLevel(logging.INFO)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

import myTRV

mqttGateTopic = "EQ3_Gate/Gate-Bedroom/"

logger.info("EQ3 Gate Started")

broker_address = "mybrokerIP"
client = mqtt.Client("EQ3Gate")
client.username_pw_set("user", "password")
try:
    client.connect(broker_address, keepalive=90)
    logger.info("Conected to Broker")
except:
    logger.error("Connecting to Broker failed")

trv1ModeTopic = mqttGateTopic + "Bedroom/mode"
trv1TempTopic = mqttGateTopic + "Bedroom/temp"
trv1CTempTopic = mqttGateTopic + "Bedroom/ctemp"
trv2ModeTopic = mqttGateTopic + "Dressing/mode"
trv2TempTopic = mqttGateTopic + "Dressing/temp"
trv2CTempTopic = mqttGateTopic + "Dressing/ctemp"
trv3ModeTopic = mqttGateTopic + "Danny/mode"
trv3TempTopic = mqttGateTopic + "Danny/temp"
trv3CTempTopic = mqttGateTopic + "Danny/ctemp"

trv1 = myTRV.myTRV("00:1A:22:XX:XX:XX")
trv1.gateTopic = mqttGateTopic
trv1.trvName = "Bedroom"
trv1.mqttGateTopic = mqttGateTopic
trv1.mqttClient = client
trv1.logger = logger

trv2 = myTRV.myTRV("00:1A:22:XX:XX:XX")
trv2.gateTopic = mqttGateTopic
trv2.trvName = "Dressing"
trv2.mqttClient = client
trv2.mqttGateTopic = mqttGateTopic
trv2.logger = logger

trv3 = myTRV.myTRV("00:1A:22:XX:XX:XX")
trv3.gateTopic = mqttGateTopic
trv3.trvName = "Danny"
trv3.mqttClient = client
trv3.mqttGateTopic = mqttGateTopic
trv3.logger = logger

autoPublish1 = True
autoPublish2 = True
autoPublish3 = True


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.error("Unexpected MQTT disconnection. Will auto-reconnect")


def on_connect(client, userdata, flags, rc):
    logger.info("Client connected. Subscribing...")
    client.subscribe(mqttGateTopic + "#")


def on_message_mode1(client, userdata, message):
    autoPublish1 = False
    trv1.ModeSet(message.payload.decode("utf-8"))


def on_message_temp1(client, userdata, message):
    autoPublish1 = False
    trv1.TempSet(message.payload.decode("utf-8"))


def on_message_mode2(client, userdata, message):
    autoPublish2 = False
    trv2.ModeSet(message.payload.decode("utf-8"))


def on_message_temp2(client, userdata, message):
    autoPublish2 = False
    trv2.TempSet(message.payload.decode("utf-8"))


def on_message_mode3(client, userdata, message):
    autoPublish3 = False
    trv3.ModeSet(message.payload.decode("utf-8"))


def on_message_temp3(client, userdata, message):
    autoPublish3 = False
    trv3.TempSet(message.payload.decode("utf-8"))


def on_message_ctemp1(client, userdata, message):
    try:
        trv1.extTemp = float(message.payload.decode("utf-8"))
    except:
        logger.error("Bad message for ctemp1")


def on_message_ctemp2(client, userdata, message):
    try:
        trv2.extTemp = float(message.payload.decode("utf-8"))
    except:
        logger.error("Bad message for ctemp2")


def on_message_ctemp3(client, userdata, message):
    try:
        trv3.extTemp = float(message.payload.decode("utf-8"))
    except:
        logger.error("Bad message for ctemp3")


client.message_callback_add(trv1ModeTopic, on_message_mode1)
client.message_callback_add(trv1TempTopic, on_message_temp1)
client.message_callback_add(trv2ModeTopic, on_message_mode2)
client.message_callback_add(trv2TempTopic, on_message_temp2)
client.message_callback_add(trv3ModeTopic, on_message_mode3)
client.message_callback_add(trv3TempTopic, on_message_temp3)
client.message_callback_add(trv1CTempTopic, on_message_ctemp1)
client.message_callback_add(trv2CTempTopic, on_message_ctemp2)
client.message_callback_add(trv3CTempTopic, on_message_ctemp3)

client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.loop_start()
# client.subscribe(mqttGateTopic + "#")

while True:
    if autoPublish1: trv1.PublishState()
    if autoPublish2: trv2.PublishState()
    if autoPublish3: trv3.PublishState()

    autoPublish1 = True
    autoPublish2 = True
    autoPublish3 = True

    time.sleep(600)
