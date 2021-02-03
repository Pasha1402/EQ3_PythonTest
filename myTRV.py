import paho.mqtt.client as mqtt
import time
from eq3bt import Thermostat
from eq3bt import Mode

class myTRV:

    MAC = None
    gateTopic = None
    trvName = None
    trv = None
    mqttClient = None
    mqttGateTopic = None
    extTemp = 0
    logger = None

    def __init__(self, MAC):
        self.MAC = MAC
        self.trv = Thermostat(MAC)

    def trvReadStateJSON(self):
        readSuccess = True
        try:
            self.trv.update()
        except:
            time.sleep(5)
            self.logger.error("RS1: Failed to communicate with " + self.trvName)
            try:
                self.trv.update()
            except:
                self.logger.error("RS2: Failed to communicate with " + self.trvName)
                readSuccess = False

        outputValues = "{\"trv\":\""
        outputValues += self.MAC

        if readSuccess:
            outputValues += "\",\"temp\":\""
            outputValues += str(self.trv.target_temperature)
            outputValues += "\",\"ctemp\":\""
            outputValues += str(self.trv.target_temperature) if self.extTemp==0 else str(self.extTemp)
            outputValues += "\",\"mode\":\""
            outputValues += self.homeAssistantMode(self.trv.mode.value)
            outputValues += "\",\"boost\":\""
            outputValues += "active" if self.trv.boost else "inactive"
            outputValues += "\",\"valve\":\""
            outputValues += str(self.trv.valve_state)
            outputValues += "\",\"locked\":\""
            outputValues += "locked" if self.trv.locked else "unlocked"
            outputValues += "\",\"battery\":\""
            outputValues += "0" if self.trv.low_battery else "100"
            outputValues += "\",\"window\":\""
            outputValues += "open" if self.trv.window_open else "closed"
            outputValues += "\",\"error\":\"\"}"
        else:
            outputValues += "\",\"error\":\"connection failed\"}"
        return outputValues

    def eq3Mode(self, homeAssistantModeIn):
        modeToSet = str(homeAssistantModeIn)
        modeToSet = modeToSet.lower()
        eq3ObjMode = Mode(3)
        if modeToSet=="auto": eq3ObjMode = Mode(2)
        if modeToSet=="off": eq3ObjMode = Mode(0)
        if modeToSet=="on": eq3ObjMode = Mode(1)
        if modeToSet=="boost": eq3ObjMode = Mode(5)
        return eq3ObjMode

    def homeAssistantMode(self, eq3ModeIn):
        switcher={
            -1:"unknown",
            0:"off",
            1:"heat",
            2:"auto",
            3:"heat",
            4:"off",
            5:"heat"
            }
        return switcher.get(eq3ModeIn,"unknown")

    def PublishState(self):
        trvCurrentState = self.trvReadStateJSON()
        try:
            self.mqttClient.publish(self.mqttGateTopic + self.trvName + "/status", trvCurrentState)
        except:
            time.sleep(5)
            self.logger.error("Failed to publish state")
            try:
                self.mqttClient.publish(self.mqttGateTopic + self.trvName + "/status", trvCurrentState)
            except:
                self.logger.error("Failed to publish state")

    def ModeSet(self, newMode):
        try:
            self.trv.mode = self.eq3Mode(newMode)
        except:
            time.sleep(5)
            self.logger.error("SM1: Failed to communicate with " + self.trvName)
            try:
                self.trv.mode = self.eq3Mode(newMode)
            except:
                self.logger.error("SM2: Failed to communicate with " + self.trvName)
        self.PublishState()

    def TempSet(self, newTemp):

        if (float(str(newTemp))<=4.5): self.ModeSet("off")
        if (float(str(newTemp))>=30): self.ModeSet("on")
        try:
            self.trv.target_temperature = float(str(newTemp))
        except:
            time.sleep(5)
            self.logger.error("ST1: Failed to communicate with " + self.trvName)
            try:
                self.trv.target_temperature = float(str(newTemp))
            except:
                self.logger.error("ST2: Failed to communicate with " + self.trvName)
        self.PublishState()


