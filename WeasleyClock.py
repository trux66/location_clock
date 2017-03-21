#!/usr/bin/env python

"""
Name: WeasleyClock.py
Description: code to filter MQTT messages for location events
History:
    3/21 - clean up formating with pylint; using pep8 style
"""

import datetime
import getopt
import json
import logging
import sys

import paho.mqtt.client as mqtt


# provide switch/case type construct for python
class Switch(object):       # pylint: disable=too-few-public-methods
    """doc string"""

    def __init__(self, value):
        """init for class"""
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
        elif self.value in args:    # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


def transition_occured(time_stamp, data):
    """determine details of the transition event"""
    try:
        for case in Switch(data['event']):
            if case('enter'):
                print "{0} entered {1} at {2}".format(TID_NAMES[data['tid']],
                                                      data['desc'], time_stamp)
                break
            if case('leave'):
                print "{0} left {1} at {2}".format(TID_NAMES[data['tid']],
                                                   data['desc'], time_stamp)
                break
            if case():  # default
                print "I'm not sure what transition occured!"
    finally:    # this is not clean and should be managed better
        print "transition_occured() called but failed"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):    # pylint: disable=C0103, W0613
    """On Connect callback routine"""
    print "Connected with result code " + str(rc)
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("owntracks/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):  # pylint: disable=C0103, W0613
    """On Message callback"""
    logging.info('Topic: %s', str(msg.topic))
    logging.info('Payload: %s', str(msg.payload))

    topic = msg.topic
    data = json.loads(str(msg.payload))

    if data['_type'] in ('beacon', 'cmd', 'steps', 'configuration', 'card',
                         'waypoint', 'waypoints', 'encrypted'):
        print "Payload is of _type {0}, but I don't care about \
                that type.".format(data['_type'])
        return

    try:    # see if we can do something based on the _type of message received
        time_stamp = datetime.datetime.fromtimestamp(
            data['tst']).strftime('%d-%b-%Y %I:%M:%S %p %Z')
        for case in Switch(data['_type']):
            if case('lwt'):
                print "Topic {0} is in mortal peril!".format(topic)
                break
            if case('location'):
                print "{0} was at {1}, {2} on {3}".format(TID_NAMES[
                    data['tid']], data['lat'], data['lon'], time_stamp)
                break
            if case('transition'):
                transition_occured(time_stamp, data)
                break
            if case():  # default
                print "I don't know what the payload is!"
    finally:    # no specific exception handler so just log and keep going
        logging.info('Failed to Decode data: %s', str(msg.payload))
        print "Failed to decode data on topic {0}".format(topic)
        print "Received message '" + str(msg.payload) + "' on topic '" \
            + msg.topic + "' with QoS " + str(msg.qos)


# The callback for when the client wants to capture log information
def on_log(client, userdata, level, buf):  # pylint: disable=C0103, W0613
    """Log information from paho is added for DEBUG level logging only."""
    logging.debug("on_log: %s", buf)


def main(argv):
    """main code loop"""
    log_level = 'INFO'   # default level of logging
    tls_option = 'OFF'   # default is TLS Off

    try:
        # opts, args = getopt.getopt(argv, "h", ["log=", "tls="])[0]
        opts = getopt.getopt(argv, "h", ["log=", "tls="])[0]
    except getopt.GetoptError:
        print 'Usage: WeasleyClock.py --log=[DEBUG, INFO, WARNING, \
                ERROR, CRITICAL] --tls=[ON, OFF]'
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print 'Usage: WeasleyClock.py --log=[DEBUG, INFO, WARNING, \
                    ERROR, CRITICAL] --tls=[ON, OFF]'
            sys.exit(0)
        elif opt == ("--log"):
            '''
            assuming loglevel is bound to the string value obtained from the
            command line argument. Convert to upper case to allow the user to
            specify --log=DEBUG or --log=debug
            '''
            log_level = arg
            numeric_level = getattr(logging, log_level.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % log_level)
            logging.basicConfig(level=numeric_level,
                                filename='WeasleyClock.log',
                                format='[%(levelname)s: %(asctime)s]: \
                                        %(message)s',
                                datefmt='%m/%d/%Y %I:%M:%S %p')
        elif opt == ("--tls"):
            tls_option = arg

    # load the mqtt login credentials from a file
    try:
        with open('.mqttcredentials', 'r') as filename:
            user, pwd = filename.readline().strip().split(':')
    except IOError:
        print 'Problem loading MQTT Credentials file (.mqttcredentials)'
        sys.exit(1)

    # setup mqtt client options then connect
    client = mqtt.Client()
    client.username_pw_set(user, pwd)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_log = on_log

    if tls_option.upper() == 'ON':
        client.tls_set("/etc/ssl/certs/ca-certificates.crt")
        client.connect("m13.cloudmqtt.com", 28497, 60)
    elif tls_option.upper() == 'OFF':
        client.connect("m13.cloudmqtt.com", 18497, 60)

    '''
    Blocking call that processes network traffic, dispatches callbacks and
    handles reconnecting.
    Other loop*() functions are available that give a threaded interface and a
    manual interface.
    '''
    client.loop_forever()


if __name__ == "__main__":
    TID_NAMES = {'bc': 'Bruce', 'tc': 'Tracey', 'cc': 'Collin',
                 'ba': 'Andrew', 'ac': 'Allyson', 'ec': 'Ethan'}
    main(sys.argv[1:])
