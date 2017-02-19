import paho.mqtt.client as mqtt
import json, datetime, logging, sys, getopt


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


def transition_occured(dt, data):
  try:  # we even make it into the module?
    for case in switch(data['event']):
      if case('enter'):
        print "{0} entered {1} at {2}".format(tidNames[data['tid']], data['desc'], dt)
        break
      if case('leave'):
        print "{0} left {1} at {2}".format(tidNames[data['tid']], data['desc'], dt)
        break
      if case():  # default
        print "I'm not sure what transition occured!"
  except:
    print "transition_occured called but failed"

      
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  client.subscribe("owntracks/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  logging.info('Topic: %s', str(msg.topic))
  logging.info('Payload: %s', str(msg.payload))

  topic = msg.topic
  data = json.loads(str(msg.payload))

  if data['_type'] in ('beacon', 'cmd', 'steps', 'configuration', 'card', \
        'waypoint', 'waypoints', 'encrypted'):
    print "Payload is of _type {0}, but I don't care about that type.".format(data['_type'])
    return

  try: # see if we can do something based on the _type of message received
    dt = datetime.datetime.fromtimestamp(data['tst']).strftime('%d-%b-%Y %I:%M:%S %p %Z')
    for case in switch(data['_type']):
      if case('lwt'):
        print "Topic {0} is in mortal peril!".format(topic)
        break
      if case('location'):
        print "{0} was at {1}, {2} on {3}".format(tidNames[data['tid']], \
            data['lat'], data['lon'], dt)
        break
      if case('transition'):
        transition_occured(dt, data)
        break
      if case(): # default
        print "I don't know what the payload is!"
  except:
    print "Cannot decode data on topic {0}".format(topic)
    print("Received message '" + str(msg.payload) + "' on topic '" \
      + msg.topic + "' with QoS " + str(msg.qos))


# The callback for when the client wants to capture log information
def on_log(client, userdata, level, buf):
  logging.debug("on_log: %s", buf)


def main(argv):
  logLevel = 'INFO'   # default level of logging
  tlsOption = 'OFF'   # default is TLS Off

  try:
    opts, args = getopt.getopt(argv, "h", ["log=", "tls="])
  except getopt.GetoptError:
    print 'WeasleyClock.py --log=[DEBUG, INFO, WARNING, ERROR, CRITICAL] --tls=[ON, OFF]'
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print 'WeasleyClock.py --log=[DEBUG, INFO, WARNING, ERROR, CRITICAL] --tls=[ON, OFF]'
      sys.exit()
    elif opt == ("--log"):
      '''
        assuming loglevel is bound to the string value obtained from the
        command line argument. Convert to upper case to allow the user to
        specify --log=DEBUG or --log=debug
      '''
      logLevel = arg
      numeric_level = getattr(logging, logLevel.upper(), None)
      if not isinstance(numeric_level, int):
          raise ValueError('Invalid log level: %s' % logLevel)
      logging.basicConfig(level=numeric_level, filename='WeasleyClock.log', 
        format='[%(levelname)s: %(asctime)s]: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    elif opt == ("--tls"):
      tlsOption = arg

  # setup mqtt client options then connect
  client = mqtt.Client()
  client.username_pw_set("hass","hass3665")
  client.on_connect = on_connect
  client.on_message = on_message
  client.on_log = on_log

  if tlsOption.upper() == 'ON':
    client.tls_set("/etc/ssl/certs/ca-certificates.crt")
    client.connect("m13.cloudmqtt.com", 28497, 60)
  elif tlsOption.upper() == 'OFF':
    client.connect("m13.cloudmqtt.com", 18497, 60)

  '''
    Blocking call that processes network traffic, dispatches callbacks and
    handles reconnecting.
    Other loop*() functions are available that give a threaded interface and a
    manual interface.
  '''
  client.loop_forever()

if __name__ == "__main__":
  tidNames = {'bc':'Bruce', 'tc':'Tracey', 'cc':'Collin', \
    'ba':'Andrew', 'ac':'Allyson', 'ec':'Ethan'}
  main(sys.argv[1:])
