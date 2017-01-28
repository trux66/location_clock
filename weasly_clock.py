import paho.mqtt.client as mqtt
import json
import datetime

# provide switch/case type construct for python
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
    
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("owntracks/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  topic = msg.topic
  try:
    data = json.loads(str(msg.payload))
    dt = datetime.datetime.fromtimestamp(data['tst']).strftime(
      '%d-%b-%Y %I:%M:%S %p %Z')
    for case in switch(data['_type']):
      if case('location'):
        print "TID = {0} was at {1}, {2} on {3}".format(
          data['tid'], data['lat'], data['lon'], dt)
        break
      if case('lwt'):
        print "TID = {0} is in mortal peril! at {1}".format(data['tid'], dt)
        break
      if case('waypoint'):
        print "TID = {0} reached waypoint {1} on {2}".format(data['tid'], data['desc'], dt)
        break
      if case('transition'):
        for case in switch(data['event']):
          if case('enter'):
            print "TID = {0} entered {1} on {2}".format(data['tid'], data['desc'], dt)
            break
          if case('leave'):
            print "TID = {0} left {1} on {2}".format(data['tid'], data['desc'], dt)
            break
          if case(): # default
            print "Not sure what happened in this transition"
        break
      if case('beacon', 'cmd', 'steps', 'configuration', 'card', 'waypoints', 'encrypted'):
        print "payload is valid but I don't care about it"
        break
      if case(): # default
        print "I don't know what the payload is!"
  except:
    print "Cannot decode data on topic {0}".format(topic)
    print("Received message '" + str(msg.payload) + "' on topic '" 
      + msg.topic + "' with QoS " + str(msg.qos))


client = mqtt.Client()
client.username_pw_set("Node-RED","hass3665")
#client.tls_set("/etc/ssl/certs/ca-certificates.crt")
client.on_connect = on_connect
client.on_message = on_message

client.connect("m13.cloudmqtt.com", 18497, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
